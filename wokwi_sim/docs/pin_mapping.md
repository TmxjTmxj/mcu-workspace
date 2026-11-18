# Pin Mapping

Source: 开发板原理图.pdf page 1 and 图片/2.png. Package mapping CONFIRMED. Default/reset behavior: most pins high impedance; UART pins differ (manual PDF page 206).

| Package pin | MCU pin | Alternate functions | Board use | Voltage |
|---|---|---|---|---|
| 1 | P5.3 | TxD4_2 / P5.3 | H1.15 | VCC=5V design; I/O mode-dependent |
| 2 | P0.5 | T3CLKO / ADC13 / AD5 / P0.5 | tft.D10, H1.16 | VCC=5V design; I/O mode-dependent |
| 3 | P0.6 | PWMETI2_2 / T4 / ADC14 / AD6 / P0.6 | tft.D9, H1.13 | VCC=5V design; I/O mode-dependent |
| 4 | P0.7 | T4CLKO / AD7 / P0.7 | tft.D8, H1.14 | VCC=5V design; I/O mode-dependent |
| 5 | P6.0 | PWM1P_3 / P6.0 | led0.C, H1.11 | VCC=5V design; I/O mode-dependent |
| 6 | P6.1 | PWM1N_3 / P6.1 | led1.C, H1.12 | VCC=5V design; I/O mode-dependent |
| 7 | P6.2 | PWM2P_3 / P6.2 | led2.C, H1.9 | VCC=5V design; I/O mode-dependent |
| 8 | P6.3 | PWM2N_3 / P6.3 | led3.C, H1.10 | VCC=5V design; I/O mode-dependent |
| 9 | P1.0 | RxD2 / PWM1P / ADC0 / P1.0 | pot.WIPER, rtc.SCLK, wifi.TXD, bluetooth.TXD, H1.7 | VCC=5V design; I/O mode-dependent |
| 10 | P1.1 | TxD2 / PWM1N / ADC1 / P1.1 | rtc.IO, wifi.RXD, bluetooth.RXD, H1.8 | VCC=5V design; I/O mode-dependent |
| 11 | P4.7 | TxD2_2 / P4.7 | H1.5 | VCC=5V design; I/O mode-dependent |
| 12 | P1.4 | SDA / MISO / PWM3P / ADC4 / P1.4 | oled.SDA, H1.6 | VCC=5V design; I/O mode-dependent |
| 13 | P1.5 | SCL / SCLK / PWM3N / ADC5 / P1.5 | oled.SCL, H1.3 | VCC=5V design; I/O mode-dependent |
| 14 | P1.6 | XTALO / MCLKO_2 / RxD_3 / PWM4P / ADC6 / P1.6 | H1.4 | VCC=5V design; I/O mode-dependent |
| 15 | P1.7 | XTALI / PWM5_2 / TxD_3 / PWM4N / ADC7 / P1.7 | H1.1 | VCC=5V design; I/O mode-dependent |
| 16 | P1.3 | T2CLKO / MOSI / PWM2N / ADC3 / P1.3 | rtc.CE, H1.2 | VCC=5V design; I/O mode-dependent |
| 17 | UCap | UCap | H2.1 | VCC=5V design; I/O mode-dependent |
| 18 | P5.4 | P5.4 / RST / MCLKO / SS / SS_3 / PWM2P / PWM6_2 / ADC2 / T2 | reset.signal, H2.2 | VCC=5V design; I/O mode-dependent |
| 19 | Vcc/AVcc | Vcc / AVcc | see core power metadata | VCC=5V design; I/O mode-dependent |
| 20 | ADC_VRef+ | ADC_VRef+ | see core power metadata | VCC=5V design; I/O mode-dependent |
| 21 | Gnd/AGnd | Gnd / AGnd | see core power metadata | VCC=5V design; I/O mode-dependent |
| 22 | P4.0 | P4.0 / MOSI_3 | H2.6 | VCC=5V design; I/O mode-dependent |
| 23 | P6.4 | P6.4 / PWM3P_3 | led4.C, H2.7 | VCC=5V design; I/O mode-dependent |
| 24 | P6.5 | P6.5 / PWM3N_3 | led5.C, H2.8 | VCC=5V design; I/O mode-dependent |
| 25 | P6.6 | P6.6 / PWM4P_3 | led6.C, H2.9 | VCC=5V design; I/O mode-dependent |
| 26 | P6.7 | P6.7 / PWM4N_3 | led7.C, H2.10 | VCC=5V design; I/O mode-dependent |
| 27 | P3.0 | P3.0 / RxD / D- / INT4 | k0.signal, j1.4, H2.11 | VCC=5V design; I/O mode-dependent |
| 28 | P3.1 | P3.1 / TxD / D+ | k1.signal, j1.3, H2.12 | VCC=5V design; I/O mode-dependent |
| 29 | P3.2 | P3.2 / INT0 / SCLK_4 / SCL_4 / PWMETI / PWMETI2 | k2.signal, ir.OUT, H2.13 | VCC=5V design; I/O mode-dependent |
| 30 | P3.3 | P3.3 / INT1 / MISO_4 / SDA_4 / PWM4N_4 / PWM7_2 | k3.signal, H2.14 | VCC=5V design; I/O mode-dependent |
| 31 | P3.4 | P3.4 / T0 / T1CLKO / MOSI_4 / PWM4P_4 / PWM8_2 / CMPO | H2.15 | VCC=5V design; I/O mode-dependent |
| 32 | P5.0 | P5.0 / RxD3_2 | H2.16 | VCC=5V design; I/O mode-dependent |
| 33 | P5.1 | P5.1 / TxD3_2 | H2.18 | VCC=5V design; I/O mode-dependent |
| 34 | P3.5 | P3.5 / T1 / T0CLKO / SS_4 / PWMFLT / PWMFLT2 | buzzer.CONTROL, H2.19 | VCC=5V design; I/O mode-dependent |
| 35 | P3.6 | P3.6 / INT2 / RxD_2 / CMP- | sensor.DATA, H2.17 | VCC=5V design; I/O mode-dependent |
| 36 | P3.7 | P3.7 / INT3 / TxD_2 / CMP+ | H2.20 | VCC=5V design; I/O mode-dependent |
| 37 | P7.0 | P7.0 | H2.21 | VCC=5V design; I/O mode-dependent |
| 38 | P7.1 | P7.1 | H2.22 | VCC=5V design; I/O mode-dependent |
| 39 | P7.2 | P7.2 | H2.23 | VCC=5V design; I/O mode-dependent |
| 40 | P7.3 | P7.3 / PWMETI_3 | H2.24 | VCC=5V design; I/O mode-dependent |
| 41 | P4.1 | P4.1 / MISO_3 / CMPO_2 / PWMETI_2 | lcd.RS, tft.RST, H2.25 | VCC=5V design; I/O mode-dependent |
| 42 | P4.2 | P4.2 / WR | lcd.RW, tft.WR, H2.26 | VCC=5V design; I/O mode-dependent |
| 43 | P4.3 | P4.3 / RxD_4 / SCLK_3 | H2.27 | VCC=5V design; I/O mode-dependent |
| 44 | P4.4 | P4.4 / RD / TxD_4 | lcd.E, tft.CS, H2.28 | VCC=5V design; I/O mode-dependent |
| 45 | P2.0 | P2.0 / A8 / PWM1P_2 / PWM5 | lcd.D0, tft.D0, segments.a, H2.29 | VCC=5V design; I/O mode-dependent |
| 46 | P2.1 | P2.1 / A9 / PWM1N_2 / PWM6 | lcd.D1, tft.D1, segments.b, H2.30 | VCC=5V design; I/O mode-dependent |
| 47 | P2.2 | P2.2 / A10 / PWM2P_2 / PWM7 / SS_2 | lcd.D2, tft.D2, segments.c, H2.31 | VCC=5V design; I/O mode-dependent |
| 48 | P2.3 | P2.3 / A11 / PWM2N_2 / PWM8 / MOSI_2 | lcd.D3, tft.D3, segments.d, H2.32 | VCC=5V design; I/O mode-dependent |
| 49 | P2.4 | MISO_2 / SDA_2 / PWM3P_2 / A12 / P2.4 | lcd.D4, tft.D4, segments.e, H1.31 | VCC=5V design; I/O mode-dependent |
| 50 | P2.5 | SCLK_2 / SCL_2 / PWM3N_2 / A13 / P2.5 | lcd.D5, tft.D5, segments.f, H1.32 | VCC=5V design; I/O mode-dependent |
| 51 | P2.6 | PWM4P_2 / A14 / P2.6 | lcd.D6, tft.D6, segments.g, H1.29 | VCC=5V design; I/O mode-dependent |
| 52 | P2.7 | PWM4N_2 / A15 / P2.7 | lcd.D7, tft.D7, segments.dp, H1.30 | VCC=5V design; I/O mode-dependent |
| 53 | P7.4 | PWM5_4 / P7.4 | rgb.R, ultrasonic.TRIG, segments.DIG1, H1.27 | VCC=5V design; I/O mode-dependent |
| 54 | P7.5 | PWM6_4 / P7.5 | rgb.G, ultrasonic.ECHO, segments.DIG2, H1.28 | VCC=5V design; I/O mode-dependent |
| 55 | P7.6 | PWM7_4 / P7.6 | rgb.B, segments.DIG3, H1.25 | VCC=5V design; I/O mode-dependent |
| 56 | P7.7 | PWM8_4 / P7.7 | segments.DIG4, H1.26 | VCC=5V design; I/O mode-dependent |
| 57 | P4.5 | ALE / P4.5 | lcd.RST, tft.RS, H1.23 | VCC=5V design; I/O mode-dependent |
| 58 | P4.6 | RxD2_2 / P4.6 | H1.24 | VCC=5V design; I/O mode-dependent |
| 59 | P0.0 | T3_2 / PWM5_3 / RxD3 / ADC8 / AD0 / P0.0 | tft.D15, H1.21 | VCC=5V design; I/O mode-dependent |
| 60 | P0.1 | T3CLKO_2 / PWM6_3 / TxD3 / ADC9 / AD1 / P0.1 | tft.D14, H1.22 | VCC=5V design; I/O mode-dependent |
| 61 | P0.2 | T4_2 / PWM7_3 / RxD4 / ADC10 / AD2 / P0.2 | tft.D13, H1.19 | VCC=5V design; I/O mode-dependent |
| 62 | P0.3 | T4CLKO_2 / PWM8_3 / TxD4 / ADC11 / AD3 / P0.3 | tft.D12, H1.20 | VCC=5V design; I/O mode-dependent |
| 63 | P0.4 | T3 / ADC12 / AD4 / P0.4 | tft.D11, H1.17 | VCC=5V design; I/O mode-dependent |
| 64 | P5.2 | RxD4_2 / P5.2 | H1.18 | VCC=5V design; I/O mode-dependent |

