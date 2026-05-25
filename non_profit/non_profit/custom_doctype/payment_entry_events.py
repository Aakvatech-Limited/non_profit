from non_profit.non_profit.custom_doctype.sales_invoice import (
	is_membership_sales_invoice,
	mark_related_documents_paid_for_invoice,
)


def on_submit(doc, method=None):
	invoice_names = {
		reference.reference_name
		for reference in doc.references
		if reference.reference_doctype == "Sales Invoice" and reference.reference_name
	}

	for invoice_name in invoice_names:
		if not is_membership_sales_invoice(invoice_name):
			continue

		mark_related_documents_paid_for_invoice(invoice_name)
