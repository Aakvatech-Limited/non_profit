import frappe
from frappe import _
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

@frappe.whitelist()
def create_and_submit_sales_invoice(sales_order, payment_reference=None):
    """
    Create and submit Sales Invoice from Sales Order.
    If payment_reference is provided, create a Payment Entry as well.
    :param sales_order: Sales Order ID (e.g. "SAL-ORD-2025-00001")
    :param payment_reference: Reference number for payment (optional)
    :return: dict with invoice and (if applicable) payment entry details
    """

    # Check if Sales Order exists and has items
    sales_order_doc = frappe.get_doc("Sales Order", sales_order)
    if not sales_order_doc or not sales_order_doc.items:
        frappe.throw(f"Sales Invoice cannot be created because Sales Order {sales_order} has no items.")

    # Check if Sales Order is submitted
    if sales_order_doc.docstatus != 1:
        frappe.throw(f"Sales Order {sales_order} must be submitted before creating a Sales Invoice.")
    
    # Generate Sales Invoice from Sales Order
    invoice = make_sales_invoice(sales_order_doc.name)

    # Automatically enable VFD auto-generation
    invoice.is_auto_generate_vfd = 1

    # Insert and submit the Sales Invoice
    invoice.insert(ignore_permissions=True)
    invoice.submit()
    
    result = {
        "invoice_name": invoice.name,
        "status": invoice.status,
        "message": f"Sales Invoice {invoice.name} created and submitted successfully."
    }

    # Create Payment Entry only if payment_reference is given
    if payment_reference:
        payment_entry = get_payment_entry("Sales Invoice", invoice.name)
        payment_entry.reference_no = payment_reference
        payment_entry.reference_date = frappe.utils.nowdate()
        payment_entry.posting_date = frappe.utils.nowdate()
        payment_entry.insert()
        payment_entry.submit()
        result["payment_entry"] = payment_entry.name
        result["message"] += f" Payment Entry {payment_entry.name} created as well."

    return result
