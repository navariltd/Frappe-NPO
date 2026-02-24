# Copyright (c) 2025, hussain@frappe.io and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	report = DonationReport(filters)
	return report.run()

class DonationReport:
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
			{"label": _("Donation"), "fieldname": "donation", "fieldtype": "Link", "options": "Donation", "width": 150},
			{"label": _("Donor"), "fieldname": "donor", "fieldtype": "Link", "options": "Donor", "width": 200},
			{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 120},
			{"label": _("Pledged Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 150},
			{"label": _("Paid"), "fieldname": "paid", "fieldtype": "Check", "width": 100},
			{"label": _("Total Paid"), "fieldname": "total_amount_paid", "fieldtype": "Currency", "width": 150},
			{"label": _("% Paid"), "fieldname": "percent_paid", "fieldtype": "Float", "width": 200},
			{"label": _("Amount Distributed"), "fieldname": "amount_distributed", "fieldtype": "Currency", "width": 170},
			{"label": _("% Distributed"), "fieldname": "percent_distributed", "fieldtype": "Float", "width": 200}
		]

	def get_data(self):
		filters = self.filters
		conditions = {}

		if filters:
			if filters.get("from_date") and filters.get("to_date"):
				conditions["date"] = ["between", (filters["from_date"], filters["to_date"])]
			elif filters.get("from_date"):
				conditions["date"] = [">=", filters["from_date"]]
			elif filters.get("to_date"):
				conditions["date"] = ["<=", filters["to_date"]]

			if filters.get("donor"):
				conditions["donor"] = filters["donor"]
			if filters.get("donation"):
				conditions["name"] = filters["donation"]

		donations = frappe.get_all(
			"Donation",
			filters=conditions,
			fields=[
				"name", "donor", "donor_name", "amount", "paid",
				"total_amount_paid", "amount_distributed", "date"
			],
			order_by="date desc"
		)

		self.total_amount = 0
		self.total_paid = 0
		self.total_distributed = 0

		data = []
		for d in donations:
			percent_paid = percent_distributed = 0

			if d.amount:
				if d.total_amount_paid:
					percent_paid = round((d.total_amount_paid / d.amount) * 100, 2)
				if d.amount_distributed:
					percent_distributed = round((d.amount_distributed / d.amount) * 100, 2)

			data.append({
				"donation": d.name,
				"donor": d.donor,
				"donor_name": d.donor_name,
				"amount": d.amount,
				"paid": d.paid,
				"total_amount_paid": d.total_amount_paid,
				"percent_paid": percent_paid,
				"amount_distributed": d.amount_distributed,
				"percent_distributed": percent_distributed,
				"date": d.date
			})

			self.total_amount += d.amount or 0
			self.total_paid += d.total_amount_paid or 0
			self.total_distributed += d.amount_distributed or 0

		self.full_data = data

		return data

	def get_report_summary(self):
		utilization_percent = 0
		paid_percent = 0

		if self.total_paid:
			utilization_percent = round((self.total_distributed / self.total_paid) * 100, 2)

		if self.total_amount:
			paid_percent = round((self.total_paid / self.total_amount) * 100, 2)

		self.report_summary = [
			{
				"label": _("Total Pledged"),
				"value": self.total_amount,
				"indicator": "orange"
			},
			{
				"label": _("Total Paid"),
				"value": self.total_paid,
				"indicator": "blue"
			},
			{
				"label": _("Total Distributed"),
				"value": self.total_distributed,
				"indicator": "blue"
			},
			{
				"label": _("Utilization % (Distributed/Paid)"),
				"value": f"{utilization_percent}%",
				"indicator": "green"
			},
			{
				"label": _("Paid % (Honored)"),
				"value": f"{paid_percent}%",
				"indicator": "green"
			}
		]


	def get_chart_data(self):
		latest_10 = sorted(self.full_data, key=lambda x: x["date"], reverse=True)[:10]
		latest_10 = sorted(latest_10, key=lambda x: x["date"])

		labels = [d["donation"] for d in latest_10]
		pledged = [d["amount"] or 0 for d in latest_10]
		paid = [d["total_amount_paid"] or 0 for d in latest_10]
		distributed = [d["amount_distributed"] or 0 for d in latest_10]

		self.chart = {
			"data": {
				"labels": labels,
				"datasets": [
					{"name": _("Pledged"), "values": pledged},
					{"name": _("Paid"), "values": paid},
					{"name": _("Distributed"), "values": distributed}
				]
			},
			"type": "bar"
		}
