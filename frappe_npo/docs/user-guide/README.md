# Frappe NPO — User Guide

This guide is written for the people who actually run the organisation: membership
co-ordinators, fund-raisers, social workers, field staff, shelter managers,
volunteer co-ordinators and the administrator who sets things up. It explains
**what each feature is for and how to use it**, not how the code works — and it
deliberately does not walk through fields screen by screen. Every screen explains
itself as you use it; this guide explains the workflow.

Two modules ship together in this app and they are meant to be used together:

| Module | What it is for | Menu name |
| --- | --- | --- |
| **Non Profit** | The "back office" of a non-profit: members, donations, donors, volunteers, chapters, grants, certifications, 80G receipts. Combines the classic ERPNext Non Profit app with the Navari customisations. | **Frappe NPO** |
| **Beneficiaries** | The "front line": the people you serve, the cases/needs you handle, rescue and field work, services delivered (food, shelter, medical, entitlements), money and goods disbursed to them, partners and impact measurement. Based on Frappe Changemakers. | **Beneficiaries** |

Both modules share one set of masters (Company, Cost Center, Project, Item,
Customer, Supplier, Territory, Branch), so a donation, a member, a beneficiary and
a disbursement all post into the same books.

## How to find your way around the app

1. Log in and open the **Apps** screen (the grid icon at the top of the desk).
2. Click the **Frappe NPO** tile. The left sidebar shows every area of the back office.
3. Click the **Beneficiaries** tile (or switch sidebar at the top of the left panel)
   for the field-work side.

Navigation inside each sidebar is grouped into collapsible sections.
The **Frappe NPO** sidebar has: Membership, Donations, Grants, Volunteer,
Certifications and Donation Reports (with Settings at the end). The **Beneficiaries**
sidebar has: Beneficiaries, Disbursement, Health & Medical, Impact & Metrics and
Reports.

Those sidebars are a curated subset — they cover the screens you use every day and
leave the long tail (shelter homes, care centres, camps, entitlement requests, …)
reachable from the search bar at the top of the desk (the *Awesome Bar*): start typing
a screen name such as "Shelter Home" and pick it from the list. Chapter 13 includes a
"where to find it" table for every screen.

## Chapters in this guide

**Back office — Non Profit**

1. [Setting up](01-setup-and-master-data.md) — which features to switch on, the shared masters, roles, and a first-week checklist
2. [Membership](02-membership.md) — membership types, renewal rules, invoicing, online joining, expiry and renewals
3. [Donations](03-donations.md) — pledges vs money received, allocation, funding pools, 80G receipts, the five reports
4. [Grants](04-grants.md) — grant applications and the review cycle
5. [Volunteers](05-volunteers.md) — the volunteer register, availability, skills, stipends
6. [Chapters and public pages](06-chapters-and-portal.md) — chapters, the certification directory, published pages

**Front line — Beneficiaries**

7. [Beneficiaries](07-beneficiaries.md) — the person record, the lifecycle, bulk intake, duplicates and donor tagging
8. [Cases](08-cases.md) — needs, assignment, follow-ups, outcomes, closing
9. [Field operations](09-field-operations.md) — rescues, camps, daily visits and the mobile app
10. [Services](10-services.md) — food, entitlements, shelter, care, medical, reintegration, learning centres
11. [Disbursements and verification](11-disbursements.md) — paying people in batches, cash/goods/services, agent verification
12. [Partners, projects and impact](12-partners-projects-impact.md) — partners, controlled intake, budgets, impact reporting
13. [Reports and dashboards](13-reports-and-dashboards.md) — every report, the charts, a monthly routine

## The one-minute mental model

```
Donor ──gives──> Donation ──allocated by──> Donation Allocation
                                                │
                                    ┌───────────┴────────────┐
                              Funding Pool / Budget      Disbursement Order
                              (which programme)          (cash / goods / services)
                                                                │
                                                        Beneficiaries
                                                                │
                                                             Cases
                                                (the needs those people have)
```

Around that spine sit the people-facing records: **Member / Membership** (your
supporters' club), **Volunteer** and **Chapter** (people who give time),
**Certification** (accreditation you hand out), **Partner / Organisation**
(agencies you work with), and **Impact Measurement** (what you report upwards).

## A note on what "Frappe" gives you for free

You do not need to build any of the following — they are part of every screen:

- **List view** with filters, sorting, saved filters, bulk edit, export to Excel/CSV.
- **Search bar (Awesome Bar)** — type a name or a document number from anywhere.
- **Attachments**, **comments**, **tags**, **assignments**, **sharing**, **email links** on every record.
- **Print / PDF** of any record, using the print format chosen in settings.
- **Reports** can be opened, filtered and exported to Excel; charts can be drilled into.

## Something not covered here?

If a screen behaves differently from this guide, check the app's version first
(footer of the desk or **About** in the Help menu). This guide describes the
`frappe_npo` app on Frappe/ERPNext **version 16**.
