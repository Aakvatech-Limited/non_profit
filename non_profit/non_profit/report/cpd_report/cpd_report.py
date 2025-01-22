# Copyright (c) 2025, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    # Initialize conditions string
    conditions = ""
    
    # Add conditions based on filters
    if filters and filters.get("start_date"):
        conditions += " AND ts.start_time >= %(start_date)s"
    if filters and filters.get("end_date"):
        conditions += " AND ts.end_time <= %(end_date)s"
    if filters and filters.get("member"):
        conditions += " AND tsm.member = %(member)s"
    if filters and filters.get("training_program"):
        conditions += " AND ts.training_program = %(training_program)s"

    # Define columns
    columns = [
        {"label": _("Member ID"), "fieldtype": "Data", "fieldname": "member", "width": 200},
        {"label": _("Member Name"), "fieldtype": "Data", "fieldname": "member_name", "width": 200},
        {"label": _("Start Date"), "fieldtype": "Date", "fieldname": "start_time", "width": 200},
        {"label": _("End Date"), "fieldtype": "Date", "fieldname": "end_time", "width": 200},
        {"label": _("Program"), "fieldtype": "Data", "fieldname": "training_program", "width": 200},
        {"label": _("CPD Hour"), "fieldtype": "Data", "fieldname": "cpd_hour", "width": 200},
        {"label": _("Type"), "fieldtype": "Data", "fieldname": "type", "width": 200},
        {"label": _("Location"), "fieldtype": "Data", "fieldname": "location", "width": 200},
    ]

    # Fetch results
    results = frappe.db.sql(
        f"""
        SELECT
            DATE(ts.start_time) AS start_time,
            DATE(ts.end_time) AS end_time,
            ts.training_program AS training_program,
            ts.cpd_hour AS cpd_hour,
            ts.type AS type,
            ts.location AS location,
            tsm.member AS member,
            m.member_name AS member_name
        FROM
            `tabTraining Session` ts
        LEFT JOIN
            `tabTraining Session Member` tsm ON tsm.parent = ts.name
        LEFT JOIN
            `tabMember` m ON tsm.member = m.name
        WHERE
            1=1 {conditions}
        """,
        filters,
        as_dict=1
    )

    # Return columns and data
    return columns, results
