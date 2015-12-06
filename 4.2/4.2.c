#include <time.h>
#include <stdint.h>
// #include <bcm2835.h>

// Access from ARM Running Linux

#define BCM2708_PERI_BASE        0x20000000
#define GPIO_BASE                (BCM2708_PERI_BASE + 0x200000) /* GPIO controller */

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

#define PAGE_SIZE (4*1024)
#define BLOCK_SIZE (4*1024)

int  mem_fd;
void *gpio_map;

// I/O access
volatile unsigned *gpio;

// main function arguments parsing result struct
struct parse_result {
    uint8_t house;
    uint8_t code;
    int status;
    int interval_len;
};


// GPIO setup macros. Always use INP_GPIO(x) before using OUT_GPIO(x) or SET_GPIO_ALT(x,y)
#define INP_GPIO(g) *(gpio+((g)/10)) &= ~(7<<(((g)%10)*3))
#define OUT_GPIO(g) *(gpio+((g)/10)) |=  (1<<(((g)%10)*3))
#define SET_GPIO_ALT(g,a) *(gpio+(((g)/10))) |= (((a)<=3?(a)+4:(a)==4?3:2)<<(((g)%10)*3))

#define GPIO_SET *(gpio+7)  // sets   bits which are 1 ignores bits which are 0
#define GPIO_CLR *(gpio+10) // clears bits which are 1 ignores bits which are 0

// signal relative variables
// signal time slice variables
long TIME_SLICE_LEN = 0;
#define TIME_SLICE_UNIT 1000
#define LIGHT_SPEED 299792458
#define STANDARD_TIME_SLICE_LEN_US 370
#define STANDARD_FREQ 433000000

// signal interval variables
#define TS_SYN 31
#define TS_LONG_CREST 3
#define TS_SHORT_CREST 1
#define TS_INTERVAL 3
#define TS_ZERO_INTERVAL 1
#define TS_ONE_INTERVAL 3

// repeat variables
#define REPEAT_CALL 8
#define SLACK_RANGE 2

// encode length
#define HOUSE_BIN_LEN 5
#define CODE_BIN_LEN 5
#define BEGIN_FIELD_LEN 1
#define ZERO_FIELD_LEN 3
#define ONE_FIELD_LEN 3
#define INTERVAL_FIELD_LEN 1

// arguments parsing variables
#define ARG_LEN 9
#define CODE_PARSE_ERR 0x20
#define CODE_BIN_LEN 5


void setup_io();

//
// Set up a memory regions to access GPIO
//
void setup_io()
{
   /* open /dev/mem */
   if ((mem_fd = open("/dev/mem", O_RDWR|O_SYNC) ) < 0) {
      printf("can't open /dev/mem \n");
      exit(-1);
   }

   /* mmap GPIO */
   gpio_map = mmap(
      NULL,             //Any adddress in our space will do
      BLOCK_SIZE,       //Map length
      PROT_READ|PROT_WRITE,// Enable reading & writting to mapped memory
      MAP_SHARED,       //Shared with other processes
      mem_fd,           //File to map
      GPIO_BASE         //Offset to GPIO peripheral
   );

   close(mem_fd); //No need to keep mem_fd open after mmap

   if (gpio_map == MAP_FAILED) {
      printf("mmap error %d\n", (int)gpio_map);//errno also set!
      exit(-1);
   }

   // Always use volatile pointer!
   gpio = (volatile unsigned *)gpio_map;
   printf("SETUP FINISHED");
} // setup_io


/* this will register an contructor that calls the setup_io() when the app starts */
static void con() __attribute__((constructor));

void con() {
    setup_io();
}



/* use this to send power to a pin */
void set_pin(int pin) {
	GPIO_SET = 1<<pin;
}

/* use this to set no power to a pin */
void clr_pin(int pin) {
	GPIO_CLR = 1<<pin;
}


/* set time sequence values */
/* set begin */
struct timespec *set_begin(struct timespec *sub_seq) {
    sub_seq->tv_sec = 0;
    sub_seq->tv_nsec = (long)(TIME_SLICE_LEN * TS_SHORT_CREST);

    return sub_seq + BEGIN_FIELD_LEN;
}

/* set zero */
struct timespec *set_zero(struct timespec *sub_seq) {
    sub_seq[0].tv_sec = 0;
    sub_seq[0].tv_nsec = (long)(TIME_SLICE_LEN * TS_LONG_CREST);
    sub_seq[1].tv_sec = 0;
    sub_seq[1].tv_nsec = (long)(TIME_SLICE_LEN * TS_ZERO_INTERVAL);
    sub_seq[2].tv_sec = 0;
    sub_seq[2].tv_nsec = (long)(TIME_SLICE_LEN * TS_SHORT_CREST);

    return sub_seq + ZERO_FIELD_LEN;
}

/* set one */
struct timespec *set_one(struct timespec *sub_seq) {
    sub_seq[0].tv_sec = 0;
    sub_seq[0].tv_nsec = (long)(TIME_SLICE_LEN * TS_SHORT_CREST);
    sub_seq[1].tv_sec = 0;
    sub_seq[1].tv_nsec = (long)(TIME_SLICE_LEN * TS_ONE_INTERVAL);
    sub_seq[2].tv_sec = 0;
    sub_seq[2].tv_nsec = (long)(TIME_SLICE_LEN * TS_SHORT_CREST);

    return sub_seq + ONE_FIELD_LEN;
}

