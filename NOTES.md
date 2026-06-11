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

## curl Result

I cloned and built curl using CMake.

Build commands used:

```sh
cmake -S data/binaries/curl -B data/binaries/curl/build-cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CURL_EXE=ON \
  -DBUILD_EXAMPLES=OFF \
  -DBUILD_TESTING=OFF \
  -DBUILD_LIBCURL_DOCS=OFF \
  -DBUILD_MISC_DOCS=OFF \
  -DENABLE_CURL_MANUAL=OFF
cmake --build data/binaries/curl/build-cmake --target curl --parallel
```

curl commit tested: `97aed9c960`.

The built executable reports:

```text
curl 8.21.0-DEV (Linux) libcurl/8.21.0-DEV OpenSSL/3.6.3 zlib/1.3.1.zlib-ng brotli/1.2.0 zstd/1.5.7 libidn2/2.3.8 libpsl/0.21.5 libssh2/1.11.1 nghttp2/1.69.0 OpenLDAP/2.6.13
```

I copied the useful test artifacts into `data/binaries/curl-cmake/`:

- `curl`
- `libcurl.so.4.8.0`

Syft results:

| Artifact | Syft package artifacts | Imported libraries |
| --- | --- | --- |
| `curl` | `curl` version `8.21.0`, type `binary` | `libcurl.so.4`, `libssl.so.3`, `libcrypto.so.3`, `libz.so.1`, `libssh2.so.1`, `libidn2.so.0`, `libldap.so.2`, `liblber.so.2`, `libbrotlidec.so.1`, `libbrotlicommon.so.1`, `libzstd.so.1`, `libnghttp2.so.14`, `libpsl.so.5`, `libc.so.6` |
| `libcurl.so.4.8.0` | none | `libssl.so.3`, `libcrypto.so.3`, `libz.so.1`, `libssh2.so.1`, `libidn2.so.0`, `libldap.so.2`, `liblber.so.2`, `libbrotlidec.so.1`, `libbrotlicommon.so.1`, `libzstd.so.1`, `libnghttp2.so.14`, `libpsl.so.5`, `libc.so.6` |

I verified the imported libraries with `readelf -d`, and Syft's
`importedLibraries` matched the ELF `NEEDED` entries exactly.

Observation: curl is another case where Syft has a binary classifier and can
identify a package-level artifact from a C executable. However, Syft reported
version `8.21.0` while the built binary reports `8.21.0-DEV`, so the package
name was correct but the version was not exact. Syft did not identify a package
artifact for the standalone `libcurl.so.4.8.0` shared library.

Additional observation: when the same curl executable was copied to the filename
`curl-built`, Syft no longer reported the `curl` package artifact. This suggests
the binary classifier may depend partly on the executable filename, not only the
binary contents.

## jq Linux Binary Result

I tested the existing `jq-linux-amd64` binary.

The binary reports:

```text
jq-1.8.1
```

The binary is a stripped, statically linked ELF executable. Because it is
statically linked, `readelf -d` reported no dynamic `NEEDED` library entries.

I tested two filenames with identical binary contents:

- `data/binaries/jq-linux-amd64`
- `data/binaries/jq-linux/jq`

Both files have the same SHA-256:

```text
020468de7539ce70ef1bceaf7cde2e8c4f2ca6c3afb84642aabc5c97d9fc2a0d
```

Syft results:

| Artifact | Syft package artifacts | Imported libraries |
| --- | --- | --- |
| `jq-linux-amd64` | none | none |
| `jq` | `jq` version `1.8.1`, type `binary` | none |

I verified the imported-library result with `readelf -d`. Syft reported no
`importedLibraries`, which matched the absence of ELF `NEEDED` entries.

Observation: this is a strong example of filename-sensitive package detection.
Syft did not identify a package artifact when the binary was named
`jq-linux-amd64`, but it identified the exact same binary as `jq` version
`1.8.1` when the filename was changed to `jq`.

## nginx Result

I cloned and built nginx locally from source.

Build commands used:

```sh
./auto/configure --builddir=build-local \
  --prefix=/home/tylerg/sbom-research/nginx/build-install \
  --sbin-path=/home/tylerg/sbom-research/nginx/build-install/sbin/nginx \
  --with-http_ssl_module \
  --with-http_v2_module \
  --with-http_gzip_static_module \
  --with-http_stub_status_module \
  --with-threads \
  --with-pcre-jit
make -f build-local/Makefile -j$(nproc)
```

nginx commit tested: `bedf18f95`.

The built executable reports:

```text
nginx version: nginx/1.31.2
built by gcc 16.1.1 20260430 (GCC)
built with OpenSSL 3.6.3 9 Jun 2026
```

I copied the useful test artifact into `data/binaries/nginx-local/`:

- `nginx`

Syft results:

| Artifact | Syft package artifacts | Imported libraries |
| --- | --- | --- |
| `nginx` | `nginx` version `1.31.2`, type `binary` | `libcrypt.so.2`, `libpcre2-8.so.0`, `libssl.so.3`, `libcrypto.so.3`, `libz.so.1`, `libc.so.6` |

I verified the imported libraries with `readelf -d`, and Syft's
`importedLibraries` matched the ELF `NEEDED` entries exactly.

Comparison script result:

- package artifact precision: `1.0`
- package artifact recall: `1.0`
- package version accuracy: `1.0`
- imported-library precision: `1.0`
- imported-library recall: `1.0`

Observation: nginx is another C binary where Syft has a specific binary
classifier. Syft identified the package artifact, version, package URL, and CPE
candidates from the executable, and the ELF imported-library evidence matched
`readelf`.

UP NEXT:
memcached/memcached
openssl/openssl
tukaani-project/xz
