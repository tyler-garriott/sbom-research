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

## memcached Result

I tested the locally cloned and built memcached executable.

memcached commit tested: `f1674f023`.

The built executable reports:

```text
memcached 1.6.42
```

The artifact is an ELF executable:

- ELF 64-bit LSB PIE executable
- dynamically linked
- contains debug info
- not stripped

I copied two test artifacts into `data/binaries/memcached-local/`:

- `memcached`
- `memcached-built`

Both files have the same SHA-256:

```text
9b05cffb0b47312f2525207a07d8321187618ddaafd56bc01fcd7b43fcdb2e19
```

Syft results:

| Artifact | Syft package artifacts | Imported libraries |
| --- | --- | --- |
| `memcached` | `memcached` version `1.6.42`, type `binary` | `libevent-2.1.so.7`, `libc.so.6` |
| `memcached-built` | none | `libevent-2.1.so.7`, `libc.so.6` |

For the normal `memcached` filename, Syft also reported:

- package URL: `pkg:generic/memcached@1.6.42`
- CPE candidate: `cpe:2.3:a:memcached:memcached:1.6.42:*:*:*:*:*:*:*`

I verified the imported libraries with `readelf -d`, and Syft's
`importedLibraries` matched the ELF `NEEDED` entries exactly for both files.

Comparison script results:

| Sample | Package precision | Package recall | Version accuracy | Imported-library precision | Imported-library recall |
| --- | --- | --- | --- | --- | --- |
| `memcached-local` | `1.0` | `1.0` | `1.0` | `1.0` | `1.0` |
| `memcached-built` | null | `0.0` | null | `1.0` | `1.0` |

Observation: memcached is another C binary where Syft has a specific binary
classifier. With the expected filename, Syft identified the package artifact,
version, package URL, and CPE candidate. However, the identical binary copied to
the filename `memcached-built` did not produce a package artifact. This is
another strong filename-sensitivity result. The ELF imported-library evidence
was still correct for both filenames.

## OpenSSL Result

I cloned and built OpenSSL locally from source.

Build commands used:

```sh
./Configure \
  --prefix=/home/tylerg/sbom-research/openssl/build-install \
  --openssldir=/home/tylerg/sbom-research/openssl/build-install/ssl \
  no-tests
make -j$(nproc) build_sw
```

Important build note: building the direct `apps/openssl` target first failed
because generated local headers such as `include/openssl/bio.h`,
`include/openssl/ssl.h`, and `include/openssl/x509.h` did not exist yet. The
compiler then picked up system OpenSSL headers from `/usr/include/openssl`,
which mixed incompatible headers with this checkout. The broader `build_sw`
target generated the needed local headers and built the executable correctly.

OpenSSL commit tested: `1f1ce7cad`.

The built executable reports:

```text
OpenSSL 4.1.0-dev  (Library: OpenSSL 4.1.0-dev )
```

The artifact is an ELF executable:

- ELF 64-bit LSB PIE executable
- dynamically linked
- not stripped

I copied two test artifacts into `data/binaries/openssl-local/`:

- `openssl`
- `openssl-built`

Both files have the same SHA-256:

```text
dd4e930437a5ada5d6ca37823a6cd703c90bb2418828f82334f6a1c369e7fed5
```

Syft results:

| Artifact | Syft package artifacts | Imported libraries |
| --- | --- | --- |
| `openssl` | `openssl` version `4.1.0`, type `binary` | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |
| `openssl-built` | none | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |

For the normal `openssl` filename, Syft also reported:

- package URL: `pkg:generic/openssl@4.1.0`
- CPE candidate: `cpe:2.3:a:openssl:openssl:4.1.0:*:*:*:*:*:*:*`

I verified the imported libraries with `readelf -d`, and Syft's
`importedLibraries` matched the ELF `NEEDED` entries exactly for both files.

Comparison script results:

| Sample | Package precision | Package recall | Version accuracy | Imported-library precision | Imported-library recall |
| --- | --- | --- | --- | --- | --- |
| `openssl-local` | `1.0` | `1.0` | `0.0` | `1.0` | `1.0` |
| `openssl-built` | null | `0.0` | null | `1.0` | `1.0` |

