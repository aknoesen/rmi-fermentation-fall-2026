# Pre-Campaign Measurements: Setting Laser Power and Integration Time

**For:** Diego Yankelevich (measurements) and André Knoesen (decision)
**Window:** Tuesday 6 to Thursday 8 October 2026, instrument on site at the winery
**Campaign:** tank filled Friday 9 October (cold soak under house N₂); first measurements Saturday 10 October, at least one over the weekend; regular five-a-day schedule from Monday 12 October, when the tank is inoculated
**Decision due:** Thursday 8 October, 12:00
**Companion document:** `NOISE_PRIMER.md`, same folder, defines every noise term used here.

---

## Background: the 2024 deployment and what changes now

The instrument reported in the TIM paper (IEEE Trans. Instrum. Meas., vol. 75, 2026, Art. no. 7006218) monitored a six-day fermentation of 136 kg of 2024 Cabernet Sauvignon at the UC Davis Research Winery, starting 23 September 2024. It took one acquisition per day, at 515 kPa absolute (60 psig), and was powered down between acquisitions. Excitation was an MKS EXLSR-532-200 laser (200 mW), giving 60 to 80 mW at the fiber output after coupling losses. Each spectrum was a **single exposure of 1000 s** (500 s on Day 1). That integration time was chosen by inspection, long enough for spectra that looked good and short enough not to saturate the detector; it was not derived from a noise measurement. The archive shows how close the margin was: nitrogen-rich spectra at 1000 s reached 61,800 to 65,400 counts against the detector's 65,535 ceiling. Several ENLIGHTEN features were not used: no scan averaging (each spectrum is one frame, so no outlier rejection was possible), no dark subtraction, no factory relative-intensity correction, and no selection of the detector rows carrying the fiber image. The laser is external to ENLIGHTEN, so laser power was never recorded with the spectra. The TEC was set to −13 °C, and the recorded detector temperature drifted between −12.1 and −13.9 °C across the six days. One argon reference, acquired on Day 5, served the whole deployment. No bias or dark frames were taken. The noise floor was characterized after the fact, from a single spectral window (3718 to 3918 cm⁻¹) in each spectrum: σ = 54 to 90 counts. The only repeat measurements were three 500 s acquisitions on Day 1, which scattered by 10.3%. The paper's comparison with Bai *et al.* concluded that the floor was not limited by dark current and attributed it to background structure, but no measurement separated the noise terms.

The coming campaign differs on every axis that bears on this. A 5 W laser allows several times the 2024 power at the fiber output. A 1000 s single exposure is still possible, but only with the power attenuated back to roughly the 2024 level, which gives up the gain the new laser offers; at higher power a 1000 s frame saturates the N₂ band that the normalization depends on. The target shifts from three bulk gases that sat 9 to 75 times above their quantification limits to weak volatile bands followed through their rise and fall. The schedule becomes five acquisitions a day for at least a week. **The integration time therefore has to be set by measurement this time, not by inspection**: separating the noise terms, finding where longer integration stops paying, and choosing laser power, frame time and frame count to give the best SNR the schedule and the hardware allow. The rest of this document is that measurement.

---

## 1. What has to be decided by Thursday noon

Four numbers, fixed for the whole campaign:

| Symbol | Meaning |
|---|---|
| **P_op** | Operating laser power, stated as the Ophir reading at the fiber output (the 2024 deployment ran at 60 to 80 mW there) |
| **t_f** | **Frame time**: the integration time of one detector exposure |
| **M** | Frames per acquisition. The spectrum used in analysis is the combination of M frames, so the total integration time is **T = M · t_f** |
| **M_Ar** | Frames in each argon reference acquisition |

### Power control, power measurement, and what stays fixed

**Power is set at the input and measured at the output.** Input power is controlled with the half-wave plate and polarizer ahead of the fiber; coupling into the fiber can be re-optimized if it is judged to have drifted. Power is known only from the Ophir meter at the fiber output. In this document **P** always means that Ophir reading. Input power and coupling efficiency are not measured separately.

Six rules follow:

