// Copyright (c) 2026, hussain@frappe.io and contributors
// For license information, please see license.txt

var in_progress = false;
frappe.ui.form.on("Donation Disbursement Entry", {
	setup: function (frm) {
		frm.events.setup_beneficiary_filter_group(frm);
	},

	onload: function (frm) {
		if (!frm.doc.from_date) {
			frm.set_value("from_date", frappe.datetime.nowdate());
		}

		frm.set_query("paid_to", function () {
			return {
				filters: {
					account_type: "Payable",
					root_type: "Liability",
					is_group: 0,
					company: frm.doc.company,
				},
			};
		});

		frm.set_query("paid_from", function () {
			return {
				filters: {
					account_type: ["in", ["Bank", "Cash"]],
					is_group: 0,
					company: frm.doc.company,
				},
			};
		});

		frm.set_query("source_warehouse", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0,
				},
			};
		});

		sync_items_with_sales_order(frm, "sales_order", "items", "item_code");
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
					frm.page.set_primary_action(
						__("Get Beneficiaries"),
						function () {
							frm.events.get_beneficiary_details(frm);
						},
					);
				}
			} else if (frm.doc.docstatus === 1) {
				if (!frm.doc.entries_created) {
					let label =
						frm.doc.allocation_type === "Cash"
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
								donation_disbursement_entry: frm.doc.name,
							},
						},
						callback: function (r) {
							if (r.message && r.message.length > 0) {
							} else {
								frm.add_custom_button(
									__("Create Sales Invoice"),
									function () {
										frm.events.create_sales_invoice(frm);
									},
								).addClass("btn-primary");
							}
						},
					});
				}
			}
		}
	},

	sales_order: function (frm) {
		sync_items_with_sales_order(frm, "sales_order", "items", "item_code");
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
						child.qty = item_row.qty || 0;
						child.rate = item_row.rate || 0;
						child.uom = item_row.uom;
						child.amount =
							(item_row.qty || 0) * (item_row.rate || 0);

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
			frm.doc.allocation_type === "Cash"
				? "make_payment_entries"
				: "make_stock_entries";

		frappe.confirm(
			__("Create disbursement entries for all beneficiaries?"),
			function () {
				frappe.call({
					doc: frm.doc,
					method: method_name,
					freeze: true,
					callback: function () {
						frm.reload_doc();
					},
				});
			},
		);
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
					frappe.set_route(
						"Form",
						"Sales Invoice",
						data.sales_invoice,
					);
				}
			},
		});
	},

	allocation_type: function (frm) {
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

					frm.set_value(
						"saved_filters",
						JSON.stringify(frm.advanced_filters),
					);
				},
			});

			if (frm.doc.saved_filters) {
				try {
					const saved = JSON.parse(frm.doc.saved_filters);

					if (Array.isArray(saved)) {
						frm.advanced_filters = saved;

						saved.forEach((f) => {
							if (
								Array.isArray(f) &&
								f[3] !== undefined &&
								f[3] !== null
							) {
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
			title: __("Select Template Format"),
			fields: [
				{
					label: __("Format"),
					fieldname: "format",
					fieldtype: "Select",
					options: ["CSV", "Excel"],
					default: "Excel",
				},
			],
			primary_action_label: __("Download"),
			primary_action(values) {
				frm.events.download_beneficiary_template(
					frm,
					values.format.toLowerCase(),
				);
				d.hide();
			},
		});
		d.show();
	},

	download_beneficiary_template: function (frm, type) {
		frm.call({
			method: "download_beneficiary_template",
			doc: frm.doc,
			args: { file_type: type || "csv" },
			freeze: true,
			freeze_message: __("Generating Template..."),
			callback: function (r) {
				if (r.message) {
					const link = document.createElement("a");
					link.href = r.message;
					link.download = "";
					document.body.appendChild(link);
					link.click();
					document.body.removeChild(link);
				} else {
					frappe.msgprint(__("Failed to generate template."));
				}
			},
			error: function (err) {
				frappe.msgprint(__("Failed to generate template."));
				console.error(err);
			},
		});
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

frappe.ui.form.on("Beneficiary Disbursement Entry Item", {
	rate: (frm, cdt, cdn) => update_row_amount(frm, cdt, cdn, "items"),
	qty: (frm, cdt, cdn) => update_row_amount(frm, cdt, cdn, "items"),
});

frappe.ui.form.on("Beneficiary Disbursement Entry Party", {
	rate: (frm, cdt, cdn) => update_row_amount(frm, cdt, cdn, "beneficiaries"),
	qty: (frm, cdt, cdn) => update_row_amount(frm, cdt, cdn, "beneficiaries"),
});

function update_row_amount(frm, cdt, cdn, field) {
	let row = frappe.get_doc(cdt, cdn);
	row.amount = (row.qty || 0) * (row.rate || 0);
	frm.refresh_field(field);
}

function sync_items_with_sales_order(
	frm,
	sales_order_field,
	child_table_field,
	item_field = "item_code",
) {
	const so_name = frm.doc[sales_order_field];
	if (!so_name) return;

	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Sales Order",
			name: so_name,
		},
		callback: function (r) {
			if (!r.message) return;

			const so_items = r.message.items || [];

			frm.doc[child_table_field] = frm.doc[child_table_field].filter(
				(item) =>
					so_items.some(
						(so_item) => so_item.item_code === item[item_field],
					),
			);

			so_items.forEach((so_item) => {
				if (
					!frm.doc[child_table_field].some(
						(item) => item[item_field] === so_item.item_code,
					)
				) {
					frm.add_child(child_table_field, {
						[item_field]: so_item.item_code,
						uom: so_item.uom,
					});
				}
			});

			frm.refresh_field(child_table_field);

			let seen = {};
			let duplicates = [];
			frm.doc[child_table_field].forEach((item) => {
				if (seen[item[item_field]]) duplicates.push(item[item_field]);
				seen[item[item_field]] = true;
			});
			if (duplicates.length) {
				frappe.throw(
					`Duplicate items not allowed: ${duplicates.join(", ")}`,
				);
			}

			frm.set_query(
				item_field,
				child_table_field,
				function (doc, cdt, cdn) {
					return {
						filters: {
							item_code: ["in", so_items.map((i) => i.item_code)],
						},
					};
				},
			);
		},
	});
}