Observation: OpenSSL is another C binary where Syft has a specific binary
classifier. With the expected filename, Syft identified the package artifact,
package URL, and CPE candidate. However, Syft reported version `4.1.0` while the
built binary reports `4.1.0-dev`, so the package name was correct but the
version was not exact. The identical binary copied to the filename
`openssl-built` did not produce a package artifact. The ELF imported-library
evidence was still correct for both filenames.

## xz Result

I cloned and built xz locally from source using CMake.

Build commands used:

```sh
cmake -S xz -B xz/build-cmake -DCMAKE_BUILD_TYPE=Release
cmake --build xz/build-cmake --target xz --parallel
```

xz commit tested: `e95cd90da`.

The built executable reports:

```text
xz (XZ Utils) 5.8.3
liblzma 5.8.3
```

The artifact is an ELF executable:

- ELF 64-bit LSB PIE executable
- dynamically linked
- not stripped

The CMake build produced `xz/build-cmake/liblzma.a`, and the `xz` executable
linked the xz/liblzma code into the executable rather than importing a dynamic
`liblzma.so` library. Because of this, the ELF dynamic imports only showed
`libc.so.6`.

I copied two test artifacts into `data/binaries/xz-local/`:

- `xz`
- `xz-built`

Both files have the same SHA-256:

```text
edfb2eeae33a745e6dcdce3a818ae2604a3374077fc530271ae2d32316afe605
```

Syft results:

| Artifact | Syft package artifacts | Imported libraries |
| --- | --- | --- |
| `xz` | `xz` version `5.8.3`, type `binary` | `libc.so.6` |
| `xz-built` | none | `libc.so.6` |

For the normal `xz` filename, Syft also reported:

- package URL: `pkg:generic/xz@5.8.3`
- CPE candidate: `cpe:2.3:a:tukaani:xz:5.8.3:*:*:*:*:*:*:*`

I verified the imported libraries with `readelf -d`, and Syft's
`importedLibraries` matched the ELF `NEEDED` entries exactly for both files.

Comparison script results:

| Sample | Package precision | Package recall | Version accuracy | Imported-library precision | Imported-library recall |
| --- | --- | --- | --- | --- | --- |
| `xz-local` | `1.0` | `1.0` | `1.0` | `1.0` | `1.0` |
| `xz-built` | null | `0.0` | null | `1.0` | `1.0` |

Observation: xz is another C binary where Syft has a specific binary
classifier. With the expected filename, Syft identified the package artifact,
version, package URL, and CPE candidate. However, the identical binary copied to
the filename `xz-built` did not produce a package artifact. The ELF
imported-library evidence was still correct for both filenames.

## Controlled Syft Tests

I ran a small controlled follow-up to test whether the filename result depends
on basename, parent path, debug symbols, or dynamic linking behavior. The full
short write-up is in `comparison.md`.

Tool version:

```text
syft 1.44.0
```

### OpenSSL basename and parent-path controls

I copied the same OpenSSL binary into four paths:

| Test file | SHA-256 | Syft package artifacts | Imported libraries |
| --- | --- | --- | --- |
| `data/binaries/controlled-paths/basename/openssl` | `dd4e930437a5ada5d6ca37823a6cd703c90bb2418828f82334f6a1c369e7fed5` | `openssl` version `4.1.0`, type `binary` | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |
| `data/binaries/controlled-paths/basename/openssl-built` | same | none | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |
| `data/binaries/controlled-paths/random-parent/openssl` | same | `openssl` version `4.1.0`, type `binary` | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |
| `data/binaries/controlled-paths/openssl-parent/openssl-built` | same | none | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |

Observation: the basename `openssl` was enough for Syft to identify the package
artifact, even under a random parent directory. Renaming the same bytes to
`openssl-built` suppressed the package artifact, even when the parent directory
contained `openssl` in its name. This points more strongly to basename-sensitive
binary classification than to general path context.

