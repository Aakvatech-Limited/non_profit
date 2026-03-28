import frappe
from frappe import _
from time import sleep
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

@frappe.whitelist()
def create_and_submit_sales_invoice(sales_order, payment_reference=None, transaction_referance=None):
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

    try:
        # Generate Sales Invoice from Sales Order
        invoice = make_sales_invoice(sales_order_doc.name)
    
        # Insert and submit the Sales Invoice
        invoice.insert(ignore_permissions=True)
        
        # Automatically enable VFD auto-generation
        invoice.is_auto_generate_vfd = 1
        invoice.payment_reference = payment_reference
        invoice.transaction_referance = transaction_referance
    
        invoice.save(ignore_permissions=True)
        
        invoice.submit()

        # sleep invoice for 10 seconds to avoid document already modified
        sleep(2)
    
        
        result = {
            "invoice_name": invoice.name,
            "status": invoice.status,
            "message": f"Sales Invoice {invoice.name} created and submitted successfully."
        }
    
        # Create Payment Entry only if payment_reference is given
        if payment_reference:
            payment_entry = get_payment_entry("Sales Invoice", invoice.name)
            payment_entry.reference_no = transaction_referance
            payment_entry.reference_url = payment_reference
            payment_entry.reference_date = frappe.utils.nowdate()
            payment_entry.posting_date = frappe.utils.nowdate()
            payment_entry.paid_to = "Selcom Bank Account - IIAT"
            payment_entry.insert()
            payment_entry.submit()
            frappe.db.set_value("Sales Invoice", invoice.name, "payment_reference", payment_reference)
            result["payment_entry"] = payment_entry.name
            result["message"] += f" Payment Entry {payment_entry.name} created as well."
            
        return result

    except Exception as e:
        traceback = frappe.get_traceback()
        msg = f"Invoice Creation Error: {invoice.name}\n\n<br>str(e)\n\n<br>Traceback:\n<br>{traceback}"
        frappe.log_error(
            title="SO to SI Error",
            message=msg
        )
        
@frappe.whitelist()
def re_issue_sales_order(sales_order):
    """
    Cancel the given Sales Order, create an amended copy, and submit it.
    :param sales_order: Sales Order ID (e.g. "SAL-ORD-2025-00001")
    :return: dict with old and new Sales Order details
    """

    try:
        # Fetch the Sales Order
        so_doc = frappe.get_doc("Sales Order", sales_order)

        # Safely get optional fields
        url = getattr(so_doc, "payment_url", None)
        control_number = getattr(so_doc, "payment_control_number", None)

        # Ensure the Sales Order is submitted
        if so_doc.docstatus != 1:
            frappe.throw(f"Sales Order {sales_order} must be submitted before it can be cancelled and amended.")

        # Cancel the original Sales Order
        so_doc.cancel()

        # Create a new amended Sales Order
        new_so = frappe.copy_doc(so_doc)
        new_so.amended_from = so_doc.name
        new_so.docstatus = 0  # reset to draft
        new_so.insert(ignore_permissions=True)

        # Set optional fields only if available
        if url:
            new_so.payment_url = url
        if control_number:
            new_so.payment_control_number = control_number

        new_so.payment_status = "scheduled"
        new_so.save(ignore_permissions=True)

        # Submit the new Sales Order
        new_so.submit()
        frappe.db.commit()

        # Return success info
        return {
            "old_sales_order": so_doc.name,
            "new_sales_order": new_so.name,
            "status": "Success",
            "message": f"Sales Order {so_doc.name} was cancelled and amended as {new_so.name}."
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cancel & Amend Sales Order Error")
        frappe.throw(f"Failed to cancel and amend Sales Order {sales_order}: {str(e)}")
