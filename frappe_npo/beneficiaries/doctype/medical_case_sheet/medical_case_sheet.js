// Copyright (c) 2022, hussain@frappe.io and contributors
// For license information, please see license.txt

frappe.ui.form.on("Medical Case Sheet", {
	refresh(frm) {
		if (!frm.doc.date) {
			frm.set_value("date", frappe.datetime.get_today());
		}
	},
});
