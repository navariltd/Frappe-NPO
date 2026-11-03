# 10. Services

This is what the organisation actually delivers. Each service has its own record so it
can be counted, costed and audited — while all of them hang off the same beneficiary and
case.

## 10.1 Food distribution

- Distribution runs as a project: the **Distribute Food** action takes you from the
  project to a distribution record, so every distribution is tied to a programme and a
  budget.
- Stock goes out through a real stock entry, which means the warehouse figure and the
  "how many people did we feed" figure agree.
- Records who received food, when, and under which project — the basis for the monthly
  food report and for donor reporting.
- Switch the feature on in settings; if you do not hand out goods, leave it off and the
  menu stays clean.

## 10.2 Entitlement requests

Entitlement work is government paperwork: ration cards, pensions, disability
certificates, Aadhaar corrections, caste certificates.

- Each request is tracked with its own status: **Documentation Pending → In Process →
  Completed**, or **Rejected** when the department refuses.
- Attach the documents collected; the biggest cause of failure is a missing paper nobody
  noticed for a month.
- Requests carry the beneficiary and the case, so a completed entitlement closes the loop
  in both directions.
- The **Entitlement Requests per week** chart shows the throughput the team is achieving;
  the *Documentation Pending* pile is where to put effort first.

## 10.3 Shelter homes

Shelter homes are managed as places with real occupancy, not as a list of names.

- Create the shelter home, its capacity and its staff team.
- **Admission** records bring a person in: date, reason, referral, and who authorised it.
- **Service records** log what the person received while resident — meals, medical care,
  counselling, clothing — so the cost per resident is visible.
- **Exit** records close the stay with a reason: returned home, transferred, moved to
  another shelter, absconded, or a health outcome.
- Current occupancy is therefore the difference between admissions and exits, and it is
  always current because field staff close it daily.

## 10.4 Care centres

A care centre is a longer-term facility for people who need continuing support. The
admission record works like a shelter admission but carries the care plan and the
responsible team, and links to the medical records for residents under treatment.

## 10.5 Medical records

- **Medical case sheet** — the clinical picture for a person: conditions, medication,
  treatment plan, treating provider.
- **Hospitalisation record** — admission to hospital, dates, hospital, reason, outcome.
- **Healthcare provider** — the hospitals and clinics you refer to, so referrals are
  consistent and can be reported.
- **Health condition** and **disability condition** masters — the vocabulary your teams
  use, which is what lets you report "how many people with a disability did we serve this
  quarter" without reading free text.

Medical records are sensitive: share them by role, not by forwarding PDFs.

## 10.6 Family reintegration

Family work is tracked as its own record: the family meeting, who attended, the
assessment, and the outcome — including the cases that did not work out ("family members
did not come", "mismatch", "beneficiary refused"). Recording the failures is what shows
a funder that you are honest about reintegration rates.

## 10.7 Learning centres

- A learning centre is created as an organisation with its own supplier account (so fees
  and payments work without extra setup).
- Enrolling a beneficiary creates a **student** record, which is what the education
  reports count.
- Attendance, fees and progress live on the student record; the beneficiary record stays
  the person's single identity.

## 10.8 Which record do I use?

| The person… | Record used |
| --- | --- |
| was picked up from a street or station | **Rescue** |
| needs shelter for a night or a season | **Shelter Home Admission**, then service records, then **Exit** |
| needs long-term residential care | **Care Centre Admission** |
| received food or a ration kit | **Food distribution** under a project |
| needs a ration card, pension or certificate | **Entitlement Request** |
| is ill, or has been hospitalised | **Medical Case Sheet** / **Hospitalisation Record** |
| is going back to their family | **Family Reintegration** |
| is studying at your centre | **Learning Centre** + **Student** |
| needs something not listed here | a **Case** — then record the outcome on it |
