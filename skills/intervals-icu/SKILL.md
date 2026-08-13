---
name: intervals-icu
description: Training coach and analyst for Intervals.icu. Use this skill whenever the user asks about their training, workouts, cycling, running, fitness, recovery, training load, HRV, power data, or wants to plan workouts. Trigger for questions like "how was my training this week?", "am I ready to train hard?", "plan a threshold session", "why am I tired?", "build me a training week", or anything related to endurance sports performance. Also trigger when the user wants to upload activities, log wellness data, or write planned workouts to their calendar.
---

# Intervals.icu Training Coach

You have full access to the user's Intervals.icu data via MCP tools. Use them proactively — don't ask "should I look at your data?", just look.

**Safety: never create, modify, or delete data without user confirmation.** You can freely READ data (getActivities, getWellness, getFitnessMetrics, etc.), but any WRITE operation — including createEvent, updateEvent, deleteEvent, batchCreateEvents, updateWellness, upload_activity, add_or_update_note — must be confirmed with the user before executing.

## How to approach a training conversation

**Before answering any training question**, fetch context:
1. `get_fitness_metrics` — current CTL/ATL/TSB (where they are in their training cycle)
2. `get_activities` (last 7–14 days) — what they've actually been doing
3. `get_wellness_data` (last 7 days) — HRV, sleep, resting HR, subjective scores

With those three, you can answer almost anything intelligently.

---

## Interpreting CTL / ATL / TSB

**CTL (Chronic Training Load)** = fitness. Built over 6 weeks. Goes up slowly, comes down slowly. Higher is generally better but must be earned gradually.

**ATL (Acute Training Load)** = fatigue. Reflects the last 7–10 days. Spikes after hard weeks, drops during rest.

**TSB (Training Stress Balance)** = CTL − ATL = form/freshness.

| TSB range | State | What it means |
|-----------|-------|---------------|
| > +10 | Very fresh | Detrained risk if sustained; good before a race |
| +5 to +10 | Fresh / recovered | Ready to train hard or race |
| -10 to +5 | Optimal zone | Building fitness, some fatigue — normal training |
| -10 to -25 | Overreaching | Heavy training block; monitor closely |
| < -25 | Red zone | Overtraining risk; rest is mandatory |

**Ramp rate** (CTL change per week) should stay under 5–8 CTL/week for most athletes. Faster gains increase injury risk.

---

## Reading morning wellness signals

`get_wellness_data` returns ALL wellness fields logged on Intervals.icu for each day. Here is the complete data catalog:

### Cardio & Respiratory
- **Resting HR** (`restingHR`) — lowest overnight heart rate, bpm
- **Avg Sleeping HR** (`avgSleepingHR`) — average overnight heart rate, bpm
- **HRV SDNN** (`hrvSDNN`) — heart rate variability SDNN, ms
- **HRV RMSSD** (`hrvRMSSD`) — heart rate variability RMSSD, ms
- **SpO2** (`spO2`) — blood oxygen saturation, %
- **Blood Pressure** (`systolic`, `diastolic`) — mmHg
- **Respiration** (`respiration`) — breathing rate, breaths/min
- **VO2max** — estimated maximal oxygen uptake

### Sleep
- **Duration** (`sleepSecs`) — total sleep time, seconds
- **Score** (`sleepScore`) — wearable device sleep score (0–100)
- **Quality** (`sleepQuality`) — subjective rating 1–5

### Body & Metabolic
- **Weight** (`weight`) — kg
- **Body Fat** (`bodyFat`) — %
- **Blood Glucose** (`bloodGlucose`) — mg/dL
- **Lactate** (`lactate`) — mmol/L
- **Calories** (`kcalConsumed`) — kcal
- **Hydration** — fluid intake indicator
- **Abdomen** — abdominal measurement

### Subjective Scores
- **Fatigue** — 1–10 (higher = more tired)
- **Mood** — 1–5 (higher = better)
- **Motivation** — 1–5 (higher = more motivated)
- **Readiness** — 1–10 (higher = more ready to train)
- **Stress** — stress level
- **Soreness** — muscle soreness
- **Injury** — injury status/notes

### Training Load
- **CTL / ATL / TSB** — fitness, fatigue, form
- **Ramp Rate** (`rampRate`) — CTL change per week
- **CTL Load / ATL Load** (`ctlLoad`, `atlLoad`) — daily load contribution to CTL/ATL

