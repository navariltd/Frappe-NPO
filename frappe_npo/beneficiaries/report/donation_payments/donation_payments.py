# Copyright (c) 2025, hussain@frappe.io and contributors
# For license information, please see license.txt



def execute(filters=None):
    report = DonationPaymentsReport(filters)
    return report.run()

class DonationPaymentsReport:
    def __init__(self, filters=None):
        self.filters = filters
        self.columns = []
        self.data = []
        self.chart = {}
        self.report_summary = []

    def run(self):
        self.columns = self.get_columns()
        self.data = self.get_data()
        self.get_chart_data()
        self.get_report_summary()
        return self.columns, self.data, None, self.chart, self.report_summary

    def get_columns(self):
        return [
            {"label": "Donation", "fieldname": "donation", "fieldtype": "Link", "options": "Donation", "width": 150},
            {"label": "Donor", "fieldname": "donor", "fieldtype": "Data", "width": 150},
            {"label": "Amount Pledged", "fieldname": "amount_pledged", "fieldtype": "Currency", "width": 150},
            {"label": "Total Amount Paid", "fieldname": "total_amount_paid", "fieldtype": "Currency", "width": 150},
            {"label": "Payment Amount", "fieldname": "payment_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Percentage", "fieldname": "payment_percentage", "fieldtype": "Percent", "width": 150},
            {"label": "Payment Date", "fieldname": "payment_date", "fieldtype": "Date", "width": 150},
            {"label": "Payment ID", "fieldname": "payment_id", "fieldtype": "Data", "width": 150},
            {"label": "Mode of Payment", "fieldname": "mode_of_payment", "fieldtype": "Link", "options": "Mode of Payment", "width": 150},
            {"label": "Description", "fieldname": "description", "fieldtype": "Small Text", "width": 200},
        ]

    def get_data(self):
        import frappe
        import json

        filters = self.filters
        if isinstance(filters, str):
            filters = json.loads(filters)

        donor_filter = None
        frappe_filters = {}

        if filters:
            if filters.get("from_date"):
                frappe_filters["payment_date"] = [">=", filters.get("from_date")]
            if filters.get("to_date"):
                frappe_filters.setdefault("payment_date", []).extend(["<=", filters.get("to_date")])
            if filters.get("donation"):
                frappe_filters["parent"] = filters.get("donation")
            if filters.get("donor"):
                donor_filter = filters.get("donor")

        if isinstance(frappe_filters.get("payment_date"), list) and len(frappe_filters["payment_date"]) > 2:
            dates = frappe_filters.pop("payment_date")[1::2]
            frappe_filters["payment_date"] = ["between", dates]

        payments = frappe.get_all(
            "Donation Payment Item",
            filters=frappe_filters,
            fields=[
                "amount", "percentage", "payment_id", "mode_of_payment",
                "payment_date", "description", "parent"
            ],
            order_by="payment_date ASC"
        )

        payments_by_donation = {}
        for p in payments:
            payments_by_donation.setdefault(p.parent, []).append(p)

        data = []
        donation_names = list(payments_by_donation.keys())
        donations = frappe.get_all(
            "Donation",
            filters={"name": ["in", donation_names]},
            fields=["name", "donor_name", "donor", "amount"]
        )
        donation_map = {d.name: d for d in donations}

        for donation_id, payment_list in payments_by_donation.items():
            donation = donation_map.get(donation_id)

            if not donation:
                continue
            if donor_filter and donation.donor != donor_filter:
                continue

            total_amount_paid = sum(p.amount for p in payment_list)
            first = True
            for p in payment_list:
                row = {
                    "donation": donation.name if first else "",
                    "donor": donation.donor if first else "",
                    "donor_name": donation.donor_name if first else "",
                    "amount_pledged": donation.amount if first else "",
                    "total_amount_paid": total_amount_paid if first else "",
                    "payment_amount": p.amount,
                    "payment_percentage": p.percentage,
                    "payment_id": p.payment_id,
                    "mode_of_payment": p.mode_of_payment,
                    "payment_date": p.payment_date,
                    "description": p.description,
                }
                data.append(row)
                first = False

        return data

    def get_chart_data(self):
        from collections import defaultdict

        chart_labels = []
        pledged = []
        paid = []

        donation_summary = defaultdict(lambda: {
            "pledged": 0.0,
            "paid": 0.0,
        })

        for row in self.data:
            donation = row.get("donation")
            if not donation:
                continue

            summary = donation_summary[donation]
            summary["pledged"] = float(row.get("amount_pledged") or summary["pledged"] or 0)
            summary["paid"] = float(row.get("total_amount_paid") or summary["paid"] or 0)


        sorted_donations = list(donation_summary.items())[-10:]

        for donation_id, summary in sorted_donations:
            chart_labels.append(donation_id)
            pledged.append(summary["pledged"])
            paid.append(summary["paid"])

        self.chart = {
            "data": {
                "labels": chart_labels,
                "datasets": [
                    {"name": "Pledged Amount", "values": pledged},
                    {"name": "Total Paid", "values": paid},
                ]
            },
            "type": "bar",
            "barOptions": {"stacked": False}
        }

    def get_report_summary(self):
        total_pledged = 0
        total_paid = 0
        seen_donations = set()

        for row in self.data:
            donation = row.get("donation")
            if donation and donation not in seen_donations:
                total_pledged += float(row.get("amount_pledged") or 0)
                total_paid += float(row.get("total_amount_paid") or 0)
                seen_donations.add(donation)

        fulfillment_percent = (total_paid / total_pledged * 100) if total_pledged else 0

        self.report_summary = [
            {"label": "Total Pledged", "value": total_pledged, "indicator": "blue"},
            {"label": "Total Paid", "value": total_paid, "indicator": "green"},
            {"label": "Fulfillment (%)", "value": f"{fulfillment_percent:.2f}%", "indicator": "green" },
        ]
