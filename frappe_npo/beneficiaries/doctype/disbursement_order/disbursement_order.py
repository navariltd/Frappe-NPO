# Copyright (c) 2026, hussain@frappe.io and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today
import json
import csv
from io import StringIO, BytesIO
from frappe.utils.xlsxutils import make_xlsx

from ....utils.data import extract_data_from_file, get_doctype_headers


class DisbursementOrder(Document):
    def before_save(self):
        total_amount = 0
        for row in self.beneficiaries or []:
            row.amount = (row.qty or 0) * (row.rate or 0)
            total_amount += row.amount or 0

        self.total_amount = total_amount

    def before_submit(self):
        if not self.beneficiaries:
            frappe.throw(
                _("At least one beneficiary must be allocated before submitting.")
            )

    @frappe.whitelist()
    def get_beneficiaries(self, advanced_filters=None):
        """
        Return list of beneficiaries matching filters for datatable display.
        """
        beneficiaries = frappe.get_list(
            "Beneficiary",
            filters=self.get_filters() + (advanced_filters or []),
            fields=[
                "name",
            ],
        )
        if self.donor:
            for ben in beneficiaries:
                beneficiary_no = frappe.get_value(
                    "Beneficiary Donor Assignment",
                    {
                        "parent": ben.name,
                        "parentfield": "donors",
                        "parenttype": "Beneficiary",
                        "donor": self.donor,
                    },
                    ["beneficiary_no"],
                )
                ben.beneficiary_no = beneficiary_no if beneficiary_no else None

        return beneficiaries

    def get_filters(self):
        filter_fields = [
            "state",
            "beneficiary_type",
            "district",
            "zone",
            "branch",
            "donor",
        ]
        filters = [["status", "=", "Active"]]

        for d in filter_fields:
            if self.get(d):
                if d == "donor":
                    filters.append(
                        ["Beneficiary Donor Assignment", "donor", "=", self.get(d)]
                    )
                else:
                    filters.append([d, "=", self.get(d)])
        return filters

    @frappe.whitelist()
    def allocate_beneficiaries(self, beneficiaries):
        if isinstance(beneficiaries, str):
            beneficiaries = json.loads(beneficiaries)

        if not beneficiaries:
            frappe.throw("No beneficiaries selected for allocation")

        for ben_no in beneficiaries:
            doc = frappe.get_doc(
                {
                    "doctype": "Donation Allocation",
                    "recipient_type": "Beneficiary",
                    "recipient": ben_no,
                    "project": self.project,
                    "company": self.company,
                    "cost_center": self.cost_center,
                    "branch": self.branch,
                    "donation": self.donation,
                    "donor": self.donor,
                    "from_date": self.from_date,
                    "to_date": self.to_date,
                    "items": self.items,
                }
            )
            doc.insert(ignore_permissions=True)

        frappe.msgprint(f"Allocated donations to {len(beneficiaries)} beneficiaries")
        return {"success": True}

    @frappe.whitelist()
    def download_beneficiary_template(self, file_type="csv"):
        headers = get_doctype_headers("Beneficiary Disbursement Entry Party")

        sample_rows = []
        for row in (self.beneficiaries or [])[:5]:
            sample_rows.append([getattr(row, h, "") or "" for h in headers])

        if not sample_rows:
            sample_rows = [["" for _ in headers] for _ in range(5)]

        if file_type.lower() == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(headers)
            writer.writerows(sample_rows)
            filedata = output.getvalue().encode("utf-8")
            filename = "donation_beneficiary_template.csv"

        elif file_type.lower() in ["xlsx", "excel"]:
            data = [headers] + sample_rows
            xlsx_file = make_xlsx(data, sheet_name="Beneficiaries")
            filedata = xlsx_file.getvalue()
            filename = "donation_beneficiary_template.xlsx"

        else:
            frappe.throw(_("Invalid file type. Only CSV or Excel supported"))

        file_doc = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": filename,
                "attached_to_doctype": "Disbursement Order",
                "attached_to_name": self.name or "",
                "content": filedata,
                "is_private": 0,
            }
        )
        file_doc.insert(ignore_permissions=True)
        return file_doc.file_url

    @frappe.whitelist()
    def upload_beneficiaries(self, file_url):
        headers = get_doctype_headers("Beneficiary Disbursement Entry Party")
        rows = extract_data_from_file(file_url)

        rows_to_upload = [r for r in rows if not r.get("beneficiary")]

        from ..beneficiary.beneficiary import upload_beneficiary_list

        upload_results = {"beneficiaries": [], "errors": []}
        if rows_to_upload:
            upload_results = upload_beneficiary_list(file_url, donor=self.donor)

        mapped_rows = []

        for idx, row in enumerate(rows):
            beneficiary_id = row.get("beneficiary")

            if not beneficiary_id and idx < len(
                upload_results.get("beneficiaries", [])
            ):
                beneficiary_id = upload_results["beneficiaries"][idx]

            mapped_row = {}
            for header in headers:
                mapped_row[header] = row.get(header, "")

            mapped_row["beneficiary"] = beneficiary_id
            mapped_rows.append(mapped_row)

        return {"mapped_items": mapped_rows, "errors": upload_results.get("errors", [])}

    @frappe.whitelist()
    def make_payment_entries(self):
        for row in self.beneficiaries:
            if row.payment_entry:
                continue

            supplier = frappe.get_value("Beneficiary", row.beneficiary, "supplier")

            payment_entry = frappe.get_doc(
                {
                    "doctype": "Payment Entry",
                    "payment_type": "Pay",
                    "party_type": "Supplier",
                    "party": supplier,
                    "paid_from": self.paid_from,
                    "paid_to": self.paid_to,
                    "company": self.company,
                    "posting_date": today(),
                    "mode_of_payment": row.mode_of_payment,
                    "cost_center": self.cost_center,
                    "project": self.project,
                    "paid_amount": row.amount,
                    "received_amount": row.amount,
                    "disbursement_order": self.name,
                    "remarks": f"Donation disbursement to beneficiary {row.beneficiary}",
                }
            )
            payment_entry.insert(ignore_permissions=True)
            row.payment_entry = payment_entry.name
        self.entries_created = True
        self.save()
        frappe.msgprint(
            f"Payment Entries created for {len(self.beneficiaries)} beneficiaries"
        )

    @frappe.whitelist()
    def make_stock_entries(self):
        beneficiaries_by_beneficiary = {}
        for row in self.beneficiaries:
            if row.stock_entry:
                continue

            beneficiary = row.beneficiary

            if beneficiary not in beneficiaries_by_beneficiary:
                beneficiaries_by_beneficiary[beneficiary] = []
            beneficiaries_by_beneficiary[beneficiary].append(row)

        for beneficiary, rows in beneficiaries_by_beneficiary.items():
            items = [
                {
                    "item_code": row.item_code,
                    "qty": row.qty,
                    "uom": row.uom,
                    "basic_rate": row.rate,
                    "amount": row.amount,
                    "s_warehouse": self.source_warehouse,
                }
                for row in rows
            ]

            stock_entry = frappe.get_doc(
                {
                    "doctype": "Stock Entry",
                    "stock_entry_type": "Material Issue",
                    "from_warehouse": self.source_warehouse,
                    "beneficiary": beneficiary,
                    "supplier": frappe.get_value(
                        "Beneficiary", beneficiary, "supplier"
                    ),
                    "company": self.company,
                    "posting_date": today(),
                    "cost_center": self.cost_center,
                    "project": self.project,
                    "disbursement_order": self.name,
                    "items": items,
                }
            )
            stock_entry.insert(ignore_permissions=True)

            for row in rows:
                row.stock_entry = stock_entry.name

        self.entries_created = True
        self.save()
        frappe.msgprint(
            f"Stock Entries created for {len(beneficiaries_by_beneficiary)} beneficiary(ies)"
        )

    @frappe.whitelist()
    def create_sales_invoice(self):
        customer = (
            frappe.get_value("Donor", self.donor, "customer") if self.donor else None
        )

        data = {"items": {}, "customer": customer, "currency": None, "total_amount": 0}

        if self.allocation_type == "Cash":
            payment_entries = frappe.get_all(
                "Payment Entry",
                filters={"disbursement_order": self.name, "docstatus": 1},
                fields=["paid_amount as amount", "paid_from_account_currency"],
            )

            data["total_amount"] = sum(pe.amount for pe in payment_entries)
            data["currency"] = (
                payment_entries[0].paid_from_account_currency
                if payment_entries
                else None
            )

            if self.items:
                item = self.items[0]
                data["items"][item.item_code] = {
                    "item_code": item.item_code,
                    "item_name": frappe.get_value("Item", item.item_code, "item_name"),
                    "amount": data["total_amount"],
                    "qty": 1,
                    "uom": item.uom,
                    "rate": data["total_amount"],
                }

        elif self.allocation_type == "Items":
            stock_entries = frappe.get_all(
                "Stock Entry",
                filters={"disbursement_order": self.name, "docstatus": 1},
                fields=["name", "total_outgoing_value as amount"],
            )

            data["total_amount"] = sum(se.amount for se in stock_entries)

            for se in stock_entries:
                items = frappe.get_all(
                    "Stock Entry Detail",
                    filters={"parent": se.name},
                    fields=[
                        "item_code",
                        "item_name",
                        "amount",
                        "qty",
                        "basic_rate",
                        "uom",
                        "s_warehouse as warehouse",
                    ],
                )

                for item in items:
                    code = item.item_code
                    if code not in data["items"]:
                        data["items"][code] = {
                            "item_code": code,
                            "item_name": item.item_name,
                            "uom": item.uom,
                            "warehouse": item.warehouse,
                            "amount": 0,
                            "qty": 0,
                            "rate": item.basic_rate,
                        }

                    data["items"][code]["amount"] += item.amount
                    data["items"][code]["qty"] += item.qty
                    data["items"][code]["rate"] = item.basic_rate

        else:
            frappe.throw("Invalid Allocation Type")

        si = frappe.new_doc("Sales Invoice")

        si.flags.ignore_mandatory = True
        si.flags.ignore_permissions = True
        si.flags.ignore_links = True

        si.customer = data["customer"]
        si.disbursement_order = self.name

        for item in data["items"].values():
            row = si.append("items", {})
            row.item_code = item["item_code"]
            row.item_name = item["item_name"]
            row.qty = item["qty"]
            row.stock_qty = item["qty"]
            row.rate = item["rate"]
            row.amount = item["amount"]
            row.uom = item["uom"]
            row.stock_uom = item["uom"]
            row.conversion_factor = 1.0
            if item.get("warehouse"):
                row.warehouse = item["warehouse"]

        si.insert(ignore_permissions=True)

        return {"sales_invoice": si.name}
