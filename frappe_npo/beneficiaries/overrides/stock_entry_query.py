import frappe
import json
from frappe import _


@frappe.whitelist()
def get_filtered_beneficiaries(project):
    branch = frappe.db.get_value("Project", project, "custom_branch")
    if not branch:
        return []

    beneficiaries = frappe.get_all(
        'Beneficiary', filters={'status': 'Active', 'branch': branch}, fields=['name']
    )
    stock_entries = frappe.get_all(
        'Stock Entry', filters={'project': project,}, fields=['custom_beneficiary']
    )
    excluded = {entry['custom_beneficiary'] for entry in stock_entries}
    return [b['name'] for b in beneficiaries if b['name'] not in excluded]


@frappe.whitelist()
def get_bom_items(project):
    bom_name = frappe.db.get_value('BOM', {'project': project}, 'name')
    if not bom_name:
        return []

    bom_items = frappe.get_all(
        'BOM Item',
        filters={'parent': bom_name},
        fields=['*']
    )
    return bom_items


@frappe.whitelist()
def get_distribution_data(project):

	project_doc = frappe.get_doc("Project", project)
	branch = project_doc.custom_branch

	bom = frappe.db.get_value("BOM", {
		"project": project,
		"docstatus": 1
	}, "name", order_by="creation desc")

	used_beneficiaries = frappe.get_all("Stock Entry",
		filters={"project": project, "branch": branch},
		fields=["custom_beneficiary"]
	)
	used_beneficiaries_set = {d.custom_beneficiary for d in used_beneficiaries if d.custom_beneficiary}

	beneficiaries = frappe.get_all("Beneficiary", 
		filters={
			"branch": branch,
			"status": "Active",
			"name": ["not in", list(used_beneficiaries_set)]
		},
		fields=["name as beneficiary", "beneficiary_no", "full_name"]
	)

	return {
		"bom": bom,
		"beneficiaries": beneficiaries
	}
 

@frappe.whitelist()
def create_food_stock_entries(project, bom, beneficiaries, warehouse=None):
    """
    Creates a unique Stock Entry of type 'Distribution' for each beneficiary,
    populating it with items from the specified Bill of Materials (BOM).

    :param project: The Project name (str) associated with the distribution.
    :param bom: The Bill of Materials name (str) containing the items to distribute.
    :param beneficiaries: A JSON string representing a list of beneficiary dictionaries.
                          Each dictionary must contain a 'beneficiary' key with the beneficiary's ID.
                          Example: '[{"beneficiary": "BEN001"}, {"beneficiary": "BEN002"}]'
    :return: A list of names of the created Stock Entry documents (list of str).
    :raises frappe.ValidationError: If no beneficiaries are selected, or if no BOM items are found.
    """
    beneficiaries = json.loads(beneficiaries)
    project_doc = frappe.get_doc("Project", project)

    if not beneficiaries:
        frappe.throw(_("No beneficiaries selected."))

    bom_items = frappe.get_all(
        'BOM Item',
        filters={'parent': bom},
        fields=['*']
    )

    if not bom_items:
        frappe.throw(_("No BOM items found for the selected BOM."))

    from_warehouse = warehouse
    if project_doc.custom_branch and not from_warehouse:
        warehouse = frappe.get_value("Warehouse", {"name": ["like", f"%{project_doc.custom_branch}%"]}, "name")
        if warehouse:
            from_warehouse = warehouse
        else:
            frappe.msgprint(_(f"No warehouse found matching branch '{project_doc.custom_branch}'. "
                               "Stock Entry will be created without a source warehouse if not explicitly set."))

    created_stock_entries = [] 

    for b in beneficiaries:
        beneficiary_id = b.get("beneficiary")
        beneficiary_no = frappe.db.get_value("Beneficiary", beneficiary_id, "beneficiary_no") if beneficiary_id else None
        if not beneficiary_id:
            frappe.msgprint(_(f"Skipping beneficiary entry with missing 'beneficiary' ID: {b}"))
            continue
        if frappe.db.exists("Stock Entry", {
            "project": project, 
            "stock_entry_type": "Distribution",
            "custom_beneficiary": beneficiary_id
        }):
            frappe.msgprint(_(f"Stock Entry already exists for Beneficiary {beneficiary_id} in this project!"))
            continue

        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Distribution" if frappe.db.exists("Stock Entry Type", "Distribution") else "Material Issue"
        se.project = project
        se.branch = project_doc.custom_branch
        se.cost_center = project_doc.cost_center
        se.custom_beneficiary = beneficiary_id
        se.beneficiary_no = beneficiary_no

        if from_warehouse:
            se.from_warehouse = from_warehouse

        for item in bom_items:
            se.append("items", {
                "item_code": item.get("item_code"),
                "item_name": item.get("item_name"),
                "item_group": item.get("item_group"),
                "s_warehouse": se.from_warehouse, 
                "uom": item.get("stock_uom"),
                "stock_uom": item.get("stock_uom"),
                "conversion_factor": item.get("conversion_factor") or 1,
                "qty": item.get("qty"), 
                "expense_account": item.get("expense_account")
            })

        try:
            se.insert(ignore_permissions=True, ignore_mandatory=True) 
            created_stock_entries.append(se.name)
        except Exception as e:
            frappe.log_error(f"Error creating Stock Entry for beneficiary {beneficiary_id}: {e}", "Stock Entry Creation Error")
            frappe.msgprint(_(f"Failed to create Stock Entry for Beneficiary {beneficiary_id}. Error: {e}"))

    return created_stock_entries