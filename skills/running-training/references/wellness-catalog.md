# Complete Wellness Data Catalog (Intervals.icu)

Use `get_wellness_data` to fetch daily wellness data. This catalog documents every field
that Intervals.icu may return. When a user asks about a specific metric (HRV, sleep, RHR,
readiness, etc.), check this catalog to understand the field names and interpretation.

> **Reading tip:** Only fetch/display the fields relevant to the user's question — not every
> field. A user asking "how recovered am I?" needs HRV, resting HR, sleep, fatigue, and TSB
> — not the entire catalog.

## Cardio & Respiratory

| Field | Key | Unit | Notes |
|-------|-----|------|-------|
| Resting HR | `restingHR` | bpm | Lowest overnight heart rate |
| Avg Sleeping HR | `avgSleepingHR` | bpm | Average overnight heart rate |
| HRV SDNN | `hrvSDNN` | ms | Heart rate variability, SDNN |
| HRV RMSSD | `hrvRMSSD` | ms | Heart rate variability, RMSSD |
| SpO2 | `spO2` | % | Blood oxygen saturation |
| Systolic BP | `systolic` | mmHg | Systolic blood pressure |
| Diastolic BP | `diastolic` | mmHg | Diastolic blood pressure |
| Respiration | `respiration` | breaths/min | Breathing rate |
| VO2max | `vo2max` | ml/kg/min | Estimated maximal oxygen uptake |

## Sleep

| Field | Key | Unit | Notes |
|-------|-----|------|-------|
| Duration | `sleepSecs` | seconds | Total sleep time |
| Score | `sleepScore` | 0–100 | Wearable device sleep score |
| Quality | `sleepQuality` | 1–5 | Subjective rating |

## Body & Metabolic

| Field | Key | Unit | Notes |
|-------|-----|------|-------|
| Weight | `weight` | kg | Body weight |
| Body Fat | `bodyFat` | % | Body fat percentage |
| Blood Glucose | `bloodGlucose` | mg/dL | Blood sugar |
| Lactate | `lactate` | mmol/L | Blood lactate |
| Calories | `kcalConsumed` | kcal | Calorie intake |
| Hydration | `hydration` | — | Fluid intake indicator |
| Abdomen | `abdomen` | — | Abdominal measurement |

## Subjective Scores

| Field | Key | Range | Notes |
|-------|-----|-------|-------|
| Fatigue | `fatigue` | 1–10 | Higher = more tired |
| Mood | `mood` | 1–5 | Higher = better |
| Motivation | `motivation` | 1–5 | Higher = more motivated |
| Readiness | `readiness` | 1–10 | Higher = more ready to train |
| Stress | `stress` | — | Stress level |
| Soreness | `soreness` | — | Muscle soreness |
| Injury | `injury` | — | Injury status/notes |

## Training Load

| Field | Key | Notes |
|-------|-----|-------|
| CTL / ATL / TSB | `ctl`, `atl`, `tsb` | Fitness, fatigue, form |
| Ramp Rate | `rampRate` | CTL change per week |
| CTL Load / ATL Load | `ctlLoad`, `atlLoad` | Daily load contribution |

## Sport-Specific

| Field | Key | Notes |
|-------|-----|-------|
| Sport Info | `sportInfo` | Nested: type, eFTP, wPrime, tSport (TSS) |
| Steps | `steps` | Daily step count |

## Flags & Notes

| Field | Key | Notes |
|-------|-----|-------|
| Locked | `locked` | Entry is locked/protected |
| Temp Weight | `tempWeight` | Manually entered weight flag |
| Temp Resting HR | `tempRestingHR` | Manually entered HR flag |
| Comments | `comments` | Free-text notes |

## Other (rare / athlete-specific)

- `baevskySI` — Baevsky Stress Index
- `carbohydrates`, `fatTotal`, `protein` — Macronutrients
- `menstrualPhase` — Menstrual cycle phase (female athletes)
