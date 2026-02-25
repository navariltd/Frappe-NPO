frappe.ui.form.on("Sales Order", {
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Disbursement Order"),
				function () {
					frappe.model.with_doctype("Disbursement Order", function () {
						const ddtMeta = frappe.get_meta("Disbursement Order");
						let values = { sales_order: frm.doc.name };
						ddtMeta.fields.forEach(function (field) {
							if (
								frm.doc.hasOwnProperty(field.fieldname) &&
								field.fieldtype !== "Table" &&
								!field.no_copy
							) {
								values[field.fieldname] = frm.doc[field.fieldname];
							}
						});
						frappe.new_doc("Disbursement Order", values);
					});
				},
				__("Create"),
			);
			frm.page.set_inner_btn_group_as_primary(__("Create"));
		}
	},
});
