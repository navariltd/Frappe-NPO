# Copyright (c) 2022, hussain@frappe.io and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Case(Document):
    def before_save(self):
        self.set_created_by()
        self.set_total_amount()
        if self.beneficiary:
            update_beneficiary_status(self)

    def set_created_by(self):
        if not self.created_by:
            owner = frappe.db.get_value("User", self.owner, "full_name")
            self.created_by = owner

    def set_total_amount(self):
        self.total_amount = sum(row.amount for row in self.payment_details)


def update_beneficiary_status(case_doc):
    case_status_to_beneficiary_status = {
        "Closed": {
            "Bereavement": "Deceased",
            "Relocation": "Relocated",
            "Disqualification": "Disqualified",
            "Local Administration Acknowledgement": "Endorsed",
        },
    }
    
    status_map = case_status_to_beneficiary_status.get(case_doc.status)
    if not status_map:
        return 

    new_beneficiary_status = status_map.get(case_doc.type)
    if not new_beneficiary_status:
        return 
    
    beneficiary_doc = frappe.get_doc("Beneficiary", case_doc.beneficiary)
    beneficiary_doc.status = new_beneficiary_status
    beneficiary_doc.save()
    