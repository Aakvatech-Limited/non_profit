# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form



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
    def generate_bulk_invoice(self, save=True, with_payment_entry=False):
        # Fetch members linked to this employer
        members = frappe.db.get_all(
            "Member",
            filters={
                'employer_name': self.name,
                'invoice_to': 'Member Employer'
            },
            fields=['name', 'member_name', 'customer']
        )
        member_count = len(members)
        
        # Validate members
        if not members:
            frappe.throw(_("No members found linked to this employer."))
        
        total_amount = 0
        items = []
        
        for member in members:
            # Check if customer is linked to the member
            if not member['customer']:
                frappe.throw(_("No customer linked to member {0}.").format(frappe.bold(member['member_name'])))

            # Fetch membership details
            membership_doc = frappe.get_doc("Membership", {'member': member['name']})
            
            # Check for existing invoices
            if membership_doc.invoice:
                frappe.throw(_("An invoice is already linked to member {0}.").format(member['member_name']))
            
            plan = frappe.get_doc("Membership Type", membership_doc.membership_type)
            settings = frappe.get_doc("Non Profit Settings")
            self.validate_membership_type_and_settings(plan, settings)
            
            # Correctly append dictionary to the items list
            items.append({
                "item_code": plan.linked_item,
                "rate": membership_doc.amount,
                "membership_id": membership_doc.name,
                "qty": 1
            })

        # Generate the invoice
        invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": self.name,
            "debit_to": settings.membership_debit_account,
            "currency": self.currency,
            "company": settings.company,
            "is_pos": 0,
            "items": items
        })
        invoice.set_missing_values()
        invoice.insert()
        invoice.submit()

        frappe.msgprint(_("Sales Invoice created successfully"))
        self.reload()
        self.invoice = invoice.name
        self.paid = 1
        
        for member in members:
            membership_doc = frappe.get_doc("Membership", {'member': member['name']})
            frappe.db.set_value("Membership", membership_doc.name, {
                'paid': 1,
                'invoice': invoice.name
            })

        return invoice

    def validate_membership_type_and_settings(self, plan, settings):
        settings_link = get_link_to_form("Non Profit Settings", "Non Profit Settings")
        
        if not settings.membership_debit_account:
            frappe.throw(_("You need to set <b>Debit Account</b> in {0}").format(settings_link))
        if not settings.company:
            frappe.throw(_("You need to set <b>Default Company</b> for invoicing in {0}").format(settings_link))
        if not plan.linked_item:
            frappe.throw(_("Please set a Linked Item for the Membership Type {0}").format(get_link_to_form("Membership Type", self.membership_type)))