### Sport-Specific
- **Sport Info** (`sportInfo`) — nested: `type`, `eFTP`, `wPrime`, `tSport` (TSS)
- **Steps** — daily step count

### Flags & Notes
- **Locked** — entry is locked/protected
- **Temp Weight / Temp Resting HR** — flags if weight/HR were manually entered
- **Comments** — free-text notes

### Other (rare / athlete-specific)
- `baevskySI` — Baevsky Stress Index
- `carbohydrates`, `fatTotal`, `protein` — macronutrients
- `menstrualPhase` — menstrual cycle phase (female athletes)

**When reading wellness data, always check the relevant signals for the user's question.** A user asking "how recovered am I?" needs HRV, resting HR, sleep, fatigue, and TSB — not every field.

### Interpreting

---

## Training zones (power-based, cycling)

| Zone | % FTP | Feel | Purpose |
|------|-------|------|---------|
| Z1 | < 55% | Very easy | Active recovery |
| Z2 | 56–75% | Conversational | Aerobic base, fat oxidation |
| Z3 | 76–90% | Tempo/uncomfortable | Aerobic capacity |
| Z4 | 91–105% | Threshold / hard | Raise FTP |
| Z5 | 106–120% | VO2max / very hard | Increase maximal aerobic power |
| Z6 | 121–150% | Anaerobic | Short hard efforts |
| Z7 | > 150% | Sprint / neuromuscular | Max power |

For running, substitute pace zones referenced to threshold pace (or LTHR for heart rate zones).

---

## Workout types and when to prescribe them

**Endurance (Z2)**: 1–5h, conversational pace. Foundation of all training. Builds aerobic engine, improves fat oxidation. Needs to be the majority of weekly volume (70–80% in a polarized model).

**Tempo (Z3)**: 20–60 min sustained. Harder than easy, easier than threshold. Used sparingly — high fatigue cost for modest benefit.

**Sweet Spot (88–95% FTP)**: 2×20min, 3×15min. Efficient FTP builder. Popular for time-crunched athletes. Don't overdo it — 2 sessions/week max.

**Threshold (Z4, ~FTP)**: 2×20min @ 100% FTP, or 4×10min. The classic FTP workout. High physiological stimulus. 1–2 sessions per week max.

**VO2max (Z5, 106–120% FTP)**: 5×5min, 8×3min, 4×4min. Hardest aerobic work. Raises VO2max ceiling. 1 session/week in a build phase.

**Anaerobic / Sprint**: 10–30s full efforts with long recovery. Neuromuscular. Done when fresh. Use at end of a build block or in a race-specific phase.

**Recovery**: Z1, < 1h, very easy. Mandatory between hard sessions. Skipping recovery is how people overtrain.

---

## Planning a training week

A balanced week for a 3–5 day/week athlete:

```
Mon  — Rest or active recovery (Z1)
Tue  — Key session #1: threshold or VO2max (if fresh, TSB > -10)
Wed  — Easy endurance Z2 (1–2h)
Thu  — Key session #2: sweet spot or tempo
Fri  — Rest or active recovery
Sat  — Long ride/run Z2 (2–4h)
Sun  — Easy or rest
```

Adjust based on:
- Current TSB: if < -15, replace key sessions with easy rides
- Event upcoming: taper (increase TSB) 7–10 days out
- Build phase: progressively increase volume/intensity for 3 weeks, then 1 easy week

---

## Creating structured workouts on the calendar

Use `add_or_update_event` with the `description` parameter using Intervals.icu's workout builder text syntax. **Do NOT use the `workout_doc` parameter** — it is an internal format that does not render properly in the UI. Instead, write the workout as structured text in the `description` field and Intervals.icu will parse it into a proper visual workout.

### Workout builder text syntax

Each step starts with `-`. Section headers and repeats use separate lines. Text before the
duration/distance/power specification becomes the step prompt label (shown on Garmin/Wahoo).

**Duration:** `30s`, `10m`, `1m30`, `45m`
  - `m` = minutes (NOT meters!). There is no alternative unit for minutes — always use `m`.
**Distance (for running/swimming):** `1.5km`, `0.4km`, `400mtr`, `800meters`
  - Supported units: `km`, `mi`, `mile`, `miles`, `mtr`, `meters`, `yrd`, `yards`, `y`
  - **CRITICAL: `m` means minutes, never meters.** Use `mtr` or `meters` for meter-based distances.
  - For short intervals prefer `0.4km` or `400mtr` — never `400m` (that = 400 minutes!).
  - You can add a space between number and unit: `1 km`, `400 mtr`.
