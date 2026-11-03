# 1. Setting up

Frappe NPO is configured rather than customised: one **Frappe NPO Settings** screen
decides which capabilities your organisation gets. A one-person charity and a
multi-state trust run the same app — they just switch different things on.

## 1.1 Choose the features you want

**Memberships**

- Run a paid membership scheme end to end: membership types, fee invoices and
  renewals.
- Choose the print format used for membership invoices and membership cards, so every
  branch prints the same thing.
- Email a thank-you once a membership is paid, using the template you pick.
- Let people join and pay online: when the payment confirms, the membership is created,
  marked paid and invoiced without anyone touching it.
- Bill on a cycle (monthly, quarterly, yearly) instead of raising each invoice by hand,
  including for memberships that arrive from a website form.

**Donations**

- Decide whether donations carry an instalment table. On, you can track pledges and
  part-payments; off, a donation is simply money received.
- Let the app create the accounting entry for each donation payment, or keep it manual
  so a finance person checks every one.
- Create a customer automatically for every donor, so donors can also be invoiced or
  given a receipt against an open item.
- Fix the account that membership fees and donation money land in, so the books stay
  right whichever route the money came through.
- Accept online donations and membership payments through a secure webhook.
- Issue 80G tax-exemption certificates (see [chapter 3](03-donations.md)).

**Beneficiaries and programmes**

- Turn the **beneficiary lifecycle** on or off. On, the app guides staff through the
  right steps and blocks shortcuts; off, statuses are whatever staff type.
- Allow or forbid staff changing a beneficiary's status by hand, and choose the status
  a new beneficiary starts in.
- Show programme details on beneficiary records only if you run funded programmes.
- Keep the supplier list in step automatically — a supplier per beneficiary (so money
  can be paid to them) and per learning centre (so fees can be collected).
- Create a student record automatically when a beneficiary enrols in a learning centre.
- Turn on food distribution, which adds a **Distribute Food** action to projects.

**Money going out**

- Map each disbursement route to the accounts it posts to, so cash, goods and services
  hit the right ledgers.
- Let the app create the payment entries for a submitted disbursement order, or keep it
  manual for four-eyes checking.
- Give every field agent their own project (from a project template) so you can see cost
  per agent.
- Set the status that auto-created orders, invoices and payment entries start in, so
  nothing reaches the ledger before you want it to.

**Reporting and analysis**

- Switch on the **Beneficiary** and **Territory** accounting dimensions for cost per
  beneficiary and area-wise reporting. Do this _before_ you post anything — dimensions
  cannot be added to entries made earlier.

> The **Enable Progressive Disbursement** switch exists but is not connected to
> anything yet. Leave it alone; disbursement behaviour is controlled by the settings
> above.

## 1.2 Set up the shared masters first

Everything in both modules posts into the same books, so the plumbing comes first.
Work down this list and you will not be stuck mid-task:

1. **Company, chart of accounts, fiscal year** — the money side.
2. **Cost centres** — one per programme or department; this is how you report spend.
3. **Territories** — state → district → zone → ward → habitation. Beneficiaries, cases,
   rescues and camps all use them, so load the areas you actually work in.
4. **Items and warehouses** — the goods you hand out (food kits, blankets, hygiene kits)
   and where they are stored.
5. **Projects** — one per programme, campaign or intake round; donations and
   disbursements are tagged to them.
6. **Branches / offices** — who owns which case, member and volunteer.
7. Then the people-side masters: donor types, membership types, volunteer types,
   beneficiary types, case types, funding pools, organisations and partners.
