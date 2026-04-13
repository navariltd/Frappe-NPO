// Copyright (c) 2026, Navari Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Program Indicator Tracker", {
	refresh(frm) {},
});
frappe.ui.form.on("Objective Indicator", {
	refresh(frm) {
		// your code here
	},

	entry_log: (frm, cdt, cdn) => {
		row = locals[cdt][cdn];
		console.log(row);
	},
});
