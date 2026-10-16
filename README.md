# Olist Delivery Health

A one-page Streamlit dashboard for the **customer-experience manager** at Olist, the Brazilian
marketplace these orders come from.

**Live app:** <!-- PASTE YOUR STREAMLIT URL HERE -->
**Dataset:** [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle)



---

## Step 1 — The dataset and the decision-maker

**Dataset: Olist Brazilian E-Commerce Public Dataset.**

- **Source:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- **Period covered:** September 2016 to August 2018
- **One row is:** one delivered order — a single purchase a customer made from a marketplace seller.
- **Real or synthetic:** **real**. These are genuine anonymised orders from Olist, a Brazilian
  marketplace that connects small sellers to the big carriers. The company published them for
  research; the customer and seller identities are hashed, but the timestamps, prices, delivery
  dates and review scores are the actual records.
- **Size:** the raw download is **9 CSV files, about 130 MB**. What is committed here is a single
  **6.9 MB** file with **96,470 rows × 12 columns**.

**How I reduced it.** The dashboard needs one row per order with the delivery outcome, the buyer's
state, the order value and the review score. The nine raw tables are one order per row spread
across orders, order items, payments, reviews, customers, products, sellers, geolocation and a
category translation. `prep_data.py` joins them, keeps the orders that were actually delivered, and
writes the one file the app reads. I dropped the geolocation table entirely (see Step 3) and kept
only the twelve category names that carry real volume, grouping the long tail into `other`.

**The decision-maker: the customer-experience manager.**

Not "the operations team". One person, whose job is the review score and the complaint inbox. They
own the apology, the refund and the follow-up email, and they are the person who has to explain to
the marketplace leadership why the average rating moved.

---

## Step 2 — Why this dashboard earns its place

**1. Who looks at it, and how often?**

The customer-experience manager, **every Monday morning**. That is when the week's priorities get
set and when the carrier account managers can still be reached about the previous week's loads.

**2. What decision does it support?**

> If **the CX manager** sees **a state's on-time delivery sitting below 90% for three months
> running**, they will **call the carriers and the top sellers serving that state that week and
> ask to move those orders off the slowest lane — and, in the meantime, lengthen the delivery date
> shown to buyers in that state**.

That last clause matters and comes straight from the data: the review score collapses the moment
the promised date is missed, so lengthening the promise is a real lever, not a cop-out. A phone
promised in 23 days and delivered in 24 is scored worse than one promised in 30 and delivered in
25.

**3. What do they do today without it?**

Today this is a quarterly exercise. Someone exports the order table, matches it against the carrier
tracking files in a spreadsheet, and produces a PowerPoint for the leadership review — **a full
day's work, four times a year**. In between, nobody is watching. The March 2018 collapse (on-time
delivery fell to **78.6%**, and in Rio de Janeiro to **63.1%**) was visible in the data for weeks
before anyone acted on it.

**4. Why a dashboard, rather than a weekly email, a report, or an alert?**

- **Not an alert**, because there is no single threshold that means "act now". A state at 89% for
  one month is normal variance; at 89% for three months it is a broken lane. The judgement needs
  the trend, and a trend is something a person reads, not something a rule fires on.
- **Not a weekly report**, because the manager wants to *choose* the state to look at. Half the
  platform's late orders come from Rio de Janeiro, but when a seller escalates a complaint from
  Bahia, the manager needs to answer "what does Bahia look like right now?" in ten seconds.
- **A dashboard earns its place** because the same questions come up every week — *is it getting
  better, where is it worst, how much does a late delivery actually cost us* — and the answers
  change weekly.

---

## Step 3 — What I showed and what I cut

### The three headline numbers

Shown side by side at the top, for the **last three complete months** against the three before:

| Metric | What it answers |
|---|---|
| **On-time delivery** | Is anything wrong right now? |
| **Average delivery time (days)** | Is the problem speed, or is it accuracy against the promise? |
| **Average review score** | Is it costing us customers? |

I deliberately show the on-time rate **alongside** the review score rather than on its own. The
rate is measured against a promise Olist sets itself, and that promise is generous (see the caveat
below), so the rate alone can look healthy while the reviews are poor. Two numbers that can
disagree are more honest than one that cannot.

### The two supporting charts

1. **On-time delivery by month** — the trend, against a 90% target line. This is what turns a
   number into a decision: it shows *when* something broke and whether the fix held. It makes the
   two events in this data obvious — Black Friday 2017, and the March 2018 logistics backlog.
2. **Average review score by how late the delivery was** — a bar chart, and the reason the whole
   dashboard exists. On-time orders average **4.29**; one to three days late, **3.29**; four to
   seven days late, **2.11**; more than two weeks late, **1.62**. The score falls off a cliff at
   the first missed day and then barely moves. That is the business case for spending effort on
   small delays rather than on the rare disaster.

### The one filter

**Customer state.** A nationwide selector defaulting to the whole country, which can be narrowed to
a single state.

That is the only filter, because it is the only dimension that changes what the manager does. The
data confirms it: among states with at least 1,000 orders, the gap between the best and the worst
on-time rate is **10.3 percentage points** (Paraná at 95.0% down to Ceará at 84.7%). The equivalent
gap between the best and worst **product category** is **2.1 points**. The state is where the
variance lives; the category is noise.

### Two things I chose NOT to show, and why

1. **The geolocation table.** It has 1,000,163 rows of latitude and longitude keyed by zip-code
   prefix, and it is the single largest file in the download at 61 MB. It is genuinely interesting —
   you can map delivery times across Brazil — and it would not change a single decision. The
   manager does not deploy trucks; the carrier does. The state breakdown already answers "where is
   it slow" at the resolution the manager can act on, so the 61 MB and the map both stay out.
