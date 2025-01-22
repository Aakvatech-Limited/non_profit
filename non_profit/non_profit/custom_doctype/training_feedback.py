# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document



def validate(self, method):
    training_event = frappe.get_doc("Training Event", self.training_event)
    if training_event.docstatus != 1:
        frappe.throw(_("{0} must be submitted").format(_("Training Event")))

    member_event_details = frappe.db.get_value(
        "Training Event Employee",
        {"parent": self.training_event, "member": self.member},
        ["name", "attendance"],
        as_dict=True,
    )

    if not member_event_details:
        frappe.throw(
            _("Member {0} not found in Training Event Participants.").format(
                frappe.bold(self.member_name)
            )
        )

    if member_event_details.attendance == "Absent":
        frappe.throw(_("Feedback cannot be recorded for an absent Member."))

def on_submit(self, method):
    member = frappe.db.get_value(
        "Training Event Employee", {"parent": self.training_event, "member": self.member}
    )

    if member:
        frappe.db.set_value("Training Event Employee", member, "status", "Feedback Submitted")

def on_cancel(self):
    member = frappe.db.get_value(
        "Training Event Employee", {"parent": self.training_event, "member": self.member}
    )

    if member:
        frappe.db.set_value("Training Event Employee", member, "status", "Completed")
