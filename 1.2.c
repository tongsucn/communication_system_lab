/*
 * Communication Systems Lab
 * Assignment 1
 * Task 1.2
 * Author: Tong
 *
 * */

#include <stdio.h>
#include <stdint.h>
// uint8_t support
#include <stdlib.h>
#include <string.h>
// strlen support
#include <unistd.h>
#include <errno.h>

#include <sys/types.h>
#include <sys/socket.h>
// socket related
#include <netinet/in.h>
// IPPROTO_TCP definition, address related
#include <arpa/inet.h>
// Byte ordering convert
#include <netdb.h>
// getaddrinfo related


// Data structure definition
#define JOKER_REQUEST_TYPE 1
#define JOKER_RESPONSE_TYPE 2

typedef struct {
    uint8_t        type;
} __attribute__ ((__packed__)) joker_header;

typedef struct {
    uint8_t        type;
    uint8_t        len_first_name;
    uint8_t        len_last_name;
} __attribute__ ((__packed__)) joker_request;
/*
 * __attribute__ ((__packed__)) is used here for avoiding padding,
 * otherwise gcc will do data structure alignment by default.
 *
 */

typedef struct {
    joker_header   header;
    uint32_t       length;
} __attribute__ ((__packed__)) joker_info;


// Function declaration
// Reading 256 characters
void read_256(char *hints, char *buf);

// Exiting with error information
void err_exit(int err_num);


// Macro definition
// Max user name size
#define NAME_LEN 256

// Timeout second
#define TIMEOUT_SEC 3

// Timeout millisecond
#define TIMEOUT_MS 0

// Connecting retry times
#define RETRY_TIME 5


