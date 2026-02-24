// Copyright (c) 2024, hussain@frappe.io and contributors
// For license information, please see license.txt

frappe.ui.form.on("Recruitment Phase", {
	refresh(frm) {
		frm.events.validate_available_slots(frm);
	},

	validate_available_slots(frm) {
		if (!frm.is_new()) {
			frappe.call({
				method: "frappe_npo.beneficiaries.doctype.recruitment_phase.recruitment_phase.validate_available_slots",
				args: {
					phase_name: frm.doc.name,
				},
				callback: function (r) {
					if (r.message && frm.doc.available_slots != r.message.available_slots) {
						frm.set_value("available_slots", r.message.available_slots);
						frm.save();
					}
				},
			});
		}
	},
});
