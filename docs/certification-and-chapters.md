# Certification and Chapters

**Module:** Non Profit · **Sidebar:** Non Profit → *Members → Chapter, Certification Application, Certified Consultant*

Certification applications taken through paid web forms, the register of certified consultants, and member chapters with public join and leave pages.

## Doctypes

| Doctype | Naming | Permissions | Purpose |
| --- | --- | --- | --- |
| Certification Application | `NPO-CAPP-.YYYY.-.#####` | System Manager | An application for certification, with its fee. |
| Certified Consultant | `NPO-CONS-.YYYY.-.#####` | Non Profit Manager, System Manager | A certified person, with optional public profile. |
| Chapter | entered on creation | Non Profit Manager | A local chapter with a public web page and a member list. |
| Chapter Member | child of Chapter | | user, introduction, website_url, enabled, leave_reason |

Certification Application and Certified Consultant have no server logic beyond the standard save.

### Certification Application

| Field | Type |
| --- | --- |
| name_of_applicant | Data, required |
| email | Link → User, required |
| certification_status | Select: Yet to appear / Certified / Not Certified |
| paid | Check |
| currency | Select: USD / INR |
| amount | Float |

### Certified Consultant

name_of_consultant, country, email, phone, website_url, address, image, `certification_application` (required link), from_date / to_date, introduction, details, discuss_id, github_id, show_in_website.

## Web forms

| Web form | Route | Doctype | Login | Payment |
| --- | --- | --- | --- | --- |
| certification-application | `/certification-application` | Certification Application | required | Razorpay, amount from the `amount` field |
| certification-application-usd | `/certification-application-usd` | Certification Application | required | PayPal, USD, amount from the `amount` field |
| grant-application | `/my-grant` | Grant Application | required | none (see [Donations and Grants](donations-and-grants.md)) |

The two certification forms prefill the applicant's name and email from the logged-in user, and set the currency and amount: INR 20,000 on the first form, USD 300 on the second. Both are hidden when an existing application is opened.

The portal menu has a **Certification** entry (`/certification`) for the role **Non Profit Portal User**. The app doesn't create that role, so the entry shows only on sites where it was added by hand.

## Chapters

A Chapter is a website page when **Published** is ticked. Its route defaults to `chapters/<name>`, and `/chapters` lists all published chapters.

| Field | Notes |
| --- | --- |
| chapter_head | Link → Member, required |
| region | required |
| introduction | required |
| meetup_embed_html | HTML shown on the chapter page |
| members | Chapter Member rows |

**Join / leave pages** (logged-in website users):

- `/non_profit/join-chapter?name=<chapter>`: shows a form. Posting it adds the user to the chapter's members, with their introduction and website. A user who is already an enabled member is told so.
- `/non_profit/leave-chapter?name=<chapter>`: asks for a reason, then disables the user's own Chapter Member row. The server always uses the logged-in user, whatever user the page sends.