- **Set power with the half-wave plate, not the laser.** The laser runs at a fixed output of about 5 W, well above threshold, so its noise and pointing characteristics do not change with the power delivered; the half-wave plate and polarizer attenuate it. Log the half-wave plate angle with every frame. The polarizer must follow the half-wave plate, so that the polarization launched into the fiber stays constant while the power changes.
- **Most of the 5 W goes somewhere other than the fiber.** The beam rejected by the polarizer carries nearly all of the laser output at low settings, and the half-wave plate and polarizer see the full 5 W at every setting. The rejected beam must end in a beam dump rated for 5 W. The laser and the dump sit outside the instrument enclosure, so that heat does not reach the optics. Whether the laser stays on between runs is a safety decision (Section 3).
- **Define a reference state.** The fixed laser output and one half-wave plate angle, recorded in M0. The Ophir reading at the reference state is the coupling check. A fall at an unchanged reference state means coupling loss or damage at the fiber input, not a change of power.
- **Input-side adjustments are allowed, and are events.** A coupling re-optimization or a change of half-wave plate angle is logged with its time. After a coupling adjustment, take an argon reference and one ambient-air check acquisition before resuming, because re-coupling can change the mix of fiber modes excited and with it the silica background, not only the power. During the campaign, make coupling adjustments only before the morning argon reference, so that each day's headspace data sit between two references taken in one alignment.
- **Do not compensate a coupling loss with power.** Turning up the half-wave plate to restore the Ophir reading raises the power at the input face, which is where the damage risk is. Compensate only within the input range already passed in M2; otherwise re-optimize the coupling.
- **Everything from the fiber output onward stays fixed:** collection optics, the 45° edge filter, the notch filter, the spectrometer coupling and the Ophir head. Dark frames are taken with the laser off or its internal shutter closed, never with a block in the beam. If anything downstream of the fiber output is disturbed, M3 to M5 must be repeated, since every number they produce belongs to one detection geometry.

"Integration time" in the 2024 work meant a single 1000 s exposure. At any power above the 2024 level it has to be split into a frame time and a frame count, for the reason in Section 2. Every frame is saved individually, so the analysis can later use fewer than M frames if a frame is spoiled, and the effective integration time remains adjustable after the fact downward, never upward.

---

## 2. What the 2024 setting would cost now

### The detector was already at its ceiling

The detector's converter records at most 65,535 counts per channel. In the 2024 archive, nitrogen-rich spectra at 1000 s and 60 to 80 mW already reached that ceiling at the N₂ band (2331 cm⁻¹):

