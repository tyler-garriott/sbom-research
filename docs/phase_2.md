# Phase 2 Plan: Syft Binary Classifier Investigation

## Current Status

Phase 1 showed that Syft behaves differently depending on the type of evidence
being extracted from C/C++ binaries.

Main findings so far:

* Syft usually extracts ELF imported libraries correctly.
* Syft does not always turn imported libraries into package-level SBOM artifacts.
* Some known binaries are detected through Syft package artifacts, but coverage is uneven.
* Several controlled rename tests showed filename sensitivity: the same binary bytes produced a package artifact under the expected filename, but no package artifact after renaming.
* Imported-library extraction stayed consistent across renamed copies.

## Phase 2 Goal

The goal of Phase 2 is to explain why Syft detects some C/C++ binaries as
package artifacts and misses others.

Main research question:

> What signals does Syft use to identify package artifacts in standalone C/C++
> binaries?

Sub-questions:

1. Does Syft rely on filename or basename patterns?
2. Does Syft rely on version strings inside the binary?
3. Which binaries have explicit Syft classifiers?
4. Does behavior change between Syft versions?
5. How should package artifacts, ELF imports, and string evidence be reported separately?

Working hypothesis:

> Syft package artifact detection for standalone C/C++ binaries depends on
> explicit binary classifiers that use signals such as basename, path, and
> version strings.

## Guiding Principle

Phase 2 should stay focused on explaining the Phase 1 result. The goal is not
to test every SBOM tool or every binary. The goal is to separate evidence types
and understand when Syft package artifact detection succeeds or fails.

Keep these evidence types separate:

1. Syft package artifacts
2. Syft imported libraries
3. `readelf` imported libraries
4. String or version evidence inside the binary
5. Source-code evidence from Syft's classifier implementation

Do not automatically treat imported libraries as package artifacts.

### Step 1: Freeze Phase 1 Results

Create a clean written summary of the current findings.

Main deliverable:

* `docs/phase1_results.md`

Include:

* research question
* environment
* Syft version
* distinction between package artifacts and imported libraries
* main results table
* filename sensitivity table
* OpenSSL controlled rename test
* FFmpeg case study
* limitations
* conclusion

Purpose:

This gives Phase 1 a stable written result before Phase 2 adds more experiments
and source-code interpretation.

### Step 2: Reproduce Core Rename Tests

Re-run the strongest controlled rename tests and save the evidence cleanly.

Core binary pairs:

* `openssl` vs `openssl-built`
* `memcached` vs `memcached-built`
* `xz` vs `xz-built`
* `jq` vs `jq-linux-amd64`

For each pair, record:

* whether the files are byte-identical
* file type
* ELF imported libraries
* Syft package artifacts
* Syft imported libraries

Expected result to verify:

* same bytes
* same imported libraries
* different package artifact result

Purpose:

This confirms that the strongest Phase 1 finding is reproducible and not just a
one-off observation from earlier notes.

### Step 3: Compare Syft Versions

Repeat the strongest rename tests with Syft 1.44.0 and Syft 1.45.1.

Record whether behavior changes for:

* `openssl` vs `openssl-built`
* `memcached` vs `memcached-built`
* `xz` vs `xz-built`
* `jq` vs `jq-linux-amd64`

Main deliverable:

* a small version comparison table

Purpose:

If results are the same, the filename-sensitivity finding is stronger. If
results changed, document which version changed and why that matters.

### Step 4: Inspect Syft Source Code

Inspect Syft source code for binary classifier behavior.

Focus on:

* filename checks
* basename checks
* path pattern checks
* string or regex matching
* version extraction logic
* package URL generation
* CPE generation
* hardcoded package names

Binaries to investigate:

* `openssl`
* `memcached`
* `xz`
* `jq`
* `curl`
* `zstd`
* `ffmpeg`

Main deliverable:

* `docs/syft_classifier_notes.md`

Purpose:

This moves the project from observing behavior to explaining the likely
classifier signals behind that behavior.

### Step 5: Create a Classifier Signal Matrix

Combine experiment results with source-code observations.

Main deliverable:

* `docs/classifier_signal_matrix.md`

Suggested columns:

* binary
* Syft package artifact found
* rename-sensitive
* version exact
* imported libraries correct
* classifier found
* likely signals
* notes

Important wording:

For FFmpeg, avoid saying no classifier exists unless the source-code inspection
proves that. A safer statement is:

> classifier may exist, but did not match this binary

Purpose:

This table should connect the experiments to the classifier logic and make the
Phase 2 explanation easy to present.

### Step 6: Build a Small Evidence Report Script

Create a small script that summarizes binary evidence without turning it into a
full SBOM generator.

Main deliverable:

* `scripts/evidence_report.py`

The script should summarize:

* binary path
* hash
* Syft package artifacts
* Syft imported libraries
* `readelf` imported libraries
* optional string or version evidence
* short interpretation

Purpose:

This makes the project more reproducible and reinforces the main principle:
package artifacts, ELF imports, and string evidence are different kinds of
evidence.

### Step 7: Run One Filesystem Context Comparison

Run one controlled comparison between:

* scanning a standalone binary
* scanning a package-managed filesystem or container that contains that binary

Use a controlled container or root filesystem. Do not scan the host `/`.

Possible targets:

* `curl`
* `openssl`
* `ffmpeg`

Compare:

* package artifacts from binary scan
* package artifacts from filesystem scan
* imported libraries from binary scan
* whether package manager metadata changes Syft's output

Expected interpretation:

Standalone binary scans depend heavily on binary classifiers and available
binary evidence. Filesystem scans may find more package components because
package metadata is available.

Purpose:

This shows that Syft's behavior changes when package-manager metadata is
available, which is different from binary-only analysis.

## Final Phase 2 Write-Up

After this phase of work, create:

* `docs/phase2_findings.md`


## Deliverables Checklist

* [ ] `docs/phase1_results.md`
* [ ] reproduced rename test evidence
* [ ] Syft 1.44.0 vs 1.45.1 comparison
* [ ] `docs/syft_classifier_notes.md`
* [ ] `docs/classifier_signal_matrix.md`
* [ ] `scripts/evidence_report.py`
* [ ] one standalone binary vs filesystem-context comparison
* [ ] `docs/phase2_findings.md`
