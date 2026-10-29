import frappe
from erpnext.accounts.doctype.journal_entry.journal_entry import get_default_bank_cash_account
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import get_account_currency
from frappe.utils.data import flt, getdate


class NonProfitPaymentEntry(PaymentEntry):
	"""Lets a Donor pay against a Donation.

	Mixed in through `extend_doctype_class`, so erpnext's own reference validation and the
	Payment Entry override from hrms keep working for every other party type.
	"""

	def get_valid_reference_doctypes(self):
		if self.party_type == "Donor":
			return ("Donation",)
		return super().get_valid_reference_doctypes()

	def set_missing_ref_details(
		self,
		force: bool = False,
		update_ref_details_only_for: list | None = None,
		reference_exchange_details: dict | None = None,
	) -> None:
		other_refs = []
		for d in self.get("references"):
			if not d.allocated_amount:
				continue
			ref = (d.reference_doctype, d.reference_name)
			if update_ref_details_only_for and ref not in update_ref_details_only_for:
				continue
			if d.reference_doctype != "Donation":
				other_refs.append(ref)
				continue
			if d.exchange_gain_loss:
				continue

			for field, value in get_donation_reference_details(d.reference_name).items():
				if field == "exchange_rate" or not d.get(field) or force:
					if self.get("_action") in ("submit", "cancel"):
						d.db_set(field, value)
					else:
						d.set(field, value)

		if other_refs:
			super().set_missing_ref_details(
				force=force,
				update_ref_details_only_for=other_refs,
				reference_exchange_details=reference_exchange_details,
			)


@frappe.whitelist()
def get_donation_payment_entry(dt, dn, party_amount=None, bank_account=None, bank_amount=None):
	reference_doc = None
	doc = frappe.get_doc(dt, dn)

	party_account = get_party_account("Donor", doc.get("donor"), doc.company)
	party_account_currency = doc.get("party_account_currency") or get_account_currency(party_account)
	grand_total, outstanding_amount = set_grand_total_and_outstanding_amount(party_amount, doc)

	# bank or cash
	bank = get_bank_cash_account(doc, bank_account)

	paid_amount, received_amount = set_paid_amount_and_received_amount(
		party_account_currency, bank, outstanding_amount, bank_amount, doc
	)

	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Receive"
	pe.company = doc.company
	pe.cost_center = doc.get("cost_center")
	pe.posting_date = getdate()
	pe.mode_of_payment = doc.get("mode_of_payment")
	pe.party_type = "Donor"
	pe.party = doc.get("donor")
	pe.contact_person = doc.get("contact_person")
	pe.contact_email = doc.get("contact_email")

	pe.paid_from = party_account
	pe.paid_to = bank.account
	pe.paid_from_account_currency = party_account_currency
	pe.paid_to_account_currency = bank.account_currency
	pe.paid_amount = paid_amount
	pe.received_amount = received_amount
	pe.letter_head = doc.get("letter_head")

	pe.append(
		"references",
		{
			"reference_doctype": dt,
			"reference_name": dn,
			"bill_no": doc.get("bill_no"),
			"due_date": doc.get("due_date"),
			"total_amount": grand_total,
			"outstanding_amount": outstanding_amount,
			"allocated_amount": outstanding_amount,
		},
	)

	pe.setup_party_account_field()
	pe.set_missing_values()

	if party_account and bank:
		pe.set_exchange_rate(ref_doc=reference_doc)
		pe.set_amounts()

	return pe


def set_grand_total_and_outstanding_amount(party_amount, doc):
	grand_total = outstanding_amount = 0
	if party_amount:
		grand_total = outstanding_amount = party_amount
	else:
		grand_total = doc.amount
		outstanding_amount = doc.amount

	return grand_total, outstanding_amount


def get_bank_cash_account(doc, bank_account):
	bank = get_default_bank_cash_account(
		doc.company, "Bank", mode_of_payment=doc.get("mode_of_payment"), account=bank_account
	)

	if not bank:
		bank = get_default_bank_cash_account(
			doc.company, "Cash", mode_of_payment=doc.get("mode_of_payment"), account=bank_account
		)

	return bank


def set_paid_amount_and_received_amount(party_account_currency, bank, outstanding_amount, bank_amount, doc):
	paid_amount = received_amount = 0
	if party_account_currency == bank.account_currency:
		paid_amount = received_amount = abs(outstanding_amount)
	else:
		paid_amount = abs(outstanding_amount)
		if bank_amount:
			received_amount = bank_amount
		else:
			received_amount = paid_amount * doc.get("conversion_rate", 1)

	return paid_amount, received_amount


def get_donation_reference_details(donation):
	amount = flt(frappe.db.get_value("Donation", donation, "amount"))
	return frappe._dict(
		{
			"due_date": None,
			"total_amount": amount,
			"outstanding_amount": amount,
			"exchange_rate": 1,
			"bill_no": None,
		}
	)
