# Pre-Campaign Noise Tests: Start Here

**For:** Diego Yankelevich
**From:** André Knoesen
**Date:** 6 October 2026
**Campaign:** tank filled Friday 9 October (cold soak under house N₂); first measurements Saturday 10 October, at least one over the weekend; regular five-a-day schedule from Monday 12 October, when the tank is inoculated. **Decision on laser power and integration time:** Thursday 8 October, 12:00.

---

## What this is

Before the volatiles campaign starts this weekend we have to fix four numbers that hold for the whole run: the laser power at the fiber output (read on the Ophir), the frame time, the number of frames per acquisition, and the number of frames in each argon reference. In 2024 the integration time (one 1000 s exposure) was picked by eye. The same could be done with the RPK laser attenuated to the 2024 power, but that gives up the extra power that is the reason for the new laser, and at higher power a 1000 s frame saturates the N₂ band. How to use the extra power, and how to divide the time into frames, is what these measurements decide. The measurements fit in Tuesday to Thursday.

## What is in this folder

| File | What it is | Read it |
|---|---|---|
| `README_START_HERE.md` | This page | First |
| `MEMO_to_Diego.md` | Who prepared this material and how | First |
| `PRELAUNCH_CHECKLIST.md` | Set up Box Drive, ENLIGHTEN and the app, and test the whole chain once before M1 | Second, and do it Tuesday |
| `INTEGRATION_TIME_PLAN.md` | The measurements M0 to M6: what to do, in what order, the pass criteria, and the done-when for each | Before Tuesday's work |
| `NOISE_PRIMER.md` | Definitions of every noise term (shot, dark, read, fixed-pattern, cosmic rays, processing) and how each scales | As a reference |
| `Archive\noise-floor-characterization-protocol.pdf` | The earlier protocol (13 September). **Superseded by `INTEGRATION_TIME_PLAN.md`**; kept for the record only | No |

Each document is also here as a PDF with the same name, for reading without a Markdown viewer. The logging app is in the sibling folder `Apps for measurements`.

## Where things go

