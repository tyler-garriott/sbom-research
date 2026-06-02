#include <curl/curl.h>
#include <stdio.h>

int main() {
    CURLcode status = curl_global_init(CURL_GLOBAL_DEFAULT);
    if (status != CURLE_OK) {
        printf("curl_global_init failed\n");
        return 1;
    }

    CURL *handle = curl_easy_init();
    if (handle == NULL) {
        printf("curl_easy_init failed\n");
        curl_global_cleanup();
        return 1;
    }

    char *escaped = curl_easy_escape(handle, "sbom research with curl", 23);
    if (escaped == NULL) {
        printf("curl_easy_escape failed\n");
        curl_easy_cleanup(handle);
        curl_global_cleanup();
        return 1;
    }

    curl_version_info_data *info = curl_version_info(CURLVERSION_NOW);

    printf("libcurl version: %s\n", info->version);
    printf("escaped string: %s\n", escaped);

    curl_free(escaped);
    curl_easy_cleanup(handle);
    curl_global_cleanup();

    return 0;
}