| File (`Archive_TIM-26-07018\data\01_raw_spectrometer\`) | Peak counts |
|---|---|
| `2024-11-06\enlighten-20241106-130234-...csv` | 65,444 |
| `2024-10-12\enlighten-20241012-135920-...csv` | 65,020 |
| `2024-10-13\enlighten-20241013-182528-...csv` | 64,191 |
| `2024-09-27\enlighten-20240927-120454-...csv` | 61,783 |

Signal scales with power × time. **At any power above the 2024 level, a single 1000 s frame will saturate the N₂ band**, and N₂ is the internal standard of the three-gas normalization. A saturated N₂ band invalidates every molar fraction in that spectrum.

Estimated frame-time ceiling, holding the N₂ peak in pure nitrogen to 75% of full scale (about 49,000 counts):

> t_f,max ≈ 52,700 / P  (seconds, with P the Ophir reading in mW)

| P | 70 mW | 200 mW | 500 mW | 1 W |
|---|---|---|---|---|
| t_f,max | 750 s | 260 s | 105 s | 53 s |

The estimate is an **upper bound**: the 2024 laser power for those files was not logged, and the top file may itself be clipped. Measurement M3 replaces it.

### Power and time are not interchangeable for every noise term

| Term | Scales with power | Scales with frame time |
|---|---|---|
| Raman signal | P | t |
| Laser-induced background (silica Raman, fluorescence, stray light, elastic leakage) | P | t |
| Dark signal | no | t |
| Read noise | no | once per frame |

Raising power at fixed total time T raises signal and background together while leaving dark charge unchanged. If the 2024 floor was set by dark charge, SNR improves in proportion to P. If it was set by background shot noise, SNR improves as √P. If it was set by fixed-pattern structure, SNR does not improve at all. Measurements M1 and M2 determine which case holds, and with it how much the new laser actually buys.

---

## 3. The schedule sets the total time

Headspace runs start at **09:00, 11:00, 13:00, 15:00 and 17:00**. Each is done in an on-site window of about **30 minutes**, and the team is not on site between runs. The winery is shared with a Viticulture and Enology class, so students are present when the team is not.

**Whether the laser may stay on between runs**, with its shutter closed and the usual shrouding, is a laser-safety decision for Diego Yankelevich under the site's laser-safety rules, not a measurement decision. This plan assumes the laser is switched off between runs, and measures what that costs (M1b).

Every run window must then hold the laser warm-up, the fill, pressurization, acquisition and purge:

> T_max = 30 min − (warm-up + fill + pressurize + purge)

| Fill + pressurize + purge | Warm-up | T_max |
|---|---|---|
| 10 min | 0 min | 20 min |
| 10 min | 5 min | 15 min |
| 10 min | 10 min | 10 min |

The overhead is timed in M0 and the warm-up in M1b.

**What this means.** T is set by the schedule, at 10 to 20 minutes, which is comparable to the 1000 s (17 minutes) of 2024. The gain over 2024 therefore has to come from laser power, not time. Collected signal scales with P · T: at P_op = 500 mW and T = 15 min the instrument collects about 6.4 times the 2024 exposure of 70 mW × 1000 s. Whether that buys a factor of 6.4 in SNR, √6.4 ≈ 2.5, or less depends on which noise term dominates (Section 2). The power ramp (M2) is therefore the most consequential measurement in this plan, and the noise measurements (M4, M5) establish how much of the extra power turns into SNR.

The gas is static in the fiber once pressurized, so each spectrum describes the headspace at the moment of filling. The pressure hold over T is checked in M6.

**Argon references** are taken in their own windows, before the 09:00 run and after the 17:00 run. With M_Ar = 2M (Section 5) each needs about 2T plus 15 minutes for fill and purge.

---

## 4. Measurements

**Owner: Diego Yankelevich** for every measurement. **Owed back for every measurement:** the spectra, every frame saved separately, in `IEEE Fermentation\Noise Floor Characterization\data\<YYYY-MM-DD>\`, plus a line per frame in the run log (Section 6). Analysis is returned the same day.

### M0. Lock and record the configuration

**When:** Tuesday 6 October, before any other measurement.

1. In ENLIGHTEN, turn off: dark subtraction, baseline correction, any deconvolution or processing, Raman intensity correction, scan averaging (set to 1), boxcar (set to 1).
2. Record: the vertical binning rows (which of the detector's 58 rows are summed, read from the spectrometer configuration since it is not written to the CSV), the TEC setpoint, the gain and offset registers, and the horizontal region of interest.
3. Record the maximum power each optical component sees at the intended top power, against its rating: the half-wave plate, polarizer and beam dump (each at the full 5 W), the fiber input face and couplers (including any adhesive), the 45° edge filter (10CGA-610) and the 532 nm notch filter. Also record the **Ophir head's rated maximum power**: it caps the highest power that can be measured without touching the path, and so the highest power that can be used.
4. Time one nitrogen purge, one fill and one pressurization to 60 psi.
5. Optimize the fiber coupling once, with the laser at its fixed output, then choose the reference half-wave plate angle (Section 1). Record the Ophir reading at the reference state.

**Done when:** one test spectrum's CSV header shows every processing flag off, and the settings, component ratings, timings and reference state with its Ophir reading are written into `CONFIG_RECORD.md` in the data folder.

### M1. Bias and dark frames (laser off)

**When:** Tuesday night into Wednesday morning, unattended.
**Gas:** any. **Laser:** off. The laser sits outside the instrument enclosure, so the detector's thermal state does not depend on it, and an unattended overnight run needs no laser. Nothing is placed in the beam.

1. Allow the detector temperature to settle at the setpoint.
2. 20 bias frames at the shortest integration time ENLIGHTEN allows.
3. Dark frames in **pairs** at 10, 30, 100, 300 and 1000 s, and one at 3000 s.

**Gives:** electronic offset, read noise, dark rate at the operating temperature, dark non-uniformity and hot pixels.
**Done when:** all frames are saved, and the header temperature of every frame is within 0.5 °C of the setpoint.

### M1b. Laser warm-up from a cold start

**When:** Wednesday 7 October, first thing (the laser has been off overnight); repeated once at midday after the laser has been off for two hours, matching the campaign's interval between runs.
**Gas:** ambient air at 60 psi. **Laser:** reference half-wave plate angle.

1. Switch the laser on at its fixed output.
2. Log the Ophir reading continuously, and take consecutive 60 s frames for 45 minutes.

**Gives:** the warm-up time, defined as the time until the Ophir reading is within 1% of its final value **and** the quiet-window background per unit Ophir power is within 2% of its final value. The second condition matters because re-pointing during warm-up can change the background even after the power has settled.
**Done when:** the warm-up time is stated for both starts.

### M2. Power ramp, ambient air at 60 psi

**When:** Wednesday 7 October, morning.
**Gas:** ambient air, 60 psi. Air gives the N₂ and O₂ bands as a signal and the quiet window as a background, and is benign.

1. With the laser at its fixed output, start at the 2024 level (about 70 mW on the Ophir) and step up the power with the half-wave plate by a factor of about 1.5, stopping at the lowest component limit from M0 or the Ophir rating, whichever comes first.
2. At each step, take three frames, with the frame time scaled inversely with power so that the N₂ peak stays near 30,000 counts. Log the half-wave plate angle, the Ophir reading at the start and end of each frame (continuously, if the Centauri meter is set to log), and the fiber enclosure temperature.
3. At the highest step that passes, hold for 60 minutes with one frame every 5 minutes.

**Criteria, fixed before looking at the data.** Every "per mW·s" below uses the Ophir reading. A power step passes only if all five hold:

- N₂ band area per mW·s within 2% of the 70 mW value: the detector and coupling remain linear.
- Quiet-window (3718 to 3918 cm⁻¹) background per mW·s within 5% of the 70 mW value: no new fluorescence or heating-driven background.
- During the hold, no monotonic trend greater than 2% per hour in the background or the N₂ area.
- After the step, returning the half-wave plate to the reference state gives an Ophir reading within 2% of its value before the ramp: no loss at the fiber input from the higher power.
- During the hold, Ophir drift under 2% at a fixed half-wave plate angle, and the fiber enclosure within its 40 °C specification.

**P_op** is one step below the highest passing step, which leaves margin for a week of daily operation.

**Stop rule.** If the Ophir reading at the reference state drops more than 2 %, the fiber enclosure leaves its 40 °C specification, or anything near the fiber input shows discoloration, smell or heat: return to the last power step that passed, stop the ramp, and call André Knoesen before going higher. A week-long campaign depends on not damaging the fiber input face.
**Done when:** P_op is stated with the passing data for every step.

### M3. Saturation ceiling at P_op

**When:** Wednesday, after M2.
**Gas:** house nitrogen at 60 psi (worst case for the N₂ band); then pure CO₂ at 60 psi, if available (worst case for the CO₂ dyad late in fermentation).

1. Take frames at increasing integration time, starting at half the estimate in Section 2, until the brightest band reaches about 60,000 counts.
2. Plot peak counts against time to find where response departs from a straight line.

**Gives:** **t_f,max**, the longest frame time keeping the brightest band at or below 75% of the linear limit, taken as the smaller of the two gases.
**Done when:** t_f,max is stated, with the counts-versus-time data.

### M4. Noise versus total time, argon at 60 psi

**When:** Wednesday afternoon.
**Gas:** argon at 60 psi. **Laser:** P_op.

1. Frame pairs at t_f,max/10, t_f,max/3 and t_f,max. These give the conversion gain (the photon transfer curve, primer Section 8) and the temporal noise of one frame.
2. Twelve consecutive frames at t_f,max.

**Gives:** the noise of the mean of m frames, for m = 1 to 12, in both the 3718 to 3918 cm⁻¹ window and the 2800 to 3000 cm⁻¹ (C–H) window. This is the integration-time curve, built from frames at a safe exposure rather than from long single exposures that would saturate.
**Done when:** all frames are saved and the power log shows under 2% drift across the twelve frames.

### M5. Noise versus total time with strong bands present, ambient air at 60 psi

**When:** Thursday 8 October, morning.
**Gas:** ambient air at 60 psi. **Laser:** P_op.

1. Twelve consecutive frames at t_f,max.

**Gives:** the same integration-time curve as M4 with N₂ and O₂ on the array; the cosmic-ray rate per frame; and **ambient-air spectra in the deployed configuration**, which close the oxygen response-factor gap left open in the TIM paper.
**Done when:** all frames are saved, with the power log.

### M6. Dress rehearsal of one campaign day

**When:** Thursday afternoon, after the decision in Section 5.
**Settings:** the chosen P_op, t_f, M and M_Ar.

1. Run the daily sequence at the real cadence and in real 30-minute windows, with ambient air standing in for headspace and the laser handled as it will be during the campaign: argon, purge, then air acquisitions starting two hours apart (two fit in a Thursday afternoon, three if started by 12:30), each followed by a purge, then argon.
2. Log the fill pressure at the start and end of every acquisition.

**Gives:** the real slot durations; the pressure hold over a full T (a drift above 1% over T sets T lower); the repeatability of the N₂/O₂ ratio across the air acquisitions, against the 10.3% repeat-to-repeat scatter found on Day 1 in 2024; and a final check that nothing drifts over a working day at P_op.
**Done when:** the sequence completes inside the planned slots, and the run log is complete.

### Optional, not gating: CO₂ response factor

If pure CO₂ is on hand, fill with pure CO₂ and then pure N₂ at the same 60 psi and P_op, consecutively, each with M frames. At equal pressure and temperature the number densities are equal, apart from a CO₂ non-ideality correction of about 2% at 515 kPa and 40 °C. The ratio of band areas then gives the CO₂ response factor relative to N₂ directly, with no prepared mixture. The two fills must have the same throughput: normalize each by its Ophir reading, and repeat the N₂ fill after the CO₂ fill to confirm the coupling did not move. Nothing in the published work measures this factor.

---

## 5. The decision, Thursday 12:00

From M1b, M3, M4 and M5:

1. **t_f = t_f,max** from M3.
2. **Total time T.** In each window, plot the noise (σ) of the mean of m frames against total time m · t_f, on log-log axes. The mean keeps the signal at single-frame scale, so σ itself is the relative noise. A slope of −0.5 means averaging is still paying. A slope flatter than about −0.35 means the floor is fixed-pattern or structure, and further frames buy nothing. Take **T** = T_max from the schedule (Section 3), unless the slope flattens earlier; then take the shorter T and return the time to the run window.
3. **M = T / t_f**, rounded up.
4. **M_Ar ≥ 2M**, and 4M if the morning and evening argon windows allow. The argon reference is subtracted from every sample, so its noise enters every result: at M_Ar = 2M it adds about 22% to the random noise of a sample, at 4M about 12%.

**Done when:** André signs off P_op, t_f, M and M_Ar, and they are entered in `CONFIG_RECORD.md`.

---

## 6. Run log

One row per frame, in `data\<YYYY-MM-DD>\run_log.csv`:

```
file, measurement (M0-M6), gas, pressure_psig, laser_setting, waveplate_angle_deg, ophir_start_mW,
ophir_end_mW, pressure_start_psig, pressure_end_psig, frame_time_s, frame_index, detector_temp_C, enclosure_temp_C,
hall_temp_C, timestamp, coupling_adjusted_since_last_frame (y/n), notes
```

---

## 7. What these measurements cannot settle

The volatiles of interest (esters, aldehydes, higher alcohols) have bands in the C–H region near 2800 to 3000 cm⁻¹, where the fermentation headspace also carries a strong ethanol C–H envelope. None of the gases on hand has a band in that window, so the extra noise from working beside a strong band there cannot be measured before Friday. Two mitigations follow from the design above:

- Every frame is saved, so the headspace acquisitions show the in-window noise directly, and the analysis can use fewer frames if required. The weekend cold-soak spectra give the baseline before fermentation; the ethanol envelope builds after Monday's inoculation.
- T is set at the largest value the noise curve justifies, never longer than the schedule allows, so the campaign is not short of signal for the weakest bands by choice.

A dilute methane cylinder (methane's main band is at 2917 cm⁻¹, inside the window, and it does not condense) would allow this measurement directly, if one can be obtained in time.
