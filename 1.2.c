/*
 * Communication Systems Lab
 * Assignment 1
 * Task 1.2
 * Author:
 *
 * */

#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include <sys/types.h>
#include <sys/socket.h>


// Data structure definition
#define JOKER_REQUEST_TYPE 1
#define JOKER_RESPONSE_TYPE 2

typedef struct {
    uint8_t type;
} __attribute__ ((__packed__)) joker_header;

typedef struct {
    uint8_t type;
    uint8_t len_first_name;
    uint8_t len_last_name;
} __attribute__ ((__packed__)) joker_request;


// main
int main(int argc, char *argv[])
{
    // User name variable
    #define NAME_LEN 256
    char first_name[NAME_LEN];
    char last_name[NAME_LEN];
    int name_count;
    uint8_t first_name_len;
    uint8_t last_name_len;

    // Read user's first name from keyboard
    printf("First name: ");
    name_count = 0;
    while (name_count < NAME_LEN - 1 && (first_name[name_count] = getchar()) != '\n')
        name_count++;
    first_name[name_count] = '\0';
    first_name_len = (uint8_t) strlen(first_name);

    // Read user's last name from keyboard
    printf("Last name: ");
    name_count = 0;
    while (name_count < NAME_LEN - 1 && (last_name[name_count] = getchar()) != '\n')
        name_count++;
    last_name[name_count] = '\0';
    last_name_len = (uint8_t) strlen(first_name);


    return 0;
}
