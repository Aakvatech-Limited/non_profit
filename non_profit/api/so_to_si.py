import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

@frappe.whitelist()
def create_and_submit_sales_invoice(sales_order):
    """
    Create and submit Sales Invoice from Sales Order
    :param sales_order: Sales Order ID (e.g. "SAL-ORD-2025-00001")
    :return: frappe.response['message'] with invoice details
    """

    # Check if Sales Order exists and has items
    sales_order = frappe.get_doc("Sales Order", sales_order)
    if not sales_order or not sales_order.items:
        frappe.throw(f"Sales Invoice cannot be created because Sales Order {sales_order} has no items.")

    # Check if Sales Order is submitted
    if so_doc.docstatus != 1:
        frappe.throw(f"Sales Order {sales_order} must be submitted before creating a Sales Invoice.")
    
    # Generate Sales Invoice from Sales Order
    invoice = make_sales_invoice(sales_order.name)

    # Insert and submit the Sales Invoice
    invoice.insert(ignore_permissions=True)
    invoice.submit()

    # Commit transaction
    

    return {
        "invoice_name": invoice.name,
        "status": invoice.status,
        "message": f"Sales Invoice {invoice.name} created and submitted successfully."
    }
