/* Standard 12T 8051 simulator fixture. This is not the STC board firmware. */
#include <REG51.H>

#ifndef LED_BIT
#define LED_BIT 0
#endif

volatile unsigned char timer_ticks;
volatile unsigned int checksum;
volatile unsigned char input_high;
volatile unsigned char input_low;

void timer0_isr(void) interrupt 1 {
    ++timer_ticks;
    TR0 = 0;
}

void checkpoint_high(void) { P1 = 0xff; }
void checkpoint_low(void) { P1 = 0xff; }
void test_done(void) { for (;;) {} }

static void serial(char code *text) {
    while (*text) {
        SBUF = *text++;
        while (!TI) {}
        TI = 0;
    }
}

void main(void) {
    unsigned char i;
    EA = 0;
    timer_ticks = 0;
    checksum = 0;
    P3 = 0xff;
    checkpoint_high();
    input_high = (P3 & 0x04) ? 1 : 0;
    checkpoint_low();
    input_low = (P3 & 0x04) ? 1 : 0;
    for (i = 1; i <= 10; ++i) checksum += i;
    P1 = (unsigned char) ~(1 << LED_BIT);
    TMOD = 0x21; /* Timer1 baud generator; Timer0 16-bit timer. */
    TH0 = 0xfc;
    TL0 = 0x18;
    ET0 = 1;
    EA = 1;
    TR0 = 1;
    while (!timer_ticks) {}
    EA = 0;
    SCON = 0x50;
    TH1 = 0xfd; /* 9600 baud at 11.0592MHz, standard 12T 8051. */
    TL1 = 0xfd;
    TR1 = 1;
    TI = 0;
    serial("KEIL_UART_OK\r\n");
    test_done();
}
