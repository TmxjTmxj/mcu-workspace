/* Minimal STC bring-up. Register definitions are reused from STC's supplied BSP.
 * Configure STC-ISP IRC=24MHz; J1 UART 3-5/4-6; J2 closed. No hardware is flashed.
 * Polling UART/Timer0 avoids linking the full BSP under Keil's 2KB evaluation cap.
 */
#include "STC8xxxx.H"

static void serial(char code *s) {
    unsigned int budget;
    while (*s) {
        TI = 0;
        SBUF = *s++;
        budget = 60000;
        while (!TI && --budget) {}
        if (!budget) return;
    }
}

static void delay_ms(unsigned int ms) {
    while (ms--) {
        TR0 = 0;
        TF0 = 0;
        TH0 = 0xf8; /* 24MHz / 12: reload 65536-2000 */
        TL0 = 0x30;
        TR0 = 1;
        while (!TF0) {}
    }
    TR0 = 0;
}

void main(void) {
    unsigned char index = 0, pressed = 0;
    EA = 0;
    P6 = 0xff;
    P6M1 = 0;
    P6M0 = 0xff; /* strong push-pull outputs; active low */
    P3M1 &= ~0x08;
    P3M0 &= ~0x08;
    P33 = 1; /* quasi-bidirectional K3 input */
    P_SW1 &= 0x3f; /* UART1 P3.0/P3.1 */
    SCON = 0x50;
    AUXR = (AUXR & ~0x81) | 0x40; /* T0=12T, T1=1T, UART uses T1 */
    TMOD = (TMOD & 0x0f) | 0x01; /* STC T1 mode0 auto reload, T0 mode1 */
    TH1 = 0xff;
    TL1 = 0xcc; /* STC BSP formula 65536-(24000000/4/115200) */
    TR1 = 1;
    serial("[BOOT] STC8H8K64U native IRC24MHz required\r\n");
    serial("[TEST] UART_TX READY\r\n");
    serial("[TEST] LED CONFIGURED active-low P6 J2 required\r\n");
    delay_ms(10);
    serial("[TEST] TIMER ELAPSED\r\n");
    serial("[TEST] I2C SKIP unknown attached OLED\r\n");
    serial("SYSTEM READY NATIVE UNVERIFIED\r\n");
    for (;;) {
        P6 = ~(1 << index);
        index = (index + 1) & 7;
        if (!P33) {
            if (!pressed) serial("[EVENT] BUTTON K3 PRESSED\r\n");
            pressed = 1;
        } else pressed = 0;
        delay_ms(50);
    }
}
