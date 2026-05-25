# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form

from non_profit.non_profit.doctype.membership.membership import (
	build_membership_sales_order_item,
	make_sales_order,
)



class MemberEmployer(Document):
    def before_save(self):
        # Create a new Customer if it doesn't exist
        if not frappe.db.exists("Customer", {"customer_name": self.member_employer_name}):
            doc = frappe.get_doc({
                'doctype': 'Customer',
                'customer_name': self.member_employer_name,
                'customer_type': 'Company',
                'customer_group': 'IIA Members',
                'territory': 'All Territories'
            })
            doc.insert(ignore_permissions=True)
            frappe.msgprint(
                msg=_("Customer {0} created successfully.").format(self.member_employer_name),
                title=_("Success"),
                indicator='green'
            )

    @frappe.whitelist()
    def generate_bulk_sales_order(self, save=True, with_payment_entry=False):
        members = frappe.db.get_all(
            "Member",
            filters={
                "employer_name": self.name,
                "invoice_to": "Member Employer"
            },
            fields=["name", "member_name"]
        )

        if not members:
            frappe.throw(_("No members found linked to this employer."))

        customer = self.get_customer_name()
        if not customer:
            frappe.throw(_("No customer found for employer {0}.").format(frappe.bold(self.member_employer_name)))

        settings = frappe.get_doc("Non Profit Settings")
        memberships = []
        items = []

        for member in members:
            membership_rows = frappe.get_all(
                "Membership",
                filters={
                    "member": member["name"],
                    "membership_status": "New",
                },
                fields=["name", "sales_order", "invoice"],
                order_by="creation desc",
                limit=1,
            )

            if not membership_rows:
                continue

            membership_row = membership_rows[0]
            membership_doc = frappe.get_doc("Membership", membership_row["name"])
            if membership_row["invoice"]:
                frappe.throw(_("An invoice is already linked to member {0}.").format(member["member_name"]))
            if membership_row["sales_order"]:
                frappe.throw(_("A sales order is already linked to member {0}.").format(member["member_name"]))

            plan = frappe.get_doc("Membership Type", membership_doc.membership_type)
            self.validate_membership_type_and_settings(plan, settings)
            items.append(build_membership_sales_order_item(membership_doc, plan, include_reference=True))
            memberships.append(membership_doc)

        if not items:
            frappe.throw(_("No eligible memberships found for this employer."))

        sales_order = make_sales_order(customer, memberships[0], settings, items)
        self.db_set("sales_order", sales_order.name)

        for membership_doc in memberships:
            membership_doc.db_set("sales_order", sales_order.name)

        frappe.msgprint(_("Sales Order created successfully"))
        return sales_order

    @frappe.whitelist()
    def generate_bulk_invoice(self, save=True, with_payment_entry=False):
        return self.generate_bulk_sales_order(save=save, with_payment_entry=with_payment_entry)

    def get_customer_name(self):
        return frappe.db.get_value("Customer", {"customer_name": self.member_employer_name}, "name")

    def validate_membership_type_and_settings(self, plan, settings):
        settings_link = get_link_to_form("Non Profit Settings", "Non Profit Settings")
        
        if not settings.company:
            frappe.throw(_("You need to set <b>Default Company</b> for sales orders in {0}").format(settings_link))
        if not plan.linked_item:
            frappe.throw(_("Please set a Linked Item for the Membership Type {0}").format(
                get_link_to_form("Membership Type", plan.name)
            ))