// main
int main(int argc, char *argv[])
{
    // Fetch server name and port as command line arguments
    // Only accept laboratory.comsys.rwth-aachen.de as server name,
    // and 2345 as port number.
    char *server_name;
    uint16_t port_num;

    if (argc != 3)
    {
        fprintf(stderr, "Usage: joker_client [URL] [PORT]");
        exit(-1);
    }
    else
    {
        server_name = argv[1];
        port_num = atoi(argv[2]);
    }


    // Read user's first name from keyboard
    char *first_name = (char *)malloc(NAME_LEN * sizeof(char));
    if (first_name == NULL)
        err_exit(errno);
    read_256("First name: ", first_name);
    uint8_t first_name_len = (uint8_t) strlen(first_name) - 1;

    // Read user's last name from keyboard
    char *last_name = (char *)malloc(NAME_LEN * sizeof(char));
    if (last_name == NULL)
        err_exit(errno);
    read_256("Last name: ", last_name);
    uint8_t last_name_len = (uint8_t) strlen(last_name) - 1;


    // Getting address information
    printf("\nFetching server information...\n");
    struct addrinfo *server_addrinfo, hint = {
        AI_ADDRCONFIG,
        AF_INET,
        0, IPPROTO_TCP, 0, NULL, NULL, NULL
    };

    // Trying to fetch server information for max. RETRY_TIME times
    int err = 1, err_count = RETRY_TIME;
    while (err && err_count--)
        err = getaddrinfo(server_name, NULL, &hint, &server_addrinfo);
    if (err && err_count == 0)
    {
        fprintf(stderr, "%s\n", gai_strerror(err));
        exit(-1);
    }

    uint32_t *in_addr =
        &((struct sockaddr_in *)server_addrinfo->ai_addr)->sin_addr.s_addr;

    // Assembled address structure for sending request
    struct sockaddr_in server_addr = {
        AF_INET,
        htons(port_num),
        {*in_addr},
        {0}    // zero-padding
    };
    char abuf[INET_ADDRSTRLEN];
    const char *addr = inet_ntop(AF_INET, in_addr, abuf, INET_ADDRSTRLEN);
    printf("Server address: %s\n", addr);


    // Assembling request head
    joker_request req = {
        JOKER_REQUEST_TYPE,
        first_name_len,
        last_name_len
    };

    // Preparing send data buf
    size_t send_buf_size = sizeof(req) + first_name_len + last_name_len;
    uint8_t *send_buf = (uint8_t *)malloc(send_buf_size);
    if (send_buf == NULL)
        err_exit(errno);

    // Copying head and data by order
    memcpy(send_buf, &req, sizeof(req));
    memcpy(send_buf + sizeof(req), first_name, first_name_len);
    memcpy(send_buf + sizeof(req) + first_name_len,
            last_name, last_name_len);

    // Free name strings and addrinfo
    free(first_name);
    free(last_name);
    freeaddrinfo(server_addrinfo);


    // Network operation
    int attempt_times = RETRY_TIME;
    joker_info *recv_data;
    uint32_t joke_len;


    while (attempt_times)
    {
        // Setting socket
        int socket_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (socket_fd == -1)
            err_exit(errno);

        // Setting 3 seconds timeout
        struct timeval timeout = {TIMEOUT_SEC, TIMEOUT_MS};
        setsockopt(socket_fd, IPPROTO_TCP, SO_RCVTIMEO,
                &timeout, sizeof(timeout));


        // Sending data via TCP Fast Open
        printf("\nSending data via TFO...\n");
        err = -1, err_count = RETRY_TIME;
        while (err == -1 && err_count)
        {
            err = sendto(socket_fd, send_buf, send_buf_size, MSG_FASTOPEN,
                (struct sockaddr *)&server_addr, sizeof(server_addr));
            err_count--;
        }
        if (err == -1 && err_count == 0)
            err_exit(errno);
        printf("Sent!\n");


        // Preparing receiving buf
        uint16_t recv_buf_size = ~0;
        uint8_t *recv_buf = (uint8_t *)malloc(recv_buf_size);
        if (recv_buf == NULL)
            err_exit(errno);


        // Receiving data, call recv for 10 times
        printf("\nReceiving data via TFO...\n");
        size_t recv_size = 0;
        int recv_times = 0, ret_value;
        int addr_len = sizeof(server_addr);
        for ( ; recv_times < 10; recv_times++)
        {
            ret_value = recvfrom(socket_fd, recv_buf + recv_size,
                    recv_buf_size - recv_size, MSG_FASTOPEN,
                    (struct sockaddr *)&server_addr,
                    (socklen_t *)&addr_len);
            if (ret_value == -1)
                err_exit(errno);
            else
                recv_size += ret_value;
        }

        recv_data = (joker_info *)recv_buf;

        if (recv_size < 5
            || (joke_len = ntohl(recv_data->length)) + 5 > (uint32_t)recv_size)
        {
            printf("\n  --!!**!!-- Warning! --!!**!!--\n");
            printf("  Some data is lost because of connection lost,\n");
            printf("  only part of the joke could be shown, try again.\n");
            printf("  Attempt left: %d\n\n", --attempt_times);
            if (attempt_times == 0)
            {
                fprintf(stderr, "Failed for %d times, exit with error.\n",
                        RETRY_TIME);
                exit(-1);
            }
        }
        else
        {
            // Getting data
            recv_data = (joker_info *)malloc(joke_len + 5);
            memcpy(recv_data, recv_buf, joke_len + 5);
             attempt_times = 0;
        }

        // Free some resources
        free(recv_buf);
        close(socket_fd);
    }


    // Slicing the joke out of the memory block
    char *joke_begin = (char *)(recv_data + 1);
    char *joke = (char *)malloc(joke_len + 1);
    if (joke == NULL)
        err_exit(errno);
    memcpy(joke, joke_begin, joke_len);
    joke[joke_len] = '\0';

    printf("\nHere is the joke:\n%s\n\n", joke);


    // Free allocated memory
    free(send_buf);
    free(joke);
    free(recv_data);


    return 0;
}


// Function definition
void read_256(char *hints, char *buf)
{
#define READ_LEN 256
    int read_count = 0;
    char *input_str = buf;

    // Show hints on screen
    printf("%s", hints);

    // Read input
    while (read_count < READ_LEN - 1
            && (input_str[read_count++] = getchar()) != '\n') ;

    // Write line end
    input_str[read_count] = '\0';
}

void err_exit(int err_num)
{
    fprintf(stderr, "%s\n", strerror(err_num));
    exit(-1);
}
