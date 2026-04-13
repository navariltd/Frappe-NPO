# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ProgramIndicatorTracker(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from frappe_npo.frappe_npo.doctype.objective_indicator.objective_indicator import ObjectiveIndicator

		goal: DF.SmallText | None
		indicators: DF.Table[ObjectiveIndicator]
		objective: DF.SmallText
		program: DF.Link
		year: DF.Link | None
	# end: auto-generated types

	pass
