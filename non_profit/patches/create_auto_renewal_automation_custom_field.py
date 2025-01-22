import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Member": [
            dict(
                fieldname="custom_auto_subscription",
                fieldtype="Check",
                label="Auto Subscription",
                insert_after= "membership_type",
            ),
        ]
    }
    create_custom_fields(fields, update=True)