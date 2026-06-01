#!/usr/bin/env python3
"""Compare expected components with components found by Syft."""

import argparse
import json


def load_ground_truth(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    expected = {}
    for component in data["components"]:
        name = component["name"].lower()
        expected[name] = component.get("version")

    return expected


def load_syft_output(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    reported = {}
    for artifact in data.get("artifacts", []):
        name = artifact.get("name")
        if name:
            reported[name.lower()] = artifact.get("version")

    return reported


def divide(top, bottom):
    if bottom == 0:
        return 0
    return top / bottom


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ground_truth")
    parser.add_argument("syft_output")
    args = parser.parse_args()

    expected = load_ground_truth(args.ground_truth)
    reported = load_syft_output(args.syft_output)

    expected_names = set(expected)
    reported_names = set(reported)

    true_positives = expected_names & reported_names
    false_positives = reported_names - expected_names
    false_negatives = expected_names - reported_names

    precision = divide(len(true_positives), len(true_positives) + len(false_positives))
    recall = divide(len(true_positives), len(true_positives) + len(false_negatives))

    result = {
        "true_positives": sorted(true_positives),
        "false_positives": sorted(false_positives),
        "false_negatives": sorted(false_negatives),
        "precision": precision,
        "recall": recall,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