/* set interval */
struct timespec *set_interval(struct timespec *sub_seq) {
    sub_seq->tv_sec = 0;
    sub_seq->tv_nsec = (long)(TIME_SLICE_LEN * TS_INTERVAL);

    return sub_seq + INTERVAL_FIELD_LEN;
}

/* set sync */
void set_sync(struct timespec *sub_seq) {
    sub_seq->tv_sec = 0;
    sub_seq->tv_nsec = (long)(TIME_SLICE_LEN * TS_SYN);
}


/* generating signal sequence */
void sequence(
        struct timespec *seq,
        uint8_t house,
        uint8_t code,
        uint8_t status) {
    struct timespec *pos = seq;
    const uint8_t compare = 1;

    // set begin flag
    pos = set_begin(pos);
    pos = set_interval(pos);

    // set house
    int i;
    for (i = 0; i < HOUSE_BIN_LEN; i++) {
        if (house & compare)
            pos = set_one(pos);
        else
            pos = set_zero(pos);
        house >>= 1;
        pos = set_interval(pos);
    }

    // set code
    for (i = 0; i < CODE_BIN_LEN; i++) {
        if (code & compare)
            pos = set_one(pos);
        else
            pos = set_zero(pos);
        code >>= 1;
        pos = set_interval(pos);
    }

    // set on or off
    switch(status) {
        case 0:
            pos = set_zero(pos);
            pos = set_interval(pos);
            pos = set_one(pos);
            break;
        default:
            pos = set_one(pos);
            pos = set_interval(pos);
            pos = set_zero(pos);
            break;
    }

    // set sync
    set_sync(pos);
}


/* send signal with for loop */
void send(const struct timespec *signal_seq, int left) {
    int i;
    int loop_times = left * 2;
    for (i = 0; i < loop_times; i += 2) {
        set_pin(17);
        nanosleep(signal_seq + i, NULL);
        clr_pin(17);
        nanosleep(signal_seq + i + 1, NULL);
    }
}


/* control logic, used to send signal*/
void control(struct parse_result arg) {
    struct timespec signal_seq[50];
    sequence(signal_seq, arg.house, arg.code, arg.status);
    int k;

    int i, j;
    for (i = 0; i < REPEAT_CALL; i++)
        send(signal_seq, 25);
}


/* calculating time slice in mu second */
int calc_interval(int antenna_len_mm) {
    float antenna_len_m = antenna_len_mm * 4 * 0.001;
    float scale = LIGHT_SPEED / (STANDARD_FREQ * antenna_len_m);
    return (int)(STANDARD_TIME_SLICE_LEN_US * scale);
}


/* parse plug code into binary format */
uint8_t parse_code(const char *code_str) {
    if (strlen(code_str) != CODE_BIN_LEN)
        return CODE_PARSE_ERR;

    uint8_t result = 0;
    int i;
    for (i = 0; i < CODE_BIN_LEN; i++) {
        switch (code_str[i]) {
            case '0':
                break;
            case '1':
                result |= (1 << i);
                break;
            default:
                return CODE_PARSE_ERR;
        }
    }

    return result;
}


/* the main function for parsing arguments */
int parse_arg(int argc, char *argv[], struct parse_result *result) {
    if (argc != ARG_LEN)
        return -1;

    uint8_t house, code;
    int status, antenna_len;
    uint8_t arg_count = 0;

    int i, arg_fail = 0;
    for (i = 1; i < ARG_LEN; i += 2) {
        switch (argv[i][1]) {
            case 'h':
                if ((house = parse_code(argv[i + 1])) == CODE_PARSE_ERR)
                    return -1;
                arg_count |= 0x1;
                break;
            case 'c':
                if ((code = parse_code(argv[i + 1])) == CODE_PARSE_ERR)
                    return -1;
                arg_count |= 0x2;
                break;
            case 's':
                if (strcmp("on", argv[i + 1]) == 0)
                    status = 1;
                else if (strcmp("off", argv[i + 1]) == 0)
                    status = 0;
                else
                    return -1;
                arg_count |= 0x4;
                break;
            case 'l':
                if ((antenna_len = atoi(argv[i + 1])) == 0)
                    return -1;
                arg_count |= 0x8;
                break;
            default:
                return -1;
        }
    }

    if (arg_count != 0x0F)
        return -1;

    result->house = house;
    result->code = code;
    result->status = status;
    result->interval_len = calc_interval(antenna_len);

    return 0;
}


/* print usage */
void print_usage() {
    const char *usage = "Usage: -h [HOUSE] -c [CODE] -s [STATUS] -l [LENGTH]\n"
                        " -h: house [01]{5}\n"
                        " -c: code [01]{5}\n"
                        " -s: status [on|off]\n"
                        " -l: length of antenna (integer, in mm)\n";

    printf("%s", usage);
}


int main(int argc, char *argv[])
{
    // this is called after the contructor!
    INP_GPIO(17); // must use INP_GPIO before we can use OUT_GPIO
    OUT_GPIO(17);

    // parse arguments
    struct parse_result result;
    if (parse_arg(argc, argv, &result)) {
         print_usage();
         exit(1);
    }

    // perform control
    int i;
    for (i = result.interval_len - SLACK_RANGE;
            i < result.interval_len + SLACK_RANGE;
            i++) {
        TIME_SLICE_LEN = TIME_SLICE_UNIT * i;
        control(result);
    }

    return 0;
}
