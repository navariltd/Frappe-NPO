frappe.ui.form.on("Sales Person", {
	refresh: function (frm) {
		if (frm.doc.employee) {
			set_user_from_employee(frm);
		}
	},

	employee: function (frm) {
		set_user_from_employee(frm);
	},
});

function set_user_from_employee(frm) {
	if (frm.doc.employee) {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Employee",
				fieldname: "user_id",
				filters: { name: frm.doc.employee },
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value("user", r.message.user_id);
					frm.set_query("user", function () {
						return {
							filters: {
								name: r.message.user_id,
							},
						};
					});
				}
			},
		});
	}
}