## H1

| Header pin | Net |
|---|---|
| 1 | P1.7 |
| 2 | P1.3 |
| 3 | P1.5 |
| 4 | P1.6 |
| 5 | P4.7 |
| 6 | P1.4 |
| 7 | P1.0 |
| 8 | P1.1 |
| 9 | P6.2 |
| 10 | P6.3 |
| 11 | P6.0 |
| 12 | P6.1 |
| 13 | P0.6 |
| 14 | P0.7 |
| 15 | P5.3 |
| 16 | P0.5 |
| 17 | P0.4 |
| 18 | P5.2 |
| 19 | P0.2 |
| 20 | P0.3 |
| 21 | P0.0 |
| 22 | P0.1 |
| 23 | P4.5 |
| 24 | P4.6 |
| 25 | P7.6 |
| 26 | P7.7 |
| 27 | P7.4 |
| 28 | P7.5 |
| 29 | P2.6 |
| 30 | P2.7 |
| 31 | P2.4 |
| 32 | P2.5 |

## H2

| Header pin | Net |
|---|---|
| 1 | UCap |
| 2 | P5.4 |
| 3 | VCC |
| 4 | VCC |
| 5 | GND |
| 6 | P4.0 |
| 7 | P6.4 |
| 8 | P6.5 |
| 9 | P6.6 |
| 10 | P6.7 |
| 11 | P3.0 |
| 12 | P3.1 |
| 13 | P3.2 |
| 14 | P3.3 |
| 15 | P3.4 |
| 16 | P5.0 |
| 17 | P3.6 |
| 18 | P5.1 |
| 19 | P3.5 |
| 20 | P3.7 |
| 21 | P7.0 |
| 22 | P7.1 |
| 23 | P7.2 |
| 24 | P7.3 |
| 25 | P4.1 |
| 26 | P4.2 |
| 27 | P4.3 |
| 28 | P4.4 |
| 29 | P2.0 |
| 30 | P2.1 |
| 31 | P2.2 |
| 32 | P2.3 |

## P1

| Header pin | Net |
|---|---|
| 1 | 3V3 |
| 2 | GND |
| 3 | 3V3 |
| 4 | GND |
| 5 | 3V3 |
| 6 | GND |
| 7 | 3V3 |
| 8 | GND |
| 9 | VCC |
| 10 | GND |
| 11 | VCC |
| 12 | GND |
| 13 | VCC |
| 14 | GND |
| 15 | VCC |
| 16 | GND |

TFT upper data bus is reversed: D8=P0.7 through D15=P0.0.
UCap is an internal regulator decoupling pin, not a general supply output. ADC_VRef+ is tied to VCC.
Analog or shared-net inputs require the peripheral profile and jumper constraints in hardware_graph.json.