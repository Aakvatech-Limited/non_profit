# Setup and Integration

**Module:** Non Profit · **Sidebar:** Non Profit → *Setup → Non Profit Settings*

How the app is installed and configured, what it adds to other apps, and the parts that depend on per-site configuration.

## Dependencies

| App | Version | Why |
| --- | --- | --- |
| frappe | `>=16.0.0,<17.0.0` | |
| erpnext | `>=16.0.0,<17.0.0` | Customers, Sales Orders/Invoices, Payment Entry, Company, Fiscal Year. |
| payments | `>=0.0.1,<1.0.0` | Razorpay / PayPal gateway controllers for web forms and subscriptions. |
| hrms | `>=16.0.0,<17.0.0` | Training Program / Event / Result / Feedback used for CPD. The custom-field patches need these doctypes. |

All four are in `required_apps` (hooks.py) and in `pyproject.toml`. A test in `test_non_profit_settings.py` checks that the two lists agree.

## On install

`after_install` (`non_profit.setup.setup_non_profit`):

- creates Party Types **Member** and **Donor** (Receivable);
- adds custom fields: on **Company** an 80G section (80G Number, 80G With Effect From, PAN Number), and **PAN Details** on Member and Donor;
- adds **Non Profit** to Domain Settings → Active Domains. Most doctypes are restricted to the *Non Profit* domain, so this keeps them visible.

## Patches

| Patch | Adds |
| --- | --- |
| rename_non_profit_fields | Renames `razorpay_payment_id` to `payment_id` on Donation and the 80G certificate tables. |
| create_auto_renewal_automation_custom_field | Member → **Auto Subscription** (`custom_auto_subscription`). |
| create_employer_name_field | Member → **Employer Name** (Link → Member Employer). |
| create_cdp_hour_custom_fields | **CPD Hour** on Training Program and Training Event. |
| create_start_and_end_date_in_non_profit_settings | Non Profit Settings → **Start Date**, **End Date**. |
| create_membership_field_sales_invoice | Sales Invoice Item → **Membership ID**, **Member Name**. |
| create_membership_reference_sales_order | The same two fields on Sales Order Item (and Sales Invoice Item). |
| create_member_field | **Member**, **Member Name** on Training Event Employee, Training Result Employee, Training Feedback. |
| property_setter_for_employee | Makes Training Feedback → Employee optional. |

## Non Profit Settings

| Section | Fields |
| --- | --- |
| Membership billing | Company (required), Billing Cycle (Monthly / Yearly), Billing Frequency, Allow Invoicing, Automate Membership Invoicing, Automate Membership Payment Entries, Membership Payment Account, Membership Debit Account |
| Membership period | Start Date, End Date. On save, End Date = Start Date + 1 year (Yearly) or + 1 month (Monthly). |
| Emails | Send Email, Send Invoice, Email Template, Membership Print Format, Invoice Print Format |
| Donations | Donation Company (required), Default Donor Type (required), Automate Donation Payment Entries, Donation Payment Account, Donation Debit Account |
| Razorpay | Enable Razorpay for Memberships, membership and donation webhook secrets (**Generate Secret** / **Revoke** buttons; a secret is shown once) |
| Webhooks | Creation User (required): the user that webhook-created records are saved as |

## Sales Order API (`non_profit/api/sales_order_api.py`)

Two whitelisted endpoints used by an external payment integration. They are not called from the app's own pages.

| Method | HTTP | What it does |
| --- | --- | --- |
| `non_profit.api.sales_order_api.create_and_submit_sales_invoice` | GET or POST | Makes and submits a Sales Invoice from a submitted Sales Order. If `payment_reference` is given, it also creates and submits a Payment Entry. Errors are logged as "SO to SI Error" and the call returns nothing. |
| `non_profit.api.sales_order_api.re_issue_sales_order` | **POST only** | Cancels a Sales Order, submits an amended copy (status *scheduled*), and returns the old and new names. |

These rely on values that exist only on the Aakvatech site:

- Mode of Payment **Selcom Bank Account** and account **Selcom Bank Account - IIAT**;
- Sales Invoice fields `is_auto_generate_vfd`, `payment_reference`, `transaction_reference` (VFD fields come from csf_tz);
- Sales Order fields `payment_url`, `payment_control_number`, `payment_status`.

## Navigation (v16)

| What | Where |
| --- | --- |
| Apps-screen tile | `add_to_apps_screen` in hooks.py, logo `public/images/non_profit-logo.svg`. It has no route, so it opens the first sidebar item (Member). |
| Sidebar | `non_profit/sidebar/non_profit/non_profit.json` |
| Dock | `dock/non_profit/non_profit.json` |
| Desktop icon | `desktop_icon/non_profit.json`, links to `/desk/non-profit/member` |

A site gets the Sidebar and Dock records on `bench --site <site> migrate` (or install). The logo needs `bench build --app non_profit`.

## Known site-specific or incomplete pieces

- `doctype_js` loads `public/js/payment_entry.js` into the Sales Invoice form, but the file isn't in the app. Frappe skips it silently.
- The **Non Profit Portal User** role, used by the portal Certification menu item, isn't created by the app.
- Member Employer needs the customer group **IIA Members** to exist.
- The workspace JSON (`non_profit/workspace/non_profit/non_profit.json`) still has a *Loan Management* card for the lending app. The v16 sidebar doesn't include it.
