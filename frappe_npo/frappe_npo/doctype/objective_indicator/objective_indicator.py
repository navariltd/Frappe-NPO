# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ObjectiveIndicator(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		annual_target: DF.Int
		april: DF.Int
		august: DF.Int
		baseline: DF.Int
		december: DF.Int
		february: DF.Int
		january: DF.Int
		july: DF.Int
		june: DF.Int
		march: DF.Int
		may: DF.Int
		november: DF.Int
		october: DF.Int
		outcome_indicator: DF.SmallText | None
		output_indicator: DF.SmallText | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		september: DF.Int
	# end: auto-generated types

	pass
