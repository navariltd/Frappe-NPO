import frappe

def update_links_for_donation_allocation() -> None:
    doctypes = ["Donation", "Donor", "Project"]
    for doctype in doctypes:
        try:
            doc = frappe.get_doc("DocType", doctype)

            doc.links = [
                link for link in doc.get("links", [])
                if link.link_doctype != "Donation Allocation"
            ]

            if doctype == "Donation":
                doc.append("links", {
                    "link_doctype": "Donation Allocation",
                    "link_fieldname": "donation",
                    "group": "Allocation"
                })
            elif doctype == "Donor":
                doc.append("links", {
                    "link_doctype": "Donation Allocation",
                    "link_fieldname": "donor"
                })
            elif doctype == "Project":
                doc.append("links", {
                    "link_doctype": "Donation",
                    "link_fieldname": "project",
                    "group": "Donations"
                })
                doc.append("links", {
                    "link_doctype": "Donation Allocation",
                    "link_fieldname": "project",
                    "group": "Donations"
                })

            doc.save()
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(
                message=f"Error updating links for {doctype}: {str(e)}",
                title="Update Links Error"
            )

def execute() -> None:
    update_links_for_donation_allocation()
