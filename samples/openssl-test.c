#include <openssl/evp.h>
#include <openssl/opensslv.h>
#include <stdio.h>
#include <string.h>

int main() {
    const char message[] = "sbom research with openssl";
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_len = 0;

    EVP_MD_CTX *context = EVP_MD_CTX_new();
    if (context == NULL) {
        printf("could not create OpenSSL digest context\n");
        return 1;
    }

    if (
        EVP_DigestInit_ex(context, EVP_sha256(), NULL) != 1 ||
        EVP_DigestUpdate(context, message, strlen(message)) != 1 ||
        EVP_DigestFinal_ex(context, digest, &digest_len) != 1
    ) {
        printf("OpenSSL digest failed\n");
        EVP_MD_CTX_free(context);
        return 1;
    }

    EVP_MD_CTX_free(context);

    printf("OpenSSL version: %s\n", OPENSSL_VERSION_TEXT);
    printf("sha256: ");
    for (unsigned int i = 0; i < digest_len; i++) {
        printf("%02x", digest[i]);
    }
    printf("\n");

    return 0;
}
