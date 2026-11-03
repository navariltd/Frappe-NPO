# 7. Beneficiaries

Everything in this half of the app hangs off one record: the **beneficiary** — the
person (or household, school or group) you serve. Cases, camps, shelter stays, medical
records, food and money all point back to it, which is what makes "what have we done for
this person?" a single lookup.

## 7.1 What the app does for you

- Keeps one record per person with identity, household, address, territory, documents and
  photo — the file a social worker would otherwise carry in a plastic folder.
- Runs a **lifecycle** so nobody skips steps: a person arrives on a waitlist, is
  acknowledged, becomes active, and later becomes an alumnus or leaves for a documented
  reason.
- Creates the records you would otherwise forget: a supplier account so money can be
  paid to them, a student record when they join a learning centre, a customer if fees are
  involved.
- Tags each person to a programme, a lead donor and sub-donors, a recruitment phase and a
  location, so every report can be cut the way a funder asks for it.
- Captures the donor relationship on the person: which donor funded them, from when to
  when, and how much.
- Lets you **bulk upload** a whole intake from a spreadsheet, with validation before
  anything is created.
- Lets you merge duplicates by marking the survivor, instead of losing history.
- Produces the beneficiary list report used at every review meeting.

## 7.2 The lifecycle, and why it matters

Statuses are not decoration — several of them change what the app allows:

| Status | What the app does with it |
| --- | --- |
| **Waitlist** | Offers a **Local Administrator Acknowledgement** action, which files that acknowledgement as a case. |
| **Active** | The working state. Offers **Disqualification**, **Relocation** and **Bereavement** actions, which open a case of that type. |
| **Relocated / Deceased / Disqualified** | Requires a **Replacement** — the app will not leave the person un-replaced, because a funder needs to know who took their place. |
| Any status change | Drives whether the person counts against a recruitment phase's slots, and whether they appear as active in reports. |

The lifecycle can be switched off in settings for organisations that only keep a list;
for everyone else, leaving it on prevents the classic NGO data problem of a status that
means something different in every district.

## 7.3 Adding one person

1. Search first — check they are not already on file under a different spelling.
2. Create the beneficiary: name, gender, date of birth or age, contact, address and
   territory. The address is what your case and camp reports group by.
3. Record the household and social details your programmes report on.
4. Attach identity documents and a photo. "Identity proof available" is a real reporting
   question, so answer it, do not leave it blank.
5. Tag the **programme**, **lead donor** and any sub-donors, and the **recruitment phase**
   they came in through. Without these tags the person will not appear in funded
   reporting.
6. Save. Supplier (and student, where relevant) records are created for you.

## 7.4 Adding a whole intake

When a camp or survey brings 200 people:

1. Download the blank template from the beneficiary list.
2. Fill it in one row per person, using exactly the values the sheet asks for.
3. Use **Upload Beneficiaries** on the list view; the app checks every row and tells you
   which ones fail and why.
4. Fix and re-upload the failures — successful rows are already in.
5. Reconcile the count against the camp register before you close the day.

Bulk upload is how field teams avoid weeks of typing. Do one small file first (five
rows), confirm it looks right, then load the rest.

## 7.5 Actions on the beneficiary screen

The screen offers context-aware actions under **Create** — you only see the ones that
make sense for that person's status:

- **Local Administrator Acknowledgement** — for someone on the waitlist.
- **Disqualification / Relocation / Bereavement** — for an active beneficiary; each opens
  a case of that type so the exit is documented, not just a status change.
- **Replacement** — offered when a person is relocated, deceased or disqualified and no
  replacement has been named yet.

Each action creates a linked record rather than an isolated note, which is why an auditor
can follow the story from intake to exit.

## 7.6 Merging duplicates and retiring records

- **Duplicates:** pick the record you will keep and mark the other as replaced by it. The
  losing record stays visible for history but stops appearing as a live person. Do not
  delete — cases, payments and camp attendance point at it.
- **Data protection:** if someone asks to be erased, remove the identifying details but
  keep the statistical record, so past reports still add up.
- **Wrong status:** if the lifecycle setting allows status editing, correct it; if not,
  use the matching case action so the change is explained.

## 7.7 The Beneficiary report

The report is the answer to "who are we serving?" — filter by programme, lead donor,
sub-donor, beneficiary type, status, country/state/county, institution, course, thematic
area or by intake dates, then export. It is the standard annexure for donor reporting and
for the monthly programme review.

Once a person is on file, the work you do for them lives in [cases](08-cases.md).

