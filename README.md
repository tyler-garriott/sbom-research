# SBOM Research

This is a beginner research project about Software Bills of Materials, or
SBOMs.

The starting question:

> Can Syft correctly identify the software components inside a compiled binary?

## What This Means

An SBOM is a list of the software parts inside a program. For example, a
program might use OpenSSL, zlib, curl, or other libraries.

This project compares:

- what components should be in a program
- what Syft says is in the program

## Repo Files

- `samples/`: small C programs used to create test binaries
- `data/ground-truth/example.json`: example expected components
- `data/syft-output/`: place to save Syft output
- `scripts/compare_sbom.py`: compares expected package artifacts and ELF imports with Syft output
- `docker/`: reproducible Linux environment for building and scanning binaries
- `scripts/`: utility scripts for building samples and comparing Syft output
- `docs/`: notes and documentation


## Ground Truth Fields

Ground-truth files separate two different questions:

- `components`: package/component identities that you expect Syft to report
  under `artifacts`. These are names like `zstd`, `openssl`, `pgvector`, or
  `fastfetch`.
- `imported_libraries`: ELF shared libraries that you expect Syft to report
  under `files[].executable.importedLibraries`. These are names from
  `readelf -d`, such as `libcrypto.so.3`, `libz.so.1`, or `libc.so.6`.

Do not treat an imported library name as the same thing as a package artifact.
For example, `openssl` is a package/component expectation, while
`libcrypto.so.3` is binary dependency evidence.

## Accuracy Terms

The comparison script reports two separate measurements:

- `package_artifacts`: whether Syft emitted expected SBOM package/component records under `artifacts`
- `imported_libraries`: whether Syft extracted expected ELF `NEEDED` entries under `files[].executable.importedLibraries`

## Docker Environment

Use Docker when working from a MacBook or when you want reproducible Linux
results. The image installs common C/C++ build tools, development headers,
`readelf`, `jq`, and the latest Syft release available when the image is built.
Record `syft version` with any new experiment results.

Build the image:

```sh
docker build -t sbom-research docker
```

Run it from the repo root:

```sh
docker run --rm -it -v "$PWD":/work -w /work sbom-research
```

On an Apple Silicon Mac, use `linux/amd64` for results comparable with
the current x86-64 Linux results:

```sh
docker build --platform linux/amd64 -t sbom-research docker
docker run --platform linux/amd64 --rm -it -v "$PWD":/work -w /work sbom-research
```

You can also use Docker Compose:

```sh
docker compose -f docker/compose.yaml run --rm research
```

Inside the container, a minimal scan workflow is:

```sh
bash scripts/build_samples.sh
syft data/binaries/zlib-test -o syft-json=data/syft-output/zlib-test.json
readelf -d data/binaries/zlib-test
```

## Dev Container

This repo also includes a Dev Container config for editors that support it.

Open the project in the editor and choose the option to reopen the project in a
container. The config is in:

```text
.devcontainer/devcontainer.json
```

The Dev Container uses the same Dockerfile in `docker/Dockerfile` and mounts
the repo at `/work` inside the container.

## Next Phase

The Phase 2 plan is in:

```text
docs/phase_2.md
```

It focuses on investigating Syft's binary classifiers, reproducing the strongest
rename tests, comparing Syft versions, and separating package artifacts, ELF
imports, and string evidence.