### Stripped OpenSSL controls

I stripped two OpenSSL copies with `strip --strip-all`:

| Test file | SHA-256 | Syft package artifacts | Imported libraries |
| --- | --- | --- | --- |
| `data/binaries/controlled-strip/openssl` | `d3313b26c828bd4e8c5c696db2d414126093bcaacdcd7fcc92684aab61321413` | `openssl` version `4.1.0`, type `binary` | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |
| `data/binaries/controlled-strip/openssl-built` | same | none | `libssl.so.4`, `libcrypto.so.4`, `libc.so.6` |

Observation: stripping did not stop Syft from identifying OpenSSL when the
basename was `openssl`. The stripped copy named `openssl-built` still produced
no package artifact. For this binary, the package artifact result is not simply
dependent on debug symbols.

### Small linking controls

I also built small dynamic and static test binaries:

| Test file | Link style | Syft package artifacts | Imported libraries |
| --- | --- | --- | --- |
| `data/binaries/controlled-linking/zlib-test-dynamic` | dynamic | none | `libz.so.1`, `libc.so.6` |
| `data/binaries/controlled-linking/hello-dynamic` | dynamic | none | `libc.so.6` |
| `data/binaries/controlled-linking/hello-static` | static | none | none |

The static `zlib-test` build failed because the static `libz.a` library is not
installed in this environment:

```text
/usr/bin/ld: cannot find -lz: No such file or directory
```

Observation: Syft extracted dynamic ELF `NEEDED` entries as imported libraries.
The statically linked `hello-static` binary had no dynamic section, and Syft
reported no imported libraries. The dynamic zlib sample imported `libz.so.1`,
but Syft did not turn that imported library into a package artifact named
`zlib`.

## FFmpeg System Binary Result

I tested the system `ffmpeg` executable as a larger real-world C/C++ case study.

The source binary was:

```text
/usr/bin/ffmpeg
```

The copied artifacts are:

- `data/binaries/ffmpeg-system/ffmpeg`
- `data/binaries/ffmpeg-system/ffmpeg-renamed`

Both files have the same SHA-256:

```text
bac0566dbe413e9af0a1bfd700abd941f2537545b0d76e0c7ce120dd29272407
```

The binary is:

- ELF 64-bit LSB PIE executable
- dynamically linked
- stripped

The copied executable reports:

```text
ffmpeg version n8.1.2
built with gcc 16.1.1 (GCC) 20260430
```

The `ffmpeg -version` output also reports a long build configuration with many
enabled libraries, including `--enable-libx264`, `--enable-libx265`,
`--enable-libvpx`, `--enable-libwebp`, `--enable-libxml2`, `--enable-libssh`,
and many others. This is build configuration evidence, not the same thing as ELF
dynamic import evidence.

`readelf -d` showed the same ELF `NEEDED` entries for both copied files:

```text
libavdevice.so.62
libavfilter.so.11
libavformat.so.62
libavcodec.so.62
libswresample.so.6
libswscale.so.9
libavutil.so.60
libm.so.6
libz.so.1
libc.so.6
```

Syft results:

| Artifact | Syft package artifacts | Imported libraries |
| --- | --- | --- |
| `ffmpeg` | none | `libavdevice.so.62`, `libavfilter.so.11`, `libavformat.so.62`, `libavcodec.so.62`, `libswresample.so.6`, `libswscale.so.9`, `libavutil.so.60`, `libm.so.6`, `libz.so.1`, `libc.so.6` |
| `ffmpeg-renamed` | none | `libavdevice.so.62`, `libavfilter.so.11`, `libavformat.so.62`, `libavcodec.so.62`, `libswresample.so.6`, `libswscale.so.9`, `libavutil.so.60`, `libm.so.6`, `libz.so.1`, `libc.so.6` |

Comparison script results:

| Sample | Package precision | Package recall | Version accuracy | Imported-library precision | Imported-library recall |
| --- | --- | --- | --- | --- | --- |
| `ffmpeg-system` | null | `0.0` | null | `1.0` | `1.0` |
| `ffmpeg-renamed` | null | `0.0` | null | `1.0` | `1.0` |

