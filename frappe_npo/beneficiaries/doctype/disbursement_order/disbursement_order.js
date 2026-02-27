// Copyright (c) 2026, hussain@frappe.io and contributors
// For license information, please see license.txt

var in_progress = false;
frappe.ui.form.on("Disbursement Order", {
	setup: function (frm) {
		frm.events.setup_beneficiary_filter_group(frm);
	},

	onload: function (frm) {
		if (!frm.doc.from_date) {
			frm.set_value("from_date", frappe.datetime.nowdate());
		}

		frm.set_query("source_warehouse", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0,
				},
			};
		});
		set_district_filter(frm);
	},

	territory: function (frm) {
		set_district_filter(frm);
	},

	refresh: function (frm) {
		if (frm.doc.docstatus == 0 && !frm.is_new()) {
			frm.trigger("render_custom_buttons");
		}
		if (frm.is_dirty()) {
			frm.page.set_primary_action(__("Save"), () => frm.save());
		} else {
			if (frm.doc.docstatus === 0) {
				if (!(frm.doc.beneficiaries || []).length && !frm.is_new()) {
					frm.page.set_primary_action(__("Get Beneficiaries"), function () {
						frm.events.get_beneficiary_details(frm);
					});
				}
			} else if (frm.doc.docstatus === 1) {
				if (!frm.doc.entries_created) {
					let label =
						frm.doc.disbursement_type === "Cash"
							? __("Create Payment Entries")
							: __("Create Stock Entries");
					frm.page.set_primary_action(label, () => {
						frm.events.process_disbursement(frm);
					});
				} else {
					frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "Sales Invoice",
							fields: ["name"],
							filters: {
								disbursement_order: frm.doc.name,
							},
						},
						callback: function (r) {
							if (r.message && r.message.length > 0) {
							} else {
								frm.add_custom_button(__("Create Sales Invoice"), function () {
									frm.events.create_sales_invoice(frm);
								}).addClass("btn-primary");
							}
						},
					});
				}
			}
		}
	},

	get_beneficiary_details: function (frm) {
		return frappe.call({
			doc: frm.doc,
			args: {
				advanced_filters: frm.advanced_filters,
			},
			method: "get_beneficiaries",
			freeze: true,
			freeze_message: __("Fetching Beneficiaries"),
			callback: function (r) {
				frm.clear_table("beneficiaries");

				const beneficiaries = r.message;
				const items = frm.doc.items || [];

				beneficiaries.forEach((ben) => {
					items.forEach((item_row) => {
						let child = frm.add_child("beneficiaries");

						child.beneficiary = ben.name;
						child.beneficiary_no = ben.beneficiary_no;
						child.item_code = item_row.item_code;
						child.territory = ben.territory;
						child.district = ben.district;
						child.qty = item_row.qty || 0;
						child.rate = item_row.rate || 0;
						child.uom = item_row.uom;
						child.amount = (item_row.qty || 0) * (item_row.rate || 0);

						child.mode_of_payment = frm.doc.mode_of_payment;
					});
				});

				frm.refresh_field("beneficiaries");
				frm.scroll_to_field("beneficiaries");
			},
		});
	},

	process_disbursement: function (frm) {
		let method_name =
			frm.doc.disbursement_type === "Cash" ? "make_payment_entries" : "make_stock_entries";

		frappe.confirm(__("Create disbursement entries for all beneficiaries?"), function () {
			frappe.call({
				doc: frm.doc,
				method: method_name,
				freeze: true,
				callback: function () {
					frm.reload_doc();
				},
			});
		});
	},

	create_sales_invoice: function (frm) {
		frappe.call({
			doc: frm.doc,
			method: "create_sales_invoice",
			freeze: true,
			callback: function (r) {
				if (!r.message) return;

				const data = r.message;

				if (!data.sales_invoice) {
					frappe.msgprint(__("Sales Invoice could not be created."));
					return;
				} else {
					frappe.set_route("Form", "Sales Invoice", data.sales_invoice);
				}
			},
		});
	},

	disbursement_type: function (frm) {
		frm.clear_table("beneficiaries");
		frm.refresh();
	},

	company: function (frm) {
		frm.clear_table("beneficiaries");
		frm.refresh();
	},

	setup_beneficiary_filter_group(frm) {
		const filter_wrapper = frm.fields_dict.filter_list.$wrapper;
		filter_wrapper.empty();

		frappe.model.with_doctype("Beneficiary", () => {
			frm.filter_list = new frappe.ui.FilterGroup({
				parent: filter_wrapper,
				doctype: "Beneficiary",
				on_change: () => {
					frm.advanced_filters = frm.filter_list
						.get_filters()
						.filter(
							(item) =>
								item &&
								item.length >= 4 &&
								item[3] !== undefined &&
								item[3] !== null,
						);

					frm.set_value("saved_filters", JSON.stringify(frm.advanced_filters));
				},
			});

			if (frm.doc.saved_filters) {
				try {
					const saved = JSON.parse(frm.doc.saved_filters);

					if (Array.isArray(saved)) {
						frm.advanced_filters = saved;

						saved.forEach((f) => {
							if (Array.isArray(f) && f[3] !== undefined && f[3] !== null) {
								frm.filter_list.add_filter(...f);
							}
						});
					}
				} catch (e) {
					console.error("Failed to load saved filters:", e);
				}
			}
		});
	},

	render_custom_buttons: function (frm) {
		const grid_wrapper = frm.get_field("beneficiaries").$wrapper;

		grid_wrapper.find(".custom-table-actions").remove();

		const $btn_container = $(`
		<div class="custom-table-actions" style="margin-bottom:10px;display:flex;gap:10px;">
			<button type="button" class="btn btn-primary btn-sm btn-download-template">
				<i class="fa fa-download"></i> ${__("Download Template")}
			</button>
			<button type="button" class="btn btn-primary btn-sm btn-upload-list">
				<i class="fa fa-upload"></i> ${__("Upload List")}
			</button>
		</div>
	`).prependTo(grid_wrapper);

		$btn_container
			.find(".btn-download-template")
			.off("click")
			.on("click", () => frm.trigger("download_template_dialog"));

		$btn_container
			.find(".btn-upload-list")
			.off("click")
			.on("click", () => frm.trigger("upload_list"));
	},

	download_template_dialog: function (frm) {
		const d = new frappe.ui.Dialog({
			title: __("Download Template"),
			fields: [
				{
					label: __("Format"),
					fieldname: "format",
					fieldtype: "Select",
					options: ["Excel", "CSV"],
					default: "Excel",
				},
				{
					label: __("Include Beneficiary Fields"),
					fieldname: "include_beneficiary_data",
					fieldtype: "Check",
					default: 0,
				},
			],
			primary_label: __("Download"),
			primary_action: (values) => {
				let fields = frappe
					.get_meta("Disbursement Order Party")
					.fields.filter((df) => !frappe.model.no_value_type.includes(df.fieldtype))
					.map((df) => df.fieldname);

				if (values.include_beneficiary_data) {
					let ben_fields = frappe
						.get_meta("Beneficiary")
						.fields.filter((df) => !frappe.model.no_value_type.includes(df.fieldtype))
						.map((df) => df.fieldname);

					fields = [...new Set([...fields, ...ben_fields])];
				}

				const method =
					"frappe_npo.beneficiaries.doctype.beneficiary.beneficiary.export_beneficiary_template";
				const args = {
					file_format: values.format,
					extra_fields: JSON.stringify(fields),
					include_beneficiary_data: values.include_beneficiary_data,
					first: false,
				};

				window.open(`/api/method/${method}?${$.param(args)}`);
				d.hide();
			},
		});

		d.show();
	},

	upload_list: function (frm) {
		new frappe.ui.FileUploader({
			allow_multiple: false,
			on_success: (file) => {
				frm.call({
					method: "upload_beneficiaries",
					doc: frm.doc,
					args: { file_url: file.file_url },
					freeze: true,
					freeze_message: __("Processing file..."),
					callback: function (r) {
						if (r.message.mapped_items.length) {
							frm.clear_table("beneficiaries");
							r.message.mapped_items.forEach((d) => {
								let row = frm.add_child("beneficiaries");
								Object.assign(row, d);
							});
							frm.refresh_field("beneficiaries");
						}
					},
				});
			},
			restrictions: { allowed_file_types: [".csv", ".xlsx", ".xls"] },
		});
	},
});

frappe.ui.form.on("Disbursement Order Item", {
	rate: (frm, cdt, cdn) => update_row_amount(frm, cdt, cdn, "items"),
	qty: (frm, cdt, cdn) => update_row_amount(frm, cdt, cdn, "items"),
});

frappe.ui.form.on("Disbursement Order Party", {
	rate: (frm, cdt, cdn) => update_row_amount(frm, cdt, cdn, "beneficiaries"),
	qty: (frm, cdt, cdn) => update_row_amount(frm, cdt, cdn, "beneficiaries"),
});

function update_row_amount(frm, cdt, cdn, field) {
	let row = frappe.get_doc(cdt, cdn);
	row.amount = (row.qty || 0) * (row.rate || 0);
	frm.refresh_field(field);
}

function set_district_filter(frm) {
	frm.set_query("district", function () {
		return {
			filters: {
				territory: frm.doc.territory,
			},
		};
	});
}
