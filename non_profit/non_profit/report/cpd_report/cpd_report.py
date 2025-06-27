# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    # Initialize conditions string
    conditions = ""
    
    # Add conditions based on filters
    if filters and filters.get("start_date"):
        conditions += " AND te.start_time >= %(start_date)s"
    if filters and filters.get("end_date"):
        conditions += " AND te.end_time <= %(end_date)s"
    if filters and filters.get("member"):
        conditions += " AND tem.member = %(member)s"
    if filters and filters.get("training_program"):
        conditions += " AND te.training_program = %(training_program)s"

    # Define columns
    columns = [
        {"label": _("Member ID"), "fieldtype": "Link", "fieldname": "member", "options":"Member", "width": 200, "align": "left"},
        {"label": _("Member Name"), "fieldtype": "Data", "fieldname": "member_name", "width": 200, "align": "left"},
        {"label": _("Start Date"), "fieldtype": "Date", "fieldname": "start_time", "width": 200, "align": "left"},
        {"label": _("End Date"), "fieldtype": "Date", "fieldname": "end_time", "width": 200, "align": "left"},
        {"label": _("Program"), "fieldtype": "Data", "fieldname": "training_program", "width": 200, "align": "left"},
        {"label": _("CPD Hour"), "fieldtype": "Data", "fieldname": "cpd_hour", "width": 200, "align": "left"},
        {"label": _("Type"), "fieldtype": "Data", "fieldname": "type", "width": 200, "align": "left"},
        {"label": _("Location"), "fieldtype": "Data", "fieldname": "location", "width": 200, "align": "left"},
    ]

    # Fetch results
    results = frappe.db.sql(
        f"""
        SELECT
            DATE(te.start_time) AS start_time,
            DATE(te.end_time) AS end_time,
            te.training_program AS training_program,
            te.cpd_hour AS cpd_hour,
            te.type AS type,
            te.location AS location,
            tem.member AS member,
            m.member_name AS member_name
        FROM
            `tabTraining Event` te
        LEFT JOIN
            `tabTraining Event Employee` tem ON tem.parent = te.name
        LEFT JOIN
            `tabMember` m ON tem.member = m.name
        WHERE
            1=1 {conditions}
        """,
        filters,
        as_dict=1
    )

    # Return columns and data
    return columns, results
