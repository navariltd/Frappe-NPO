frappe.ui.form.on("Payment Entry", {
	refresh: function (frm) {
		if (frm.doc.party_type == "Donor") {
			frm.set_query("reference_doctype", "references", function () {
				return {
					filters: { name: ["in", ["Donation", "Journal Entry"]] },
				};
			});
		}

		if (frm.doc.docstatus === 1 && frm.doc.references) {
			const has_donation = frm.doc.references.some(
				(ref) => ref.reference_doctype === "Donation",
			);

			if (has_donation) {
				frm.add_custom_button("Allocate Donation", () => {
					frappe.call({
						method: "frappe_npo.beneficiaries.doctype.donation_allocation.donation_allocation.get_available_donations_for_payment_entry",
						args: {
							payment_entry_name: frm.doc.name,
						},
						callback: function (r) {
							if (r.message) {
								const donations = r.message;

								if (donations.length === 0) {
									frappe.msgprint(
										"No unallocated donations found for this Payment Entry.",
									);
									return;
								}

								const donationMap = {};
								const donationOptions = donations.map((d) => {
									donationMap[d.name] = d;
									return d.name;
								});

								const dialog = new frappe.ui.Dialog({
									title: "Allocate Donation",
									fields: [
										{
											label: "Select Donation",
											fieldname: "donation",
											fieldtype: "Link",
											options: "Donation",
											reqd: 1,
											get_query: () => ({
												filters: [["name", "in", donationOptions]],
											}),
										},
										{
											label: "Allocate to Budget",
											fieldname: "allocate_to_budget",
											fieldtype: "Check",
											default: 0,
										},
										{
											label: "Budget",
											fieldname: "budget",
											fieldtype: "Link",
											options: "Budget",
											depends_on: "eval:doc.allocate_to_budget == 1",
											mandatory_depends_on:
												"eval:doc.allocate_to_budget == 1",
											get_query: () => ({
												query: "frappe_npo.beneficiaries.doctype.donation_allocation.donation_allocation.get_available_budgets",
											}),
										},
									],
									primary_action_label: "Allocate",
									primary_action: function (values) {
										frappe.route_options = {
											donation: values.donation,
											total_amount:
												donationMap[values.donation]?.remaining_amount,
										};

										const temp_data = {
											budget: values.budget,
											payment_entry: frm.doc.name,
										};

										localStorage.setItem(
											"donation_allocation_temp",
											JSON.stringify(temp_data),
										);

										frappe.new_doc("Donation Allocation");
										dialog.hide();
									},
								});

								dialog.show();
							} else {
								frappe.msgprint("Error fetching available donations.");
							}
						},
					});
				});
			}
		}

		frm.trigger("handle_payment_proof_upload");
		render_field_preview(frm);

		if (frm.doc.beneficiaries.length > 0 && frm.doc.docstatus === 1) {
			add_payment_verification_button(frm);
		}
	},

	payment_proof: function (frm) {
		render_field_preview(frm);
	},

	handle_payment_proof_upload: function (frm) {
		if (frm.doc.payment_type !== "Pay" || frm.doc.docstatus !== 0 || frm.doc.payment_proof)
			return;
		add_payment_proof_button(frm);
	},
});

function add_payment_verification_button(frm) {
	frm.add_custom_button(
		"Verification Requests",
		() => {
			frappe.call({
				method: "frappe_npo.overrides.payment_entry.make_payment_verification_requests",
				args: {
					name: frm.doc.name,
				},
				callback: function (r) {
					if (r.message) {
						const verificationRequestNames = r.message;
						if (verificationRequestNames.length === 0) {
							frappe.msgprint("No verification requests created.");
							return;
						}
						frm.reload_doc();
					}
				},
			});
		},
		"Create",
	);
}

function render_field_preview(frm) {
	if (frm.fields_dict.payment_proof_preview) {
		if (frm.doc.payment_proof) {
			const html = get_preview_html(frm.doc.payment_proof);
			frm.fields_dict.payment_proof_preview.$wrapper.html(html);
		} else {
			frm.fields_dict.payment_proof_preview.$wrapper.html("");
		}
	}
}

function get_preview_html(fileUrl) {
	const extension = fileUrl.split(".").pop().toLowerCase();
	if (["jpg", "jpeg", "png", "gif", "webp"].includes(extension)) {
		return `<div style="text-align:center; padding: 10px; border: 1px solid #d1d8dd; border-radius: 4px;">
			<img src="${fileUrl}" style="max-width:100%; max-height:500px; border-radius:4px;" />
		</div>`;
	} else if (extension === "pdf") {
		return `<iframe src="${fileUrl}" style="width:100%; height:600px; border:1px solid #d1d8dd; border-radius: 4px;"></iframe>`;
	} else {
		return `<div style="text-align:center; padding:20px; border: 1px dashed #d1d8dd;">
			<p>Preview not available for this file type.</p>
			<a href="${fileUrl}" target="_blank" class="btn btn-xs btn-default">Open File</a>
		</div>`;
	}
}

function add_payment_proof_button(frm) {
	frm.add_custom_button("Upload Payment Proof", () => {
		new frappe.ui.FileUploader({
			allow_multiple: false,
			on_success: function (file) {
				show_confirmation_dialog(frm, file.file_url, file.file_url);
			},
		});
	});
}

function show_confirmation_dialog(frm, fileUrl, fileName) {
	const previewDialog = new frappe.ui.Dialog({
		title: "Confirm Payment Proof",
		size: "large",
		fields: [{ fieldtype: "HTML", fieldname: "file_preview" }],
		primary_action_label: "Confirm & Attach",
		primary_action() {
			frappe.call({
				method: "frappe.client.set_value",
				args: {
					doctype: "Payment Entry",
					name: frm.doc.name,
					fieldname: "payment_proof",
					value: fileName,
				},
				callback: function () {
					frappe.msgprint("Payment proof attached successfully.");
					previewDialog.hide();
					frappe.call({
						method: "frappe_npo.overrides.payment_entry.rename_payment_proof_file",
						args: {
							name: frm.doc.name,
						},
						callback: function (r) {
							frm.reload_doc();
						},
					});
				},
			});
		},
		secondary_action_label: "Cancel",
		secondary_action() {
			frappe.call({
				method: "frappe.client.delete",
				args: { doctype: "File", name: fileName },
				callback: function () {
					frappe.msgprint("Cancelled: Uploaded file deleted.");
				},
			});
			previewDialog.hide();
		},
	});

	previewDialog.fields_dict.file_preview.$wrapper.html(get_preview_html(fileUrl));
	previewDialog.show();
}
