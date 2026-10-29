# Donations, Grants and Volunteers

**Module:** Non Profit · **Sidebar:** Non Profit → *Donations*, *Grants & Volunteers*

## Doctypes

| Doctype | Naming | Submittable | Permissions | Purpose |
| --- | --- | --- | --- | --- |
| Donor | by email | no | Non Profit Manager | A person or organisation that donates. |
| Donor Type | by type name | no | Non Profit Manager | Grouping for donors. |
| Donation | `NPO-DTN-.YYYY.-` series | **yes** | Non Profit Manager, System Manager | One donation. |
| Tax Exemption 80G Certificate | `NPO-80G-.YYYY.-` series | no | System Manager | Indian 80G tax-exemption certificate for a donation or a member's payments. |
| Grant Application | | no | Non Profit Manager | An application for a grant, with a public page. |
| Volunteer | by email | no | Non Profit Manager | A volunteer, with skills and availability. |
| Volunteer Type | entered on creation | no | Non Profit Manager | Volunteer category with an amount. |

The app creates **Donor** and **Member** as ERPNext *Party Types* (Receivable) on install, so payments can be booked against them.

## Donations

Donation fields: donor (required), donor_name, email, date (required), amount (required), mode_of_payment, paid, company (required), payment_id.

- **Create Payment Entry** (button on a submitted, unpaid Donation) opens a new Payment Entry: party type *Donor*, the donation amount, the default bank (or cash) account for the mode of payment.
- **Payment Entry for donors.** non_profit extends the ERPNext Payment Entry controller (through `extend_doctype_class`, so hrms's own Payment Entry override still applies). For party type *Donor*, the only valid reference is *Donation*, and a Donation row's total and outstanding are the donation amount at exchange rate 1. All other party types keep erpnext/hrms behaviour.
- **Automatic payment entries.** When a Donation is marked paid by a payment gateway, and **Automate Donation Payment Entries** is on in settings, a Payment Entry is created and submitted from *Donation Debit Account* to *Donation Payment Account*.
- **Razorpay webhook** (`capture_razorpay_donations`, guest): on `payment.captured` it verifies the signature with the donation webhook secret, finds or creates the Donor by email, creates and submits a Donation (amount converted from paise), then creates its Payment Entry when *Automate Donation Payment Entries* is on. Subscription payments are skipped. Failures are written to the Error Log and emailed to System Managers.

## 80G certificates

For Indian tax exemption. The company must have **80G Number** and **PAN Number** set (custom fields added to Company on install, under *Non Profit Settings*).

| Recipient | How it works |
| --- | --- |
| Donor | Pick the Donation. Only one certificate per donation is allowed. |
| Member | Pick the member and fiscal year, then **Get Payments** to list that year's non-cancelled memberships with their amount, invoice and payment ID. The total is summed. |

Print formats: **80G Certificate for Donation** and **80G Certificate for Membership**.

## Grant Applications

Fields: applicant_type (Individual / Organization), applicant_name, email, contact_person, grant_description, amount, has_any_past_grant_record, status (Open / Received / In Progress / Approved / Rejected / Expired / Withdrawn), assessment_manager, assessment_mark, note.

- Applicants apply through the **`/my-grant`** web form (login required). Published applications have a public page at `grant-application/<name>`, and `/grant-application` lists them.
- When the status is *Received*, **Send Grant Review Email** emails the assessment manager a link to the application, sets the status to *In Progress* and records that the email was sent.

## Volunteers

Volunteer fields: volunteer_name, volunteer_type, email, availability (Weekly / Weekdays / Weekends), availability_timeslot (Morning / Afternoon / Evening / Anytime), volunteer_skills (table), note. Donor and Volunteer forms show linked addresses and contacts.
