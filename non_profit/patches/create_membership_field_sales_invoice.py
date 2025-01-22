import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Sales Invoice Item": [
            dict(
                fieldname="membership_id",
                fieldtype="Link",
                label="Membership ID",
                insert_after= "delivery_status",
                options= "Membership",
            ),
            dict(
                fieldname="member_name",
                fieldtype="Data",
                label="Member Name",
                insert_after= "membership_id",
                fetch_from= "membership_id.member_name",
                in_list_view= 1
            ),
        ]
        
    }
    create_custom_fields(fields, update=True)