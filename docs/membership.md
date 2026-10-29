# Membership

**Module:** Non Profit · **Sidebar:** Non Profit → *Member*, *Membership*, *Membership Type* (top), *Members → Member Employer*, *Reports → Expiring Memberships*

Members, their yearly or monthly memberships, and how memberships are billed through ERPNext Sales Orders and Sales Invoices, either to the member or to their employer.

## Doctypes

| Doctype | Naming | Purpose |
| --- | --- | --- |
| Member | `NPO-MEM-.YYYY.-` series | A person who holds memberships. Linked to an ERPNext Customer. |
| Membership | `NPO-MSH-.YYYY.-.#####` | One membership period for a member: type, dates, amount, payment and billing links. |
| Membership Type | the type name | A membership plan: amount, the service Item billed for it, and an optional Razorpay plan ID. |
| Member Employer | the employer name | An organisation that pays for its employees' memberships in one Sales Order. |

None of these are submittable. Permissions: **Non Profit Manager** and **Non Profit Member** can read and write Member and Membership; Membership Type is Non Profit Manager only; Member Employer is System Manager only.

### Member

| Field | Type | Notes |
| --- | --- | --- |
| member_name | Data, required | |
| membership_type | Link → Membership Type, required | |
| email_id | Data | Validated as an email address on save. |
| customer | Link → Customer | Set by **Create Customer** (see below). |
| membership_expiry_date | Date | |
| invoice_to | Select: Member / Member Employer | Who is billed. |
| employer_name | Link → Member Employer | Custom field added by a patch. |
| custom_auto_subscription | Check | Custom field added by a patch. Used only by the disabled auto-renewal job. |
| subscription_id, customer_id, subscription_start/end, subscription_status | | Razorpay subscription details. |

Form buttons, once saved: **Accounting Ledger** and **Accounts Receivable** (open the reports for the linked customer), and **Create Customer** when no customer is linked. Create Customer makes an *Individual* Customer in the default customer group and territory from Selling Settings, plus a Contact linked to both the Customer and the Member.

### Membership

| Field | Type | Notes |
| --- | --- | --- |
| member | Link → Member | Required for desk users (see below). |
| membership_type | Link → Membership Type, required | The amount is fetched from the type. |
| membership_status | Select: New / Current / Expired / Pending / Cancelled | |
| from_date, to_date | Date, required | `to_date` is recalculated on every save. |
| paid | Check | |
| amount, currency | | |
| sales_order, invoice | Link | Set by the billing flow below. |
| company | Link → Company, required | |

**Validation on save:**

- If there is no member, a website user gets a Member created from their User record; a desk user gets "Please select a Member".
- If the member already has a paid membership, a new one can only be created within 30 days of the last one's `to_date`, and its `from_date` is moved to the day after that `to_date`. Administrator is exempt.
- `to_date` is set to `from_date` + 1 year when **Non Profit Settings → Billing Cycle** is *Yearly*, otherwise + 1 month.

**Buttons:** **Generate Sales Order** (when there is no Sales Order yet) and **Send Acknowledgement** (when *Send Email* is on in settings). The list view has a **Bulk Sales Orders** menu item for the selected rows.

### Membership Type

`amount` (required), `linked_item` (the Item billed; must not be a stock item) and `razorpay_plan_id`.

### Member Employer

On every save, if no Customer has the employer's name, a *Company* Customer is created in customer group **IIA Members** and territory **All Territories**. That customer group must exist on the site, or saving fails.

**Bulk Membership Sales Order** builds one Sales Order to the employer's Customer. It has one line per member whose `employer_name` is this employer and whose `invoice_to` is *Member Employer*, using each member's latest membership with status *New*. It stops if any of those memberships already has a Sales Order or invoice.

## Billing flow

```
Membership (New) ──Generate Sales Order──▶ Sales Order (submitted)
                                              │  items carry membership_id / member_name
                                              ▼
                                    Sales Invoice (submitted) ──▶ Membership.invoice set
                                              │                   Member Employer.invoice set
                                              ▼
                                    Payment Entry (submitted) ──▶ Membership: paid = 1, status Current
                                                                  Member Employer: paid = 1
```

1. **Generate Sales Order** checks that the member has a Customer, that Non Profit Settings has a company, and that the Membership Type has a linked Item. It then creates and submits a Sales Order: one line for the linked Item at the membership amount, delivery date = membership `to_date`.
2. Each Sales Order Item and Sales Invoice Item carries `membership_id` and `member_name` custom fields (added by patches).
3. **Sales Invoice on_submit** (hook): copies `membership_id` / `member_name` from the Sales Order rows onto the invoice rows if missing. It then writes the invoice onto each referenced Membership, and onto the Member Employer when the member is billed to an employer.
4. **Payment Entry on_submit** (hook): for every referenced Sales Invoice that has membership rows and is now fully paid, it marks the Memberships *paid* and *Current*, and the Member Employer *paid*.

`generate_invoice` and `generate_bulk_invoice` are kept as aliases of the Sales Order functions.

## Scheduled job

**Daily:** `set_expired_status` sets every non-cancelled Membership whose `to_date` is before today to *Expired*.

`auto_renewal_membership` is in the code but its call is commented out. If enabled, it would create a *Current* membership for members with **Auto Subscription** ticked and an expired membership, using **Non Profit Settings → Start Date / End Date** as the period.

## Expiring Memberships report

Script report on Membership, for Non Profit Manager and Non Profit Member.

| Filter | Notes |
| --- | --- |
| Fiscal Year (required) | Compared with the *calendar year* of the expiry date, so it only matches fiscal years named like `2026`. |
| Month | Jan–Dec. |

For each member, the report takes the latest `to_date` among their **paid** memberships and lists those that fall in the chosen month and year. Columns: Membership Type, Membership ID, Member ID, Member Name, Email, Expiring On. The Membership Type and ID shown come from an arbitrary paid membership of that member, not necessarily the latest one. This is a long-standing quirk of the query, kept as is.

## Acknowledgement email

**Send Acknowledgement** emails the member using the **Email Template** set in Non Profit Settings, rendered with `doc` (the Membership) and `member`. It attaches the Membership printed in *Membership Print Format*, and the Sales Invoice in *Invoice Print Format* when *Send Invoice* is on. It needs *Send Email* enabled and an email on the Member.

## Razorpay (optional)

With **Enable Razorpay for Memberships** on, `trigger_razorpay_subscription` (guest webhook) creates or updates Members and Memberships from Razorpay subscription events, and `update_halted_razorpay_subscription` marks halted subscriptions. The webhook signature is checked against the secret generated in Non Profit Settings. `get_or_create_member` and `register_member` filter Member on `email`, which is not a Member field (it is `email_id`), so those two paths currently fail. Aakvatech sites bill through Sales Orders instead.
