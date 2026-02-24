# Copyright (c) 2025, hussain@frappe.io and contributors
# For license information, please see license.txt

import frappe
# defaultdict is a subclass of dict that calls a factory function to supply missing values.
from collections import defaultdict

# This is the main entry point for the report.
# It instantiates the DonationDistributionReport class and runs it.
def execute(filters=None):
    # Create an instance of the DonationDistributionReport class, passing any filters.
    report = DonationDistributionReport(filters)
    # Run the report and return its results.
    return report.run()

# Defines the DonationDistributionReport class which encapsulates the logic for generating the report.
class DonationDistributionReport:
    # Constructor for the class. Initializes report properties.
    def __init__(self, filters=None):
        # Store the filters, ensuring they are a frappe._dict for easier access.
        self.filters = frappe._dict(filters or {})
        # Initialize an empty list to hold the report data rows.
        self.data = []
        # Initialize an empty list to hold the column definitions for the report.
        self.columns = []
        # Initialize chart data to None. It will be populated later if a chart is needed.
        self.chart = None
        # Initialize an empty list to hold the summary statistics for the report.
        self.report_summary = []

    # This method orchestrates the report generation process.
    def run(self):
        # Get the column definitions for the report.
        self.columns = self.get_columns()
        # Get the main data for the report.
        self.data = self.get_data()
        # Prepare the data for the chart.
        self.get_chart_data()
        # Calculate and set the report summary.
        self.get_report_summary()
        # Return all the components needed to render the report in Frappe.
        return self.columns, self.data, None, self.chart, self.report_summary

    # Defines the columns that will be displayed in the report.
    def get_columns(self):
        # Basic columns that are always included.
        columns = [
            # Link to the 'Donation' DocType, with specific width.
            {"label": "Donation", "fieldname": "donation", "fieldtype": "Link", "options": "Donation", "width": 230},
            # Link to the 'Donor' DocType, with specific width.
            {"label": "Donor", "fieldname": "donor", "fieldtype": "Link", "options": "Donor", "width": 150},
        ]

        # Conditionally add 'Pledged Amount' column if the filter 'show_total_pledged' is true.
        if self.filters.get("show_total_pledged"):
            columns.append({"label": "Pledged Amount", "fieldname": "pledged_amount", "fieldtype": "Currency", "width": 150})

        # Conditionally add 'Total Paid Amount' column if the filter 'show_total_paid' is true.
        if self.filters.get("show_total_paid"):
            columns.append({"label": "Total Paid Amount", "fieldname": "total_amount_paid", "fieldtype": "Currency", "width": 150})

        # Conditionally add 'Total Distributed Amount' column if the filter 'show_total_distributed' is true.
        if self.filters.get("show_total_distributed"):
            columns.append({"label": "Total Distributed Amount", "fieldname": "amount_distributed", "fieldtype": "Currency", "width": 170})

        # Additional columns that are always included.
        columns += [
            # Link to the 'Donation Allocation' DocType.
            {"label": "Distribution", "fieldname": "distribution", "fieldtype": "Link", "options": "Donation Allocation", "width": 150},
            # Date field for distribution date.
            {"label": "Date", "fieldname": "distribution_date", "fieldtype": "Date", "width": 150},
            # Currency field for total amount.
            {"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
            # Currency field for allocated amount.
            {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150},
            # Percentage field for allocation percentage.
            {"label": "Percentage", "fieldname": "percentage", "fieldtype": "Percent", "width": 150},
            # Data field for recipient type.
            {"label": "Recipient Type", "fieldname": "recipient_type", "fieldtype": "Data", "width": 150},
            # Dynamic Link field where options depend on 'recipient_type'.
            {"label": "Recipient", "fieldname": "recipient", "fieldtype": "Dynamic Link", "options": "recipient_type", "width": 150},
            # Data field for general/admin allocation.
            {"label": "General/ Admin", "fieldname": "general_admin", "fieldtype": "Data", "width": 150},
            # Link to the 'Project' DocType.
            {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
            # Text field for remarks.
            {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Text", "width": 200},
        ]

        return columns

    # Fetches and structures the data for the report.
    def get_data(self):
        filters = self.filters # Shorthand for easier access to filters.
        frappe_filters = {} # Filters for the 'Donation Allocation' DocType.
        item_filters = {} # Filters for the 'Donation Allocation Item' DocType.

        # Apply date filters if provided.
        if filters.get("from_date"):
            frappe_filters["date"] = [">=", filters.get("from_date")]
        if filters.get("to_date"):
            # Use setdefault to ensure 'date' is a list before extending.
            frappe_filters.setdefault("date", []).extend(["<=", filters.get("to_date")])
        # Apply donation filter if provided.
        if filters.get("donation"):
            frappe_filters["donation"] = filters.get("donation")
        # Apply donor filter if provided.
        if filters.get("donor"):
            frappe_filters["donor"] = filters.get("donor")

        # Apply recipient type and specific recipient filters.
        if filters.get("recipient_type"):
            item_filters["recipient_type"] = filters["recipient_type"]

            recipient_type = filters["recipient_type"]
            # Map recipient types to their corresponding field names in Donation Allocation Item.
            recipient_field_map = {
                "Beneficiary": "beneficiary",
                "Student": "student",
                "Learning Centre": "learning_centre",
                "Budget": "budget",
                "Employee": "employee"
            }

            specific_fieldname = recipient_field_map.get(recipient_type)
            if specific_fieldname:
                recipient_value = filters.get(specific_fieldname)
                if recipient_value:
                    item_filters["recipient"] = recipient_value

        # Apply general/admin filter if provided. Using 'like' for partial matching.
        if filters.get("general_admin"):
            item_filters["general_admin"] = ["like", f"%{filters['general_admin']}%"]

        # Apply project filter if provided.
        if filters.get("project"):
            item_filters["project"] = filters["project"]

        # Adjust date filter format for 'between' clause if both from and to dates are present.
        if isinstance(frappe_filters.get("date"), list) and len(frappe_filters["date"]) > 2:
            # Extract the actual dates (second and fourth elements after modification).
            dates = frappe_filters.pop("date")[1::2]
            frappe_filters["date"] = ["between", dates]

        # Fetch Donation Allocations based on filters.
        distributions = frappe.get_all(
            "Donation Allocation",
            filters=frappe_filters,
            fields=["name", "donation", "donor", "date as distribution_date", "total_amount", "remarks"],
            order_by="donation, date ASC" # Order for consistent grouping.
        )

        # If no distributions are found, return an empty list.
        if not distributions:
            return []

        # Get a list of names (IDs) of the fetched distributions.
        distribution_names = [d.name for d in distributions]
        # Set the parent filter for Donation Allocation Items to include only relevant distributions.
        item_filters["parent"] = ["in", distribution_names]

        # Fetch Donation Allocation Items related to the distributions.
        items = frappe.get_all(
            "Donation Allocation Item",
            filters=item_filters,
            fields=["parent", "amount", "percentage", "recipient_type", "recipient", "project", "general_admin"],
            order_by="parent, idx" # Order for consistent item display within allocations.
        )

        # Group items by their parent (Donation Allocation name).
        items_by_distribution = {}
        for item in items:
            items_by_distribution.setdefault(item.parent, []).append(item)

        # Filter out distributions that have no associated items after item filtering.
        distributions = [d for d in distributions if d.name in items_by_distribution]
        # Get unique donation names from the filtered distributions.
        donation_names = list(set(d.donation for d in distributions))

        donations = []
        # Fetch Donation details for the relevant donations.
        if donation_names:
            donations = frappe.get_all(
                "Donation",
                filters={"name": ["in", donation_names]},
                fields=["name", "donor", "amount as pledged_amount", "total_amount_paid", "amount_distributed"],
                order_by="creation DESC"
            )

        # Fetch donor names for display.
        donor_names = {}
        donor_ids = list(set([d.donor for d in donations if d.donor])) # Get unique donor IDs.
        if donor_ids:
            for d in frappe.get_all("Donor", filters={"name": ["in", donor_ids]}, fields=["name", "donor_name"]):
                donor_names[d.name] = d.donor_name

        # Group distributions by donation.
        distributions_by_donation = {}
        for dist in distributions:
            distributions_by_donation.setdefault(dist.donation, []).append(dist)

        # Create a map for quick lookup of donation details by name.
        donation_map = {d.name: d for d in donations}
        data = [] # List to store the final structured report data.

        # Iterate through each donation to build the hierarchical report data.
        for donation_name in distributions_by_donation.keys():
            donation = donation_map.get(donation_name)
            if not donation:
                continue # Skip if donation details are not found.

            donor_name = donor_names.get(donation.donor, "")
            distributions_for_donation = distributions_by_donation.get(donation.name, [])

            # Get the first distribution and its items for this donation.
            first_dist = distributions_for_donation[0] if distributions_for_donation else None
            first_items = items_by_distribution.get(first_dist.name, []) if first_dist else []
            first_item = first_items[0] if first_items else None

            # Create the main row for the donation (group header).
            row = {
                "donation": donation.name,
                "donor": donation.donor,
                "donor_name": donor_name,
                "pledged_amount": donation.pledged_amount,
                "total_amount_paid": donation.total_amount_paid or 0,
                "amount_distributed": donation.amount_distributed or 0,
                "is_group": 1, # Flag to indicate this is a group row.
                "bold": 1, # Make this row bold.
                "indent": 0 # No indent for the main donation row.
            }

            # Add details from the first distribution and its first item to the main donation row.
            if first_dist:
                row.update({
                    "distribution": first_dist.name,
                    "distribution_date": first_dist.distribution_date,
                    "total_amount": first_dist.total_amount,
                    "remarks": first_dist.remarks
                })
                if first_item:
                    row.update({
                        "amount": first_item.amount,
                        "percentage": first_item.percentage,
                        "recipient_type": first_item.recipient_type,
                        "recipient": first_item.recipient,
                        "project": first_item.project,
                        "general_admin": first_item.general_admin
                    })

            data.append(row) # Add the donation group row to the report data.

            # Add subsequent items of the first distribution as indented rows.
            for item in first_items[1:]:
                data.append({
                    "donation": "", "donor": "", "donor_name": "", "pledged_amount": "",
                    "total_amount_paid": "", "amount_distributed": "",
                    "distribution": "", "distribution_date": "", "total_amount": "",
                    "amount": item.amount, "percentage": item.percentage,
                    "recipient_type": item.recipient_type, "recipient": item.recipient,
                    "project": item.project, "remarks": "", "indent": 1, # Indent for items.
                    "general_admin": item.general_admin
                })

            # Iterate through subsequent distributions (after the first one) for the current donation.
            for dist in distributions_for_donation[1:]:
                items = items_by_distribution.get(dist.name, [])
                if not items:
                    continue

                first_item_of_dist = items[0]
                # Create a row for the current distribution.
                dist_row = {
                    "donation": "", "donor": "", "donor_name": "", "pledged_amount": "",
                    "total_amount_paid": "", "amount_distributed": "",
                    "distribution": dist.name, "distribution_date": dist.distribution_date,
                    "total_amount": dist.total_amount, "remarks": dist.remarks,
                    "is_group": 1, "bold": 0, "indent": 1, # Indent for distributions under a donation.
                    "amount": first_item_of_dist.amount, "percentage": first_item_of_dist.percentage,
                    "recipient_type": first_item_of_dist.recipient_type, "recipient": first_item_of_dist.recipient,
                    "project": first_item_of_dist.project,
                    "general_admin": first_item_of_dist.general_admin
                }

                data.append(dist_row) # Add the distribution row to the report data.

                # Add subsequent items of the current distribution as further indented rows.
                for item in items[1:]:
                    data.append({
                        "donation": "", "donor": "", "donor_name": "", "pledged_amount": "",
                        "total_amount_paid": "", "amount_distributed": "",
                        "distribution": "", "distribution_date": "", "total_amount": "",
                        "amount": item.amount, "percentage": item.percentage,
                        "recipient_type": item.recipient_type, "recipient": item.recipient,
                        "project": item.project, "remarks": "", "indent": 2, # Further indent for items under distributions.
                        "general_admin": item.general_admin
                    })

        return data

    # Prepares data for the chart visualization.
    def get_chart_data(self):
        # Use defaultdict to easily aggregate amounts for each donation.
        summary_map = defaultdict(lambda: {"pledged": 0, "paid": 0, "distributed": 0})

        # Iterate through the report data to aggregate values.
        for row in self.data:
            donation = row.get("donation")
            if not donation:
                continue # Skip rows that are not primary donation rows.

            indent = row.get("indent", 0)

            # Only process rows with indent 0, which are the main donation rows.
            if indent == 0:
                summary_map[donation]["pledged"] = row.get("pledged_amount", 0)
                summary_map[donation]["paid"] = row.get("total_amount_paid", 0)
                summary_map[donation]["distributed"] = row.get("amount_distributed", 0)

        items = list(summary_map.items()) # Convert the defaultdict to a list of (key, value) pairs.

        sorted_data = items # Data is already sorted by donation name implicitly from the defaultdict keying.

        # Structure the chart data in a format suitable for Frappe charts.
        self.chart = {
            "data": {
                "labels": [d[0] for d in sorted_data], # Donation names as labels.
                "datasets": [
                    {
                        "name": "Pledged Amount",
                        "values": [d[1]["pledged"] for d in sorted_data]
                    },
                    {
                        "name": "Paid Amount",
                        "values": [d[1]["paid"] for d in sorted_data]
                    },
                    {
                        "name": "Distributed Amount",
                        "values": [d[1]["distributed"] for d in sorted_data]
                    }
                ]
            },
            "type": "bar", # Type of chart (bar chart).
            "fieldtype": "Currency", # Data type for values in the chart.
            "height": 300 # Height of the chart.
        }

    # Calculates and sets the summary metrics for the report.
    def get_report_summary(self):
        total_pledged = 0
        total_paid = 0
        total_distributed = 0

        # Iterate through the report data to sum up totals.
        for row in self.data:
            # Only consider the main donation rows (indent 0) to avoid double counting.
            if row.get("indent", 0) == 0:
                total_pledged += row.get("pledged_amount") or 0
                total_paid += row.get("total_amount_paid") or 0
                total_distributed += row.get("amount_distributed") or 0

        # Format the summary data for display in the report header.
        self.report_summary = [
            {
                "label": "Total Pledged Amount",
                "value": total_pledged,
                "datatype": "Currency",
                "indicator": "blue" # Visual indicator color.
            },
            {
                "label": "Total Paid Amount",
                "value": total_paid,
                "datatype": "Currency",
                "indicator": "green"
            },
            {
                "label": "Total Distributed Amount",
                "value": total_distributed,
                "datatype": "Currency",
                "indicator": "orange"
            }
        ]