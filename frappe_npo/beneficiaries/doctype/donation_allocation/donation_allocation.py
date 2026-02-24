# Copyright (c) 2025, hussain@frappe.io and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, nowdate
from frappe import _


class DonationAllocation(Document):
    def validate(self):
        if not self.from_date:
            self.from_date = nowdate()

        total_amount = 0.0
        for item in self.items:
            total_amount += flt(item.amount)
        self.total_amount = total_amount

        if total_amount > 0:
            for item in self.items:
                item.percentage = flt((item.amount / total_amount) * 100, 2)

        self.validate_total_against_donation()

    def before_submit(self):
        self.validate_total_against_donation()

    def validate_total_against_donation(self):
        donation_doc = frappe.get_doc("Donation", self.donation)
        total_distributed = get_total_allocated_amount(
            self.donation, exclude_allocation=self.name
        )
        new_total = total_distributed + self.total_amount

        if new_total > donation_doc.amount:
            frappe.db.set_value(
                "Donation",
                self.donation,
                "amount_distributed",
                total_distributed,
                update_modified=False,
            )
            frappe.throw(
                _(
                    "Total distributed amount ({0}) exceeds the original Donation amount ({1})."
                ).format(new_total, donation_doc.amount)
            )
        else:
            frappe.db.set_value(
                "Donation",
                self.donation,
                "amount_distributed",
                new_total,
                update_modified=False,
            )


@frappe.whitelist()
def get_total_allocated_amount(donation_name, exclude_allocation=None):
    """
    Returns the total amount already allocated (submitted) for a given Donation.
    Optionally exclude a specific Donation Allocation document (e.g., current draft).
    """
    filters = {
        "donation": donation_name,
        "docstatus": 1,
    }
    if exclude_allocation:
        filters["name"] = ["!=", exclude_allocation]

    allocations = frappe.get_all(
        "Donation Allocation", filters=filters, fields=["total_amount"]
    )
    return sum(flt(alloc.total_amount) for alloc in allocations)


@frappe.whitelist()
def get_budget_accounts(budget_name):
    """
    Returns a list of all accounts associated with a specific budget.

    Args:
            budget_name (str): The name of the budget document

    Returns:
            list: List of account names from the budget
    """
    if not budget_name:
        return []

    accounts = frappe.get_all(
        "Budget Account",
        filters={"parent": budget_name},
        fields=["account"],
        distinct=True,
    )
    return [d.get("account") for d in accounts if d.get("account")]


@frappe.whitelist()
def get_available_budgets(doctype, txt, searchfield, start, page_len, filters):
    budgets = frappe.get_all(
        "Budget",
        filters={"docstatus": 1, searchfield: ("like", f"%{txt}%")},
        fields=["name"],
        start=start,
        page_length=page_len,
    )

    valid_budgets = []
    for budget in budgets:
        accounts = frappe.get_all(
            "Budget Account",
            filters={"parent": budget.name},
            fields=["account", "budget_amount"],
        )

        for acc in accounts:
            allocated = (
                frappe.db.get_value(
                    "Donation Allocation Item",
                    {"account": acc.account},
                    ["SUM(amount)"],
                )
                or 0
            )

            if float(acc.budget_amount) > float(allocated):
                valid_budgets.append((budget.name,))
                break

    return valid_budgets


@frappe.whitelist()
def allocate_to_budget(total_amount_to_allocate, budget):
    total_amount_to_allocate = flt(total_amount_to_allocate)
    if total_amount_to_allocate <= 0:
        frappe.throw(_("No amount available for allocation."))

    budget_accounts = frappe.get_all(
        "Budget Account",
        filters={"parent": budget},
        fields=["account", "budget_amount"],
        order_by="idx asc",
    )

    allocation_rows = []

    for acc in budget_accounts:
        allocated = (
            frappe.db.get_value(
                "Donation Allocation Item",
                filters={"account": acc.account},
                fieldname=["SUM(amount)"],
            )
            or 0.0
        )

        remaining = flt(acc.budget_amount) - flt(allocated)

        if remaining <= 0:
            continue

        if total_amount_to_allocate <= 0:
            break

        alloc_amount = min(remaining, total_amount_to_allocate)

        allocation_rows.append({"account": acc.account, "amount": alloc_amount})

        total_amount_to_allocate -= alloc_amount

    return allocation_rows


@frappe.whitelist()
def get_available_donations_for_payment_entry(payment_entry_name):
    """
    Fetches Donation names and available amounts from a Payment Entry's references.
    """
    if not payment_entry_name:
        return []

    donations_in_payment_entry = frappe.get_all(
        "Payment Entry Reference",
        filters={"parent": payment_entry_name, "reference_doctype": "Donation"},
        fields=["reference_name"],
    )

    donation_names = [d.get("reference_name") for d in donations_in_payment_entry]

    if not donation_names:
        return []

    available_donations = []

    for donation_name in donation_names:
        donation_doc = frappe.get_doc("Donation", donation_name)
        total_amount = donation_doc.get("total_amount_paid")
        allocated_amount = donation_doc.get("amount_distributed", 0)

        if total_amount is None:
            frappe.log_error(
                f"Total amount not found for Donation {donation_name}",
                "Donation Allocation Error",
            )
            continue

        remaining = float(total_amount) - float(allocated_amount)

        if remaining > 0:
            available_donations.append(
                {
                    "name": donation_name,
                    "total_amount": total_amount,
                    "allocated_amount": allocated_amount,
                    "remaining_amount": remaining,
                }
            )

    return available_donations
