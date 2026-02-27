# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FrappeNPOSettings(Document):
    def validate(self):
        if self.enable_territory_dimension:
            self.create_accounting_dimension("Territory", "territory")
        else:
            self.delete_accounting_dimension("Territory")

        if self.enable_beneficiary_dimension:
            self.create_accounting_dimension("Beneficiary", "beneficiary")
        else:
            self.delete_accounting_dimension("Beneficiary")

    def create_accounting_dimension(self, document_type, field_name):
        if frappe.db.exists("Accounting Dimension", document_type):
            return

        dimension = frappe.new_doc("Accounting Dimension")
        dimension.document_type = document_type
        dimension.field_name = field_name
        dimension.label = document_type
        dimension.disabled = 0
        dimension.insert(ignore_permissions=True)
        frappe.db.commit()

    def delete_accounting_dimension(self, document_type):
        if frappe.db.exists("Accounting Dimension", document_type):
            frappe.delete_doc(
                "Accounting Dimension", document_type, ignore_permissions=True
            )
            frappe.db.commit()
