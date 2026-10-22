---
name: analysis-reports
description: Principles for building a stakeholder analysis report, such as an HTML data report or a written analysis behind a decision, that a reader with no context understands. Covers aligning the skeleton first, structuring by the reader's questions, bracketing contested numbers, the assumptions table, and the final consistency pass. Use when building or substantially revising a report that other people will read.
---

# Producing analysis reports

These are principles, not a template. Don't copy one report's sections or styling onto a different question.

## Align the skeleton before building

Before generating anything, show the user the one-sentence headline, the section list, the questions each section answers, and what gets a chart versus a table. If a report-building skill has an interview step, run it. Reviewing a skeleton costs minutes; rebuilding a finished report costs hours.

## Write for a reader who has never seen the ticket

- **Open with a short Context section:** what is being proposed, the key prices or terms, and the question the report answers.
- **Title the report with a plain sentence** that a cold reader understands before opening it: "Switching subscribers from monthly to prepaid annual billing barely changes revenue", not "Monthly-to-annual switching is a cash lever".
- **Put the headline numbers in a "Bottom line" list,** each a full sentence carrying its assumption: "If 0.85% of the 12,793 subscribers accept, year-one revenue changes by about +$2,500." No KPI tiles: a big bare number separates the value from its denominator and assumptions.
- **State methods in plain words** ("of everyone subscribed at the start of a month, the share gone a month later"), never by method name.
- **A chart supplements the numbers table, never replaces it.**
- **Show every derived quantity as a formula,** plus one worked example with concrete units.
- **Gloss a term of art at its first use in every section that stands alone,** so a reader who starts at the recommendation doesn't need the earlier sections.
- **State facts and options on their merits.** Don't attribute positions to named people. Naming a person as the source of a figure, or a function as the owner of a decision, is fine.

## Structure follows the reader's questions, not the order of the work

The order in which the analysis was done is not the order a manager, finance, or an executive needs. Their questions run roughly: what is this about, what happens if we do it at the grain I manage, how do the customers actually behave, what does the arithmetic rest on, and what is still unknown. Let those questions name the sections.

## Answer or explicitly defer every question stakeholders asked

Before calling the report done, sweep the originating thread or ticket. Each question is either answered in a findable place or listed under "what this doesn't answer yet" with the data that would answer it. Silence reads as "covered".

## Bracket contested numbers

When a load-bearing assumption is genuinely uncertain, present a ceiling, a plausible middle, and a floor, each with its assumption named in the same sentence, and choose the middle honestly rather than leading with the flattering bound. Tie a linked number to its caveat with a footnote marker, and show negative values in the palette's negative color, matching the charts.

## Give assumptions their own table

Four columns: the assumption, the value used, where it comes from, and what happens if it's wrong, with direction and rough size. If an assumption's failure can't be stated concretely, that is itself a finding.

## Separate money that moves in time from money that changes in amount

Cash collected earlier is not revenue gained, and a discount's full value is a worst case, not the expected cost. Say which kind each headline number is.

## Finish with a whole-report consistency pass

After any substantive revision, reread the whole report, as plain text if needed, looking for sentences the revision made false: a changed conclusion that survives in a subtitle, a takeaway, or a summary. Recheck the arithmetic in worked examples after any rounding change.

## Keep the report and its technical write-up in different registers

The report is for stakeholders: plain words, every term glossed. A technical write-up of the same analysis holds method names, model names, and reproduction detail. Keep their conclusions in sync, and include both in the consistency pass.
