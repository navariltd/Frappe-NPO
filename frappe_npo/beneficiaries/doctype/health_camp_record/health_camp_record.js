// Copyright (c) 2022, hussain@frappe.io and contributors
// For license information, please see license.txt

frappe.ui.form.on("Health Camp Record", {
	setup: (frm) => {
		frappe_npo.utils.set_query_for_district(frm);
		frappe_npo.utils.set_query_for_zone(frm);
		frappe_npo.utils.set_query_for_ward(frm);
	},
	state: frappe_npo.utils.handle_state_field,
	district: frappe_npo.utils.handle_district_field,
	zone: frappe_npo.utils.handle_zone_field,
	ward: frappe_npo.utils.handle_ward_field,
	bottom_save_button: (frm) => {
		frm.save();
	},
});
