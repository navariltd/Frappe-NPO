// Copyright (c) 2026, hussain@frappe.io and contributors
// For license information, please see license.txt

frappe.listview_settings["Beneficiary"] = {
	onload: function (listview) {
		listview.page.add_inner_button(__("Upload Beneficiaries"), function () {
			new frappe.ui.FileUploader({
				allow_multiple: false,
				restrictions: {
					allowed_file_types: [".csv", ".xlsx", ".xls"],
				},
				on_success: (file) => {
					frappe.call({
						method: "frappe_npo.beneficiaries.doctype.beneficiary.beneficiary.upload_beneficiary_list",
						args: {
							file_url: file.file_url,
						},
						freeze: true,
						freeze_message: __("Processing file..."),
						callback: function (r) {
							const result = r.message || {};
							const beneficiaries = result.beneficiaries || [];
							const errors = result.errors || [];

							if (beneficiaries.length) {
								frappe.show_alert(
									{
										message: __("{0} beneficiaries processed successfully", [
											beneficiaries.length,
										]),
										indicator: "green",
									},
									7,
								);
							}

							if (errors.length) {
								let html = `
									<div style="max-height: 400px; overflow: auto">
										<table class="table table-bordered table-sm">
											<thead>
												<tr>
													<th>${__("Row")}</th>
													<th>${__("Field")}</th>
													<th>${__("Error")}</th>
												</tr>
											</thead>
											<tbody>
								`;

								errors.forEach((e) => {
									html += `
										<tr>
											<td>${e.row || "-"}</td>
											<td>${e.field || "-"}</td>
											<td>${frappe.utils.escape_html(e.error || "")}</td>
										</tr>
									`;
								});

								html += `
											</tbody>
										</table>
									</div>
								`;

								frappe.msgprint({
									title: __("Upload Errors"),
									message: html,
									indicator: "red",
									wide: true,
								});
							}

							listview.refresh();
						},
					});
				},
			});
		});
	},
};
