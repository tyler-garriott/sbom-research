#include <sqlite3.h>
#include <stdio.h>

int main() {
    sqlite3 *database = NULL;
    char *error = NULL;

    int status = sqlite3_open(":memory:", &database);
    if (status != SQLITE_OK) {
        printf("could not open sqlite database\n");
        return 1;
    }

    status = sqlite3_exec(
        database,
        "CREATE TABLE notes (message TEXT);"
        "INSERT INTO notes VALUES ('sbom research with sqlite');",
        NULL,
        NULL,
        &error
    );

    if (status != SQLITE_OK) {
        printf("sqlite error: %s\n", error);
        sqlite3_free(error);
        sqlite3_close(database);
        return 1;
    }

    printf("sqlite version: %s\n", sqlite3_libversion());

    sqlite3_close(database);
    return 0;
}