Observation: this larger real-world binary reinforces the separation between
three evidence types. The executable's own version output describes many
enabled build features, `readelf` and Syft both show the directly imported
shared libraries, but Syft did not report a package artifact for the top-level
`ffmpeg` executable. The renamed copy produced the same result because there was
no package artifact for the expected filename either.

## Syft Filename-Sensitivity Summary

The strongest pattern so far is that Syft's package-level binary classifiers
are sensitive to the filename or path basename. In several tests, two files had
identical bytes and identical ELF imported libraries, but Syft reported a
package artifact for one filename and no package artifact for the other.

Byte-identical filename tests:

| Component | Filenames tested | Expected-name result | Alternate-name result | Version exact? | Imported libraries |
| --- | --- | --- | --- | --- | --- |
| `curl` | `curl`, `curl-built` | found `curl` | none | no: `8.21.0` vs `8.21.0-DEV` | exact |
| `jq` | `jq`, `jq-linux-amd64` | found `jq` | none | yes | exact, no imports |
| `memcached` | `memcached`, `memcached-built` | found `memcached` | none | yes | exact |
| `openssl` | `openssl`, `openssl-built` | found `openssl` | none | no: `4.1.0` vs `4.1.0-dev` | exact |
| `xz` | `xz`, `xz-built` | found `xz` | none | yes | exact |

The zstd results point in the same direction, although they are not a
byte-identical rename test. Syft found a package artifact for the main `zstd`
executable but did not identify related zstd build artifacts such as `unzstd`,
`zstdcat`, `zstdmt`, `zstd-frugal`, `libzstd.so.1.6.0`, or `libzstd.a`.

Current interpretation: the evidence so far suggests Syft is not doing general
C/C++ binary composition analysis that recognizes a component from arbitrary
compiled code. For these cases, package artifact detection appears to depend on
Syft having a specific binary classifier and on the scanned file matching the
classifier's expected filename or path pattern. The same binary contents under a
different filename can lose the package-level SBOM component.

This does not affect Syft's ELF imported-library extraction. Across these
filename tests, Syft's `files[].executable.importedLibraries` output stayed
consistent and matched the ELF `NEEDED` entries from `readelf -d`.

## Results so far
Syft seems to be able to identify some known C/C++ binaries as package
artifacts, but this appears to depend heavily on specific binary classifiers,
filename/path basename expectations, and version strings. It reliably extracts
ELF imported libraries, but that is dependency evidence, not full binary
composition analysis.

The larger `ffmpeg` case study fits this interpretation. Syft did not identify
the top-level `ffmpeg` package artifact at all, but it did exactly extract the
direct ELF imports. The program's build configuration listed many more enabled
libraries than the direct ELF `NEEDED` list, which is another reminder that
different evidence sources answer different questions.

## Up Next

The experimental evidence is probably sufficient. The next work should focus on
turning the results into a clear, reproducible write-up rather than collecting
more random binaries.

Tomorrow's checklist:

1. Freeze the main claim:

   ```text
   Syft can identify some known C/C++ binaries as package artifacts, but this is
   classifier and filename dependent. Syft reliably extracts ELF imported
   libraries, but imported libraries are dependency evidence, not full SBOM
   component detection.
   ```

2. Create a clean `RESULTS.md` or expand `README.md` with:

   - research question
   - method
   - tested binaries
   - main result table
   - controlled filename/path tests
   - FFmpeg case study
   - conclusion
   - limitations

3. Add a small summary script, for example:

   ```sh
   python3 scripts/summarize_syft.py data/syft-output/ffmpeg-system/ffmpeg.json
   ```

   The script should print:

   - package artifacts
   - imported libraries
   - artifact count
   - imported-library count

4. Optional final contrast test:

   Compare scanning a single binary file with scanning a package-managed
   filesystem or root directory. This could show that Syft may detect packages
   from package metadata during a filesystem scan, which is different from
   identifying components from one compiled binary.