| What | Where |
|---|---|
| Spectra (ENLIGHTEN files) | Box: `2026 Measurements\YYYY-MM-DD\`, one folder per day, as for 4 October |
| The record of each acquisition, events, results | The **Noise Test Log** web app (see below) |
| Photos of your lab notebook pages | Box: the same day folder, in a subfolder `notebook\` |

## Getting the spectra into Box

Every file has to reach the day's Box folder, `2026 Measurements\YYYY-MM-DD\`, so that the analysis can start the same day. Two ways, depending on the instrument computer:

**Recommended: Box Drive on the instrument computer.** Box Drive is Box's Windows app; it shows Box as an ordinary folder in File Explorer (usually `C:\Users\<you>\Box\`) and syncs in the background. Install it from box.com (Downloads, Box Drive) and sign in with your UC Davis account. If the installation gives any trouble, contact André Knoesen (aknoesen@ucdavis.edu), who already runs Box Drive.

1. Keep ENLIGHTEN saving to a local folder on the instrument computer, one folder per day, so acquisition never depends on the winery network.
2. At the end of each 30-minute window, copy that window's new files into the Box Drive day folder.
3. Box Drive uploads them as soon as there is a connection; if the Wi-Fi is down, they upload later on their own. Check the Box Drive icon in the taskbar shows the sync complete before you leave the site.

**Without Box Drive: download and upload by hand.**

1. ENLIGHTEN saves to a local folder on the instrument computer, one folder per day.
2. At the end of each window, or at least at the end of each day, open ucdavis.box.com in a browser, go to `2026 Measurements`, create the day folder if it does not exist, and drag the new files in.
3. Confirm the upload finished (file count and sizes match) before closing the browser.

When a batch of files is in Box and ready for analysis, let André Knoesen know: email (aknoesen@ucdavis.edu), text, phone call, or a voice recording sent to him. Analysis starts on that message, not on the upload.

**Photograph your notebook.** Please take phone photos of each day's lab notebook pages, at the end of every window or at least at the end of the day, and put them in the day folder's `notebook\` subfolder. Hand-written settings, sketches and observations are often exactly what explains an odd spectrum later, and a photo costs seconds.

Either way: do not rename or edit a file once it is in Box, so that the copy analyzed is the copy acquired. If a file was named wrongly, say so in the log entry's notes.

## The Noise Test Log app

A web form; nothing to install. It opens in a browser on a phone or laptop after signing in to claude.ai. André shares it with you; the link is in `Apps for measurements\Noise Test Log.url`.

For each ENLIGHTEN file you save:

1. Pick the measurement tab (M0 to M6) and the planned item.
2. Copy the **suggested file name** the form shows and use it in ENLIGHTEN, so every file can be matched to its log entry automatically.
3. Fill in the form. Values carry over from your previous entry, so normally only the file name, Ophir start and end, and the brightest-peak counts change.
4. Save. The form flags Ophir drift over 2 %, a peak above 75 % of full scale, saturation, detector temperature more than 0.5 °C from setpoint, and fill-pressure drift over 1 %.

Use the **Quick log** bar for anything that is not a file: laser on or off, shutter, coupling adjusted, half-wave plate changed, an Ophir reading, or a note. Each tap is time-stamped. A coupling adjustment is attached to the next file automatically.

**Tell us how the app works for you.** Use it as it is for each day's measurements, and note anything awkward, confusing or missing: tap **App feedback** in the quick log bar the moment something gets in the way, or tell André Knoesen by any of the usual routes. The app will be updated after each day's run, never during one, so it does not change under you mid-measurement.

Tick the steps and the **done-when** box on each tab as you go. The tab rail shows what is done, in progress or not started.

## Settings to change in ENLIGHTEN first

The 4 October N₂ test (`2026-10-04\Batch_40scans_System_Test_10_4_2026_N2_30psi.csv`) shows three settings that have to change before any noise measurement:

| Setting | 4 October | Required |
|---|---|---|
| Dark subtraction | On (one stored dark of about 806 counts, subtracted from all 40 scans) | **Off**; dark frames are taken separately in M1 |
| Baseline correction | ALS | **Off**; baseline removal is done in the analysis |
| Scan averaging | 3 | **1**; every frame is saved so that noise can be measured frame to frame |

Two things that test already shows, which these measurements are designed to settle:

- **The noise floor is mostly fixed structure.** Scan to scan, one pixel varies by about 2.2 counts; across the quiet window in one scan the scatter is about 4.8 counts; averaging all 40 scans brings it down only to 4.3, where random noise would reach 0.8. The stored dark frame, subtracted identically from every scan, is the first suspect.
- **The N₂ signal fell 10 % over 19 minutes** (1288 to 1160 counts), then dropped to 909 and 689 in the last two scans. Was that the end of the fill, a pressure loss, or the laser? The Ophir and pressure fields in the form are there so that the cause is on record next time.

## Your tasks

| Task | When | Done when | Owed back |
|---|---|---|---|
| M0 Lock and record the configuration | Tue 6 Oct | A test spectrum's header shows the three settings above corrected; configuration record in the app's M0 tab complete | Test file in Box; M0 tab complete |
| M1 Bias and dark frames, laser off | Tue night, unattended | All frames saved; every frame's detector temperature within 0.5 °C of setpoint | Files in Box; one log entry per file |
| M1b Laser warm-up from cold | Wed first thing, and midday after 2 h off | Warm-up time entered in the M1b tab for both starts | Files in Box; Ophir readings in the log |
| M2 Power ramp | Wed morning | P_op and the reference half-wave plate angle entered in the M2 tab, all five criteria ticked or failed | Files in Box; log entries |
| M3 Saturation ceiling | Wed, after M2 | t_f,max entered in the M3 tab | Files in Box; peak counts in every entry |
| M4 Noise vs time, argon | Wed afternoon | All frames saved, Ophir drift under 2 % across the twelve | Files in Box; log entries |
| M5 Noise vs time, air | Thu morning | All frames saved with Ophir readings | Files in Box; log entries |
| M6 Rehearsal of one campaign day | Thu afternoon, after the decision | Sequence completes inside the 30-minute windows; pressure drift under 1 % | Files in Box; log entries |

Analysis of each day's files comes back the same day.

## Stop rule for the hardware

If the Ophir reading at the reference state drops more than 2 %, the fiber enclosure leaves its 40 °C specification, or anything near the fiber input shows discoloration, smell or heat: return to the last power step that passed, stop the ramp, and call André Knoesen before going higher. A week-long campaign depends on not damaging the fiber input face.

## If time runs short

M0 to M5 have to fit between Tuesday and Thursday morning, and Wednesday is full. If something slips, keep the measurements in this order and drop from the bottom:

| Priority | Measurement | Why |
|---|---|---|
| 1, essential | M0 configuration, M2 power ramp, M3 saturation ceiling | Together they set the laser power and the frame time |
| 2 | M5 noise vs time, air | The noise curve with real bands present, and ambient-air spectra for the oxygen factor |
| 3 | M1b laser warm-up | Sets how much of each 30-minute window is lost; skip only if the laser may stay on between runs |
| 4 | M4 noise vs time, argon; M1 bias and dark | Separate the noise terms; valuable, but the decision can be made without them |
| 5 | CO₂ response factor | Optional |

Tell André Knoesen as soon as anything is dropped, so the decision on Thursday is made knowing it.

## Your judgment over the plan

You know the instrument; the plan was written without seeing it. If a step is impractical, a criterion is wrong, or there is a better way to get the same answer, say so before running it rather than working around it. The plan is changed in Box, not on the bench, so that the record matches what was done.

## One decision that is yours

Whether the laser may stay on (shutter closed, shrouded) between runs while the students are in the winery is a laser-safety call for you under the site's rules. The plan assumes it is switched off between runs, and M1b measures what that costs: every minute of warm-up comes out of each 30-minute window. Please let André know which it will be.
