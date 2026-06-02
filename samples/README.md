# Sample Programs

These are tiny C programs for testing Syft against binaries with known
dependencies.

Build them into `data/binaries/`:

```sh
gcc samples/zlib-test.c -lz -o data/binaries/zlib-test
gcc samples/openssl-test.c -lcrypto -o data/binaries/openssl-test
gcc samples/curl-test.c -lcurl -o data/binaries/curl-test
gcc samples/sqlite-test.c -lsqlite3 -o data/binaries/sqlite-test
```

Then run Syft:
```sh
syft data/binaries/zlib-test -o syft-json > data/syft-output/zlib-test.syft.json
syft data/binaries/openssl-test -o syft-json > data/syft-output/openssl-test.syft.json
syft data/binaries/curl-test -o syft-json > data/syft-output/curl-test.syft.json
syft data/binaries/sqlite-test -o syft-json > data/syft-output/sqlite-test.syft.json
```
