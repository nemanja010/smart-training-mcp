#!/usr/bin/env python3
"""
VDOT calculator and training pace finder.
Uses Daniels & Gilbert (1979) formula.

Usage:
  python vdot.py --distance 5k --time 25:00
  python vdot.py --vdot 50
  python vdot.py --distance marathon --time 3:45:00 --predict-all
"""

import argparse
import sys
import math


DISTANCES = {
    "1500m": 1500,
    "mile":  1609,
    "3k":    3000,
    "5k":    5000,
    "8k":    8000,
    "10k":   10000,
    "15k":   15000,
    "hm":    21097,
    "half":  21097,
    "marathon": 42195,
}


def parse_time(s: str) -> float:
    parts = s.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    raise ValueError(f"Cannot parse time: {s}")


def fmt_time(secs: float) -> str:
    secs = int(secs)
    hrs = secs // 3600
    mins = (secs % 3600) // 60
    s = secs % 60
    if hrs > 0:
        return f"{hrs}:{mins:02d}:{s:02d}"
    return f"{mins}:{s:02d}"


def fmt_pace(sec_per_km: float) -> str:
    m = int(sec_per_km // 60)
    s = int(sec_per_km % 60)
    return f"{m}:{s:02d}/km"


def compute_vdot(dist_m: float, time_secs: float) -> float:
    t = time_secs / 60
    v = dist_m / t  # m/min
    pct = 0.8 + 0.1894393 * (1 - math.exp(-0.012778 * t)) + \
              0.2989558 * (1 - math.exp(-0.1932605 * t))
    vo2 = -4.60 + 0.182258 * v + 0.000104 * v ** 2
    return vo2 / pct


def vdot_to_vo2max_velocity(vdot: float) -> float:
    """Return velocity at VO2max in m/min (vVO2max)."""
    a, b, c_coef = 0.000104, 0.182258, -(vdot + 4.60)
    disc = b ** 2 - 4 * a * c_coef
    return (-b + math.sqrt(disc)) / (2 * a)


def vdot_to_paces(vdot: float) -> dict:
    """Return Daniels training paces in sec/km."""
    vvo2max = vdot_to_vo2max_velocity(vdot)  # m/min
    sec_per_km_at_vvo2max = 60000 / vvo2max

    return {
        "E_low":  sec_per_km_at_vvo2max / 0.76,
        "E_high": sec_per_km_at_vvo2max / 0.70,
        "M":      sec_per_km_at_vvo2max / 0.84,
        "T":      sec_per_km_at_vvo2max / 0.92,
        "I":      sec_per_km_at_vvo2max / 0.98,
        "R":      sec_per_km_at_vvo2max / 1.05,
    }


def predict_race_time(vdot: float, dist_m: float, tolerance: float = 0.5) -> float:
    """Binary search for the time at which compute_vdot(dist, time) ≈ vdot."""
    lo, hi = 60.0, 36000.0  # 1 min to 10 hr in seconds
    for _ in range(60):
        mid = (lo + hi) / 2
        v = compute_vdot(dist_m, mid)
        if abs(v - vdot) < tolerance:
            return mid
        if v > vdot:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def print_paces(vdot: float) -> None:
    p = vdot_to_paces(vdot)
    print(f"\nVDOT: {vdot:.1f}")
    print("\nDaniels training paces:")
    print(f"  E  Easy        {fmt_pace(p['E_low'])} – {fmt_pace(p['E_high'])}")
    print(f"  M  Marathon    {fmt_pace(p['M'])}")
    print(f"  T  Threshold   {fmt_pace(p['T'])}")
    print(f"  I  Interval    {fmt_pace(p['I'])}")
    print(f"  R  Repetition  {fmt_pace(p['R'])}")


def print_predictions(vdot: float) -> None:
    print("\nRace time predictions:")
    for name, dist in [("1500m", 1500), ("Mile", 1609), ("3K", 3000), ("5K", 5000),
                       ("8K", 8000), ("10K", 10000), ("HM", 21097), ("Marathon", 42195)]:
        t = predict_race_time(vdot, dist)
        pace = t / (dist / 1000)
        print(f"  {name:<10} {fmt_time(t)}  ({fmt_pace(pace)})")


def main():
    parser = argparse.ArgumentParser(description="VDOT calculator")
    parser.add_argument("--distance", help="Race distance (5k, 10k, hm, marathon, ...)")
    parser.add_argument("--time", help="Race time (MM:SS or HH:MM:SS)")
    parser.add_argument("--vdot", type=float, help="Known VDOT (skip race input)")
    parser.add_argument("--predict-all", action="store_true",
                        help="Predict race times for all standard distances")
    args = parser.parse_args()

    if args.vdot:
        vdot = args.vdot
    elif args.distance and args.time:
        key = args.distance.lower()
        if key not in DISTANCES:
            print(f"Unknown distance '{args.distance}'. Options: {', '.join(DISTANCES)}")
            sys.exit(1)
        dist_m = DISTANCES[key]
        time_secs = parse_time(args.time)
        vdot = compute_vdot(dist_m, time_secs)
        print(f"\nInput: {args.distance} in {args.time}")
    else:
        parser.print_help()
        sys.exit(1)

    print_paces(vdot)

    if args.predict_all:
        print_predictions(vdot)

    print()


if __name__ == "__main__":
    main()
