// Copyright (c) 2026, hussain@frappe.io and contributors
// For license information, please see license.txt

frappe.listview_settings["Beneficiary"] = {
	onload: function (listview) {
		listview.page.add_inner_button(__("Upload Beneficiaries"), function () {
			const d = new frappe.ui.Dialog({
				title: __("Upload Beneficiaries"),
				fields: [
					{
						label: __("Template Format"),
						fieldtype: "Select",
						fieldname: "format",
						options: ["Excel", "CSV"],
						default: "Excel",
					},
					{
						fieldtype: "HTML",
						fieldname: "download_help",
						options: `
                            <div style="margin-bottom: 20px;">
                                <button class="btn btn-xs btn-default" id="download-template-btn">
                                    <i class="fa fa-download"></i> ${__("Download Template")}
                                </button>
                            </div>
                        `,
					},
					{
						label: __("Select File"),
						fieldtype: "Attach",
						fieldname: "file",
						reqd: 1,
					},
					{
						fieldtype: "HTML",
						fieldname: "results_area",
					},
				],
				primary_label: __("Upload"),
				primary_action: (values) => {
					frappe.call({
						method: "frappe_npo.beneficiaries.doctype.beneficiary.beneficiary.upload_beneficiary_list",
						args: { file_url: values.file },
						freeze: true,
						freeze_message: __("Processing file..."),
						callback: function (r) {
							const result = r.message || {};
							const beneficiaries = result.beneficiaries || [];
							const errors = result.errors || [];

							let result_html = "";

							if (beneficiaries.length) {
								result_html += `
                                    <div class="alert alert-success" style="margin-top: 15px;">
                                        ${__("{0} beneficiaries processed successfully", [beneficiaries.length])}
                                    </div>
                                `;
							}

							if (errors.length) {
								result_html += `
                                    <div style="margin-top: 15px;">
                                        <h6 class="text-danger">${__("Upload Errors")}</h6>
                                        <div style="max-height: 200px; overflow-y: auto; border: 1px solid #d1d8dd;">
                                            <table class="table table-bordered table-sm small">
                                                <thead class="bg-light">
                                                    <tr>
                                                        <th>${__("Row")}</th>
                                                        <th>${__("Field")}</th>
                                                        <th>${__("Error")}</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    ${errors
														.map(
															(e) => `
                                                        <tr>
                                                            <td>${e.row || "-"}</td>
                                                            <td>${e.field || "-"}</td>
                                                            <td class="text-danger">${frappe.utils.escape_html(e.error || "")}</td>
                                                        </tr>
                                                    `,
														)
														.join("")}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                `;
							}

							d.get_field("results_area").$wrapper.html(result_html);

							listview.refresh();
						},
					});
				},
			});

			d.show();

			d.$wrapper.find("#download-template-btn").on("click", () => {
				const method =
					"frappe_npo.beneficiaries.doctype.beneficiary.beneficiary.export_beneficiary_template";
				const args = { file_format: d.get_value("format") };
				window.open(`/api/method/${method}?${$.param(args)}`);
			});
		});
	},
};
