# Memo

**To:** Diego Yankelevich
**From:** Claude (AI model, Anthropic), in consultation with André Knoesen
**Date:** 6 October 2026
**Re:** Pre-campaign noise tests: what has been prepared, and how it was made

---

André Knoesen asked me to write to you directly, so that it is clear who did what in the material now in this folder.

## What I prepared

Working with André over the morning of 6 October, I wrote:

- `INTEGRATION_TIME_PLAN.md`: the measurement plan (M0 to M6) for setting laser power, frame time and frame count before Friday.
- `NOISE_PRIMER.md`: definitions of the noise terms the plan relies on.
- `README_START_HERE.md`: the guide to this folder, the Box routine, and your task list.
- The **Noise Test Log** web app, for recording each acquisition, with the guide in `Apps for measurements`.

I also made the first analysis of your 4 October N₂ test, summarized in `README_START_HERE.md`.

## How it was made

André set the objective and the constraints, and corrected me where I was wrong. The plan reflects his decisions on points I could not have known: the RPK laser running at a fixed output with power set by the half-wave plate and polarizer; the laser and beam dump sitting outside the enclosure; coupling adjustments being allowed on the input side; the 09:00 to 17:00 schedule with 30-minute windows; the students in the winery; and Box as the place the data lives.

My part was drafting, checking the plan against the 2024 archive and the published paper, and the arithmetic. Two of the numbers in the plan come from the archive rather than from correspondence: the 2024 spectra that already reached 61,800 to 65,400 counts at 1000 s, and the ENLIGHTEN settings recorded in the 4 October file headers.

## What to treat with care

- I have not seen the instrument. Where the plan assumes something about the hardware (the order of the half-wave plate and polarizer, the component ratings, the Ophir head's range), your knowledge of the bench overrides it. Please tell André where it is wrong.
- The 4 October findings come from one file. They are reasons to run M1 to M5, not conclusions.
- The frame-time estimate in the plan (about 52,700 s divided by the Ophir reading in mW) is an upper bound from 2024 data with unlogged laser power. M3 replaces it.
- The laser-safety question in `README_START_HERE.md`, whether the laser may stay on between runs, is yours to decide, not mine or the plan's.

## How the analysis will work this week

When a day's files are in Box and ready for analysis, let André Knoesen know by email (aknoesen@ucdavis.edu), text, phone call, or a voice recording sent to him; that message is the signal to start. André's computer gives me read access to the `2026 Measurements` folder. I match each file to its Noise Test Log entry, run the analysis, and return results the same day. Nothing in Box is modified; the analysis works on copies.

Questions about the plan or the app can go to André by any of those routes, including a call or a voice recording when typing is impractical at the instrument; André relays them. They can also be raised in the log's notes, which I read.
