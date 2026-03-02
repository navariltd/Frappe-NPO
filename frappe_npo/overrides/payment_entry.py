import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.file_manager import get_file


@frappe.whitelist()
def download_payment_proofs_zip(payment_entries, folder_name):
    """
    Generate a permanent zip of payment proofs from selected Payment Entries
    """
    if not payment_entries:
        frappe.throw("No Payment Entries selected")

    payment_entries = [p for p in payment_entries if p]
    if not payment_entries:
        frappe.throw("No valid Payment Entries selected")


def after_save(doc: Document, method: str = None) -> None:
    rename_payment_proof_file(doc.name)


@frappe.whitelist()
def rename_payment_proof_file(name):
    doc = frappe.get_doc("Payment Entry", name)
    if not doc.payment_proof:
        return

    file_name = frappe.db.get_value(
        "File",
        {
            "file_url": doc.payment_proof,
            "attached_to_name": doc.name,
            "attached_to_doctype": doc.doctype,
        },
        "name",
    )

    if file_name:
        file_doc = frappe.get_doc("File", file_name)

    else:
        return

    beneficiary = frappe.get_all(
        "Beneficiary", filters={"supplier": doc.party}, fields=["name", "is_proxy"]
    )
    if not beneficiary:
        frappe.throw(_("No beneficiary found for party {0}").format(doc.party))

    beneficiary = beneficiary[0]
    is_proxy = beneficiary.is_proxy

    donor = frappe.db.get_value("Disbursement Order", doc.disbursement_order, "donor")

    donor_link = frappe.get_all(
        "Beneficiary Donor Assignment",
        filters={"parent": beneficiary.name, "donor": donor},
        fields=["name", "beneficiary_no"],
    )
    beneficiary_no = donor_link[0].beneficiary_no if donor_link else beneficiary.name

    prefix = "L+" if is_proxy else ""
    new_file_name = f"{prefix}{beneficiary_no}"

    if file_doc.file_name == new_file_name:
        return

    file_doc.file_name = new_file_name
    file_doc.file_url = file_doc.file_url.replace(file_doc.file_name, new_file_name)
    file_doc.save(ignore_permissions=True)
    doc.payment_proof = file_doc.file_url
    doc.save(ignore_permissions=True)


@frappe.whitelist()
def make_payment_verification_requests(name):
    doc = frappe.get_doc("Payment Entry", name)
    if not doc.beneficiaries:
        frappe.throw(_("No beneficiaries found for this Payment Entry."))

    personal_beneficiaries = []
    proxy_with_focal = {}
    proxy_no_focal = []

    for row in doc.beneficiaries:
        account_subtype = frappe.db.get_value(
            "Bank Account", row.bank_account, "account_subtype"
        )

        item_data = {
            "beneficiary": row.beneficiary,
            "beneficiary_no": row.beneficiary_no,
            "bank_account": row.bank_account,
            "focal_point": row.focal_point,
            "amount": row.amount,
            "currency": row.currency,
            "beneficiary_contact": row.beneficiary_contact,
            "beneficiary_address": row.beneficiary_address,
            "status": "Open",
        }

        if account_subtype == "Beneficiary":
            personal_beneficiaries.append(item_data)
        elif account_subtype == "Proxy":
            if row.focal_point:
                if row.focal_point not in proxy_with_focal:
                    proxy_with_focal[row.focal_point] = []
                proxy_with_focal[row.focal_point].append(item_data)
            else:
                proxy_no_focal.append(item_data)

    created_requests = []

    if personal_beneficiaries:
        vr_personal = create_vr_doc(doc, "Personal Accounts", personal_beneficiaries)
        created_requests.append(vr_personal.name)

    for focal_point, items in proxy_with_focal.items():
        vr_proxy = create_vr_doc(doc, "Proxy Accounts", items, focal_point)
        created_requests.append(vr_proxy.name)

    if proxy_no_focal:
        vr_proxy_bulk = create_vr_doc(doc, "Proxy Accounts", proxy_no_focal)
        created_requests.append(vr_proxy_bulk.name)

    return created_requests


def create_vr_doc(parent_doc, req_type, items, focal_point=None):
    vr = frappe.new_doc("Verification Request")
    vr.state = parent_doc.territory
    vr.verification_type = req_type
    vr.disbursement_order = parent_doc.disbursement_order
    vr.agent_payment_entry = parent_doc.name

    if focal_point:
        vr.focal_point = focal_point

    for item in items:
        vr.append("items", item)

    vr.insert()
    return vr
