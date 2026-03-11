import frappe
from frappe import _
import json
from frappe.query_builder.functions import Sum


@frappe.whitelist()
def get_disbursement_orders(
    from_date=None,
    to_date=None,
    company=None,
    donor=None,
    po_no=None,
    disbursement_type=None,
    item_code=None,
):
    filters = {"docstatus": 1}

    if from_date and to_date:
        filters["creation"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["creation"] = [">=", from_date]
    elif to_date:
        filters["creation"] = ["<=", to_date]

    if company:
        filters["company"] = company
    if donor:
        filters["donor"] = donor
    if po_no:
        filters["po_no"] = ["like", f"%{po_no}%"]
    if disbursement_type:
        filters["disbursement_type"] = disbursement_type

    disbursement_orders = frappe.get_all(
        "Disbursement Order",
        filters=filters,
        fields=[
            "name",
            "donor",
            "po_no",
            "po_date",
            "disbursement_type",
        ],
        order_by="creation desc",
    )

    unbilled_orders = []

    for order in disbursement_orders:
        existing_invoice = frappe.db.exists(
            "Sales Invoice Item",
            {
                "disbursement_order": order.name,
                "docstatus": ["!=", 2],
            },
        )

        if not existing_invoice:
            unbilled_orders.append(order)

    return unbilled_orders


@frappe.whitelist()
def get_disbursement_totals(orders):
    if isinstance(orders, str):
        orders = json.loads(orders)

    if not orders:
        return {}

    do = frappe.qb.DocType("Disbursement Order")
    donor_dt = frappe.qb.DocType("Donor")

    header_data = (
        frappe.qb.from_(do)
        .join(donor_dt)
        .on(do.donor == donor_dt.name)
        .select(do.donor, donor_dt.customer)
        .where(do.name.isin(orders))
    ).run(as_dict=True)

    unique_donors = list(set(d.donor for d in header_data))
    unique_customers = list(set(d.customer for d in header_data))

    customer = unique_customers[0] if len(unique_customers) == 1 else None
    donor = unique_donors[0] if len(unique_donors) == 1 else None

    pe = frappe.qb.DocType("Payment Entry")
    payments = (
        frappe.qb.from_(pe)
        .select(pe.disbursement_order, Sum(pe.paid_amount).as_("total_paid"))
        .where(pe.disbursement_order.isin(orders))
        .where(pe.payment_type == "Pay")
        .where(pe.docstatus == 1)
        .groupby(pe.disbursement_order)
    ).run(as_dict=True)

    paid_map = {p.disbursement_order: p.total_paid for p in payments}

    dop = frappe.qb.DocType("Disbursement Order Party")
    fees = (
        frappe.qb.from_(dop)
        .select(dop.parent, Sum(dop.bank_transfer_fee).as_("total_fee"))
        .where(dop.parent.isin(orders))
        .groupby(dop.parent)
    ).run(as_dict=True)

    fee_map = {f.parent: f.total_fee for f in fees}

    items_list = []

    for order_name in orders:
        doi = frappe.qb.DocType("Disbursement Order Item")
        order_items = (
            frappe.qb.from_(doi)
            .select(
                doi.item_code, doi.project, doi.uom, doi.item_name, doi.rate, doi.qty
            )
            .where(doi.parent == order_name)
        ).run(as_dict=True)

        order_payment = paid_map.get(order_name, 0)
        order_fee = fee_map.get(order_name, 0)

        for i, item in enumerate(order_items):
            if i == 0:
                calc_rate = (order_payment or 0) + (order_fee or 0)
                calc_qty = 1
            else:
                calc_rate = item.rate
                calc_qty = item.qty

            items_list.append(
                {
                    "item_code": item.item_code,
                    "item_name": item.item_name or item.item_code,
                    "qty": calc_qty,
                    "uom": item.uom,
                    "rate": calc_rate,
                    "amount": float(calc_rate) * float(calc_qty),
                    "project": item.project,
                    "disbursement_order": order_name,
                }
            )

    return {"items": items_list, "customer": customer, "donor": donor}
