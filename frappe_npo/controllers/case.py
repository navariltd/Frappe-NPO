import frappe


def before_save(doc, method=None):
    """
    Hook function to be called before saving a ToDo document related to an Case.
    - If the ToDo is an assignment (status 'Open') for an Case
        appends the assigned user's details to the Case's assigned_paralegals table.
    - If the ToDo's status changes to 'Cancelled',
        removes the user from the Case's assigned_paralegals table and deletes
        the corresponding Paralegal User record.
    Args:
        doc: The ToDo document being saved.
        method: Optional method argument (not used).
    Returns:
        None
    """
    # Check if the ToDo is an assignment for an Case
    if doc.reference_type != "Case" or not doc.reference_name:
        return

    parent_case = frappe.get_doc("Case", doc.reference_name)

    # Handle a new assignment (Todo status is 'Open')
    if parent_case.status != "Closed":
        user_details = frappe.db.get_value(
            "User", doc.allocated_to, ["full_name", "phone"], as_dict=True
        )

        if user_details:
            parent_case.append(
                "assigned_paralegals",
                {
                    "user": doc.allocated_to,
                    "full_name": user_details.get("full_name"),
                    "phone": user_details.get("phone"),
                },
            )
            parent_case.save()

    # Handle a user unassignment (Todo status is changed to 'Cancelled')
    if doc.has_value_changed("status") and doc.status == "Cancelled":
        for row in parent_case.get("assigned_paralegals"):
            if row.user == doc.allocated_to:
                parent_case.remove(row)
                parent_case.save()
                frappe.db.delete(
                    "Paralegal User",
                    {"parent": parent_case.name, "user": doc.allocated_to},
                )
                frappe.db.commit()

                break
