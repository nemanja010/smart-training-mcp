# Sources and References — Running Training Skill

This file documents the primary sources used to build the content in this skill. Every methodology, zone model, physiological claim, and training prescription in `references/`, `scripts/`, and `assets/` traces to one or more of these sources. Anyone wanting to verify the logic or dig deeper can start here.

---

## Inspiration repositories

These repositories were referenced for structure, format, and scope when designing this skill. No code or text was copied.

| Repository | Author | License | How it influenced this skill |
|-----------|--------|---------|------------------------------|
| [disco-trooper/skills — cycling-training](https://github.com/disco-trooper/skills/tree/main/cycling-training) | disco-trooper | MIT | Primary structural inspiration — multi-file skill layout (SKILL.md + references/ + scripts/ + assets/), tone, and breadth of topic coverage. The running skill deliberately extends what cycling-training covers for running-specific physiology and methodology. |
| [disco-trooper/skills — hypertrophy-training](https://github.com/disco-trooper/skills/tree/main/hypertrophy-training) | disco-trooper | MIT | Consulted for how periodization and volume landmarks are handled in non-running skills. |
| [borisghidaglia/science-based-lifter](https://github.com/borisghidaglia/science-based-lifter) | Boris Ghidaglia | MIT | Consulted for how evidence-based training content is organized across multiple sub-skills and how sources are cited within a skill structure. |

---

## Primary sources by topic

### Training zones and VDOT

**Daniels, J. (2014). *Daniels' Running Formula* (3rd ed.). Human Kinetics.**
- Source for the VDOT system, the five training paces (E/M/T/I/R), and the % VO2max anchors for each.
- The VDOT table in `references/zones-and-testing.md` is derived from Daniels' published tables and formula.
- Quality session volume caps (≤8% weekly mileage at I pace, ≤5% at R pace) are directly from Daniels.
- Formula reference: Daniels, J. & Gilbert, J. (1979). Oxygen power: Performance tables for distance runners. Published privately.

**Friel, J. (2009). *The Triathlete's Training Bible* (3rd ed.). VeloPress.**
- Source for the 7-zone heart rate model anchored to LTHR.
- The 30-minute time trial protocol for LTHR is the standard Friel field test.

**McMillan, G. McMillan Running Calculator.**
- The McMillan zone names and race-pace equivalency approach in `references/zones-and-testing.md`.
- McMillan's calculator uses a curve-fitting approach to race equivalencies, similar to Riegel's formula but tuned to his empirical athlete database.

**Riegel, P.S. (1981). Athletic records and human endurance. *American Scientist*, 69(3), 285–290.**
- Source for the Riegel performance predictor formula: `T2 = T1 × (D2/D1)^1.06`.
- Used in `references/race-specific.md` for cross-distance time prediction.

---

### Polarized training (80/20)

**Seiler, K.S., & Kjerland, G.Ø. (2006). Quantifying training intensity distribution in elite endurance athletes: is there evidence for an "optimal" distribution? *Scandinavian Journal of Medicine & Science in Sports*, 16(1), 49–56.**
- First major publication documenting the 80/20 intensity distribution in elite cross-country skiers.

**Seiler, S. (2010). What is best practice for training intensity and duration distribution in endurance athletes? *International Journal of Sports Physiology and Performance*, 5(3), 276–291.**
- Most cited review of polarized training; documents the 75–80% Z1 / 5% Z2 / 15–20% Z3 split across multiple elite sports including running.

**Stöggl, T.L., & Sperlich, B. (2015). The training intensity distribution among well-trained and elite endurance athletes. *Frontiers in Physiology*, 6, 295.**
- Meta-analysis showing polarized training superior to threshold-heavy training for well-trained athletes over a 9-week intervention.

**Seiler, S., & Tønnessen, E. (2009). Intervals, thresholds, and long slow distance: the role of intensity and duration in endurance training. *Sportscience*, 13, 32–53.**
- Explains why the "gray zone" (Z2) is metabolically expensive without providing proportionally greater adaptation — the core mechanistic argument for polarized training.

---

### Lactate threshold and physiology

**Brooks, G.A. (1985). Anaerobic threshold: review of the concept and directions for future research. *Medicine and Science in Sports and Exercise*, 17(1), 22–34.**
- Foundational paper on the lactate threshold concept and the distinction between LT1 and LT2.

**Billat, V.L. (2001). Interval training for performance: a scientific and empirical practice. Special recommendations for middle- and long-distance running. *Sports Medicine*, 31(1), 13–31.**
- Source for the Billat 30/30 interval protocol (vVO2max intervals with equal rest).
- Establishes that vVO2max intervals are the most time-efficient VO2max stimulus.

**Midgley, A.W., McNaughton, L.R., & Wilkinson, M. (2006). Is there an optimal training intensity for enhancing the maximal oxygen uptake of distance runners? *Sports Medicine*, 36(2), 117–132.**
- Confirms that I-pace (95–100% VO2max) is the optimal stimulus for VO2max improvement in trained runners.

**Coyle, E.F. (1995). Integration of the physiological factors determining endurance performance ability. *Exercise and Sport Sciences Reviews*, 23, 25–63.**
- Source for the three-pillar model (VO2max × LT% × running economy) used in `references/physiology.md`.

---

### Running economy

**Saunders, P.U., Pyne, D.B., Telford, R.D., & Hawley, J.A. (2004). Factors affecting running economy in trained distance runners. *Sports Medicine*, 34(7), 465–485.**
- Comprehensive review of all factors affecting running economy: form, cadence, stiffness, strength, shoes.

**Barnes, K.R., & Kilding, A.E. (2015). Running economy: measurement, norms, and determining factors. *Sports Medicine Open*, 1(1), 8.**
- Practical guide to running economy measurement and the range of values across populations.

**Hoogkamer, W., Kipp, S., Frank, J.H., Farina, E.M., Luo, G., & Kram, R. (2018). A comparison of the energetic cost of running in marathon racing shoes. *Sports Medicine*, 48(4), 1009–1019.**
- The primary evidence for the ~4% running economy benefit of carbon-plate shoes (Nike Vaporfly).

---

### Norwegian double threshold

**Tjelta, L.I. (2016). The training of international level distance runners. *International Journal of Sports Science & Coaching*, 11(1), 122–134.**
- Documents the Norwegian approach to threshold training as applied to elite middle-distance runners.

**Filipas, L., Bonato, M., Gallo, G., & La Torre, A. (2022). Effects of 16 weeks of pyramidal and polarized training intensity distributions in well-trained endurance runners. *Scandinavian Journal of Medicine & Science in Sports*, 32(3), 498–511.**
- Comparison of training distributions relevant to the double-threshold debate.

*Note: The double-threshold method as practiced by Gjert Ingebrigtsen and his athletes (Jakob, Henrik, Filip Ingebrigtsen) is documented primarily in coach interviews and Norwegian sports science publications rather than peer-reviewed RCTs. The lactate-controlled sub-threshold approach is well-supported mechanistically (see Brooks 1985 and Seiler 2010); the specific twice-daily application at 2 mmol/L is Ingebrigtsen's practical innovation.*

---

### Pfitzinger marathon method

**Pfitzinger, P., & Douglas, S. (2019). *Advanced Marathoning* (3rd ed.). Human Kinetics.**
- Source for the Pfitzinger high-mileage marathon plans (55, 70, 85 mpw versions).
- Key concepts: medium-long run, periodized mileage buildup, lactate threshold as marathon-specific work.

**Pfitzinger, P., & Douglas, S. (2014). *Faster Road Racing: 5K to Half Marathon*. Human Kinetics.**
- Source for Pfitzinger 10K and half marathon plans.

---

### Hanson method

**Hanson, L., & Hanson, K. (2012). *Hansons Marathon Method*. VeloPress.**
- Source for the cumulative fatigue approach, the 16-mile long run cap, and the six-days-per-week structure.

---

### Lydiard method

**Lydiard, A., & Gilmour, G. (1978). *Run to the Top*. Minerva Ltd.**
**Lydiard, A., & Gilmour, G. (2000). *Running to the Top*. Meyer & Meyer Sport.**
- Source for the four-phase Lydiard periodization model (aerobic base → anaerobic → speed → racing).
- Original documentation of "running 100 miles a week" as aerobic base philosophy.

---

### Training load — TSS, CTL, ATL, TSB

**Coggan, A.R. (2003). Training and racing with a power meter. Lecture, USA Cycling Coaching Summit.**
- Original formulation of TSS (Training Stress Score), IF (Intensity Factor), NP (Normalized Power), and the CTL/ATL/TSB model.
- Formally published in: Allen, H., & Coggan, A. (2010). *Training and Racing with a Power Meter* (2nd ed.). VeloPress.

**Skiba, P.F., Chidnok, W., Vanhatalo, A., & Jones, A.M. (2012). Modeling the expenditure and reconstitution of work capacity above critical power. *Medicine and Science in Sports and Exercise*, 44(8), 1526–1532.**
- Theoretical basis for the ATL/CTL differential equations model.

*Note: The application of TSS/CTL/ATL/TSB to running (rTSS, hrTSS) is Intervals.icu's and TrainingPeaks' practical extension of Coggan's cycling framework. The formulas in `scripts/tss.py` follow the published TrainingPeaks / Intervals.icu methodology.*

---

### ACWR (Acute:Chronic Workload Ratio) and injury risk

**Gabbett, T.J. (2016). The training—injury prevention paradox: should athletes be training smarter and harder? *British Journal of Sports Medicine*, 50(5), 273–280.**
- Establishes ACWR >1.5 as the high-risk threshold; defines the 0.8–1.3 "sweet spot."

**Malone, S., Owen, A., Newton, M., Mendes, B., Collins, K.D., & Gabbett, T.J. (2017). The acute:chronic workload ratio in relation to injury risk in professional soccer. *Journal of Science and Medicine in Sport*, 20(6), 561–565.**
- Confirms the ACWR risk curve across a different sport, supporting its generalizability.

**Hulin, B.T., Gabbett, T.J., Lawson, D.W., Caputi, P., & Sampson, J.A. (2016). The acute:chronic workload ratio predicts injury: high chronic workload may decrease injury risk in elite rugby league players. *British Journal of Sports Medicine*, 50(4), 231–236.**
- Documents the protective effect of high chronic load — established athletes can handle higher ACWR.

---

### Stryd running power

**Stryd. (2020). *Stryd Power User Guide*. Stryd Inc.**
- Source for Critical Power calculation and the Stryd power zone model.
- Form Power, Leg Spring Stiffness, and Ground Contact Time definitions.

**Pallarés, J.G., Morán-Navarro, R., Ortega, J.F., Fernández-Elías, V.E., & Mora-Rodriguez, R. (2016). Validity and reliability of ventilatory and blood lactate thresholds in well-trained cyclists. *PLOS ONE*, 11(9), e0163389.**
- Critical Power / functional threshold methodology that the Stryd zone model adapts from cycling.

---

### Heart rate variability (HRV)

**Plews, D.J., Laursen, P.B., Stanley, J., Kilding, A.E., & Buchheit, M. (2013). Training adaptation and heart rate variability in elite endurance athletes: opening the door to effective monitoring. *Sports Medicine*, 43(9), 773–781.**
- Framework for HRV monitoring in endurance athletes: RMSSD, ln(RMSSD), rolling average interpretation.

**Altini, M., & Plews, D. (2021). What is behind the morning HRV measurement? Reflections following four years of data collection. *Quantified Self*.**
- Practical guidance on HRV4Training methodology and how to avoid overreacting to single-day readings.

**Buchheit, M. (2014). Monitoring training status with HR measures: Do all roads lead to Rome? *Frontiers in Physiology*, 5, 73.**
- Explains the relative value of RHR vs. HRV for daily monitoring in athletes.

---

### Nutrition and fueling

**Burke, L.M., et al. (2011). Carbohydrates for training and competition. *Journal of Sports Sciences*, 29(Suppl 1), S17–S27.**
- Source for CHO recommendations during exercise (60–90 g/hr for events >2.5 hr).

**Thomas, D.T., Erdman, K.A., & Burke, L.M. (2016). Position of the Academy of Nutrition and Dietetics, Dietitians of Canada, and the American College of Sports Medicine: Nutrition and Athletic Performance. *Journal of the Academy of Nutrition and Dietetics*, 116(3), 501–528.**
- Source for daily macronutrient targets for endurance athletes.

**Mountjoy, M., et al. (2014). The IOC consensus statement: beyond the female athlete triad — Relative Energy Deficiency in Sport (RED-S). *British Journal of Sports Medicine*, 48(7), 491–497.**
- Foundation for the RED-S section in `references/nutrition-recovery.md`.

**Guest, N.S., et al. (2021). International society of sports nutrition position stand: caffeine and exercise performance. *Journal of the International Society of Sports Nutrition*, 18, 1.**
- Source for caffeine dosing (3–6 mg/kg) and timing recommendation.

---

### Injuries and prevention

**van der Worp, M.P., et al. (2016). Iliotibial band syndrome in runners: a systematic review. *Sports Medicine*, 46(7), 1093–1110.**
- Source for ITBS mechanism, hip weakness connection, and management protocol.

**Alfredson, H., Pietilä, T., Jonsson, P., & Lorentzon, R. (1998). Heavy-load eccentric calf muscle training for the treatment of chronic Achilles tendinosis. *The American Journal of Sports Medicine*, 26(3), 360–366.**
- The original Alfredson eccentric protocol for Achilles tendinopathy.
- Follow-up: Beyer, R., et al. (2015). Heavy slow resistance versus Alfredson's protocol for Achilles tendinopathy. *American Journal of Sports Medicine*, 43(7), 1704–1711.

**Gabbett, T.J., & Domrow, N. (2007). Relationships between training load, injury, and fitness in sub-elite collision sport athletes. *Journal of Sports Sciences*, 25(13), 1507–1519.**
- Background on training load → injury cascade, foundation for the 10% mileage rule.

**Hreljac, A. (2004). Impact and overuse injuries in runners. *Medicine and Science in Sports and Exercise*, 36(5), 845–849.**
- Review of the most common running injuries and their biomechanical causes.

---

### Sleep and recovery

**Mah, C.D., Mah, K.E., Kezirian, E.J., & Dement, W.C. (2011). The effects of sleep extension on the athletic performance of collegiate basketball players. *Sleep*, 34(7), 943–950.**
- The sleep extension study cited in `references/nutrition-recovery.md` (sprint speed, reaction time, mood improvements).

**Fullagar, H.H., Skorski, S., Duffield, R., Hammes, D., Coutts, A.J., & Meyer, T. (2015). Sleep and athletic performance: the effects of sleep loss on exercise performance, and physiological and cognitive responses to exercise. *Sports Medicine*, 45(2), 161–186.**
- Comprehensive review of sleep effects on athletic performance.

---

### Strength training for runners

**Blagrove, R.C., Howatson, G., & Hayes, P.R. (2018). Effects of strength training on the physiological determinants of middle- and long-distance running performance: a systematic review. *Sports Medicine*, 48(5), 1117–1149.**
- Meta-analysis supporting strength training for running economy and performance.

**Beattie, K., Kenny, I.C., Lyons, M., & Carson, B.P. (2014). The effect of strength training on performance in endurance athletes. *Sports Medicine*, 44(6), 845–865.**
- Mechanism and magnitude of strength training effects on running.

---

## Disclaimers

1. **Individual variation**: All zone models, pacing formulas, and TSS benchmarks are approximations. Individuals vary; use these as starting points and adjust based on feel, HRV, and performance data.

2. **Medical advice**: This skill does not provide medical advice. Injury descriptions are for educational reference only. Always consult a physiotherapist or sports medicine physician for injury diagnosis and treatment.

3. **Formula approximations**: The VDOT formula in `scripts/vdot.py` is a close approximation of the Daniels & Gilbert (1979) formula, not the exact proprietary implementation. Values will match the published tables within ±1–2 VDOT points.

4. **Evolving science**: Training science evolves. The polarized vs. threshold debate, optimal ACWR thresholds, and specific fueling protocols continue to be refined in the literature. The positions taken here represent the scientific consensus as of mid-2025.