2. **Payment type and instalment plans.** Credit card is 76.9% of orders and boleto 19.9%, and the
   split is stable over time and across states, so plotting it would add a chart that never moves.
   More to the point, if it *did* move, it would be a question for the finance team about payment
   mix, not for the CX manager about delivery. A chart that belongs to someone else's decision is
   still a chart that does not belong on this page.

I also **built but cut a seller leaderboard**. It is the most tempting thing in this dataset, and
it fails the same test: a seller who ships late is usually a seller in a slow state, so ranking
sellers mostly re-ranks the states with extra steps, and it invites the manager to blame individual
merchants for a carrier problem. The state view is the honest granularity.

### Anything in the data that could mislead the viewer

Three real traps, and how the dashboard handles each:

1. **The promise is padded, so the on-time rate flatters the operation.** Orders are promised an
   average of **23.4 days** and actually arrive in **12.1 days**; **70.8% of all orders arrive more
   than a week before the promised date.** "91.9% on time" therefore does not mean customers are
   happy — it means the promise is easy to keep. *Handled by:* the caveat printed in the footer,
   and by showing the review score next to the rate so the viewer can see the difference between
   keeping a promise and satisfying a customer.
2. **Two months are statistical noise.** September 2016 and December 2016 have exactly **one order
   each**. Plotted naively they produce a trend line that swings from 0% to 100% and back, and they
   make the early period look catastrophic. *Handled by:* the trend drops any month with fewer than
   100 orders, and the chart caption says so explicitly.
3. **Small states are unstable.** Six states (AC, AM, AP, RO, RR, TO) have fewer than 300 orders
   each over two years. One late order moves their rate by several points, so they will always
   appear at both the very top and the very bottom of a naive ranking. *Handled by:* the state table
   flags the cut-off in its caption rather than silently hiding the small states, so the viewer
   knows why they are missing.

A fourth, quieter one: **the last two months of the raw file contain orders that had not been
delivered yet**, so they have no outcome and are excluded. The data therefore stops in **August
2018** rather than October, and the footer states the period as "Sep 2016 – Aug 2018" so nobody
reads the missing tail as a collapse in volume.

### The order of the page

1. **Top — the answer to "is anything wrong right now?"** Three headline numbers for the last three
   months, plus a red or green banner if the on-time rate is under the 90% working level, naming
   how many late orders that is. Someone who reads nothing else still gets the answer.
2. **Middle — why the number moved.** The monthly trend, then the review-score-by-lateness chart
   that explains why the first number is worth caring about.
3. **Bottom — the week's call list.** A state table sorted worst-first with orders, on-time rate,
   average days, late-order count, review score and the gap to target. This is for the manager who
   has seen the banner and now wants to know *which* state to pick up the phone about. It appears
   only in the national view: once a single state is selected the table would have one row, which
   is not a table.

---

## Step 4 — The refresh decision

**How often should the data be refreshed, and why?**

**Nightly**, after the carriers' tracking files land. Delivery status changes every day, so a daily
refresh is cheap and keeps the weekly numbers accurate. Hourly or real-time would add real cost for
no benefit: no decision on this page can be made faster than weekly, because the manager cannot
call a carrier account manager about a single day's dip and expect action.

**How often should someone review it? Is that the same thing?**

**No, and the gap is the point.** The data refreshes nightly; the manager reviews it **Monday
morning**. Daily refresh exists so that Monday's numbers are right, not so that anyone looks at
them daily.

**What should be tracked over time, and what should trigger action?**

**On-time delivery, by state, over a rolling three-month window.** The trigger is **three
consecutive months below 90% in a state with at least 1,000 orders**. Three months, not one,
because a single bad month is usually a holiday or a strike, and three months at scale is a lane
that is genuinely broken. Concretely, on this snapshot that rule fires for **Ceará** (7 consecutive
months), **Rio de Janeiro** (5), **Espírito Santo** (5), **Bahia** (4), **Pernambuco** (4) and
**Santa Catarina** (3) — and Rio alone carries **21.3% of every late order on the platform from
12.8% of the orders**, which is why it is the top of the call list rather than the bottom. Rio's
run is also the clearest illustration of what a dashboard buys: five straight months of
deterioration, from 91.7% before Black Friday 2017 to **63.1% in March 2018** and back to 94.1% the
following month, once the lane was sorted out.

**What does stale data cost?**

**A week of stale data costs a month of bad reviews.** The review score is essentially decided by
whether the promised date was missed — 4.29 on time against 2.57 late — and by the time a monthly
report is compiled, a broken lane has already produced several hundred one-star reviews, each one
public and permanent on the product page. The specific failure mode: a state's on-time rate slips
from 94% to 85% in the second week of the month. Without a dashboard that is invisible until the
quarterly review. With it, the manager sees it on the following Monday, while the carrier account
manager can still rebalance that week's loads.

**On the dashboard itself:**

> **Data: Sep 2016 – Aug 2018 (Olist, Kaggle snapshot). In production this would refresh nightly;
> the CX manager reviews it every Monday morning.**

---

## Notes on the build

- Built with Streamlit, deployed to Streamlit Cloud from this repository.
- The page is deliberately small: one page, three headline numbers, two charts, one filter, one
  table. Every element is there because it changes a decision.
- `prep_data.py` documents how the committed CSV was produced from the raw download. The raw files
  are in `.gitignore` — only the 6.9 MB aggregated file is committed.
- The working directory contains 96,470 delivered orders out of the 99,441 in the raw file; the
  2,971 cancelled, unavailable or still-in-transit orders are excluded because they have no
  delivery outcome to measure.
