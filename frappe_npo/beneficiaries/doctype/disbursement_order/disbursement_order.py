# Copyright (c) 2026, hussain@frappe.io and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today
from frappe.query_builder import DocType
from frappe.desk.form.assign_to import add as assign_to

from ....utils.data import extract_data_from_file, get_doctype_headers


class DisbursementOrder(Document):
    def validate(self):
        self.validate_multiple_so_setting()
        if self.from_date and self.to_date and self.from_date > self.to_date:
            frappe.throw(
                _("From Date must be earlier than or equal to To Date."),
                title=_("Invalid Date Range"),
            )
        total_amount = 0
        for row in self.beneficiaries or []:
            row.amount = (row.qty or 0) * (row.rate or 0)
            total_amount += row.amount or 0

        self.total_amount = total_amount

        if self.beneficiaries and self.disbursement_type == "Cash":
            self.calculate_bank_transfer_fees()

    def before_submit(self):
        if not self.beneficiaries:
            frappe.throw(
                _("At least one beneficiary must be allocated before submitting.")
            )

    def on_submit(self):
        if self.beneficiaries and self.disbursement_type == "Cash":
            self.create_territory_sales_orders()

    def calculate_bank_transfer_fees(self):
        from frappe.query_builder import DocType, Criterion

        Territory = DocType("Territory")
        SalesPerson = DocType("Sales Person")
        BankAccount = DocType("Bank Account")
        Bank = DocType("Bank")

        query = (
            frappe.qb.from_(Territory)
            .inner_join(SalesPerson)
            .on(Territory.territory_manager == SalesPerson.name)
            .inner_join(BankAccount)
            .on(SalesPerson.bank_account == BankAccount.name)
            .inner_join(Bank)
            .on(BankAccount.bank == Bank.name)
            .select(Territory.name.as_("territory"), Bank.bank_charge.as_("charge"))
        )

        territory_charges = {d.territory: d.charge for d in query.run(as_dict=True)}
        total_transfer_fees = 0
        for row in self.beneficiaries:
            beneficiary_territory = frappe.db.get_value(
                "Beneficiary", row.beneficiary, "territory"
            )

            if beneficiary_territory in territory_charges:
                row.bank_transfer_fee = territory_charges[beneficiary_territory]
                total_transfer_fees += row.bank_transfer_fee or 0
            else:
                row.bank_transfer_fee = 0

        self.total_bank_transfer_fee = total_transfer_fees

    def validate_multiple_so_setting(self):
        if not self.create_a_sales_order_for_each_state:
            return

        allow_multiple = frappe.db.get_single_value(
            "Selling Settings", "allow_against_multiple_purchase_orders"
        )

        if not allow_multiple:
            frappe.throw(
                _(
                    "Multiple Sales Orders per state is enabled, but your system does not "
                    "allow multiple Sales Orders against the same Customer Purchase Order.<br><br>"
                    "Please enable <b>Allow Multiple Sales Orders Against a Customer's Purchase Order</b> "
                    "in <a href='/app/selling-settings' target='_blank'><b>Selling Settings</b></a> "
                    "and try again."
                ),
                title=_("Selling Settings Configuration Required"),
            )

    @frappe.whitelist()
    def create_sales_orders(self):
        sales_order_status = frappe.db.get_single_value(
            "Frappe NPO Settings",
            "default_status_for_auto_created_sales_order",
        )
        territory_data = {}

        single_so = not self.create_a_sales_order_for_each_state
        grouping_key = "ALL" if single_so else None

        for row in self.beneficiaries:
            territory = row.territory or frappe.db.get_value(
                "Beneficiary", row.beneficiary, "territory"
            )

            if not territory and not single_so:
                continue

            key = grouping_key if single_so else territory

            if key not in territory_data:
                territory_data[key] = {
                    "distribution_amount": 0,
                    "bank_fees": 0,
                    "territory": territory if not single_so else None,
                }

            territory_data[key]["distribution_amount"] += row.amount or 0
            territory_data[key]["bank_fees"] += row.bank_transfer_fee or 0

        customer = (
            frappe.get_value("Donor", self.donor, "customer") if self.donor else None
        )

        if not customer:
            frappe.msgprint(
                _("No Customer linked to Donor. Skipping Sales Order creation.")
            )
            return

        if not self.items:
            frappe.throw(_("Please add at least one item in the Items table."))

        distribution_item_code = self.items[0].item_code

        bank_item_code = None

        for item in self.items:
            name_check = (item.item_code or "").lower()
            if any(keyword in name_check for keyword in ["bank", "fee", "charge"]):
                bank_item_code = item.item_code
                break

        if not bank_item_code:
            possible_name = "Bank Transfer Charges"

            if frappe.db.exists("Item", possible_name):
                bank_item_code = possible_name
            else:
                item = frappe.new_doc("Item")
                item.item_code = possible_name
                item.item_name = possible_name
                item.is_stock_item = 0
                item.is_sales_item = 1
                item.insert(ignore_permissions=True)
                bank_item_code = item.name

        for key, totals in territory_data.items():
            so = frappe.new_doc("Sales Order")
            so.flags.ignore_permissions = True
            so.customer = customer
            so.transaction_date = today()
            so.delivery_date = self.to_date or today()
            so.company = self.company
            so.po_no = self.po_no
            so.po_date = self.po_date
            so.donor = self.donor
            so.disbursement_order = self.name

            if not single_so:
                so.territory = totals["territory"]

            if totals["distribution_amount"] > 0:
                so.append(
                    "items",
                    {
                        "item_code": distribution_item_code,
                        "qty": 1,
                        "rate": totals["distribution_amount"],
                        "delivery_date": so.delivery_date,
                    },
                )

            if totals["bank_fees"] > 0:
                so.append(
                    "items",
                    {
                        "item_code": bank_item_code,
                        "qty": 1,
                        "rate": totals["bank_fees"],
                        "delivery_date": so.delivery_date,
                    },
                )

            if so.items:
                so.insert(ignore_permissions=True)
                if sales_order_status == "Submitted":
                    so.submit()

                if single_so:
                    frappe.msgprint(
                        _("Sales Order {0} created successfully.").format(so.name)
                    )
                else:
                    frappe.msgprint(
                        _("Sales Order {0} created for Territory {1}").format(
                            so.name, totals["territory"]
                        )
                    )

    @frappe.whitelist()
    def get_beneficiaries(self, advanced_filters=None):
        """
        Return list of beneficiaries matching filters for datatable display.
        """
        beneficiaries = frappe.get_list(
            "Beneficiary",
            filters=self.get_filters() + (advanced_filters or []),
            fields=["name", "full_name", "beneficiary_type", "district", "territory"],
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
            "territory",
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
    def upload_beneficiaries(self, file_url):
        headers = get_doctype_headers("Disbursement Order Party")
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
            mapped_row["district"] = row.get("district") or row.get("locality")
            mapped_row["territory"] = row.get("territory") or row.get("state")
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

        if self.disbursement_type == "Cash":
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

        elif self.disbursement_type == "Items":
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
