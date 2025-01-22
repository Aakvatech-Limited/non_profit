import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def execute():
    properties = [
        {
            "doc_type": "Training Feedback",
            "field_name": "employee",
            "property": "reqd",
            "property_type": "Check",
            "value": 0,
        },
    ]

    for property in properties:
        make_property_setter(
            property.get("doc_type"),
            property.get("field_name"),
            property.get("property"),
            property.get("value"),
            property.get("property_type"),
            for_doctype=property.get("for_doctype"),
            validate_fields_for_doctype=False,
        )

    frappe.db.commit()
