# Pre-Launch Checklist

**For:** Diego Yankelevich
**From:** Claude (AI model, Anthropic), in consultation with André Knoesen
**Date:** 6 October 2026
**Complete by:** Tuesday 6 October, 17:00, before M1 (the overnight bias and dark frames)

---

The point of this checklist is to prove the whole chain works once, end to end, before any measurement depends on it: a spectrum acquired with the right settings, saved to Box, logged in the Noise Test Log, and picked up for analysis. It takes about 30 minutes. Each step has a check you can make yourself.

## 1. Read the two short documents

In `Communications and docs`: `MEMO_to_Diego` (who prepared this and how) and `README_START_HERE` (the folder, the Box routine, your task list).

**Done when:** both read. The plan and primer can wait until you need them.

## 2. Install Box Drive on the instrument computer

Box Drive is Box's Windows app; it shows Box as a folder in File Explorer and syncs in the background. Install it from box.com (Downloads, Box Drive) and sign in with your UC Davis account. If the installation gives any trouble, contact André Knoesen (aknoesen@ucdavis.edu).

**Done when:** File Explorer shows `Box\...\Experimental Raman Spectra Data Folder\2026 Measurements`, containing `2026-10-04`, `Apps for measurements` and `Communications and docs`; and a folder you create there named `2026-10-06` appears within a minute at ucdavis.box.com.

**If Box Drive cannot be installed:** use the browser instead. **Done when** you have created `2026-10-06` in `2026 Measurements` at ucdavis.box.com.

## 3. Give ENLIGHTEN a local save folder

Point ENLIGHTEN's save location at a local folder on the instrument computer, one per day, for example `C:\RamanData\2026-10-06`. Acquisition then never depends on the winery network.

**Done when:** a saved spectrum appears in that local folder.

**Also check the instrument computer's clock** against your phone. Files are matched to log entries by the time stamps ENLIGHTEN writes into each header whenever a file name does not identify it, so a clock that is minutes off breaks the match. **Done when:** the clock is within a minute of your phone's time.

## 4. Correct the ENLIGHTEN settings

Turn off dark subtraction, baseline correction and the Raman intensity correction; set scan averaging to 1 and boxcar to 1. Take one short test spectrum of whatever gas is in the fiber.

**Done when:** opening the test file's CSV shows, in its header:

| Header line | Must read |
|---|---|
| `Baseline Correction Algo` | `None` |
| `Scan Averaging` | `1` |
| `Boxcar` | `1` |
| `Raman Intensity Corrected` | `False` |
| `Deconvolved` | `False` |
| The `Dark` column below the header | empty |

## 4a. Check the gases

Each campaign day uses argon twice (morning and evening references) plus house N₂ for purges, and this week's tests add argon, N₂ and air fills on top.

**Done when:** you have confirmed there is enough argon for this week's tests plus at least eight campaign days, that house N₂ is available at the winery, and whether pure CO₂ is on hand (if not, the optional CO₂ measurement is dropped). Send André Knoesen the answer.

## 5. Open the Noise Test Log

Double-click `Apps for measurements\Noise Test Log.url` (or open https://claude.ai/artifact/1t3cQum1bYyprLD4k2Mi5X) and sign in to claude.ai. Use whichever device you will log from at the winery, phone or laptop.

**Done when:** the header shows the green **Shared, live** badge and **Logging as** with your name.

- **View only** instead: André has shared the page at the wrong level. Ask for Contributor.
- **Not connected:** check you are signed in to claude.ai and online, then reload.

## 6. Log the test spectrum

1. Open the **M0** tab. Planned item: *Test spectrum, check header flags*.
2. Rename the test file to the **suggested name** the form shows (Copy button), keeping the `.csv` ending.
3. Fill in the form and **Save frame**. In the quick log bar, tap **Note** and enter `pre-launch test`.

**Done when:** the entry appears under *Frames logged for M0* and in the **Full log & export** tab, and the note appears under *Events*. If anything in these steps was awkward, tap **App feedback** and say what; the app is updated after each day's run.

## 7. Put the test file in Box and send the signal

Copy the renamed test file into `2026 Measurements\2026-10-06\`. When it shows as synced (or uploaded), let André Knoesen know: *pre-launch test in Box*. Email, text, a phone call or a voice recording all work, here and throughout the week.

**Done when:** André replies that the file was read from Box and matched to your log entry. That reply closes the checklist.

---

## What success looks like

One test spectrum that:

1. was saved with every ENLIGHTEN processing option off;
2. sits in the Box day folder under the name the app suggested;
3. has a matching entry in the Noise Test Log;
4. was found in Box and matched to that entry, confirmed by André.

When all four hold, every link the measurements rely on has been tested once. Any failure is far cheaper to fix now than at 21:00 with M1 running.

## Then launch

1. Finish **M0**: complete the configuration record in the M0 tab (binning rows, TEC setpoint, gain and offset, ROI, component ratings, purge, fill and pressurize timings, reference half-wave plate angle and Ophir reading), and tick its done-when.
2. Start **M1** (bias and dark frames, laser off) to run overnight.
3. On Wednesday morning, upload M1's files to Box, with photos of the notebook pages in the day folder's `notebook\` subfolder, and send the signal. From there, follow `INTEGRATION_TIME_PLAN`.