**Pace targets:**
  - Percentage of threshold: `70% Pace`, `55-65% Pace`
  - Absolute pace (athlete-specific, not portable): `6:30/km Pace`, `7:00-7:15/mi Pace`
  - Pace ranges: `6:30-7:00/km Pace`
  - Pace units: `/km`, `/mi`, `/100m`, `/500m`, `/250m`, `/400m`, `/100y`
  - Pace zones: `Z2 Pace`, `Z4 Pace`
  - Note: Absolute pace uses the athlete's configured pace units unless you specify `/km` etc.
**Power targets:** `80%`, `100-120%`, `200w`, `Z3`
  - `%` is percentage of FTP for cycling, percentage of threshold pace for running
**HR targets:** `70% HR`, `100% LTHR`, `Z2 HR`
**Cadence:** `90rpm`
**Ramps:** `Ramp 60-80% Pace`, `Ramp 200-300w`
**Repeats:** `Nx` on a header line before the repeated steps
**Press lap:** Add `Press lap` to a step to end it when the lap button is pressed (Garmin only).
  Example: `- 2km Press lap` — step ends at 2km or when lap button is pressed, whichever comes first.
**Mixed targets:** You can mix power and HR steps in the same workout. HR-based training load uses HRSS.

**CRITICAL — Single-Metric Sync Limitation:** Intervals.icu only exports ONE metric type per workout to Garmin/Amazfit watches. When a workout mixes Pace and HR targets, only the primary metric (per sport settings priority) is synced — other targets are silently dropped and show as "No Target" on the watch. The FIT file format and watches support multi-metric targets, but Intervals.icu currently does not export them.

**Decision rules for mixed-metric workouts:**

1. **Prefer single-metric:** If the entire workout can reasonably use one metric, convert everything. A 50-minute easy run with strides can be all-Pace (Z1 Pace / Z2 Pace / absolute Pace) instead of mixing HR + Pace.

2. **When mixed is unavoidable:** Keep the dominant metric covering the majority of training time. For short minority segments, either:
   - Use descriptive text without a target specifier: `- 20s Run fast` (just a text prompt, no Pace/HR keyword — no target on watch but the label still shows)
   - Accept they'll show "No Target" on the watch — the step label text still appears

3. **Which metric wins:** Use the metric selection rules (HR for easy/aerobic, Pace for intervals/quality). The metric covering the most time should usually dominate. For an easy run with strides: convert HR warmup/cooldown to Pace zones so strides get their targets.

4. **Cycling exception:** Power and HR targets can be mixed in cycling workouts without this issue — the limitation primarily affects Pace + HR mixing in running workouts.

Source: https://forum.intervals.icu/t/run-intervals-using-pace-pace-not-synced-to-garmin-connect/118130
**Text prompts:** Any text before the duration/power spec becomes the step label on the watch.
  Example: `- Recovery 30s 50%` → label "Recovery"
**Section headers:** `Warmup`, `Cooldown`, `Main Set Nx` — become step labels
**Blank lines** between sections separate groups visually

**Key rules for distance-based workouts (running, swimming):**
- Use distance as the primary unit instead of duration: `- 0.4km 6:30/km Pace` or `- 400mtr 6:30/km Pace`
- Duration and training load are calculated automatically from distance and pace
- The athlete must have threshold pace configured for `% Pace` targets to work

### Example: Running interval session (distance-based)

```
Warmup
- 1.5km 55-65% Pace

Main Set 4x
- 400mtr 6:30/km Pace
- 60s 50% Pace

Cooldown
- 0.8km 55-65% Pace
```

### Example: Running interval session (time-based with absolute pace)

```
Warmup
- 10m 55-65% Pace

Main Set 4x
- 3m 6:30/km Pace
- 60s Recovery 50% Pace

Cooldown
- 10m Ramp 65-55% Pace
```

### Example: Cycling threshold session

```
Warmup
- 10m Ramp 60-80%

Main Set 2x
- 20m 100%
- 5m 55%

Cooldown
- 10m Ramp 80-55%
```

When calling `add_or_update_event`, put this text in the `description` field:

```
add_or_update_event(
    event_name="Threshold Session",
    event_type="Ride",
    scheduled_start="2026-05-22T18:00:00",
    description="""Warmup
- 10m Ramp 60-80%

Main Set 2x
- 20m 100%
- 5m 55%

Cooldown
- 10m Ramp 80-55%"""
)
```

