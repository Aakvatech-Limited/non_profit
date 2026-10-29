<img src="non_profit/public/images/non_profit-logo.svg" alt="Non Profit" width="64" height="64">

# Non Profit

Membership, CPD training, certification, chapters, donations and grants for non-profit and professional bodies, on Frappe / ERPNext. It started as Frappe's `non_profit` app, and Aakvatech has extended it with Sales Order based membership billing, employer billing, member training and CPD reporting, and Selcom payment integration.

**App version:** `16.0.0` · **Frappe / ERPNext / HRMS:** `>=16.0.0,<17.0.0` · **Payments:** `>=0.0.1,<1.0.0`

## Documentation

| Area | Covers |
| --- | --- |
| [Membership](docs/membership.md) | Member, Membership, Membership Type, Member Employer, the Sales Order → Invoice → Payment billing flow, expiry job, Expiring Memberships report |
| [Training and CPD](docs/training-and-cpd.md) | Training Session, member fields and hooks on hrms training doctypes, CPD Report |
| [Certification and Chapters](docs/certification-and-chapters.md) | Certification Application (paid web forms), Certified Consultant, Chapter pages |
| [Donations, Grants and Volunteers](docs/donations-and-grants.md) | Donor, Donation, Payment Entry for donors, 80G certificates, Grant Application, Volunteer |
| [Setup and Integration](docs/setup-and-integration.md) | Dependencies, install steps, patches, Non Profit Settings, Sales Order API, navigation, site-specific assumptions |

## Doctypes

All doctypes are in the **Non Profit** module.

| Doctype | Purpose |
| --- | --- |
| Member | A member, linked to an ERPNext Customer |
| Membership | One membership period, billed through a Sales Order |
| Membership Type | Plan: amount and billed Item |
| Member Employer | Employer billed for its members in one Sales Order |
| Training Session | Member training session with attendance (submittable) |
| Certification Application | Application for certification, taken through paid web forms |
| Certified Consultant | Register of certified people |
| Chapter | Local chapter with a public page and member list |
| Donor, Donor Type | Donors |
| Donation | A donation (submittable) |
| Tax Exemption 80G Certificate | Indian 80G certificate for a donation or member payments |
| Grant Application | Grant request with public page and review email |
| Volunteer, Volunteer Type | Volunteers |
| Non Profit Settings | Billing, email, donation and webhook settings (single) |

Child tables: Chapter Member, Training Session Member, Tax Exemption 80G Certificate Detail, Volunteer Skill.

Reports: **CPD Report**, **Expiring Memberships**.

## Navigation

- **Apps screen:** a **Non Profit** tile with the green NP logo. It opens the first item of the Non Profit sidebar (Member).
- **Sidebar:** Member, Membership and Membership Type at the top, then sections for Members, Training & CPD, Donations, Grants & Volunteers, Reports and Setup.

## Installation

```sh
bench get-app non_profit          # with erpnext, payments and hrms already on the bench
bench --site <site> install-app non_profit
bench build --app non_profit
```

## Development

Checks run on pull requests: pre-commit (ruff, prettier, eslint), Semgrep with the Frappe rules, pip-audit, and Conventional Commit messages. To run pre-commit locally:

```sh
pre-commit install
pre-commit run --all-files
```

## License

GNU GPL v3
