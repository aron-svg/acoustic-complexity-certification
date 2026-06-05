# Psychoacoustic Annoyance Analyzer (`sound_analysis.py`)

This project implements an audio signal analysis tool based on **psychoacoustics** to evaluate the global annoyance index of a noise for the human ear. Unlike traditional decibel ($dB$) measurements, this tool leverages human auditory perception models to quantify the actual discomfort felt by the brain.

---

## 1. Theoretical Foundations & Literature Review

### The Decibel ($dB$) Paradox
In environmental or industrial acoustics, the classic measurement of A-weighted sound pressure level ($dB(A)$) quickly reaches its limits. The human ear is not a simple microphone: it processes frequencies and time non-linearly. Two noises with the exact same decibel level can trigger completely opposite psychological reactions (for example, the sound of ocean waves at 60 dB vs. a chalk screeching on a blackboard at 60 dB).

### The Zwicker & Fastl Annoyance Model
To bridge the gap between physics and perception, acousticians **Eberhard Zwicker** and **Hugo Fastl** developed the **Psychoacoustic Annoyance** index (denoted as $PA$). This mathematical model merges several dimensions of human perception into a single composite equation.

The fundamental equation of the model is expressed as follows:

$$PA = N_5 \left( 1 + \sqrt{w_S^2 + w_{FR}^2} \right)$$

Where each term captures a specific dimension of the sensory experience:

#### 1. Peak Loudness ($N_5$) — The Volume Effect
**Loudness** (expressed in *Sones*) represents the sensation of sound volume intensity. The model uses the 95th percentile ($N_5$), meaning the loudness level that is exceeded only 5% of the time. This gives greater weight to impulsive noises (noise peaks) rather than a linear average, as the human brain naturally focuses on sudden sound emergences.

#### 2. Sharpness Factor ($w_S$) — The High-Frequency Effect
**Sharpness** (expressed in *Acums*) evaluates the spectral balance of the sound. The more high frequencies (treble) a sound contains, the more "sharp" and aggressive it is perceived. The model applies a penalty only if the critical threshold of $1.75\text{ acum}$ is crossed:

* If $S > 1.75$:  $w_S = (S - 1.75) \cdot \ln(N_5 + 2)$
* If $S \le 1.75$:  $w_S = 0$

#### 3. Vibration Factor ($w_{FR}$) — The Modulation Effect
This factor combines **Roughness** ($R$, in *Asper*) and **Fluctuation Strength** ($F$, in *Vacil*). The human brain is hardwired to detect variations in its environment. A sound that vibrates or undergoes rapid micro-impacts saturates human attention and generates neurological fatigue:

$$w_{FR} = \sqrt{(0.3 \cdot R)^2 + (0.05 \cdot F)^2}$$

*(Note: In the standard short-term implementation, the slow fluctuation strength $F$ is often set to 0, as the rapid temporal roughness $R$ dominates the mechanical annoyance sensation).*

---

## 2. Results Interpretation Guide ($PA$)

The $PA$ index is a dimensionless value. Unlike decibels, the scale starts at 0 (absolute silence or total absence of annoyance) and theoretically has no upper limit, although the most extreme man-made noises rarely exceed 100.

### Annoyance Evaluation Grid

| $PA$ Score | Classification | Human Perception | Concrete Examples |
| :--- | :--- | :--- | :--- |
| **0 – 4** | **Negligible** | Passive background noise, almost imperceptible or relaxing. | Inside a quiet library, a whisper, a high-end silent dishwasher. |
| **4 – 12** | **Low** | Perceptible noise but easily tolerated by the mind. | Quiet open-space office, gentle ventilation, light rain. |
| **12 – 25** | **Moderate to Significant** | The noise commands attention. Impossible to ignore during intellectual work. Long-term fatigue. Continuous urban road traffic, busy restaurant, vacuum cleaner in an adjacent room. |
| **25 – 60** | **High** | Characterized noise aggression. Immediate annoyance, conversation becomes difficult. | Vacuum cleaner at 1m, lawnmower, train passing nearby. |
| **60+** | **Extreme** | Critical pain and tolerance threshold. Risk of immediate psychological and physiological stress. | Hammer drill in concrete, jet engine at takeoff. |

### Energy vs. Textural Diagnosis Matrix
To understand **why** a sound gets a specific score (e.g., a score of 17.71), you need to look at its individual components:

* **"Volume" Diagnosis (High $N_5$, Low $S$ and $R$):** The sound is annoying simply because it is loud. This is typical of a heavy but stable industrial ventilation system or a distant waterfall rumble. Standard acoustic insulation is usually enough to fix this.
* **"Aggressiveness" Diagnosis (Moderate $N_5$, High $S$ or $R$):** This is the psychoacoustic trap. The overall volume isn't very high, but the presence of micro-vibrations/roughness ($R$) or high-pitched hissing ($S$) causes the annoyance index to skyrocket. Examples include a mosquito flying near your ear or a squeaking brake pad.

---

## 3. Installation and Configuration

The analysis relies on the open-source **MOSQITO** framework (Modular Sound Quality Integrated Toolbox), developed to standardize industrial sound quality calculations.

### Prerequisites
Ensure you have Python 3.8+ installed.

### Installing Dependencies
Install the required packages via your terminal:

```bash
pip install numpy scipy mosqito librosa
```

---

## 4. Technical Limitations & Best Practices

To guarantee the scientific validity of your measurements, make sure to respect the following constraints:

1.  **The Calibration Constraint:** By default, the script processes the relative digital data from the `.wav` file. The computer does not natively know your microphone's gain or the physical distance from the source. To get absolute, highly accurate *Sone* values, the digital signal must be calibrated beforehand using a hardware acoustic calibrator (pistonphone) to map digital amplitude to a real pressure in Pascals.
2.  **Sampling Rate:** If your source file is not encoded in **48 000 Hz**, MOSQITO will automatically apply software resampling. While functional, software resampling can slightly smooth out rapid micro-variations in Roughness. Prioritize native 48 kHz recordings whenever possible.
3.  **The MP3 Format:** Avoid using lossy, compressed formats. The MP3 standard intentionally discards acoustic masking data and low-pass filters high frequencies to save storage space. Feeding an MP3 file into this script will **systematically underestimate Roughness ($R$) and Sharpness ($S$)**, artificially dragging down the overall annoyance index. Always use uncompressed formats (`.wav`, `.flac`).
