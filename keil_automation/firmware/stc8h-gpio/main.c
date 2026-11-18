/* Offline board probe: schematic LED0=P6.0, K3=P3.3, both active low.
 * No timer/baud/pin electrical characteristics are asserted here.
 * Uses the board's STC header and STC8H8K64U project selection unchanged.
 */
#include "STC8xxxx.H"

#ifndef LED_BIT
#define LED_BIT 0
#endif

volatile unsigned char phase;
volatile unsigned char key_idle, key_down, key_up;
volatile unsigned char led_idle, led_down, led_up;

void checkpoint_idle(void) { phase = 1; }
void checkpoint_pressed(void) { phase = 2; }
void checkpoint_released(void) { phase = 3; }
void test_done(void) { for (;;) {} }

static void update_led(void) {
    P6 = P33 ? 0xff : (unsigned char) ~(1 << LED_BIT);
}

void main(void) {
    EA = 0;
    P6M1 = 0;
    P6M0 = 0xff;
    P3M1 &= ~0x08;
    P3M0 &= ~0x08;
    P33 = 1;
    P6 = 0xff;
    checkpoint_idle();
    key_idle = P33;
    update_led();
    led_idle = P6;
    checkpoint_pressed();
    key_down = P33;
    update_led();
    led_down = P6;
    checkpoint_released();
    key_up = P33;
    update_led();
    led_up = P6;
    test_done();
}
