# Workout Analytics Guide

## Reading a completed run in Intervals.icu

When analyzing a completed activity, fetch these endpoints:
- `get_activity_detail` — summary stats
- `get_activity_intervals` — interval breakdown (if structured)
- `get_activity_streams` (optional) — second-by-second power/HR/pace data

---

## Key metrics explained

### TSS (Training Stress Score)

**What it is:** A composite measure of how much training stress the workout imposed.
**Formula (pace/HR based):** `TSS = (duration_hrs × NGP × IF²) × 100`
**Formula (power based):** `TSS = (duration_sec × NP × IF) / (FTP × 3600) × 100`

**Expected ranges:**
| Workout | TSS |
|---------|-----|
| Easy 30 min | 20–35 |
| Easy 60 min | 40–60 |
| Tempo 40 min + WU/CD | 70–90 |
| VO2max intervals (with WU/CD) | 80–110 |
| Long run 2 hr | 90–130 |
| Long run 3 hr | 140–180 |
| Half marathon race | 120–160 |
| Marathon race | 200–280 |

---

### Intensity Factor (IF)

**Formula:** `IF = NP (or NGP) / FTP (or CP)`
**What it means:** What fraction of your functional threshold the workout required, on average weighted by effort.

| IF range | Workout type |
|---------|-------------|
| 0.5–0.75 | Easy/recovery |
| 0.75–0.85 | Aerobic endurance / long run |
| 0.85–0.95 | Tempo |
| 0.95–1.05 | Threshold |
| 1.05–1.20 | VO2max |
| >1.20 | Anaerobic/neuromuscular (short) |

---

### Normalized Graded Pace (NGP) and Normalized Power (NP)

**NGP:** Pace adjusted for elevation — equivalent flat-ground pace. A 5:00/km run up a 6% grade is harder than 5:00/km on the flat; NGP reflects the flat equivalent.

**NP:** Power-based equivalent — weighted rolling average that accounts for variable intensity being more fatiguing than steady effort. A fartlek and a steady run with the same average power will have different NP.

Both allow IF and TSS to be calculated meaningfully for variable efforts.

---

### Aerobic decoupling (Pa:HR or Pw:HR)

**What it is:** How much heart rate drifts relative to pace (or power) during a steady-state run.
**Formula:** `Decoupling % = (HR_2nd_half / Pace_2nd_half) / (HR_1st_half / Pace_1st_half) − 1`

**Interpretation:**
| Decoupling | Meaning |
|-----------|---------|
| <5% | Well-trained for this duration and intensity |
| 5–10% | Moderate aerobic fitness; or hot/humid conditions |
| >10% | Under-fueled, dehydrated, too hot, or too fast for current fitness |
| Very negative | Possible HR data artifact |

**How to improve:** More easy mileage, better in-run fueling, better heat adaptation.

---

### Cardiac efficiency (pace/HR or power/HR)

A proxy for aerobic fitness improvement. As fitness improves, you run faster at the same HR (or the same pace requires less cardiac output).

**How to track over time:**
- Record average pace and average HR for a standard easy run weekly
- If pace improves and HR stays the same → fitness gained
- If pace stays the same but HR decreases → more efficient

Intervals.icu shows this as "Efficiency Factor" on activities.

---

### Power-to-weight ratio (Stryd W/kg)

Relevant for hilly running. A runner with 3.5 W/kg Critical Power will outperform a runner with 3.0 W/kg going uphill, even if the slower runner has better flat running economy.

---

## Analyzing a structured workout (intervals)

### What to check for each interval rep

1. **Target vs. actual pace/power:** Were the targets hit? Within ±3% is good. Consistently slower = target too hard or fatigue.
2. **HR progression through reps:** Should be fairly stable or rising slightly. If HR jumps significantly between rep 1 and rep 4, you started too fast or recovery was insufficient.
3. **Recovery HR:** How quickly does HR drop in the recovery interval? Faster = better fitness. If HR doesn't drop below ~75% LTHR in equal-duration recovery, you need more rest.

### Pacing within each rep
- First 30–60 seconds of a VO2max rep: HR is lagging — don't sprint to "hit" HR target immediately
- Best execution: even pace or slight negative split within each rep
- Blow-ups (first 60% fast, last 40% slow): too fast start; reduce target pace 3–5%

---

## Analyzing the long run

### Aerobic decoupling check
- Run first and second half at same effort
- Compare average HR in first vs. second half
- <5% drift = aerobic fitness adequate for this distance
- >10% drift = this was too long, too fast, or under-fueled

### Muscle fatigue signature
- Pace drops while HR stays stable → peripheral muscle fatigue (glycogen depletion or muscle damage)
- HR rises while pace drops → cardiac fatigue, dehydration, or heat

### Nutrition check
- If energy crashed at ~90 min: ran out of glycogen; start fueling at 40–45 min next time
- If no crash: fueling strategy worked; note it

---

## Weekly training load analysis

### Volume:quality ratio check
Rule of thumb: 80% of weekly TSS from Z1–Z2, 20% from Z3+ (polarized model).

Using Intervals.icu weekly breakdown:
- Flag weeks where Z3+ exceeds 25% of total TSS → accumulating more stress than the model predicts
- Flag weeks where there's no Z3 work → missed quality; check if intentional

### CTL trend check
- Rising CTL at ≤8 TSS/week: safe build
- Flat CTL: maintenance; appropriate before race or during recovery
- Falling CTL: detraining; check if intentional (taper) or not
- Spike CTL rise >10 TSS/week: injury risk flag

---

## Performance testing analysis

### VDOT update after time trial / race

1. Enter race time and distance into VDOT formula or table
2. Compare to previous VDOT → change indicates fitness change
3. Update training paces in the current plan
4. Note: VDOT can vary ±1–2 points between similar fitness levels (course, heat, fatigue)

### Fitness test: 8 × 400m with HR

Protocol:
1. After warmup, run 8 × 400m at 5K target pace with 60 sec jog
2. Record HR at end of each rep and end of recovery
3. Early in training: HR rises through reps; recovery HR is high
4. As fitness improves: HR at same pace decreases; recovery HR drops faster
5. Use as relative fitness indicator — not calibrated threshold

### All-out 3 km test (VO2max proxy)

1. After warmup, run 3 km all-out
2. Average pace → calculate VDOT
3. Repeat every 8–10 weeks
4. Note environmental conditions (heat, wind) for valid comparison

---

## Red flags in the data

| What you see | Possible cause | Action |
|-------------|---------------|--------|
| HR significantly above normal for easy paces | Illness, overtraining, dehydration, heat | Easy or rest day |
| TSS dramatically higher than target for same workout | Under-recovered; working harder than perceived | Adjust following days down |
| Cardiac drift >10% on a run you should handle | Under-fueled, too fast, insufficient fitness | Improve fueling; reduce pace |
| VO2max intervals: reps 5–8 are 10%+ slower than reps 1–4 | Started too fast | Reduce target pace next session |
| CTL rising but performance declining | Overtraining, RED-S, illness | Rest week; review nutrition |
| Power or pace consistently below target despite normal effort | Residual fatigue, low glycogen | Add rest day; check sleep + nutrition |

---

## Tracking progress over a training block

Quarterly check-in (every 8–12 weeks):
1. Compare VDOT then vs. now (race time or time trial)
2. Compare easy run HR at same pace → lower = more efficient
3. Compare aerobic decoupling at standard long run distance → lower = better endurance
4. Compare CTL now vs. start of block → should be higher if building
5. Review injury history → any patterns? Address with strength work

This gives a complete picture of adaptation without over-testing.
