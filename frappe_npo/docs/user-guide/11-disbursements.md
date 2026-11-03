# 11. Disbursements and verification

Disbursement is how money and goods leave the organisation and reach people. Doing it one
payment at a time does not scale past a few dozen people, so this module does it in
batches — and then proves the money arrived.

## 11.1 What it does

- Collects a **batch of beneficiaries** in one order: either pick them by hand or pull
  them in by filter (programme, status, area, recruitment phase).
- Records what each person gets, and the total, before anything is paid.
- On submission, creates the accounting behind the batch **in one go**: payment entries
  for cash, stock entries for goods, invoices for services.
- Sends each payment through the right route per location — cash payments are grouped by
  state and paid from that state's agent account, so one bank transfer covers a whole
  district.
- Can give every field agent their own project, so you can see cost per agent.
- Hands the batch to **verification**: an agent confirms each person's account details and
  uploads proof, and the record of that check stays attached.
- Refuses to pay twice: a beneficiary already paid in a batch cannot silently be paid
  again.

## 11.2 The three routes

| Route | Used for | What the app creates |
| --- | --- | --- |
| **Cash** | money transfers to people | Payment Entries, grouped per state/agent account |
| **Physical Goods** | kits, blankets, food, materials | Stock entries that move the goods out of the warehouse |
| **Services** | fees, treatment, tuition, hired services | Invoices for the service delivered |

Set the accounts for each route once, in settings. If a state has no agent bank account
configured, the batch will stop and tell you — that check exists so money is never paid
out of the wrong account.

## 11.3 Running a batch

1. **Create the order**, choose the route, the project, the date and the company.
2. **Add the beneficiaries.** The primary action fetches them; filter first so you do not
   pay the same person twice in one batch.
3. **Set the amount, item or service** per person, and check the total against your budget
   or the donation you are spending.
4. **Submit.** The app creates the payment entries, stock entries or invoices, using the
   statuses you chose in settings so nothing hits the ledger unreviewed.
5. **Verify.** Create the verification requests for the batch; field agents confirm account
   details and upload proof. Verified rows lock — a verified person cannot quietly go back
   to unverified.
6. **Pay.** Once verification is complete the payment entries are released through your
   normal payment process.
7. **File the proof.** Payment proofs can be attached to the payment entry itself, with a
   preview, so the evidence sits with the transaction instead of in someone's phone.

## 11.4 Verification, in plain terms

Verification answers a simple question: *is this person's name and bank/mobile account
really theirs?*

- **Personal accounts** — the beneficiary's own account is checked.
- **Proxy accounts** — the money goes through a relative, neighbour or agency; the proxy
  and the reason are recorded, because a proxy payment without a reason is a red flag.
- A verification request can be worked by an agent in the field, with the result uploaded
  as evidence.
- Verification can be paid per confirmed item, which is how field agents get compensated
  for the check rather than for the payment.
- Verified rows cannot be reversed to unverified; if a mistake is found, raise a fresh
  request and note why.

## 11.5 Working with orders and invoices

- A **Sales Order** can spawn a disbursement order with the same details, so a programme
  agreed with a partner becomes a payout without re-typing.
- A **Sales Invoice** can pull in lines from submitted disbursement orders, so what was
  promised, what was paid and what is being billed stay in step.
- **Payment Entries** created from a donation can be allocated back to the donors, closing
  the loop between money in and money out.
- Beneficiary payments are made against the beneficiary's **supplier** account, which is
  why the app creates one automatically.

## 11.6 Controls worth knowing

- **Submitted means submitted.** Do not edit a submitted order; amend it, so the original
  stays visible.
- **Check the route, not just the amount.** The most common error is paying cash to
  someone whose goods were delivered, or vice versa.
- **Never pay a batch twice.** If an order was submitted and then cancelled, create a new
  one and reference the old — do not re-submit.
- **Reconcile monthly.** Compare disbursement orders against payment entries and stock
  entries for the month; the three should tell the same story.
