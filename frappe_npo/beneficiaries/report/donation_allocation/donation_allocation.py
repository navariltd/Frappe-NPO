# Copyright (c) 2025, hussain@frappe.io and contributors
# For license information, please see license.txt

import frappe
from collections import defaultdict

def execute(filters=None):
    report = DonationDistributionReport(filters)
    return report.run()

class DonationDistributionReport:
    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})
        self.data = []
        self.columns = []
        self.chart = None
        self.report_summary = []

    def run(self):
        self.columns = self.get_columns()
        self.data = self.get_data()
        self.get_chart_data()
        self.get_report_summary()
        return self.columns, self.data, None, self.chart, self.report_summary

    def get_columns(self):
        columns = [
            {"label": "Donation", "fieldname": "donation", "fieldtype": "Link", "options": "Donation", "width": 230},
            {"label": "Donor", "fieldname": "donor", "fieldtype": "Link", "options": "Donor", "width": 150},
        ]

        if self.filters.get("show_total_pledged"):
            columns.append({"label": "Pledged Amount", "fieldname": "pledged_amount", "fieldtype": "Currency", "width": 150})

        if self.filters.get("show_total_paid"):
            columns.append({"label": "Total Paid Amount", "fieldname": "total_amount_paid", "fieldtype": "Currency", "width": 150})

        if self.filters.get("show_total_distributed"):
            columns.append({"label": "Total Distributed Amount", "fieldname": "amount_distributed", "fieldtype": "Currency", "width": 170})

        columns += [
            {"label": "Distribution", "fieldname": "distribution", "fieldtype": "Link", "options": "Donation Allocation", "width": 150},
            {"label": "Date", "fieldname": "distribution_date", "fieldtype": "Date", "width": 150},
            {"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150},
            {"label": "Percentage", "fieldname": "percentage", "fieldtype": "Percent", "width": 150},
            {"label": "Recipient Type", "fieldname": "recipient_type", "fieldtype": "Data", "width": 150},
            {"label": "Recipient", "fieldname": "recipient", "fieldtype": "Dynamic Link", "options": "recipient_type", "width": 150},
            {"label": "General/ Admin", "fieldname": "general_admin", "fieldtype": "Data", "width": 150},
            {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
            {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Text", "width": 200},
        ]

        return columns


    def get_data(self):
        filters = self.filters
        frappe_filters = {}
        item_filters = {}

        if filters.get("from_date"):
            frappe_filters["date"] = [">=", filters.get("from_date")]
        if filters.get("to_date"):
            frappe_filters.setdefault("date", []).extend(["<=", filters.get("to_date")])
        if filters.get("donation"):
            frappe_filters["donation"] = filters.get("donation")
        if filters.get("donor"):
            frappe_filters["donor"] = filters.get("donor")

        if filters.get("recipient_type"):
            item_filters["recipient_type"] = filters["recipient_type"]

            recipient_type = filters["recipient_type"]
            recipient_field_map = {
                "Beneficiary": "beneficiary",
                "Student": "student",
                "Learning Centre": "learning_centre",
                "Budget": "budget",
                "Employee": "employee",
            }

            specific_fieldname = recipient_field_map.get(recipient_type)
            if specific_fieldname:
                recipient_value = filters.get(specific_fieldname)
                if recipient_value:
                    item_filters["recipient"] = recipient_value

        if filters.get("general_admin"):
            item_filters["general_admin"] = ["like", f"%{filters['general_admin']}%"]


        if filters.get("project"):
            item_filters["project"] = filters["project"]


        if isinstance(frappe_filters.get("date"), list) and len(frappe_filters["date"]) > 2:
            dates = frappe_filters.pop("date")[1::2]
            frappe_filters["date"] = ["between", dates]

        distributions = frappe.get_all(
            "Donation Allocation",
            filters=frappe_filters,
            fields=["name", "donation", "donor", "date as distribution_date", "total_amount", "remarks"],
            order_by="donation, date ASC"
        )

        if not distributions:
            return []

        distribution_names = [d.name for d in distributions]
        item_filters["parent"] = ["in", distribution_names]

        items = frappe.get_all(
            "Donation Allocation Item",
            filters=item_filters,
            fields=["parent", "amount", "percentage", "recipient_type", "recipient", "project", "general_admin"], 
            order_by="parent, idx"
        )

        items_by_distribution = {}
        for item in items:
            items_by_distribution.setdefault(item.parent, []).append(item)

        distributions = [d for d in distributions if d.name in items_by_distribution]
        donation_names = list(set(d.donation for d in distributions))

        donations = []
        if donation_names:
            donations = frappe.get_all(
                "Donation",
                filters={"name": ["in", donation_names]},
                fields=["name", "donor", "amount as pledged_amount", "total_amount_paid", "amount_distributed"],
                order_by="creation DESC"
            )

        donor_names = {}
        donor_ids = list(set([d.donor for d in donations if d.donor]))
        if donor_ids:
            for d in frappe.get_all("Donor", filters={"name": ["in", donor_ids]}, fields=["name", "donor_name"]):
                donor_names[d.name] = d.donor_name

        distributions_by_donation = {}
        for dist in distributions:
            distributions_by_donation.setdefault(dist.donation, []).append(dist)

        donation_map = {d.name: d for d in donations}
        data = []

        for donation_name in distributions_by_donation.keys():
            donation = donation_map.get(donation_name)
            if not donation:
                continue

            donor_name = donor_names.get(donation.donor, "")
            distributions = distributions_by_donation.get(donation.name, [])

            first_dist = distributions[0]
            first_items = items_by_distribution.get(first_dist.name, [])
            first_item = first_items[0] if first_items else None

            row = {
                "donation": donation.name,
                "donor": donation.donor,
                "donor_name": donor_name,
                "pledged_amount": donation.pledged_amount,
                "total_amount_paid": donation.total_amount_paid or 0,
                "amount_distributed": donation.amount_distributed or 0,
                "is_group": 1,
                "bold": 1,
                "indent": 0
            }

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

            data.append(row)

            for item in first_items[1:]:
                data.append({
                    "donation": "", "donor": "", "donor_name": "", "pledged_amount": "",
                    "total_amount_paid": "", "amount_distributed": "",
                    "distribution": "", "distribution_date": "", "total_amount": "",
                    "amount": item.amount, "percentage": item.percentage,
                    "recipient_type": item.recipient_type, "recipient": item.recipient,
                    "project": item.project, "remarks": "", "indent": 1,
                    "general_admin": item.general_admin 
                })

            for dist in distributions[1:]:
                items = items_by_distribution.get(dist.name, [])
                if not items:
                    continue

                first_item = items[0]
                dist_row = {
                    "donation": "", "donor": "", "donor_name": "", "pledged_amount": "",
                    "total_amount_paid": "", "amount_distributed": "",
                    "distribution": dist.name, "distribution_date": dist.distribution_date,
                    "total_amount": dist.total_amount, "remarks": dist.remarks,
                    "is_group": 1, "bold": 0, "indent": 1,
                    "amount": first_item.amount, "percentage": first_item.percentage,
                    "recipient_type": first_item.recipient_type, "recipient": first_item.recipient,
                    "project": first_item.project,
                    "general_admin": first_item.general_admin 
                }

                data.append(dist_row)

                for item in items[1:]:
                    data.append({
                        "donation": "", "donor": "", "donor_name": "", "pledged_amount": "",
                        "total_amount_paid": "", "amount_distributed": "",
                        "distribution": "", "distribution_date": "", "total_amount": "",
                        "amount": item.amount, "percentage": item.percentage,
                        "recipient_type": item.recipient_type, "recipient": item.recipient,
                        "project": item.project, "remarks": "", "indent": 2,
                        "general_admin": item.general_admin 
                    })

        return data


    def get_chart_data(self):

        summary_map = defaultdict(lambda: {"pledged": 0, "paid": 0, "distributed": 0})


        for row in self.data:
            donation = row.get("donation")
            if not donation:
                continue

            indent = row.get("indent", 0)

            if indent == 0:
                summary_map[donation]["pledged"] = row.get("pledged_amount", 0)
                summary_map[donation]["paid"] = row.get("total_amount_paid", 0)
                summary_map[donation]["distributed"] = row.get("amount_distributed", 0)

        items = list(summary_map.items())

        sorted_data = items

        self.chart = {
            "data": {
                "labels": [d[0] for d in sorted_data],
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
                    "type": "bar",
                    "fieldtype": "Currency",
                    "height": 300
                }


    def get_report_summary(self):
        total_pledged = 0
        total_paid = 0
        total_distributed = 0

        for row in self.data:
            if row.get("indent", 0) == 0:
                total_pledged += row.get("pledged_amount") or 0
                total_paid += row.get("total_amount_paid") or 0
                total_distributed += row.get("amount_distributed") or 0

        self.report_summary = [
            {
                "label": "Total Pledged Amount",
                "value": total_pledged,
                "datatype": "Currency",
                "indicator": "blue"
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