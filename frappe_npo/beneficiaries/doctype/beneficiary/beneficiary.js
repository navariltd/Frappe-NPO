// Copyright (c) 2022, hussain@frappe.io and contributors
// For license information, please see license.txt

const settingsDoctypeName = "Frappe NPO Settings";

frappe.ui.form.on("Beneficiary", {
	refresh: async function (frm) {
		frm.toggle_display("address_html", !frm.is_new());
		frm.toggle_display("contact_html", !frm.is_new());

		frm.toggle_display("create_supplier", !frm.doc.supplier && !frm.doc.__islocal);

		const settings = await frappe.db.get_doc(settingsDoctypeName, settingsDoctypeName);

		frm.set_df_property(
			"status",
			"read_only",
			settings?.allow_beneficiary_status_editing ? 0 : 1,
		);
		frm.set_df_property(
			"beneficiary_no",
			"read_only",
			settings?.allow_beneficiary_status_editing ? 0 : 1,
		);
		frm.set_df_property(
			"programme_section",
			"hidden",
			settings?.enable_programme_details ? 0 : 1,
		);
		frm.set_df_property(
			"course_section",
			"hidden",
			settings?.enable_programme_details ? 0 : 1,
		);

		if (frm.is_new() && settings?.default_beneficiary_status && !frm.doc.status) {
			frm.set_value("status", settings.default_beneficiary_status);
		}

		if (!frm.is_new()) {
			frappe.contacts.render_address_and_contact(frm);

			if (settings?.manage_beneficiary_lifecycle) {
				if (frm.doc.status === "Waitlist") {
					frm.add_custom_button(
						"Local Administrator Acknowledgement",
						() => {
							create_case("Local Administration Acknowledgement", frm);
						},
						"Create",
					);
				}

				const requiresReplacement = ["Relocated", "Deceased", "Disqualified"];
				if (requiresReplacement.includes(frm.doc.status) && !frm.doc.replaced_by) {
					frm.add_custom_button(
						"Replacement",
						() => open_replacement_form(frm),
						"Create",
					);
				}

				if (frm.doc.status === "Active") {
					const cases = ["Disqualification", "Relocation", "Bereavement"];
					cases.forEach((caseType) => {
						frm.add_custom_button(
							caseType,
							() => create_case(caseType, frm),
							"Create",
						);
					});
				}
			}
		}

		if (frm.doc.supplier) {
			frappe.db
				.count("Bank Account", {
					filters: {
						party_type: "Supplier",
						party: frm.doc.supplier,
					},
				})
				.then((count) => {
					if (count > 0) {
						frm.set_df_property("create_bank_account", "hidden", 1);
					}
				});
		}

		calculate_and_set_age(frm);
	},

	create_supplier: (frm) => {
		frm.call({
			method: "create_supplier",
			doc: frm.doc,
			callback: function (r) {
				if (r.message) {
					frappe.msgprint("Supplier " + r.message + " created.");
				}
			},
		});
	},

	create_bank_account: (frm) => {
		if (frm.doc.supplier) {
			frappe.db
				.count("Bank Account", {
					filters: {
						party_type: "Supplier",
						party: frm.doc.supplier,
					},
				})
				.then((count) => {
					if (count === 0) {
						frappe.new_doc("Bank Account", {
							party_type: "Supplier",
							party: frm.doc.supplier,
						});
					} else {
						frappe.msgprint(__("Bank Account already exists for this Supplier."));
					}
				});
		} else {
			frappe.msgprint(__("Please create Supplier before creating Bank Account."));
		}
	},

	recruitment_phase: (frm) => {
		if (frm.doc.recruitment_phase) {
			frappe.db
				.get_value("Recruitment Phase", frm.doc.recruitment_phase, "branch")
				.then((r) => {
					if (r.message) {
						frm.set_value("branch", r.message.branch);
					}
				});
		}
	},

	dob: (frm) => {
		calculate_and_set_age(frm);
	},

	setup(frm) {
		frappe_npo.utils.set_query_for_district(frm);
		frappe_npo.utils.set_query_for_zone(frm);
		frappe_npo.utils.set_query_for_ward(frm);
	},
	state: frappe_npo.utils.handle_state_field,
	district: frappe_npo.utils.handle_district_field,
	zone: frappe_npo.utils.handle_zone_field,
	ward: frappe_npo.utils.handle_ward_field,
	bottom_save_button(frm) {
		frm.save();
	},
});

function create_case(docType, frm) {
	frappe.new_doc("Case", {
		beneficiary: frm.doc.name,
		title: `${frm.doc.name} - ${docType}`,
		type: docType,
	});
}

function calculate_and_set_age(frm) {
	if (frm.doc.dob) {
		const birthDate = frappe.datetime.str_to_obj(frm.doc.dob);
		const today = frappe.datetime.str_to_obj(frappe.datetime.now_date());
		const age = today.getFullYear() - birthDate.getFullYear();
		const monthDiff = today.getMonth() - birthDate.getMonth();
		const dayDiff = today.getDate() - birthDate.getDate();

		const adjustedAge = monthDiff < 0 || (monthDiff === 0 && dayDiff < 0) ? age - 1 : age;

		frm.set_value("age", adjustedAge);
	} else {
		frm.set_value("age", null);
	}
}

function open_replacement_form(frm) {
	const dialog = new frappe.ui.Dialog({
		title: "Select Replacement Beneficiary",
		fields: [
			{
				fieldtype: "Link",
				fieldname: "replaced_by",
				label: "Replaced By",
				options: "Beneficiary",
				reqd: 1,
				filters: {
					status: "Waitlist",
					name: ["!=", frm.doc.name],
				},
			},
		],
		primary_action_label: "Save",
		primary_action: function () {
			const replacedBy = dialog.get_values().replaced_by;
			if (replacedBy) {
				frm.set_value("replaced_by", replacedBy);

				frappe.db.get_doc("Beneficiary", replacedBy).then((doc) => {
					frappe.call({
						method: "frappe.client.set_value",
						args: {
							doctype: "Beneficiary",
							name: replacedBy,
							fieldname: {
								recruitment_phase: frm.doc.recruitment_phase,
								branch: frm.doc.branch,
								beneficiary_no: frm.doc.beneficiary_no,
							},
						},
						callback: function () {
							frm.save();
							dialog.hide();
						},
					});
				});
			} else {
				frappe.msgprint("Please select a replacement beneficiary.");
			}
		},
	});

	dialog.show();
}
