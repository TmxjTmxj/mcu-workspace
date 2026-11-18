/* Explicit AVR behavioral port. This binary cannot run on an STC8H MCU. */
#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

static void serial(const char *s) {
    while (*s) {
        while (!(UCSR0A & _BV(UDRE0))) {}
        UDR0 = *s++;
    }
}

static uint8_t twi_wait(void) {
    uint16_t budget = 60000;
    while (!(TWCR & _BV(TWINT)) && --budget) {}
    return budget != 0;
}

static uint8_t start(uint8_t address) {
    TWCR = _BV(TWINT) | _BV(TWSTA) | _BV(TWEN);
    if (!twi_wait()) return 0;
    if ((TWSR & 0xf8) != 0x08 && (TWSR & 0xf8) != 0x10) return 0;
    TWDR = address << 1;
    TWCR = _BV(TWINT) | _BV(TWEN);
    return twi_wait() && (TWSR & 0xf8) == 0x18;
}

static uint8_t write_byte(uint8_t value) {
    TWDR = value;
    TWCR = _BV(TWINT) | _BV(TWEN);
    return twi_wait() && (TWSR & 0xf8) == 0x28;
}

static void stop(void) { TWCR = _BV(TWINT) | _BV(TWEN) | _BV(TWSTO); }

int main(void) {
    uint8_t address, oled_found = 0, ok, index = 0, pressed = 0;
    uint16_t sample;
    /* Mega D22..29 = PORTA; active-low LED cathodes. K3 = D2/PE4. */
    DDRA = 0xff;
    PORTA = 0xff;
    DDRE &= ~_BV(4);
    PORTE |= _BV(4);
    UBRR0 = 16; /* U2X, 16MHz / (8 * 17) = 117647, ~2.1% baud error */
    UCSR0A = _BV(U2X0);
    UCSR0B = _BV(TXEN0) | _BV(RXEN0);
    UCSR0C = _BV(UCSZ01) | _BV(UCSZ00);
    serial("[BOOT] Board2Sim EQUIVALENT ATmega2560\n");
    serial(DDRA == 0xff ? "[TEST] GPIO_REGISTER PASS\n" : "[TEST] GPIO_REGISTER FAIL\n");
    serial("[TEST] UART_TX READY\n");
    /* Poll actual Timer1 hardware; do not mark a software delay as timer proof. */
    TCCR1B = _BV(CS11) | _BV(CS10);
    TCNT1 = 0;
    while (TCNT1 < 2500) {}
    serial("[TEST] TIMER PASS\n");
    ADMUX = _BV(REFS0); /* A0 = PF0, synthetic potentiometer */
    ADCSRA = _BV(ADEN) | _BV(ADPS2) | _BV(ADPS1) | _BV(ADPS0);
    ADCSRA |= _BV(ADSC);
    while (ADCSRA & _BV(ADSC)) {}
    sample = ADC;
    serial(sample >= 400 && sample <= 620 ? "[TEST] ADC PASS\n" : "[TEST] ADC FAIL expected midpoint\n");
    TWSR = 0;
    TWBR = 72; /* 100kHz */
    for (address = 8; address < 120; ++address) {
        if (start(address)) {
            if (address == 0x3c) {
                oled_found = 1;
                serial("[I2C] 0x3C ACK\n");
            } else serial("[I2C] other address ACK\n");
        }
        stop();
    }
    serial(oled_found ? "[TEST] I2C PASS\n" : "[TEST] I2C FAIL expected synthetic OLED at 0x3C\n");
    ok = start(0x3c) && write_byte(0x00) && write_byte(0xae) && write_byte(0xa5) && write_byte(0xaf);
    stop();
    serial(ok ? "[TEST] OLED_COMMAND ACK\n" : "[TEST] OLED_COMMAND FAIL\n");
    serial("[TEST] SPI SKIP no board SPI slave identified\n");
    if (!oled_found || !ok || sample < 400 || sample > 620) {
        serial("SYSTEM FAILED EQUIVALENT\n");
        for (;;) {}
    }
    serial("SYSTEM READY EQUIVALENT\n");
    for (;;) {
        PORTA = (uint8_t)~(1U << index);
        index = (index + 1) & 7;
        if (!(PINE & _BV(4))) {
            if (!pressed) serial("[EVENT] BUTTON K3 PRESSED\n");
            pressed = 1;
        } else pressed = 0;
        _delay_ms(50);
    }
}
