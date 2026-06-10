#!/usr/bin/env python3
"""Compare expected components and ELF imports with Syft output."""

import argparse
import json


def normalize_component_name(name):
    return name.strip().lower()


def load_ground_truth(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    components = {}
    for component in data["components"]:
        name = normalize_component_name(component["name"])
        components[name] = component.get("version")

    imported_libraries = set(data.get("imported_libraries", []))

    return {
        "sample": data.get("sample"),
        "components": components,
        "imported_libraries": imported_libraries,
    }


def load_syft_output(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    components = {}
    for artifact in data.get("artifacts", []):
        name = artifact.get("name")
        if name:
            components[normalize_component_name(name)] = artifact.get("version")

    imported_libraries = set()
    for file_record in data.get("files", []) or []:
        executable = file_record.get("executable") or {}
        for library in executable.get("importedLibraries") or []:
            imported_libraries.add(library)

    return {
        "components": components,
        "imported_libraries": imported_libraries,
    }


def divide(top, bottom):
    if bottom == 0:
        return None
    return top / bottom


def compare_sets(expected, reported):
    true_positives = expected & reported
    false_positives = reported - expected
    false_negatives = expected - reported

    precision = divide(len(true_positives), len(true_positives) + len(false_positives))
    recall = divide(len(true_positives), len(true_positives) + len(false_negatives))

    return {
        "expected_count": len(expected),
        "reported_count": len(reported),
        "true_positives": sorted(true_positives),
        "false_positives": sorted(false_positives),
        "false_negatives": sorted(false_negatives),
        "precision": precision,
        "recall": recall,
        "exact_match": not false_positives and not false_negatives,
    }


def compare_components(expected, reported):
    result = compare_sets(set(expected), set(reported))
    name_exact_match = result["exact_match"]

    version_mismatches = []
    version_checked_count = 0
    for name in result["true_positives"]:
        expected_version = expected[name]
        reported_version = reported[name]
        if expected_version is None:
            continue

        version_checked_count += 1
        if expected_version != reported_version:
            version_mismatches.append(
                {
                    "name": name,
                    "expected": expected_version,
                    "reported": reported_version,
                }
            )

    version_match_count = version_checked_count - len(version_mismatches)

    result["name_exact_match"] = name_exact_match
    result["version_mismatches"] = version_mismatches
    result["version_checked_count"] = version_checked_count
    result["version_match_count"] = version_match_count
    result["version_accuracy"] = divide(version_match_count, version_checked_count)
    result["version_exact_match"] = len(version_mismatches) == 0
    result["exact_match"] = name_exact_match and result["version_exact_match"]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ground_truth")
    parser.add_argument("syft_output")
    args = parser.parse_args()

    expected = load_ground_truth(args.ground_truth)
    reported = load_syft_output(args.syft_output)

    result = {
        "sample": expected["sample"],
        "package_artifacts": compare_components(
            expected["components"],
            reported["components"],
        ),
        "imported_libraries": compare_sets(
            expected["imported_libraries"],
            reported["imported_libraries"],
        ),
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
