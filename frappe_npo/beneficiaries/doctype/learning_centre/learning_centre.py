# Copyright (c) 2022, hussain@frappe.io and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LearningCentre(Document):
    def validate(self):
        self.validate_pin_code()

    def validate_pin_code(self):
        if not self.pin_code:
            return

        if not self.pin_code.isnumeric():
            frappe.throw("Pin Code should contain only numeric values")

        if len(str(self.pin_code)) != 6:
            frappe.throw("Pin Code should be a numeric value with exactly 6 digits")

    def after_insert(self):
        settings = frappe.get_doc("Frappe NPO Settings", "Frappe NPO Settings")
        if (
            settings.generate_supplier_when_learning_center_is_created
            or self.generate_supplier_on_creation
        ):
            self.create_supplier()

    def create_supplier(self):
        if not frappe.db.exists("Supplier Group", "Learning Centre"):
            supplier_group = frappe.new_doc("Supplier Group")
            supplier_group.supplier_group_name = "Learning Centre"
            supplier_group.flags.ignore_permissions = True
            supplier_group.insert()

        if frappe.db.exists("Supplier", self.name):
            return

        supplier = frappe.new_doc("Supplier")
        supplier.supplier_name = self.name
        supplier.supplier_type = "Company"
        supplier.supplier_group = "Learning Centre"

        supplier.flags.ignore_permissions = True
        supplier.insert()
