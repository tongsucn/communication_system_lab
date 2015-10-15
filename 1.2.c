/*
 * Communication Systems Lab
 * Assignment 1
 * Task 1.2
 * Author:
 *
 * */

#include <stdio.h>
#include <stdint.h>

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
     return 0;
}
