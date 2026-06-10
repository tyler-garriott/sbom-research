#!/usr/bin/env bash
set -euo pipefail

mkdir -p data/binaries

gcc samples/hello.c -o data/binaries/hello
gcc samples/math-test.c -lm -o data/binaries/math-test
gcc samples/zlib-test.c -lz -o data/binaries/zlib-test
gcc samples/openssl-test.c -lcrypto -o data/binaries/openssl-test
gcc samples/curl-test.c -lcurl -o data/binaries/curl-test
gcc samples/sqlite-test.c -lsqlite3 -o data/binaries/sqlite-test

file data/binaries/hello \
  data/binaries/math-test \
  data/binaries/zlib-test \
  data/binaries/openssl-test \
  data/binaries/curl-test \
  data/binaries/sqlite-test
