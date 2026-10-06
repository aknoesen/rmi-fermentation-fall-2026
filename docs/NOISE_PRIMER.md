# Noise in the HC-ARF Raman Instrument: A Primer

**Prepared for:** André Knoesen and Diego Yankelevich
**Date:** 6 October 2026
**Purpose:** a shared vocabulary for the noise-floor characterization that precedes the Fall 2026 campaign. Every noise term that can appear in a spectrum from this instrument is defined here, traced to where it enters the signal chain, and described by how it scales and how it can be isolated. The detector receives most of the attention because most of the terms originate there.

**Conventions.** Numbers marked *datasheet* are the Hamamatsu specification ranges for the S7031-1006 and are not measurements of our unit. Numbers marked *as run* come from the ENLIGHTEN headers of the 2024 deployment files in `Archive_TIM-26-07018\data\`. Numbers marked *TIM* are from the published paper (IEEE Trans. Instrum. Meas., vol. 75, 2026, Art. no. 7006218).

---

## 1. The signal chain, and where noise enters

A Raman photon becomes a number in a CSV file in eight steps. Noise can enter at each one.

| Step | What happens | Noise that enters here |
|---|---|---|
| 1. Excitation | 532 nm light is coupled into the hollow-core anti-resonant fiber (HC-ARF), a fiber that guides light in a gas-filled core rather than in glass | Laser power and coupling fluctuations |
| 2. Scattering | Gas molecules in the core scatter Raman light; the fiber wall, filters and optics add unwanted light | Background light (Section 4.3) |
| 3. Filtering and dispersion | Edge and notch filters reject the laser line; the grating spreads the remaining light across the detector | Elastic-scatter leakage, stray light, wavelength drift |
| 4. Photoconversion | Each photon absorbed in a detector pixel frees one electron with probability equal to the quantum efficiency | Shot noise (Section 4.1) |
| 5. Integration | Charge accumulates in each pixel for the integration time *t* | Dark current (Section 4.4), cosmic-ray events (Section 4.8) |
| 6. Readout | Charge is shifted to an output node, converted to a voltage and sampled | Read noise (Section 4.5) |
| 7. Digitization | The voltage is converted to an integer number of counts | Quantization noise (Section 4.6) |
| 8. Processing | Argon subtraction, regridding, baseline removal, peak fitting | Added, correlated or reshaped noise (Section 4.10) |

Terms entering at steps 1 to 3 are optical; the detector cannot distinguish them from signal. Terms entering at steps 4 to 7 belong to the detector. Step 8 is ours.

---

## 2. The detector

The spectrometer is a Wasatch Photonics WP-532-C-EXR-IC. Its detector is a **Hamamatsu S7031-1006**, a **back-thinned full-frame-transfer CCD**.

- **CCD (charge-coupled device):** a silicon array in which each pixel collects photoelectrons during exposure. The charge is then moved, pixel by pixel, to a single output amplifier.
- **Full-frame transfer (FFT):** the whole array is light-sensitive, with no shielded storage area, so the array must not be illuminated during readout. In a spectrometer that condition is met because readout is fast compared with the integration time.
- **Back-thinned:** the silicon is thinned and illuminated from the back, so light does not pass through the electrode structure. Quantum efficiency is high (above 90% at peak, *datasheet*). The thin silicon can act as a weak optical cavity at red wavelengths, which is the origin of etaloning (Section 4.7).
- **MPP (multi-pinned phase) operation:** a biasing mode that suppresses the surface contribution to dark current. The S7031 runs in MPP mode (*datasheet*).
- **TEC (thermoelectric cooler):** a Peltier element that holds the detector below ambient.

### Detector facts

| Quantity | Value | Source |
|---|---|---|
| Pixel size | 24 × 24 µm | datasheet |
| Active pixels | 1024 (spectral) × 58 (vertical) | datasheet |
| Pixels used, spectral axis | 20 to 746, i.e. 727 of 1024 | as run (`ROI Pixel Start/End`) |
| Rows binned, vertical axis | **not recorded in the CSV** | open item, Section 9 |
| Full well, single pixel (vertical register) | 240 to 320 ke⁻ | datasheet |
| Full well, horizontal register (binned charge) | 800 to 1000 ke⁻ | datasheet |
| Output node sensitivity | 1.8 to 2.2 µV/e⁻ | datasheet |
| Read noise | 8 to 16 e⁻ rms (at −40 °C, 150 kHz, Hamamatsu camera) | datasheet |
| Dark current at 0 °C | 10 to 100 e⁻/pixel/s | datasheet |
| Dark current temperature dependence | roughly doubles every 5 to 7 °C | datasheet |
| Charge transfer efficiency | 0.99995 to 0.99999 per transfer | datasheet |
| Detector temperature, Days 1 to 6 | −12.1 to −13.9 °C | as run (`Temperature`) |
| Detector temperature, full 2024 archive | −16.0 to +5.1 °C | as run |
| Gain register | 1.9 (Wasatch's legacy default) | as run (`CCD Gain`) |
| Offset register | 0 | as run (`CCD Offset`) |
| Scan averaging, boxcar | 1, 1 | as run |
| ENLIGHTEN dark subtraction | not applied (`Dark` column empty) | as run |
| Factory relative-intensity correction | not applied | as run, TIM |

**Binning** means adding the charge of several pixels together on the chip before readout. A spectrometer normally bins the rows of each column that the entrance slit illuminates, so that one spectral channel is the sum of those rows. Binning on the chip, before the amplifier, adds read noise once per column. Adding the same rows in software after readout would add it once per row. The number of rows binned matters to three terms in this primer (dark current, cosmic rays and saturation), and it is not in the file headers.

---

## 3. Units: photons, electrons and counts

Three units appear, and confusing them is the most common source of error in noise arithmetic.

- **Photons** arrive at the detector.
- **Electrons** (e⁻) are what the pixel stores. Electrons = photons × quantum efficiency.
- **Counts** (also called ADU, analog-to-digital units) are what the file records.

The link between the last two is the **conversion gain**, written *G* here, in counts per electron. *G* is set by the output node sensitivity, the amplifier and the analog-to-digital converter (ADC), and is changed by the gain register.

**Every physical noise statement is made in electrons.** Shot noise is √N in electrons; it is not √N in counts unless *G* = 1. A σ of 90 counts means 90 electrons if *G* = 1, 45 if *G* = 2, and 180 if *G* = 0.5, three different physical situations. **Our *G* has never been measured**, and the gain register value of 1.9 is a setting, not a conversion factor. Section 8 gives the measurement that determines *G*: the photon transfer curve.

In what follows, *N* denotes a number of electrons and *t* the integration time of one exposure.

---

## 4. The noise terms

Each term is given the same treatment: what it is, where it comes from, how it scales, what reduces it, and how to isolate it by measurement.

### 4.1 Shot noise: the principle

Light and charge come in discrete units that arrive at random times. If on average *N* electrons are collected, the number actually collected in one exposure fluctuates with a **Poisson distribution**, whose standard deviation is **√N**. This is **shot noise**. It is a property of the arrival process, not a defect of the detector, and no instrument design removes it.

Three consequences matter here:

1. Shot noise grows with the signal, so a stronger signal is noisier in absolute terms while its relative noise, √N / N = 1/√N, falls.
2. Shot noise from independent sources adds **in quadrature**: the variances add, not the standard deviations. Signal electrons, background electrons and dark electrons all carry their own shot noise, and the total variance is *N*_signal + *N*_background + *N*_dark.
3. **Subtracting the mean of an unwanted contribution does not remove its shot noise.** Argon subtraction removes the average background level; the √N fluctuation of that background stays in the spectrum. This is why a large background limits detection even when it is perfectly subtracted.

The next three sections are the three sources of shot noise.

### 4.2 Signal shot noise

- **What:** shot noise on the Raman photons of the species being measured.
- **Scaling:** variance = *N*_S, which is proportional to *t*, to laser power, to gas number density (so to pressure), and to the species' Raman cross-section.
- **Reduced by:** nothing, relative to the signal. It sets the ultimate SNR ceiling, √*N*_S.
- **Practical consequence:** the noise at the top of a strong peak is larger than the noise in an empty region of the same spectrum. The N₂ peak top carries more noise than the 3718 to 3918 cm⁻¹ window does. A σ measured in an empty window therefore describes the noise on a weak band in empty surroundings, not on a weak band sitting under a strong one.

### 4.3 Background shot noise

- **What:** shot noise on every photon that reaches the detector without being Raman signal from the gas. Background has two parts: a **mean level**, which subtraction can remove, and a **shot noise**, which it cannot.
- **Origin.** Four sources in this instrument:
  - **Silica Raman:** the laser excites Raman scattering in the glass of the fiber microstructure and in any glass in the beam path. The silica bands are broad.
  - **Fluorescence:** emission from glass, coatings, adhesives, filter materials or contamination, excited by the laser. It is broad and featureless.
  - **Stray light:** light that reaches the detector by unintended paths, such as scattering inside the spectrometer.
  - **Elastic-scatter leakage:** laser-wavelength light (Rayleigh scattering from the gas, plus reflections) that the filters fail to reject completely. Rayleigh scattering scales with gas number density, so this term rises with fill pressure.
- **Scaling:** variance = *N*_B, proportional to *t* and to laser power. The elastic part also scales with pressure.
- **Reduced by:** rejecting the background before it reaches the detector: better filters, cleaner optics, and reading out only the detector rows that carry the fiber image (row selection), since rows outside the image collect background and dark charge but no signal.
- **Isolated by:** an argon-filled fiber with the laser on. Argon has no first-order Raman activity, so everything recorded is background plus dark. Comparing argon at two pressures separates the pressure-dependent elastic part.
- **Status in TIM:** the published comparison with Bai *et al.* found our detection limits more than two orders of magnitude above what dark current, slit and integration time account for, and attributed the residual to background structure.

### 4.4 Dark current and dark shot noise

- **What:** electrons generated thermally in the silicon, collected whether or not light is present. **Dark current** is the generation rate (e⁻/pixel/s). **Dark signal** is the accumulated charge *N*_D. **Dark shot noise** is its Poisson fluctuation, √*N*_D.
- **Scaling:**
  - with time: *N*_D is proportional to *t*;
  - with binning: proportional to the number of rows binned, *n*_rows, since each binned pixel contributes its own dark charge;
  - with temperature: roughly doubles every 5 to 7 °C (*datasheet*).
- **Size at our operating point.** Scaling the *datasheet* 0 °C range to −13 °C gives roughly **1.7 to 28 e⁻/pixel/s**. Per spectral channel that is multiplied by *n*_rows. For example, with 20 rows binned and a 1000 s exposure the dark signal would be 34,000 to 560,000 e⁻ per channel, and its shot noise 180 to 750 e⁻. The range is wide because the datasheet range is wide; the laser-off measurement in Section 8 replaces it with our unit's value.
- **Temperature stability.** Across Days 1 to 6 the recorded detector temperature varied by 1.9 °C, enough to change the dark current by 20 to 30%. Some archive spectra were recorded at +5 °C, where dark current is 6 to 12 times its −13 °C value. The detector temperature must be logged with every acquisition, and the TEC must be settled before acquiring.
- **Cooling.** From −13 °C to −70 °C the dark current falls by a factor of roughly 300 to 2,700, which is the TIM paper's "roughly three orders of magnitude."
- **Mean versus noise.** The mean dark signal is removed by subtracting a dark frame or the argon reference, which contains it. Dark shot noise is not removed (Section 4.1, consequence 3).
- **Isolated by:** frames taken with the laser blocked, at several integration times, with the detector at its operating temperature.

### 4.5 Read noise

- **What:** the uncertainty added when the charge in a channel is converted to a voltage and sampled. It is quoted in electrons rms.
- **Origin:** the output amplifier, and the reset of the output node between pixels. **Correlated double sampling (CDS)**, which samples the node before and after the charge arrives and takes the difference, removes most of the reset component.
- **Scaling:** fixed **per readout**, independent of *t*. It rises with readout speed.
- **Size:** 8 to 16 e⁻ rms (*datasheet*, under Hamamatsu's conditions; Wasatch's electronics and readout speed will give their own value).
- **Practical consequence:** read noise matters only when the other terms are small, which means short exposures and low backgrounds. At the 2024 operating point (1000 s, thousands of counts of background in the quiet window) it is negligible. It is the term that penalizes co-adding many short frames, because it is paid once per frame (Section 5.3).
- **Isolated by:** a **bias frame**, the shortest possible exposure with the laser blocked. Its frame-to-frame scatter is the read noise.

### 4.6 Quantization noise

- **What:** the rounding error of the ADC. A continuous voltage is recorded as an integer, and the rounding error is uniformly distributed over one count.
- **Size:** 1/√12 ≈ 0.29 counts rms.
- **Practical consequence:** negligible against σ of 54 to 90 counts. Listed for completeness.

### 4.7 Fixed-pattern noise

- **What:** pixel-to-pixel differences that are **the same in every exposure**. These terms do not fluctuate in time, so they are not noise in the statistical sense, but they appear as scatter across the pixels of a single spectrum. **That is how the project measures σ** (Section 7), so they count.
- **Components:**
  - **Dark signal non-uniformity (DSNU):** pixels differ in dark current. It scales with *t* and with temperature.
  - **Photo-response non-uniformity (PRNU):** pixels differ in sensitivity, typically by a fraction of a percent. It scales with the signal level, so it is a fixed percentage of whatever light falls on the pixel.
  - **Hot pixels:** individual pixels with dark current far above the rest. They are stable in position.
  - **Etaloning:** a back-thinned CCD's thin silicon forms a weak optical cavity, producing a fringe pattern in sensitivity that strengthens toward the red. It is generally significant above about 700 nm. Our quiet window, 3718 to 3918 cm⁻¹, falls at 663 to 672 nm and the water band at 660 nm, so it should be checked for rather than assumed.
- **Scaling:** proportional to the signal or dark level, so **proportional to *t***, not √*t*. Averaging frames does not reduce fixed pattern, because every frame carries the same pattern.
- **Reduced by:** subtracting a reference taken under identical conditions (removes DSNU and hot pixels), and dividing by a flat field (removes PRNU and etaloning). We subtract argon but do not flat-field.
- **Isolated by:** comparing the scatter **within** one frame with the scatter **between** repeated frames (Section 7).

### 4.8 Cosmic-ray events

- **What:** charged particles, mostly secondary muons from cosmic rays plus radiation from nearby materials, that deposit charge in a few pixels during the exposure. They appear as sharp spikes one or two channels wide.
- **Rate:** the sea-level muon flux is of order one per cm² per minute. The full active area of the S7031-1006 is about 0.34 cm², giving several hits over the whole chip in a 1000 s exposure. Only hits within the binned rows reach the spectrum.
- **Scaling:** the number of hits is proportional to *t* and to *n*_rows.
- **Practical consequence:** a spike is not Gaussian noise and inflates a standard deviation out of proportion. A spike in a fit window can shift a fitted amplitude. The risk grows with exposure length, which is the argument for splitting a long exposure into several frames and taking their median (Section 5.3).
- **Isolated by:** comparing repeated frames. A spike appears in one frame only.

### 4.9 Fluctuations upstream of the detector

These are not detector noise but they change what the detector records.

- **Laser power and coupling.** These are multiplicative: every Raman band and the laser-induced background scale together. Molar fractions are ratios within one spectrum, so they cancel. They do not cancel in absolute counts, in the scale factor used for argon subtraction, or in any comparison of absolute σ between exposures. Over the 2024 campaign that scale factor varied 2.6-fold. ENLIGHTEN does not control or record the external laser (`Laser Enable` reads False and `Laser Power mW` is blank in every file), so power must be logged from the Ophir PD300 power meter.
- **Spectrograph drift.** Temperature changes inside the spectrometer shift features across pixels. A feature that moves between the reference and the sample leaves a derivative-shaped residual after subtraction, which then behaves like structured noise.
- **Pressure.** Number density, and with it every Raman and Rayleigh signal, scales with absolute pressure.

### 4.10 Noise added or reshaped by processing

The σ quoted in the TIM paper is measured after four processing steps, and each one changes the noise.

- **Argon subtraction**, *I*_corr = *I*_sample − *k* · *I*_argon. This removes the mean background and the fixed pattern common to both frames. It adds the argon frame's own random noise, scaled by *k*: with equal integration times and *k* ≈ 1 the random component grows by up to √2. In the 2024 pipeline *k* is fitted over 3718 to 3918 cm⁻¹, so in that window part of the noise is fitted away and σ there reads low.
- **Regridding** to the standard 5.0 cm⁻¹ axis by linear interpolation. Each output point is a weighted average of two neighbouring pixels. On average this reduces the variance to about two-thirds, a σ about 18% lower than the native pixel noise, and it correlates neighbouring points.
- **Baseline removal by asymmetric least squares (ALS).** ALS fits a smooth curve under the spectrum and subtracts it; λ sets the stiffness and *p* the asymmetry (2024: λ = 10⁹, *p* = 0.001). Structure slower than the baseline is removed; structure faster than the baseline but slower than the noise remains and is counted as noise.
- **Window statistics.** σ estimated from 40 points has a statistical uncertainty of about 11%, before any correlation between points is accounted for.

---

## 5. Putting the terms together

### 5.1 The noise equation

For one spectral channel and one exposure of length *t*, in electrons:

> σ²(e⁻) = *N*_S + *N*_B + *N*_D + σ_R² + σ_FP²

| Symbol | Meaning | Scales with *t* as |
|---|---|---|
| *N*_S | signal electrons (its own shot-noise variance) | *t* |
| *N*_B | background electrons (shot-noise variance) | *t* |
| *N*_D | dark electrons, = *n*_rows · *D*(*T*) · *t* (shot-noise variance) | *t* |
| σ_R | read noise, per readout | constant |
| σ_FP | fixed-pattern and structured background, as seen across channels | *t* (so σ_FP² goes as *t*²) |

In counts, multiply σ(e⁻) by *G* and add the quantization variance, 1/12.

The signal-to-noise ratio of a band is

> SNR = *N*_S,peak / σ

where *N*_S,peak is the signal at the band maximum.

### 5.2 Regimes and the dependence on integration time

Whichever term dominates σ sets how σ responds to *t*. There are two ways to plot this, and **the two give slopes of opposite sign**, so any criterion must state which is meant.

| Dominant term | σ in counts goes as | slope of log σ vs log *t* | σ relative to signal (σ / *t*) goes as | slope | SNR goes as |
|---|---|---|---|---|---|
| Read noise | *t*⁰ | 0 | *t*⁻¹ | −1 | *t* |
| Shot noise (signal, background or dark) | *t*^½ | +0.5 | *t*^−½ | −0.5 | √*t* |
| Fixed pattern or structured background | *t* | +1 | *t*⁰ | 0 | constant |

Reading the table:

- In the **shot-noise regime**, doubling *t* improves SNR by √2. The 2024 analysis assumed this regime when it rescaled Day 1 (500 s) to the 1000 s basis.
- In the **fixed-pattern regime**, longer integration buys nothing: noise and signal grow together. The only remedy is to remove the structure, by better references, flat-fielding or row selection.
- At **short times** a read-noise-dominated σ gives the steepest relative slope. A steep slope at the short end of a series has this physical cause before it is attributed to processing.
- A real instrument moves between regimes as *t* changes: typically read-noise-limited at the shortest times, shot-noise-limited in the middle, and fixed-pattern-limited at the longest. The break points between regimes are the result the characterization is after.

### 5.3 One long exposure or several short ones

A total time *T* can be acquired as one exposure or as *M* frames of *T*/*M* that are combined afterwards.

- **Shot noise and dark signal** are identical either way: the same total charge is collected.
- **Read noise** is paid *M* times, so its variance is *M*·σ_R². With σ_R = 16 e⁻ and *M* = 6 that is 39 e⁻ rms in total, small against shot noise of hundreds of electrons.
- **Cosmic-ray spikes** can be rejected only when frames exist: the median of *M* frames ignores a spike present in one of them. The median is noisier than the mean by about 25% for Gaussian noise when *M* is large, less for small *M*.
- **Saturation** is less likely in short frames.
- **Fixed pattern** is identical either way.

### 5.4 Saturation

A spectral channel saturates when the binned charge exceeds the horizontal-register full well (800 to 1000 ke⁻, *datasheet*), or when the count exceeds the ADC ceiling, whichever comes first. Dark charge, background and signal all fill the well, so long exposures with many rows binned at a warm detector temperature approach the limit even on an empty spectrum. Response becomes non-linear before hard saturation. The largest value in the 2024 Day 2 spectrum is 43,834 counts.

---

## 6. Summary

| Term | Origin | Variance scales with *t* | Depends on temperature | Grows with rows binned | Reduced by averaging frames | Removed by subtracting a reference | Isolated by |
|---|---|---|---|---|---|---|---|
| Signal shot noise | photon statistics | *t* | no | no | no (same total charge) | no | (sets the SNR ceiling) |
| Background shot noise | silica Raman, fluorescence, stray light, elastic leakage | *t* | weakly | yes, if rows lie outside the fiber image | no | mean only | argon, laser on; two pressures for elastic |
| Dark shot noise | thermal generation | *t* | strongly, ×2 per 5 to 7 °C | yes | no | mean only | laser-off series |
| Read noise | output amplifier | constant per readout | weakly | no, if binned on chip | no; grows with frame count | no | bias frames |
| Quantization | ADC rounding | constant | no | no | no | no | (negligible) |
| Fixed pattern (DSNU, PRNU, etaloning, hot pixels) | pixel non-uniformity | *t*² | DSNU strongly | yes | **no** | DSNU and hot pixels yes; PRNU needs a flat field | within-frame vs between-frame scatter |
| Cosmic rays | particles | number of hits ∝ *t* | no | yes | median rejects them | no | repeated frames |
| Laser and coupling fluctuation | source | multiplicative | (laser) | no | partly | no | power meter log |
| Spectrograph drift | thermal | structured | yes | no | no | leaves derivative residual | repeated references |
| Processing | argon subtraction, regrid, ALS | as the inputs | no | no | n/a | n/a | process with and without each step |

---

## 7. What "σ" means in our work

The TIM paper defines σ as **the standard deviation of the baseline-corrected residuals across the 40 points of the 3718 to 3918 cm⁻¹ window, in one spectrum.** Four properties follow from that definition and are easy to lose sight of.

1. **σ is a spread across channels, not a spread over time.** It contains every random term **and** every fixed-pattern term and every residual of unremoved structure in the window. A spread over time, the scatter of one channel across repeated frames, contains only the random terms.
2. **Comparing the two separates random from structured noise.** Take two frames under identical conditions and difference them. The fixed pattern cancels, and the scatter of the difference divided by √2 is the temporal noise of one frame. If σ across channels is close to that temporal value, the window is limited by random noise. If σ across channels is larger, the excess is structure, and longer integration will not remove it.
3. **σ is window-specific.** It describes a weak band on an empty background. A band sitting under or beside a strong feature sees the strong feature's shot noise and its fitting residual in addition (Section 4.2). That is why a σ from the quiet window is not the noise relevant to bands in a crowded region such as the C–H stretching region near 2800 to 3000 cm⁻¹.
4. **σ is in counts after processing.** Converting it to electrons needs *G*, and comparing it with a detector specification needs the processing effects of Section 4.10 taken into account.

**A consistency check that the measurement in Section 8 will settle.** In the 2024 data the quiet window sits at about 8,000 to 8,600 counts in both the argon reference and the Day 2 spectrum, and σ on Day 2 was 89.8 counts. If that window were limited purely by shot noise, σ² would equal *G* times the level in counts, which gives *G* ≈ 1 count/e⁻. That value is not implausible, but it rests on two unverified assumptions pulling in opposite directions: an electronic offset would make the true level lower, and fixed pattern would make σ larger. Measuring *G* directly decides whether the 2024 floor was shot-limited or structure-limited.

---

## 8. Measurements that isolate each term

These are the minimum set of acquisitions for building the noise budget from measurement rather than from the datasheet. Each takes the instrument exactly as it will be deployed.

| Acquisition | Laser | Gas | Gives |
|---|---|---|---|
| Bias frames, shortest *t*, repeated | blocked | any | electronic offset; read noise from frame-to-frame scatter |
| Dark series, several *t*, repeated pairs | blocked | any | dark current per channel at the operating temperature (slope of level vs *t*); DSNU; hot pixels |
| **Photon transfer curve**: pairs of identical frames at several light levels | on | argon | conversion gain *G*. Difference each pair to cancel fixed pattern; the variance of the difference divided by 2, plotted against mean level, has slope *G* in the shot-noise regime |
| Argon, two pressures | on | argon | laser-induced background level and shot noise; elastic leakage from the pressure difference |
| Repeated frames under one condition | on | any | temporal noise vs spatial σ (Section 7); cosmic-ray rate |
| Strong band inside the target window | on | a non-condensing gas with a band in that window | penalty for working beside a strong band |

---

## 9. Records and open items

### Record with every acquisition

Gas, absolute pressure, integration time, number of frames, detector temperature (from the header), TEC setpoint, coupled laser power from the PD300 before and after, hall temperature, timestamp, and the ENLIGHTEN settings: gain, offset, horizontal ROI, vertical binning rows, scan averaging, boxcar, dark subtraction, baseline correction, intensity correction.

### Open items to settle before measuring

1. **Vertical binning rows.** Which of the 58 rows are summed into each channel is not written to the CSV. It sets the dark signal, the cosmic-ray rate and the background collected outside the fiber image. Read it from the spectrometer's configuration and record it.
2. **Conversion gain *G*.** It has never been measured. Determine it from the photon transfer curve.
3. **ENLIGHTEN processing flags.** The Day 2 file records `Baseline Correction Algo,ALS` and `Deconvolved,True`; the argon file records `None` and `True`. Whether ENLIGHTEN altered the saved intensities before they were written must be established, because a baseline correction or deconvolution applied at capture changes the noise in the saved data. For the new campaign, every processing option in ENLIGHTEN should be off and confirmed off in the header.
4. **ADC ceiling and readout rate.** Confirm the converter's bit depth (and so the count ceiling) and the pixel readout rate with Wasatch; read noise depends on the rate.
5. **Etaloning.** Check whether the 650 to 700 nm region carries a fringe pattern, by inspecting the argon and dark frames for periodic structure.

---

## Sources

- Hamamatsu Photonics, *CCD area image sensor S7030/S7031 series, back-thinned FFT-CCD*, datasheet KMPD1023E. https://www.hamamatsu.com/content/dam/hamamatsu-photonics/sites/documents/99_SALES_LIBRARY/ssd/s7030-0906_etc_kmpd1023e.pdf
- Wasatch Photonics, *Wasatch.PY settings reference* (gain register, vertical binning, ROI). https://github.com/WasatchPhotonics/Wasatch.PY/blob/master/README_SETTINGS.md
- A. Knoesen *et al.*, "Hollow-Core Fiber-Enhanced Raman Instrument for Standard-Free Multicomponent Gas Analysis in Industrial Process Environments," *IEEE Trans. Instrum. Meas.*, vol. 75, 2026, Art. no. 7006218, doi:10.1109/TIM.2026.3731740. Sections II-A, III-A, IV-B, VI-B and VI-C.
- ENLIGHTEN headers of the 2024 deployment spectra, `IEEE Fermentation\Archive_TIM-26-07018\data\02_curated_spectra\` and `01_raw_spectrometer\`.
