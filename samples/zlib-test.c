#include <stdio.h>
#include <string.h>
#include <zlib.h>

int main() {
    const char input[] = "sbom research with zlib";
    unsigned char compressed[128];
    unsigned char output[128];
    unsigned long compressed_len = sizeof(compressed);
    unsigned long output_len = sizeof(output);

    int status = compress(
        compressed,
        &compressed_len,
        (const unsigned char *)input,
        strlen(input) + 1
    );

    if (status != Z_OK) {
        printf("zlib compression failed\n");
        return 1;
    }

    status = uncompress(output, &output_len, compressed, compressed_len);

    if (status != Z_OK) {
        printf("zlib decompression failed\n");
        return 1;
    }

    printf("zlib version: %s\n", zlibVersion());
    printf("output: %s\n", output);

    return 0;
}
