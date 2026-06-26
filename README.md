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

## First Experiment

1. Pick a small binary or package.
2. Write the expected components in a ground-truth file:

   ```json
   {
     "sample": "example",
     "components": [
       {
         "name": "openssl",
         "version": "3.0.13"
       }
     ],
     "imported_libraries": [
       "libcrypto.so.3",
       "libc.so.6"
     ]
   }
   ```

3. Run Syft:

   ```sh
   syft ./path/to/binary -o syft-json > data/syft-output/example.syft.json
   ```

4. Compare the expected package artifacts and imported libraries with Syft's output:

   ```sh
   python3 scripts/compare_sbom.py \
     data/ground-truth/example.json \
     data/syft-output/example.syft.json
   ```

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

For each measurement:

- true positive: Syft found an item that should be there
- false positive: Syft reported an item that should not be there
- false negative: Syft missed an item that should be there
- precision: how many reported items were correct
- recall: how many expected items were found

For package artifacts, precision and recall are based on component names.
`version_accuracy` is reported separately when the ground truth includes
expected versions. Package `exact_match` is false if a required version does not
match.

## Docker Environment

Use Docker when working from a MacBook or when you want reproducible Linux
results. The image installs common C/C++ build tools, development headers,
`readelf`, `jq`, and Syft `1.44.0`.

Build the image:

```sh
docker build -t sbom-research docker
```

Run it from the repo root:

```sh
docker run --rm -it -v "$PWD":/work -w /work sbom-research
```

On an Apple Silicon Mac, use `linux/amd64` if you want results comparable with
the current x86-64 Linux results:

```sh
docker build --platform linux/amd64 -t sbom-research docker
docker run --platform linux/amd64 --rm -it -v "$PWD":/work -w /work sbom-research
```

Inside the container, build the starter samples:

```sh
bash scripts/build_samples.sh
```

Then scan a binary:

```sh
syft data/binaries/zlib-test -o syft-json=data/syft-output/zlib-test.json
readelf -d data/binaries/zlib-test
```

You can also use Docker Compose:

```sh
docker compose -f docker/compose.yaml run --rm research
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
