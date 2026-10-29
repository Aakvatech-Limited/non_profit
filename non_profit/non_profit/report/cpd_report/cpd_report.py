# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import Criterion
from frappe.query_builder.functions import Date


def execute(filters=None):
	# Define columns
	columns = [
		{
			"label": _("Member ID"),
			"fieldtype": "Link",
			"fieldname": "member",
			"options": "Member",
			"width": 200,
			"align": "left",
		},
		{
			"label": _("Member Name"),
			"fieldtype": "Data",
			"fieldname": "member_name",
			"width": 200,
			"align": "left",
		},
		{
			"label": _("Start Date"),
			"fieldtype": "Date",
			"fieldname": "start_time",
			"width": 200,
			"align": "left",
		},
		{"label": _("End Date"), "fieldtype": "Date", "fieldname": "end_time", "width": 200, "align": "left"},
		{
			"label": _("Program"),
			"fieldtype": "Data",
			"fieldname": "training_program",
			"width": 200,
			"align": "left",
		},
		{"label": _("CPD Hour"), "fieldtype": "Data", "fieldname": "cpd_hour", "width": 200, "align": "left"},
		{"label": _("Type"), "fieldtype": "Data", "fieldname": "type", "width": 200, "align": "left"},
		{"label": _("Location"), "fieldtype": "Data", "fieldname": "location", "width": 200, "align": "left"},
	]

	results = get_data(filters or {})

	# Return columns and data
	return columns, results


def get_data(filters):
	event = frappe.qb.DocType("Training Event")
	attendee = frappe.qb.DocType("Training Event Employee")
	member = frappe.qb.DocType("Member")

	conditions = []
	if filters.get("start_date"):
		conditions.append(event.start_time >= filters.get("start_date"))
	if filters.get("end_date"):
		conditions.append(event.end_time <= filters.get("end_date"))
	if filters.get("member"):
		conditions.append(attendee.member == filters.get("member"))
	if filters.get("training_program"):
		conditions.append(event.training_program == filters.get("training_program"))

	return (
		frappe.qb.from_(event)
		.left_join(attendee)
		.on(attendee.parent == event.name)
		.left_join(member)
		.on(attendee.member == member.name)
		.select(
			Date(event.start_time).as_("start_time"),
			Date(event.end_time).as_("end_time"),
			event.training_program.as_("training_program"),
			event.cpd_hour.as_("cpd_hour"),
			event.type.as_("type"),
			event.location.as_("location"),
			attendee.member.as_("member"),
			member.member_name.as_("member_name"),
		)
		.where(Criterion.all(conditions))
	).run(as_dict=True)
