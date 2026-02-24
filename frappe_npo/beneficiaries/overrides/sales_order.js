frappe.ui.form.on("Sales Order", {
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Disbursement Entry"),
				function () {
					frappe.model.with_doctype(
						"Donation Disbursement Entry",
						function () {
							const ddtMeta = frappe.get_meta(
								"Donation Disbursement Entry",
							);
							let values = { sales_order: frm.doc.name };
							ddtMeta.fields.forEach(function (field) {
								if (
									frm.doc.hasOwnProperty(field.fieldname) &&
									field.fieldtype !== "Table" &&
									!field.no_copy
								) {
									values[field.fieldname] =
										frm.doc[field.fieldname];
								}
							});
							frappe.new_doc(
								"Donation Disbursement Entry",
								values,
							);
						},
					);
				},
				__("Create"),
			);
			frm.page.set_inner_btn_group_as_primary(__("Create"));
		}
	},
});
