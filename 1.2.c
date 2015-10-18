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
void read_256(char *hints, char *buf);
void err_exit(int err_num);


#define NAME_LEN 256
#define TIMEOUT_SEC 3
#define TIMEOUT_MS 0


// main
int main(int argc, char *argv[])
{
    // Fetch server name and port as command line arguments
    // Only accept laboratory.comsys.rwth-aachen.de as server name,
    // and 2345 as port.
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


    // Setting address information
    printf("Fetching server information...\n");
    struct addrinfo *server_addrinfo, hint = {
        AI_ADDRCONFIG,
        AF_INET,
        0, IPPROTO_TCP, 0, NULL, NULL, NULL
    };

    int err = 1, err_count = 3;
    while (err && err_count--)
        err = getaddrinfo(server_name, NULL, &hint, &server_addrinfo);
    if (err && err_count == 0)
    {
        fprintf(stderr, "%s\n", gai_strerror(err));
        exit(-1);
    }

    uint32_t *in_addr =
        &((struct sockaddr_in *)server_addrinfo->ai_addr)->sin_addr.s_addr;
    struct sockaddr_in server_addr = {
        AF_INET,
        htons(port_num),
        *in_addr
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


    // Setting socket
    int socket_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (socket_fd == -1)
        err_exit(errno);
    struct timeval timeout = {TIMEOUT_SEC, TIMEOUT_MS};
    setsockopt(socket_fd, IPPROTO_TCP, SO_RCVTIMEO, &timeout, sizeof(timeout));


    // Setting up connection
    printf("Connecting...\n");
    err = 1, err_count = 3;
    while (err && err_count--)
        err = connect(socket_fd,
                (struct sockaddr *)&server_addr,
                sizeof(server_addr));
    if (err && err_count == 0)
        err_exit(errno);
    printf("Connected!\n");


    // Sending data
    printf("Sending data...\n");
    err = 1, err_count = 3;
    while (err && err_count--)
        err = send(socket_fd, send_buf, send_buf_size, MSG_NOSIGNAL);
    if (err && err_count == 0)
        err_exit(errno);
    printf("Done!\n");


    // Preparing receiving buf
    printf("Receiving data...\n");
    uint16_t recv_buf_size = ~0;
    uint8_t *recv_buf = (uint8_t *)malloc(recv_buf_size);
    if (recv_buf == NULL)
        err_exit(errno);

    // Receiving data
    size_t recv_size = 0;
    int recv_times = 0, ret_value;
    for ( ; recv_times < 10; recv_times++)
    {
        ret_value = recv(socket_fd, recv_buf + recv_size,
                recv_buf_size - recv_size, MSG_WAITALL);
        if (ret_value == -1)
            err_exit(errno);
        else
            recv_size += ret_value;
    }

    joker_info *recv_data = (joker_info *)recv_buf;
    uint32_t joke_len = ntohl(recv_data->length);


    // Printing the joke
    char *joke_begin = (char *)(recv_data + 1);
    char *joke = (char *)malloc(joke_len);
    if (joke == NULL)
        err_exit(errno);

    memcpy(joke, joke_begin, joke_len);
    printf("%s\n", joke);

    printf("\n\nFinished! HAHAHA...\n");


    // Free allocated memory
    free(send_buf);
    free(recv_buf);

    close(socket_fd);

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