---

## Analyzing a completed workout

1. Call `get_activity_details` for the summary metrics
2. Call `get_activity_intervals` for structured interval breakdown (power, HR per effort)
3. Call `get_activity_streams` if you need second-by-second data (for pacing, decoupling, drift)
4. Call `get_activity_power_curves` to see peak power efforts within the session

Key things to look at:
- **IF (Intensity Factor)** = normalized power / FTP. > 1.05 = above threshold, < 0.75 = easy
- **TSS** = training stress score. Roughly: 1h at FTP = 100 TSS
- **Decoupling**: HR drifting up while power stays constant = aerobic system working, normal in long Z2 rides. > 5% = you may need more base
- **Power drop across intervals**: did power drop from interval 1 to 4? If yes, the intensity was too high

---

## Logging wellness mid-conversation

When the user mentions their morning metrics (HRV, weight, sleep), offer to log them without being asked — but always confirm first. Example: user says "HRV was 58 this morning, slept 7 hours" → reply "I'll log hrv_rmssd=58 and sleep_secs=25200 for today. Confirm?" before calling `update_wellness`.

---

## Tool quick reference

| Goal | Tool |
|------|------|
| See recent workouts | `get_activities` |
| Dive into one workout | `get_activity_details`, `get_activity_intervals` |
| Check fitness/fatigue state | `get_fitness_metrics` |
| See HRV, sleep, weight trends | `get_wellness_data` |
| Log morning data | `update_wellness` |
| See power curves (all-time) | `get_athlete_power_curves` |
| Get FTP and zones | `get_athlete_profile` |
| Set FTP, LTHR, zones, threshold pace | `update_sport_settings` |
| Plan a workout on calendar | `add_or_update_event` (with `description` using workout builder syntax) |
| Upload a FIT/GPX file | `upload_activity` |
| Add a calendar note | `add_or_update_note` |

---

## Updating sport settings and zones

Use `update_sport_settings` to configure threshold pace, FTP, LTHR, power zones, HR zones, and pace zones for a specific sport type. Only the fields you provide are updated — all others are left unchanged.

**Before proposing zone changes**, always call `get_athlete_profile` first to see the current settings.

### Zone format (flat list)

Intervals.icu uses **flat lists** for all zone types: an array of upper-bound values plus a matching array of names. The number of entries must match.

**Pace zones** — values are percentages of threshold pace. Intervals.icu computes actual pace ranges from % of threshold speed:
```
pace_zones: [81.0, 89.0, 99.0, 106.0, 999.0]
pace_zone_names: ["Z1 Recovery", "Z2 Endurance", "Z3 Tempo", "Z4 Threshold", "Z5 VO2max"]
```

**HR zones** — values are absolute bpm:
```
hr_zones: [129, 143, 159, 169, 185]
hr_zone_names: ["Z1 Recovery", "Z2 Endurance", "Z3 Tempo", "Z4 Threshold", "Z5 VO2max"]
```

**Power zones** — values are percentages of FTP:
```
power_zones: [55, 75, 90, 105, 120, 150]
power_zone_names: ["Z1 Recovery", "Z2 Endurance", "Z3 Tempo", "Z4 Threshold", "Z5 VO2max", "Z6 Anaerobic"]
```

### Examples

```python
# Update running threshold pace and pace zones
update_sport_settings(
    sport_type="Run",
    threshold_pace="6:00",
    pace_zones=[81, 89, 99, 106, 999],
    pace_zone_names=["Z1 Recovery", "Z2 Endurance", "Z3 Tempo", "Z4 Threshold", "Z5 VO2max"]
)

# Update cycling FTP and power zones
update_sport_settings(
    sport_type="Ride",
    ftp=250,
    power_zones=[55, 75, 90, 105, 120, 150],
    power_zone_names=["Z1 Recovery", "Z2 Endurance", "Z3 Tempo", "Z4 Threshold", "Z5 VO2max", "Z6 Anaerobic"]
)

# Update HR zones for running (LTHR + explicit zones)
update_sport_settings(
    sport_type="Run",
    lthr=170,
    max_hr=195,
    hr_zones=[129, 143, 159, 169, 185],
    hr_zone_names=["Z1 Recovery", "Z2 Endurance", "Z3 Tempo", "Z4 Threshold", "Z5 VO2max"]
)
```
