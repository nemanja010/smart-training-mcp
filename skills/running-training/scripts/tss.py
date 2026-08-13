#!/usr/bin/env python3
"""
Running TSS calculator.
Computes rTSS (pace-based), hrTSS (HR-based), and Stryd power TSS.

Usage:
  python tss.py --mode pace --duration 60 --avg-pace 5:30 --threshold-pace 4:45
  python tss.py --mode hr   --duration 90 --avg-hr 145 --lthr 162 --max-hr 190
  python tss.py --mode power --duration 75 --avg-power 265 --cp 280
"""

import argparse
import sys
import math


def parse_pace(pace_str: str) -> float:
    """Parse MM:SS/km to seconds per km."""
    parts = pace_str.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Pace must be in MM:SS format, got: {pace_str}")
    return int(parts[0]) * 60 + float(parts[1])


def rtss(duration_min: float, avg_pace_sec_km: float, threshold_pace_sec_km: float) -> float:
    """
    Pace-based running TSS (rTSS / Daniels method).
    IF = threshold_pace / avg_pace (faster pace = lower sec/km = higher IF)
    TSS = duration_hrs * IF^2 * 100
    """
    duration_hrs = duration_min / 60
    intensity_factor = threshold_pace_sec_km / avg_pace_sec_km
    return duration_hrs * (intensity_factor ** 2) * 100


def hrtss(duration_min: float, avg_hr: float, lthr: float, hr_max: float) -> float:
    """
    Heart-rate based TSS (hrTSS).
    Based on Friel's method: hrTSS = duration_hrs * (avg_hr/lthr)^3 * 100
    Capped to avoid unrealistic values above LTHR.
    """
    duration_hrs = duration_min / 60
    hr_ratio = avg_hr / lthr
    return duration_hrs * (hr_ratio ** 3) * 100


def power_tss(duration_min: float, avg_power: float, cp: float) -> float:
    """
    Stryd power-based TSS. Same formula as cycling TSS.
    IF = avg_power / CP
    TSS = (duration_sec * NP * IF) / (CP * 3600) * 100
    For steady efforts, NP ≈ avg_power. For variable efforts, NP > avg_power.
    """
    duration_secs = duration_min * 60
    intensity_factor = avg_power / cp
    tss = (duration_secs * avg_power * intensity_factor) / (cp * 3600) * 100
    return tss


def interpret_tss(tss: float) -> str:
    if tss < 50:
        return "Low stress — easy/recovery workout"
    elif tss < 100:
        return "Moderate stress — standard training session"
    elif tss < 150:
        return "High stress — quality workout or long run"
    elif tss < 200:
        return "Very high stress — very long run or hard race"
    else:
        return "Extreme stress — marathon-length effort or race"


def interpret_if(intensity_factor: float) -> str:
    if intensity_factor < 0.75:
        return "Easy/recovery (Z1–Z2)"
    elif intensity_factor < 0.85:
        return "Aerobic endurance (Z2)"
    elif intensity_factor < 0.95:
        return "Tempo (Z3)"
    elif intensity_factor < 1.05:
        return "Threshold (Z4)"
    elif intensity_factor < 1.20:
        return "VO2max (Z5)"
    else:
        return "Anaerobic/neuromuscular (Z6+)"


def main():
    parser = argparse.ArgumentParser(description="Running TSS calculator")
    parser.add_argument("--mode", choices=["pace", "hr", "power"], required=True,
                        help="Calculation mode: pace, hr, or power")
    parser.add_argument("--duration", type=float, required=True,
                        help="Total workout duration in minutes (including warmup/cooldown)")
    parser.add_argument("--avg-pace", help="Average pace as MM:SS/km (mode=pace)")
    parser.add_argument("--threshold-pace", help="Threshold pace as MM:SS/km (mode=pace)")
    parser.add_argument("--avg-hr", type=float, help="Average HR in bpm (mode=hr)")
    parser.add_argument("--lthr", type=float, help="Lactate threshold HR in bpm (mode=hr)")
    parser.add_argument("--max-hr", type=float, help="Maximum HR in bpm (mode=hr)")
    parser.add_argument("--avg-power", type=float, help="Average power in watts (mode=power)")
    parser.add_argument("--cp", type=float, help="Critical Power in watts (mode=power)")
    args = parser.parse_args()

    print(f"\nDuration: {args.duration:.0f} min")

    if args.mode == "pace":
        if not args.avg_pace or not args.threshold_pace:
            print("--avg-pace and --threshold-pace required for pace mode")
            sys.exit(1)
        avg_secs = parse_pace(args.avg_pace)
        thr_secs = parse_pace(args.threshold_pace)
        tss = rtss(args.duration, avg_secs, thr_secs)
        IF = thr_secs / avg_secs
        print(f"Average pace:     {args.avg_pace}/km")
        print(f"Threshold pace:   {args.threshold_pace}/km")
        print(f"Intensity Factor: {IF:.3f}  ({interpret_if(IF)})")
        print(f"rTSS:             {tss:.1f}  ({interpret_tss(tss)})")

    elif args.mode == "hr":
        if not args.avg_hr or not args.lthr or not args.max_hr:
            print("--avg-hr, --lthr, and --max-hr required for hr mode")
            sys.exit(1)
        tss = hrtss(args.duration, args.avg_hr, args.lthr, args.max_hr)
        hr_ratio = args.avg_hr / args.lthr
        print(f"Average HR:       {args.avg_hr:.0f} bpm")
        print(f"LTHR:             {args.lthr:.0f} bpm")
        print(f"HR/LTHR ratio:    {hr_ratio:.3f}  ({interpret_if(hr_ratio)})")
        print(f"hrTSS:            {tss:.1f}  ({interpret_tss(tss)})")

    elif args.mode == "power":
        if not args.avg_power or not args.cp:
            print("--avg-power and --cp required for power mode")
            sys.exit(1)
        tss = power_tss(args.duration, args.avg_power, args.cp)
        IF = args.avg_power / args.cp
        print(f"Average power:    {args.avg_power:.0f} W")
        print(f"Critical Power:   {args.cp:.0f} W")
        print(f"Intensity Factor: {IF:.3f}  ({interpret_if(IF)})")
        print(f"Power TSS:        {tss:.1f}  ({interpret_tss(tss)})")

    print()

    # Weekly load context
    weekly_tss = tss * (7 / (args.duration / 60))  # rough extrapolation
    print("Weekly TSS context (approximate):")
    print(f"  At this workload every day: ~{weekly_tss:.0f} TSS/week")
    print(f"  Typical recreational runner: 300–500 TSS/week")
    print(f"  Serious amateur runner:      500–800 TSS/week")
    print(f"  Elite runner:                800–1200+ TSS/week")


if __name__ == "__main__":
    main()
