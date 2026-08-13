#!/usr/bin/env python3
"""
Running zone calculator.
Computes pace, heart rate, and Stryd power zones from a race time or test result.

Usage:
  python zones.py --distance 5k --time 25:00
  python zones.py --distance marathon --time 3:30:00
  python zones.py --lthr 162
  python zones.py --cp 280  # Stryd Critical Power in watts
"""

import argparse
import sys


DISTANCE_METERS = {
    "800m": 800,
    "1500m": 1500,
    "mile": 1609,
    "3k": 3000,
    "5k": 5000,
    "8k": 8000,
    "10k": 10000,
    "15k": 15000,
    "10mile": 16093,
    "20k": 20000,
    "hm": 21097,
    "half": 21097,
    "30k": 30000,
    "marathon": 42195,
}


def parse_time(time_str: str) -> float:
    """Parse HH:MM:SS or MM:SS string to total seconds."""
    parts = time_str.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    raise ValueError(f"Cannot parse time: {time_str}")


def seconds_to_pace(secs_per_km: float) -> str:
    """Convert seconds per km to min:sec/km string."""
    mins = int(secs_per_km // 60)
    secs = int(secs_per_km % 60)
    return f"{mins}:{secs:02d}/km"


def compute_vdot(distance_m: float, time_secs: float) -> float:
    """
    Estimate VDOT using Daniels & Gilbert (1979) formula.
    Reference: Daniels' Running Formula.
    """
    t = time_secs / 60  # minutes
    velocity = distance_m / t  # meters per minute

    # Fractional utilization of VO2max at this duration
    pct_vo2max = 0.8 + 0.1894393 * (1 - 2.718281828 ** (-0.012778 * t)) + \
                 0.2989558 * (1 - 2.718281828 ** (-0.1932605 * t))

    # VO2 at this pace
    vo2 = -4.60 + 0.182258 * velocity + 0.000104 * velocity ** 2

    return vo2 / pct_vo2max


def vdot_to_paces(vdot: float) -> dict:
    """
    Convert VDOT to training paces (seconds per km).
    Based on Daniels' Running Formula tables.
    """
    # vVO2max: pace at which VO2max is achieved (~3200m/marathon effort ratio)
    # Solve: vo2 = vdot * pct_vo2max at the pace → use iterative approach
    # Simplified: vVO2max in m/min ≈ empirically
    # Daniels' intervals are run at ~97-100% VO2max

    # Approximate velocity at VO2max (m/min) from VDOT
    # Using quadratic inverse of Daniels formula
    # v = (VDOT + 4.60) / (0.182258 + sqrt(0.182258^2 + 4*0.000104*(VDOT+4.60))) / (2*0.000104)
    a, b, c = 0.000104, 0.182258, -(vdot + 4.60)
    disc = b ** 2 - 4 * a * c
    v_vo2max_m_min = (-b + disc ** 0.5) / (2 * a)  # meters per minute

    v_vo2max_sec_km = 60000 / v_vo2max_m_min  # seconds per km

    return {
        "E_low":    v_vo2max_sec_km * (1 / 0.76),   # 76% vVO2max (easy, faster end)
        "E_high":   v_vo2max_sec_km * (1 / 0.70),   # 70% vVO2max (easy, slower end)
        "M":        v_vo2max_sec_km * (1 / 0.84),   # 84% vVO2max (marathon)
        "T":        v_vo2max_sec_km * (1 / 0.92),   # 92% vVO2max (threshold)
        "I":        v_vo2max_sec_km * (1 / 0.98),   # 98% vVO2max (interval)
        "R":        v_vo2max_sec_km * (1 / 1.05),   # 105% vVO2max (repetition)
    }


def print_pace_zones(vdot: float) -> None:
    paces = vdot_to_paces(vdot)
    print(f"\nVDOT: {vdot:.1f}")
    print("\nDaniels training paces:")
    print(f"  E  (Easy)       {seconds_to_pace(paces['E_low'])} – {seconds_to_pace(paces['E_high'])}")
    print(f"  M  (Marathon)   {seconds_to_pace(paces['M'])}")
    print(f"  T  (Threshold)  {seconds_to_pace(paces['T'])}")
    print(f"  I  (Interval)   {seconds_to_pace(paces['I'])}")
    print(f"  R  (Rep)        {seconds_to_pace(paces['R'])}")

    print("\n5-zone pace model (% vVO2max):")
    v = 60000 / paces["I"] * (1 / 0.98)  # vVO2max in km/min
    zone_pcts = [
        ("Z1 Easy",       0.00, 0.76),
        ("Z2 Moderate",   0.76, 0.88),
        ("Z3 Threshold",  0.88, 0.95),
        ("Z4 VO2max",     0.95, 1.05),
        ("Z5 Speed",      1.05, 1.20),
    ]
    for name, lo_pct, hi_pct in zone_pcts:
        lo = (60000 / (v * lo_pct)) if lo_pct > 0 else None
        hi = 60000 / (v * hi_pct)
        if lo is None:
            print(f"  {name:<18} > {seconds_to_pace(hi)}")
        else:
            print(f"  {name:<18} {seconds_to_pace(lo)} – {seconds_to_pace(hi)}")


def print_hr_zones(lthr: int) -> None:
    print(f"\nLTHR: {lthr} bpm")
    print("\nFriel 7-zone HR model (% LTHR):")
    zones = [
        ("Z1 Active recovery", 0.00, 0.81),
        ("Z2 Aerobic (easy)",  0.81, 0.89),
        ("Z3 Tempo",           0.89, 0.93),
        ("Z4 Sub-threshold",   0.93, 0.99),
        ("Z5a Threshold",      0.99, 1.02),
        ("Z5b Supra-threshold",1.02, 1.06),
        ("Z5c Anaerobic",      1.06, 1.15),
    ]
    for name, lo, hi in zones:
        lo_bpm = int(lthr * lo)
        hi_bpm = int(lthr * hi)
        if lo == 0.0:
            print(f"  {name:<26} < {hi_bpm} bpm")
        else:
            print(f"  {name:<26} {lo_bpm}–{hi_bpm} bpm")

    print("\nPolarized 3-zone HR model:")
    print(f"  Z1 Low intensity   < {int(lthr * 0.82)} bpm")
    print(f"  Z2 Medium (gray)   {int(lthr * 0.82)}–{int(lthr * 0.88)} bpm  ← minimize time here")
    print(f"  Z3 High intensity  > {int(lthr * 0.88)} bpm")


def print_power_zones(cp: int) -> None:
    print(f"\nCritical Power (CP): {cp} W")
    print("\nStryd / Coggan power zones (% CP):")
    zones = [
        ("Z1 Active recovery", 0.00, 0.55),
        ("Z2 Endurance",       0.56, 0.75),
        ("Z3 Tempo",           0.76, 0.87),
        ("Z4 Threshold",       0.88, 0.95),
        ("Z5 VO2max",          0.96, 1.05),
        ("Z6 Anaerobic",       1.06, 1.20),
        ("Z7 Neuromuscular",   1.21, 1.50),
    ]
    for name, lo, hi in zones:
        lo_w = int(cp * lo)
        hi_w = int(cp * hi)
        if lo == 0.0:
            print(f"  {name:<22} < {hi_w} W")
        else:
            print(f"  {name:<22} {lo_w}–{hi_w} W")


def main():
    parser = argparse.ArgumentParser(description="Running zone calculator")
    parser.add_argument("--distance", help="Race distance (e.g. 5k, 10k, hm, marathon)")
    parser.add_argument("--time", help="Race or time trial time (MM:SS or HH:MM:SS)")
    parser.add_argument("--lthr", type=int, help="Lactate threshold heart rate (bpm)")
    parser.add_argument("--cp", type=int, help="Stryd Critical Power (watts)")
    args = parser.parse_args()

    if not any([args.distance, args.lthr, args.cp]):
        parser.print_help()
        sys.exit(1)

    if args.distance:
        if not args.time:
            print("--time required when --distance is provided")
            sys.exit(1)
        dist_key = args.distance.lower()
        if dist_key not in DISTANCE_METERS:
            print(f"Unknown distance '{args.distance}'. Options: {', '.join(DISTANCE_METERS)}")
            sys.exit(1)
        dist_m = DISTANCE_METERS[dist_key]
        time_secs = parse_time(args.time)
        vdot = compute_vdot(dist_m, time_secs)
        print_pace_zones(vdot)

    if args.lthr:
        print_hr_zones(args.lthr)

    if args.cp:
        print_power_zones(args.cp)


if __name__ == "__main__":
    main()
