const settingsDoctypeName = "Frappe NPO Settings";

(async () => {
	const { message: settings } = await frappe.db.get_value(
		settingsDoctypeName,
		{ name: settingsDoctypeName },
		"name",
	);

	// Check if food distribution is enabled
	if (!settings || !settings.enable_food_distribution) {
		return;
	}

	// Register form events only if enabled
	frappe.ui.form.on("Stock Entry", {
		setup: async function (frm) {
			setup_beneficiary_query(frm);
			setup_collector_query(frm);
		},

		refresh: function (frm) {
			if (frm.doc.collector && frm.doc.beneficiary) {
				auto_set_collector(frm);
			}
		},

		project: function (frm) {
			load_bom_items(frm);
			setup_beneficiary_query(frm);
			set_defaults_for_distribution(frm);
		},

		stock_entry_type: function (frm) {
			load_bom_items(frm);
			setup_beneficiary_query(frm);
			set_defaults_for_distribution(frm);
		},

		custom_beneficiary: function (frm) {
			setup_collector_query(frm);
		},
	});
})();

function set_defaults_for_distribution(frm) {
	if (frm.doc.stock_entry_type === "Distribution") {
		frm.set_df_property("project", "reqd", 1);
		if (frm.doc.project) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Project",
					fieldname: ["custom_branch", "cost_center"],
					filters: { name: frm.doc.project },
				},
				callback: function (r) {
					if (r.message) {
						const branch_keyword = r.message.custom_branch || "";
						frm.set_value("cost_center", r.message.cost_center);
						frm.set_value("branch", r.message.custom_branch);

						frappe.call({
							method: "frappe.client.get_list",
							args: {
								doctype: "Warehouse",
								filters: [["name", "like", `%${branch_keyword}%`]],
								fields: ["name"],
								limit_page_length: 1,
							},
							callback: function (res) {
								if (res.message && res.message.length > 0) {
									frm.set_value("from_warehouse", res.message[0].name);
								}
							},
						});
					}
				},
			});
		}
	} else {
		frm.set_df_property("project", "reqd", 0);
	}
}

function setup_beneficiary_query(frm) {
	const project = frm.doc.project;

	if (project && frm.doc.stock_entry_type == "Distribution") {
		frappe.call({
			method: "frappe_npo.beneficiaries.overrides.stock_entry_query.get_filtered_beneficiaries",
			args: {
				project: project,
			},
			callback: function (r) {
				if (r.message) {
					const beneficiary_list = r.message;
					frm.set_query("custom_beneficiary", function () {
						return {
							filters: [["name", "in", beneficiary_list]],
						};
					});
				}
			},
		});
	}
}

function setup_collector_query(frm) {
	if (frm.doc.custom_beneficiary) {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Beneficiary",
				fieldname: "collector",
				filters: { name: frm.doc.custom_beneficiary },
			},
			callback: function (r) {
				if (r.message) {
					let collector = r.message.collector;

					frm.set_value("collector", collector);
					frm.set_query("collector", function () {
						return {
							filters: [["name", "=", collector]],
						};
					});
				}
			},
		});
	}
}

function load_bom_items(frm) {
	if (frm.doc.project && frm.doc.stock_entry_type == "Distribution") {
		frappe.call({
			method: "frappe_npo.beneficiaries.overrides.stock_entry_query.get_bom_items",
			args: { project: frm.doc.project },
			callback: function (r) {
				if (r.message && r.message.length > 0) {
					frm.clear_table("items");

					$.each(r.message, function (_, item) {
						let d = frappe.model.add_child(frm.doc, "Stock Entry Detail", "items");
						d.item_code = item.item_code;
						d.item_name = item.item_name;
						d.item_group = item.item_group;
						d.s_warehouse = frm.doc.source_warehouse;
						d.t_warehouse = frm.doc.target_warehouse;
						d.uom = item.stock_uom;
						d.stock_uom = item.stock_uom;
						d.conversion_factor = item.conversion_factor ? item.conversion_factor : 1;
						d.qty = item.qty;
						d.transfer_qty = item.stock_qty;
						d.expense_account = item.expense_account;
					});

					frm.refresh_field("items");
				} else {
					frappe.throw(__("No BOM items found for the selected project."));
				}
			},
		});
	}
}
