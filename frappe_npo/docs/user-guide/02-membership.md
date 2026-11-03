# 2. Membership

The membership feature turns supporters into a club you can bill and keep in touch
with. It handles three things: what a membership costs (**Membership Type**), who the
supporter is (**Member**), and the period they paid for (**Membership**).

## 2.1 What you can do

- Offer several kinds of membership — individual, family, student, life, corporate —
  each with its own fee and duration.
- Keep one record per supporter, linked to their customer account in the books, with
  contact details, address and photo.
- Create a membership for a period and have the app work out start and end dates,
  numbering it automatically.
- Raise the fee invoice in one click and email it, or leave invoicing off and simply
  record members as supporters.
- Collect the fee in instalments and see what is still outstanding per member.
- Email an acknowledgement once a membership is paid.
- Let people join and pay online, and have the membership appear already paid.
- Let the system expire memberships automatically so your active list is always true.
- See who is about to lapse and renew them before they do.

## 2.2 The renewal rule that saves you work

Every membership has a period. When you create the next membership for the same member _shortly before or after_ the previous one ends, the app continues from the
existing end date instead of starting a fresh period — no accidental gap, no
double-billing for days the member already paid for.

- The continuation window is **30 days** from the previous membership's end date.
- Anyone with the administrator role can override it (for late renewals or for fixing
  history).
- If the new start date falls outside the window, a completely separate period is
  created.

Practical effect: renewals run on the anniversary of the original joining date, which
is what members expect and what auditors like.

## 2.3 Joining, day to day

1. **Create the member once.** Search the list first — duplicates are the main cause of
   wrong renewal reminders.
2. **Attach a customer** to the member (one click). Without it you cannot invoice them.
3. **Create the membership**, pick the type, let the dates fill in, save.
4. **Generate the invoice** if invoicing is switched on; check the amount and send it.
5. **Record the payment** when it arrives. The membership status follows the money and
   the dates: _New_ when created, _Current_ once paid and running, _Pending_ while
   something is outstanding, _Expired_ once the end date passes, _Cancelled_ if it is
   voided.
6. **Send the acknowledgement** email, if you have not automated it.

The member record also gives you the supporter's **Accounting Ledger** and **Accounts
Receivable** in one click, so a membership co-ordinator can answer "have they paid?"
without calling finance.

## 2.4 Online joining

With online membership switched on, a visitor fills in a form on your website, pays
through configured payment gateway, and:

- a member record is created (or matched to the existing one by email),
- the membership is created for the type they chose,
- the payment is recorded and the invoice raised automatically,
- the acknowledgement email goes out.

Nobody has to reconcile the website against the books afterwards. Online donations
work the same way (chapter 3).

## 2.5 Keeping the register clean

- **Expiry runs by itself.** A scheduled job moves memberships past their end date to
  _Expired_, so "current members" means current.
- **Expiring Memberships report** lists everyone whose period ends in a chosen month,
  with contact details, ready for a renewal campaign. Run it for next month on the
  first of every month.
- **Halted members** (stopped paying on a subscription) stay visible on the member
  record rather than disappearing.
- Never delete a member who has paid. Cancel the membership instead, so the ledger and
  the register still agree.

## 2.6 Members who also donate

A member can be a donor at the same time — they are different relationships, so both
records exist. When a member gives a donation of the kind that qualifies, raise an 80G
certificate for it exactly as for any other donor
([chapter 3, section 3.5](03-donations.md#35-80g-certificates)); the
certificate uses the company's 80G number and PAN from settings.
