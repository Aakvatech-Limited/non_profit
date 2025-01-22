
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    fields = {
        "Training Event Employee":[
            dict(
                fieldname= "member",
                fieldtype="Link",
                label="Member",
                options= "Member",
                in_list_view= 1
            ),
            dict(
                fieldname= "member_name",
                fieldtype="Data",
                label="Member Name",
                read_only= 1,
                fetch_from= "member.member_name"
            )
        ],
        "Training Result Employee":[
            dict(
                fieldname= "member",
                fieldtype="Link",
                label="Member",
                options= "Member",
                in_list_view= 1
            ),
            dict(
                fieldname= "member_name",
                fieldtype="Data",
                label="Member Name",
                read_only= 1,
                fetch_from= "member.member_name"
            )
        ],
        "Training Feedback":[
            dict(
                fieldname= "member",
                fieldtype="Link",
                label="Member",
                options= "Member"
            ),
            dict(
                fieldname= "member_name",
                fieldtype="Data",
                label="Member Name",
                read_only= 1,
                fetch_from= "member.member_name"
            )
        ],
        

    }
    create_custom_fields(fields, update=True) 