# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.query_builder import Field
from frappe.query_builder.functions import Max, Month, Year


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	return [
		_("Membership Type") + ":Link/Membership Type:100",
		_("Membership ID") + ":Link/Membership:140",
		_("Member ID") + ":Link/Member:140",
		_("Member Name") + ":Data:140",
		_("Email") + ":Data:140",
		_("Expiring On") + ":Date:120",
	]


def get_data(filters):
	filters["month"] = [
		"Jan",
		"Feb",
		"Mar",
		"Apr",
		"May",
		"Jun",
		"Jul",
		"Aug",
		"Sep",
		"Oct",
		"Nov",
		"Dec",
	].index(filters.month) + 1

	member = frappe.qb.DocType("Member")
	membership = frappe.qb.DocType("Membership")

	# Latest paid membership per member. The non-aggregated name and membership_type come from
	# an arbitrary row of the group, as in the original query.
	latest = (
		frappe.qb.from_(membership)
		.select(
			membership.name,
			membership.membership_type,
			Max(membership.to_date).as_("max_membership_date"),
			membership.member,
		)
		.where(membership.paid == 1)
		.groupby(membership.member)
		.orderby(Field("max_membership_date"))
	).as_("ms")

	return (
		frappe.qb.from_(member)
		.inner_join(latest)
		.on(member.name == latest.member)
		.select(
			latest.membership_type,
			latest.name,
			member.name,
			member.member_name,
			member.email,
			latest.max_membership_date,
		)
		.where(
			(Month(latest.max_membership_date) == filters.get("month"))
			& (Year(latest.max_membership_date) == filters.get("fiscal_year"))
		)
	).run()
