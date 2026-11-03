# 9. Field operations and the mobile app

Field work happens away from a desk, often with no signal and always with a queue of
people waiting. This chapter covers the screens built for that: rescues, camps, daily
visits — and the mobile app that runs them from a phone.

## 9.1 Rescues

A **Rescue** is the record of picking someone up from the street, a station, a hotspot —
the moment of first contact.

- Capture the person (or a new, unidentified person), the date and time, approximate age
  and gender, and their condition. Free text is allowed *and* a "please specify" note, so
  the record is not forced into the wrong box.
- Record **where** it happened, with GPS coordinates, plus police station and police memo
  number — the details that decide whether a case stands up later.
- Record what happened next: referred to hospital, referred to a shelter home, and which
  one. That referral is what makes the rescue part of the person's history rather than a
  standalone statistic.
- Keeps "rescued by" so credit and follow-up responsibility are clear.

Rescues feed the **Rescues per week** chart, which is usually the first sign of a new
hotspot.

## 9.2 Awareness camps

An awareness camp is outreach: you go to a community to tell people about services,
rights and schemes.

- Records the date, time and type of camp (with a free-text option when it does not fit
  the list), the location and the local administrative area down to ward and habitation.
- Captures attendance, the agenda and the **key action points** agreed — the part that
  turns a camp into follow-up work.
- Stores GPS coordinates, so the map of your outreach builds itself.

## 9.3 Health camps

Health camps are the medical equivalent: a camp with a place, a team and a set of
patients seen. They link to the medical records of the people treated, so a camp's output
can be reported as numbers, not impressions.

## 9.4 Daily visit updates

The daily visit update is the field team's logbook: who was visited, when, by whom, and
what happened.

- One entry per visit, quick to fill from a phone.
- Feeds the **Daily Visit Update Report View**, where supervisors filter by worker and
  date to see a week of activity.
- Keeps the narrative that case outcomes cannot hold: who was at home, what the family
  said, what needs following up tomorrow.

Visit updates are deliberately lightweight. If something needs action, it also becomes a
follow-up on the case — the visit log records that you went, the case records what you
did about it.

## 9.5 The mobile app

The field app is a browser app (a PWA) rather than something from an app store:

- Open the app on a phone, then **Add to Home Screen**. It then opens full screen like a
  normal app, with its own icon.
- It is built for one-handed use: the common field actions, the person's record, visits,
  and the case you are working.
- It uses the same data and the same permissions as the desk — a field worker sees their
  own area, not the whole organisation.
- Because it is a browser app, updates arrive when you reload; there is nothing to
  install or approve.

**Before a field day:** confirm the phone has data or has synced, and that the worker's
login is still valid — field visits lost to an expired password are a recurring way to
lose a week of data. If a visit cannot be logged on the spot, write it down and enter it
the same evening; a visit entered a month later is worth very little.
