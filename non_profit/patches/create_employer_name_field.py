import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Member": [
            dict(
                fieldname="employer_name",
                fieldtype="Link",
                label="Employer Name",
                insert_after= "custom_column_break",
                options="Member Employer",
            ),
        ]
    }
    create_custom_fields(fields, update=True)