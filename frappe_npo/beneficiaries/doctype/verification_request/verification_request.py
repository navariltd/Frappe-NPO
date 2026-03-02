# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import openpyxl
import csv
import requests
from io import BytesIO, StringIO

from frappe.model.document import Document
from frappe.utils import nowdate


class VerificationRequest(Document):
    def validate(self):
        """Called before save/submit"""
        self.prevent_reverting_open()
        enable_progressive_disbursement = frappe.db.get_single_value(
            "Frappe NPO Settings",
            "enable_progressive_disbursement",
        )
        if enable_progressive_disbursement and self.docstatus == 0:
            self.create_payments_on_verified_items()

    def on_submit(self):
        """Create Payment Entries for all verified beneficiaries if progressive disbursement is disabled"""
        enable_progressive_disbursement = frappe.db.get_single_value(
            "Frappe NPO Settings",
            "enable_progressive_disbursement",
        )
        if not enable_progressive_disbursement:
            self.create_payments_for_all_verified()

    @frappe.whitelist()
    def process_verification_upload(self, file_url):
        rows = self.get_rows_from_file(file_url)
        updated = False
        enable_progressive_disbursement = frappe.db.get_single_value(
            "Frappe NPO Settings",
            "enable_progressive_disbursement",
        )

        for row in rows:
            beneficiary = row.get("beneficiary") or row.get("Beneficiary")
            status = row.get("status") or row.get("Status")
            comments = row.get("comments") or row.get("Comments")

            if not beneficiary or not status:
                continue

            for item in self.items:
                if item.beneficiary == beneficiary:
                    item.status = status
                    if comments:
                        item.comments = str(comments)
                    updated = True
                    if enable_progressive_disbursement:
                        self.create_payment_for_item(item)
                    break

        if updated:
            self.save()
            return True
        return False

    def get_rows_from_file(self, file_url):
        if file_url.startswith("/private") or file_url.startswith("/files"):
            path = frappe.get_site_path(file_url.strip("/"))
            with open(path, "rb") as f:
                file_content = f.read()
        else:
            response = requests.get(file_url)
            file_content = response.content

        rows = []
        if file_url.endswith(".csv"):
            content = file_content.decode("utf-8")
            reader = csv.DictReader(StringIO(content))
            for row in reader:
                rows.append(row)

        elif file_url.endswith((".xlsx", ".xls")):
            wb = openpyxl.load_workbook(BytesIO(file_content), data_only=True)
            sheet = wb.active
            headers = [cell.value for cell in sheet[1]]
            for row in sheet.iter_rows(min_row=2, values_only=True):
                rows.append(dict(zip(headers, row)))

        return rows

    def prevent_reverting_open(self):
        for item in self.items:
            if item.name:
                original_status = frappe.db.get_value(
                    "Verification Request Item", item.name, "status"
                )
                if (
                    original_status
                    and original_status != "Open"
                    and item.status == "Open"
                ):
                    frappe.throw(
                        _(
                            "Cannot revert status back to 'Open' for beneficiary {0}"
                        ).format(item.beneficiary)
                    )

    def create_payment_for_item(self, item):
        """Create Payment Entry of type Pay for a single verified item"""
        target_account = None
        settings = frappe.get_single("Frappe NPO Settings")
        account_row = next(
            (d for d in settings.beneficiary_accounts if d.company == self.company),
            None,
        )

        if account_row:
            target_account = account_row.account
        if item.status != "Verified":
            return
        party = frappe.db.get_value("Beneficiary", item.beneficiary, "supplier")
        existing = frappe.get_all(
            "Payment Entry", filters={"reference_no": self.name, "party": party}
        )
        if existing:
            return

        pe = frappe.get_doc(
            {
                "doctype": "Payment Entry",
                "payment_type": "Pay",
                "party_type": "Supplier",
                "party": (party),
                "reference_name": item.name,
                "paid_to": target_account,
                "paid_from": self.agent_account,
                "posting_date": nowdate(),
                "paid_amount": item.amount or 0,
                "received_amount": item.amount or 0,
                "amount": item.amount or 0,
                "territory": self.state,
                "disbursement_order": self.disbursement_order,
                "reference_no": self.name,
                "reference_date": nowdate(),
            }
        )
        pe.insert(ignore_permissions=True)

    def create_payments_on_verified_items(self):
        """Iterate all items and create Payment Entries for those verified (progressive)"""
        for item in self.items:
            self.create_payment_for_item(item)

    def create_payments_for_all_verified(self):
        """Create Payment Entries for all items with status 'Verified' (batch)"""
        for item in self.items:
            if item.status == "Verified":
                self.create_payment_for_item(item)
