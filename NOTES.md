# Research Notes

## Project Direction

Dr. Kim wants this project to focus on C/C++ binaries for now. Go
binaries may be easier for SBOM tools because they often include more metadata,
but this project should stay focused on the harder C/C++ binary analysis case.

## Initial Syft Tests
Syft finds much more when source/project metadata is available, but binary-only extraction is harder and produces less package-level information.

When scanning `/bin/ls` as a single binary, Syft found ELF metadata and imported libraries but reported zero package artifacts.

For `/bin/ls`, Syft reported zero package artifacts, but its imported library detection matched the ELF `NEEDED` entries: `libcap.so.2` and `libc.so.6`.

Syft has the following formats:
* table
* text
* syft-json
* cyclonedx-json
* spdx-json

- If Syft reports an artifact, it is saying it found an SBOM component.
- If Syft only reports an imported library, it found evidence of linking, but not a full package/component entry.

## Initial Controlled Binary Results

I tested Syft 1.44.0 on several small compiled C binaries: hello, math-test,
zlib-test, openssl-test, curl-test, sqlite-test, and /bin/ls.

For every standalone binary, Syft reported zero package artifacts:

- hello: 0 artifacts
- math-test: 0 artifacts
- zlib-test: 0 artifacts
- openssl-test: 0 artifacts
- curl-test: 0 artifacts
- sqlite-test: 0 artifacts
- /bin/ls: 0 artifacts

However, Syft did detect ELF imported libraries for each binary:

- hello: libc.so.6
- math-test: libm.so.6, libc.so.6
- zlib-test: libz.so.1, libc.so.6
- openssl-test: libcrypto.so.3, libc.so.6
- curl-test: libcurl.so.4, libc.so.6
- sqlite-test: libsqlite3.so.0, libc.so.6
- /bin/ls: libcap.so.2, libc.so.6

I verified the imported libraries with `readelf -d`, and Syft's `importedLibraries` matched the ELF `NEEDED` entries for these samples.

Observation: when scanning standalone C binaries, Syft may not identify SBOM
package artifacts, even when the binary clearly links to libraries such as zlib,
OpenSSL, curl, or sqlite. The useful data appears under ELF file metadata rather
than under the main `artifacts` package list.

## Fastfetch Result

I built and scanned Fastfetch, a larger real-world C project.

Build commands used:

```sh
mkdir -p build
cd build
cmake ..
cmake --build . --target fastfetch
```

No custom CMake options were passed. This means Fastfetch was built using the
default detected configuration on this system.

Important caveat: Fastfetch's build documentation says that if the build process
does not find the headers for an optional dependency, Fastfetch will build
without support for that feature. Because of this, this binary may not include
all possible Fastfetch features or dependencies.

Fastfetch version tested: `2.63.1-108`.

Syft reported zero package artifacts for the standalone Fastfetch binary.
However, Syft detected the ELF imported libraries:

- `libm.so.6`
- `libc.so.6`

I verified this with `readelf -d data/binaries/fastfetch`, and Syft's
`importedLibraries` matched the ELF `NEEDED` entries exactly.

Observation: even for a larger C project, scanning only the standalone binary
did not produce package-level SBOM artifacts. Syft still captured direct ELF
shared library imports correctly.

## FreeRTOS Kernel Result

I cloned FreeRTOS-Kernel temporarily and built the included CMake example.

Build commands used:

```sh
cmake -S FreeRTOS-Kernel/examples/cmake_example -B FreeRTOS-Kernel/examples/cmake_example/build
cmake --build FreeRTOS-Kernel/examples/cmake_example/build
```

FreeRTOS-Kernel commit tested: `d877cd539`.

The build produced two useful binary artifacts:

- `freertos-cmake-example`: Linux ELF executable
- `libfreertos_kernel.a`: static library archive

I copied them into `data/binaries/` and scanned them with Syft.

For `freertos-cmake-example`, Syft reported zero package artifacts. Syft
detected one imported library:

- `libc.so.6`

I verified this with `readelf -d data/binaries/freertos-cmake-example`, and
Syft's `importedLibraries` matched the ELF `NEEDED` entry exactly.

For `libfreertos_kernel.a`, Syft reported zero package artifacts and no file
records. The archive contains object files such as `tasks.c.o`, `queue.c.o`,
`timers.c.o`, `heap_4.c.o`, and `port.c.o`, but Syft did not convert those into
SBOM package artifacts.

Observation: the FreeRTOS example is useful because it tests an embedded-style C
project and a static library archive. The executable result matches the earlier
pattern, binary-only scanning did not produce package-level artifacts, but ELF
imported-library detection was correct.

## pgvector Result

I built pgvector and copied the PostgreSQL extension shared library into
`data/binaries/vector.so`.

The artifact is an ELF shared object, not a standalone executable:

- `vector.so`: PostgreSQL extension shared library
- pgvector version string found in the binary: `0.8.2`
- compiler string: `GCC 16.1.1`

Syft reported zero package artifacts for `vector.so`. Syft detected one imported
library:

- `libc.so.6`

I verified this with `readelf -d data/binaries/vector.so`, and Syft's
`importedLibraries` matched the ELF `NEEDED` entry exactly.

Observation: pgvector is a useful test case because it is a real C project that
produces a plugin-style `.so` shared library instead of a normal executable.
The binary-only Syft result still did not produce package-level artifacts, but
ELF imported-library detection was correct.

## zstd Result

I cloned and built zstd using CMake.

Build commands used:

```sh
cmake -S . -B build-cmake
cmake --build build-cmake
```

zstd commit tested: `5233c58e`.

The build produced several useful C binary artifacts:

- `zstd`: main command-line executable
- `unzstd`: decompression executable
- `zstdcat`: cat-style decompression executable
- `zstdmt`: multi-threaded executable
- `zstd-frugal`: smaller command-line executable
- `libzstd.so.1.6.0`: shared library
- `libzstd.a`: static library archive

I copied these into `data/binaries/` and scanned them with Syft.

Syft results:

| Artifact | Syft package artifacts | Imported libraries |
| --- | --- | --- |
| `zstd` | `zstd` version `1.6.0`, type `binary` | `libc.so.6` |
| `unzstd` | none | `libc.so.6` |
| `zstdcat` | none | `libc.so.6` |
| `zstdmt` | none | `libc.so.6` |
| `zstd-frugal` | none | `libc.so.6` |
| `libzstd.so.1.6.0` | none | `libc.so.6` |
| `libzstd.a` | none | none |

I verified the imported libraries for the ELF executable/shared-library files
with `readelf -d`, and Syft's `importedLibraries` matched the ELF `NEEDED`
entries.

Observation: zstd is the first test case where Syft identified a package-level
SBOM artifact from a C binary. Syft recognized the main `zstd`
executable as `zstd` version `1.6.0`, type `binary`. However, Syft did not
identify package artifacts for related executables with different names, the
shared library, or the static archive.

Compared to the other C binaries, `zstd` is the first case where Syft produced a
package-level SBOM artifact from binary-only scanning. The difference is that
Syft has a specific `zstd-binary` classifier. Other binaries, including
Fastfetch, pgvector, FreeRTOS, and the small test programs, were treated as
generic ELF files: Syft detected imported libraries but did not identify
package-level SBOM artifacts.

UP NEXT:
jqlang/jq
curl/curl
nginx/nginx
memcached/memcached
openssl/openssl
tukaani-project/xz
