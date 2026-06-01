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

- `data/ground-truth/example.json`: example expected components
- `data/syft-output/`: place to save Syft output
- `scripts/compare_sbom.py`: compares expected components with Syft output

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
