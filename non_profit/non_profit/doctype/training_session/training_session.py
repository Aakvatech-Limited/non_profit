# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds


class TrainingSession(Document):
	def validate(self):
		self.validate_period()

	def on_update_after_submit(self):
		self.set_status_for_attendees()

	def validate_period(self):
		if time_diff_in_seconds(self.end_time, self.start_time) <= 0:
			frappe.throw(_("End time cannot be before start time"))

	def set_status_for_attendees(self):
		if self.event_status == "Completed":
			for member in self.members:
				if member.attendance == "Present" and member.status != "Feedback Submitted":
					member.status = "Completed"

		elif self.event_status == "Scheduled":
			for member in self.members:
				member.status = "Open"

		self.db_update_all()