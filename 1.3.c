/*
 * Communication Systems Lab
 * Assignment 1
 * Task 1.3
 * Author: Tong Su, Michael Deutschen
 *
 * */

#include <stdio.h>
#include <stdlib.h>
#include <netdb.h>
#include <netinet/in.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

// Data structure definition
#define JOKER_REQUEST_TYPE 1
#define JOKER_RESPONSE_TYPE 2
#define NUMBER_OF_CONNECTIONS 10 // Prerequisite from assignment
#define MAX_MESSAGE_LENGTH 515 // 1byte TYPE, 1byte length firstname, 1byte length lastname, 2 x max 256 byte first/lastname.
#define PORT 2345
#define TCP_FASTOPEN 23

// Write response with given length to client on specified socket.
void writeToClient(int socket, char response[], int length)
{
	int checkWrite;
	checkWrite = write(socket, response, length);
   	if (checkWrite < 0)
	{
      	perror("Could not write to socket.\n");
      	exit(1);
   	}
}

// Tell joke to client, which is already accepted at [(int) socket].
void tellJokeToClient(int socket)
{
	// Read from socket.
   	int checkRead;
   	char request[MAX_MESSAGE_LENGTH];
   	bzero(request, MAX_MESSAGE_LENGTH);
   	checkRead = read(socket, request, MAX_MESSAGE_LENGTH - 1);
   	if (checkRead < 0)
	{
      	perror("Could not read from socket.\n");
      	exit(1);
   	}

    // Checking format correctness
    if (checkRead < 3 || request[0] != JOKER_REQUEST_TYPE
        || checkRead != 3 + (uint8_t)request[1] + (uint8_t)request[2])
    {
		perror("Request format error.\n");
		writeToClient(socket, "Malformed (wrong type)", 22);
        exit(1);
    }

    char outputInfo[MAX_MESSAGE_LENGTH];
    sprintf(outputInfo, "Received following message: ");
    strncat(outputInfo, request + 3, (uint8_t)request[1] + (uint8_t)request[2]);
   	printf("%s\n", outputInfo);


	// 2nd and 3rd byte have to be numbers in range of 0 - 255 (Firstname/Lastname length).
	// Every char is a number in this range, thus the check of 2nd and 3rd byte can be omitted.
	// Wrong numbers are not harmful (tested).

	// Receive length of firstname from request.
	uint8_t lengthFirstName = (int)request[1];

	// Receive length of lastname from request.
	uint8_t lengthLastName = (int)request[2];

	// Receive firstname from request.
	char firstName[lengthFirstName + 1];
	strncpy(firstName, request + 3, lengthFirstName);
	firstName[lengthFirstName] = '\0';

	// Receive lastname from request.
	char lastName[lengthLastName + 1];
	strncpy(lastName, request + 3 + lengthFirstName, lengthLastName);
	lastName[lengthLastName] = '\0';

	printf("First name: %s. %i characters.\n", firstName, lengthFirstName);
	printf("Last name: %s. %i characters.\n", lastName, lengthLastName);

	// Select a joke and concatenate it with user's name.
	char * text[] = {
  		"how do you make a dog sound like a cat? You freeze the dog and cut it with a chainsaw. MEEEEEEOOOOOWWW.",
  		"how do you make a cat sound like a dog? You dump gas over the cat and set it on fire. WOOOOOF."
	};
	srand(time(NULL));
	int random = rand() % 2;
	int jokeLength = strlen(text[random]) + lengthFirstName + lengthLastName + 9;
	char joke[jokeLength];
	bzero(joke, jokeLength);
	strcat(joke, "Hello ");
	strcat(joke, firstName);
	strcat(joke, " ");
	strcat(joke, lastName);
	strcat(joke, ", ");
	strcat(joke, text[random]);

	// Create response.
	int responseLength = strlen(joke) + 5;
	char response[responseLength];
	bzero(response, responseLength);

	// First byte is of JOKER_RESPONSE TYPE.
	response[0] = JOKER_RESPONSE_TYPE;

	// 2nd to 5th byte is the length of the joke.
	uint32_t lengthOfJoke = htonl(strlen(joke));
	memcpy(response + 1, &lengthOfJoke, sizeof(lengthOfJoke));

	// From 6th byte on, the joke occurs.
	memcpy(response + 5, joke, strlen(joke)+1);

	// Finally write joke to client with correct format.
	writeToClient(socket, response, responseLength);
}

// main.
int main( /* int argc, char *argv[] */ )
{
   	struct sockaddr_in server, client;

	// Create socket.
	int socketfd;
   	socketfd = socket(AF_INET, SOCK_STREAM, 0);
   	if (socketfd < 0)
	{
        perror("Could not open socket.\n");
        exit(1);
   	}

	// Initialize socket binding.
   	server.sin_family = AF_INET;
   	server.sin_addr.s_addr = INADDR_ANY;
   	server.sin_port = htons(PORT);

   	if (bind(socketfd, (struct sockaddr *) &server, sizeof(server)) < 0) {
		perror("Could not bind socket.\n");
		exit(1);
   	}

	// TCP Fast Open.
	int qlen = NUMBER_OF_CONNECTIONS;
	if ((setsockopt(socketfd, IPPROTO_TCP, TCP_FASTOPEN, &qlen, sizeof(qlen))) == -1)
	{
		printf("Could not establish TCP Fast Open, but who cares.\n");
	}

	// Start listening [blocking].
   	listen(socketfd, NUMBER_OF_CONNECTIONS);

	// Loop to give jokes to all connected clients.
   	while (1)
	{
		int childSocketfd;
		socklen_t clientLength = sizeof(client);
      	childSocketfd = accept(socketfd, (struct sockaddr *) &client, &clientLength);

      	if (childSocketfd < 0)
		{
         	perror("Could not accept the connection.\n");
         	exit(1);
      	}

      	// Create new process.
		int processId;
      	processId = fork();

      	if (processId < 0)
		{
         	perror("Could not create new process.\n");
         	exit(1);
      	}
		else if (processId > 0) // We are in parent fork here.
		{
			// shutdown() can be omitted because we don't want to read further pending data from this socket.
			close(childSocketfd);
		}
		else // We are in child fork here.
		{
         	close(socketfd);
         	tellJokeToClient(childSocketfd);
         	exit(0);
      	}
   	}
}


