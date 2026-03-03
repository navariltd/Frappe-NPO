frappe.ui.form.on("Company", {
	refresh: function (frm) {
		setup_disbursement_bank_account_filter(frm);
	},
});

function setup_disbursement_bank_account_filter(frm) {
	frm.set_query("default_disbursement_bank_account", function () {
		return {
			filters: {
				disabled: 0,
				is_company_account: 1,
				company: frm.doc.name,
				account_subtype: "Company",
			},
		};
	});
}
