# Copyright (c) 2024, hussain@frappe.io and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class RecruitmentPhase(Document):
    def validate(self):
        self.calc_available_slots()

    def calc_available_slots(self):
        allocated_slots = self.total_slots or 0
        active_beneficiary_count = frappe.db.count(
            "Beneficiary",
            {"status": "Active", "recruitment_phase": self.name},
        )
        self.available_slots = max(allocated_slots - active_beneficiary_count, 0)

        if active_beneficiary_count > allocated_slots:
            frappe.throw(
                _(
                    "Allocated slots exceeded for {}. Active Beneficiaries: {0}, Allocated Slots: {1}"
                ).format(active_beneficiary_count, allocated_slots)
            )


@frappe.whitelist()
def validate_available_slots(phase_name):
    recruitment_phase = frappe.get_doc("Recruitment Phase", phase_name)
    recruitment_phase.calc_available_slots()
    return recruitment_phase