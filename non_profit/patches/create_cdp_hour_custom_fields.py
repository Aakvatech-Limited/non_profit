import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    fields = {
        "Training Program": [
            dict(
                fieldname="cpd_hour",
                fieldtype="Data",
                label="CPD Hour",
                insert_after= "company",
            ),
        ],
        "Training Event": [
            dict(
                fieldname="cpd_hour",
                fieldtype="Data",
                label="CPD Hour",
                insert_after= "training_program",
                fetch_from= "training_program.cpd_hour",
                read_only= 1
            ),
        ]
    }
    create_custom_fields(fields, update=True)