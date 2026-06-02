# Research Notes

## Initial Syft Tests

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
