# Copyright (c) 2024, hussain@frappe.io and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ImpactMeasurement(Document):
	def validate(self):
		if self.number_of_beneficiaries_supported and self.total_amount_donated:
			self.cost_per_beneficiary = (
				self.total_amount_donated / self.number_of_beneficiaries_supported
			)
		else:
			self.cost_per_beneficiary = 0
