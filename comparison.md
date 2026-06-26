# Controlled Syft Tests

Date: 2026-06-25

Tool:

```text
syft 1.44.0
```

These tests check whether Syft's binary package detection changes when the same
bytes are moved, renamed, stripped, or linked differently.

## 1. OpenSSL Filename And Path Controls

All four OpenSSL path-control files are byte-identical:

```text
dd4e930437a5ada5d6ca37823a6cd703c90bb2418828f82334f6a1c369e7fed5
```

| Test file | Syft package artifacts | Syft imported libraries |
| --- | --- | --- |
| `data/binaries/controlled-paths/basename/openssl` | `openssl` `4.1.0`, type `binary` | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |
| `data/binaries/controlled-paths/basename/openssl-built` | none | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |
| `data/binaries/controlled-paths/random-parent/openssl` | `openssl` `4.1.0`, type `binary` | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |
| `data/binaries/controlled-paths/openssl-parent/openssl-built` | none | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |

Observation: for this OpenSSL binary, the basename `openssl` is enough for Syft
to report the package artifact, even under a random parent directory. Renaming
the same bytes to `openssl-built` suppresses the package artifact, even under a
parent directory named `openssl-parent`. The ELF imported-library result is
unchanged across all four files.

## 2. Stripped OpenSSL Controls

The stripped OpenSSL copies are byte-identical to each other:

```text
d3313b26c828bd4e8c5c696db2d414126093bcaacdcd7fcc92684aab61321413
```

| Test file | Syft package artifacts | Syft imported libraries |
| --- | --- | --- |
| `data/binaries/controlled-strip/openssl` | `openssl` `4.1.0`, type `binary` | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |
| `data/binaries/controlled-strip/openssl-built` | none | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |

Observation: stripping did not stop Syft from identifying OpenSSL when the file
basename was `openssl`. The renamed stripped copy still produced no package
artifact. This suggests the OpenSSL result is not simply dependent on debug
symbols.

## 3. Small Linking Controls

| Test file | Link style | Syft package artifacts | Syft imported libraries |
| --- | --- | --- | --- |
| `data/binaries/controlled-linking/zlib-test-dynamic` | dynamic | none | `libz.so.1`, `libc.so.6` |
| `data/binaries/controlled-linking/hello-dynamic` | dynamic | none | `libc.so.6` |
| `data/binaries/controlled-linking/hello-static` | static | none | none |

Static `zlib-test` could not be built in this environment because the static
`libz.a` library is not installed:

```text
/usr/bin/ld: cannot find -lz: No such file or directory
```

Observation: Syft extracted dynamic ELF `NEEDED` entries as imported libraries.
The statically linked `hello-static` binary had no dynamic section, and Syft
reported no imported libraries. The dynamic zlib sample imported `libz.so.1`,
but Syft did not turn that into a package artifact named `zlib`.

## Current Interpretation

These controls strengthen the earlier filename-sensitivity result. For the
OpenSSL binary, package-level detection appears tied strongly to the executable
basename. Path parent names did not rescue detection after a rename, and
stripping did not break detection when the basename stayed `openssl`.

The ELF imported-library extractor behaved separately and consistently: when a
dynamic binary had `NEEDED` entries, Syft reported them; when a static binary had
no dynamic section, Syft reported no imported libraries.

The practical takeaway is that Syft is reliable here for ELF dynamic import
evidence, but package artifact detection for C/C++ binaries should not be
treated as general binary composition analysis.
