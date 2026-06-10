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
- `scripts/compare_sbom.py`: compares expected components with Syft output
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
     ]
   }
   ```

3. Run Syft:

   ```sh
   syft ./path/to/binary -o syft-json > data/syft-output/example.syft.json
   ```

4. Compare the expected components with Syft's output:

   ```sh
   python3 scripts/compare_sbom.py \
     data/ground-truth/example.json \
     data/syft-output/example.syft.json
   ```

## Accuracy Terms

- true positive: Syft found a component that should be there
- false positive: Syft reported a component that should not be there
- false negative: Syft missed a component that should be there
- precision: how many reported components were correct
- recall: how many expected components were found

## Docker Environment

Use Docker when working from a MacBook or when you want reproducible Linux
results. The image installs common C/C++ build tools, development headers,
`readelf`, `jq`, Syft `1.44.0`, and Codex CLI `0.125.0`.

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

To use Codex inside the container, authenticate inside the container:

```sh
codex login
codex
```

Do not copy Codex credentials into the Docker image. If you want to reuse your
host Codex login instead, mount only your local auth file when starting the
container:

```sh
docker run --rm -it \
  -v "$PWD":/work \
  -v "$HOME/.codex/auth.json":/root/.codex/auth.json:ro \
  -w /work \
  sbom-research
```

You can also use Docker Compose:

```sh
docker compose -f docker/compose.yaml run --rm research
```

## Dev Container

This repo also includes a Dev Container config for editors that support it,
including Zed.

Open the project in the editor and choose the option to reopen the project in a
container. The config is in:

```text
.devcontainer/devcontainer.json
```

The Dev Container uses the same Dockerfile in `docker/Dockerfile` and mounts
the repo at `/work` inside the container.
