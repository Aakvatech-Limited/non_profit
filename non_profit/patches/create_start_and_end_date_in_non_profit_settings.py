import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Non Profit Settings": [
            dict(
                fieldname="column_break_iefqw",
                fieldtype="Column Break",
                label="",
                insert_after= "membership_webhook_secret",
            ),
            dict(
                fieldname="start_date",
                fieldtype="Date",
                label="Start Date",
                insert_after= "column_break_iefqw",
            ),
            dict(
                fieldname="end_date",
                fieldtype="Date",
                label="End Date",
                insert_after= "start_date",
            ),
        ]
    }
    create_custom_fields(fields, update=True)