import frappe
from frappe.utils import flt


def on_submit(doc, method=None):
	if not has_membership_references(doc):
		return

	sync_sales_invoice_item_references(doc)
	update_linked_membership_and_employer_invoices(doc)


def has_membership_references(doc):
	for item in doc.items:
		if get_membership_id_for_item(item):
			return True

	return False


def sync_sales_invoice_item_references(doc):
	for item in doc.items:
		updates = {}
		source_values = get_sales_order_reference_values(item)

		if not item.get("membership_id") and source_values.get("membership_id"):
			updates["membership_id"] = source_values.get("membership_id")

		if not item.get("member_name"):
			member_name = source_values.get("member_name")
			if not member_name and updates.get("membership_id"):
				member_name = frappe.db.get_value("Membership", updates["membership_id"], "member_name")
			elif not member_name and item.get("membership_id"):
				member_name = frappe.db.get_value("Membership", item.membership_id, "member_name")

			if member_name:
				updates["member_name"] = member_name

		if updates:
			frappe.db.set_value(item.doctype, item.name, updates, update_modified=False)
			item.update(updates)


def get_sales_order_reference_values(item):
	if not item.get("so_detail"):
		return {}

	values = frappe.db.get_value(
		"Sales Order Item",
		item.so_detail,
		["membership_id", "member_name"],
		as_dict=True,
	)
	return values or {}


def get_membership_id_for_item(item):
	membership_id = item.get("membership_id")
	if membership_id:
		return membership_id

	source_values = get_sales_order_reference_values(item)
	return source_values.get("membership_id")


def get_membership_ids_from_sales_invoice(doc):
	membership_ids = []
	for item in doc.items:
		membership_id = get_membership_id_for_item(item)
		if (
			membership_id
			and frappe.db.exists("Membership", membership_id)
			and membership_id not in membership_ids
		):
			membership_ids.append(membership_id)
	return membership_ids


def is_membership_sales_invoice(invoice_name):
	if not frappe.db.exists("Sales Invoice", invoice_name):
		return False

	invoice = frappe.get_doc("Sales Invoice", invoice_name)
	return bool(get_membership_ids_from_sales_invoice(invoice))


def update_linked_membership_and_employer_invoices(doc):
	membership_ids = get_membership_ids_from_sales_invoice(doc)
	if not membership_ids:
		return

	employers = set()

	for membership_id in membership_ids:
		membership = frappe.get_doc("Membership", membership_id)
		updates = {"invoice": doc.name}
		if not membership.sales_order and doc.items:
			sales_order_name = next((d.sales_order for d in doc.items if d.get("membership_id") == membership_id and d.sales_order), None)
			if sales_order_name:
				updates["sales_order"] = sales_order_name
		frappe.db.set_value("Membership", membership.name, updates, update_modified=False)

		member = frappe.db.get_value(
			"Member",
			membership.member,
			["invoice_to", "employer_name"],
			as_dict=True,
		)
		if member and member.get("invoice_to") == "Member Employer" and member.get("employer_name"):
			employers.add(member.get("employer_name"))

	for employer_name in employers:
		frappe.db.set_value(
			"Member Employer",
			employer_name,
			{"invoice": doc.name},
			update_modified=False,
		)


def mark_related_documents_paid_for_invoice(invoice_name):
	invoice = frappe.get_doc("Sales Invoice", invoice_name)
	if invoice.docstatus != 1:
		return
	if flt(invoice.outstanding_amount) > 0 and invoice.status != "Paid":
		return

	membership_ids = get_membership_ids_from_sales_invoice(invoice)
	if not membership_ids:
		return

	employers = set()
	for membership_id in membership_ids:
		membership = frappe.get_doc("Membership", membership_id)
		frappe.db.set_value(
			"Membership",
			membership.name,
			{
				"paid": 1,
				"membership_status": "Current",
				"invoice": invoice.name,
			},
			update_modified=False,
		)

		member = frappe.db.get_value(
			"Member",
			membership.member,
			["invoice_to", "employer_name"],
			as_dict=True,
		)
		if member and member.get("invoice_to") == "Member Employer" and member.get("employer_name"):
			employers.add(member.get("employer_name"))

	for employer_name in employers:
		frappe.db.set_value(
			"Member Employer",
			employer_name,
			{
				"paid": 1,
				"invoice": invoice.name,
			},
			update_modified=False,
		)
