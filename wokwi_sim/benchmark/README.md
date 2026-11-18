# Embedded bring-up benchmark

Run the normal workflow or unittest suite to execute the AVR HEX baseline and five mutated topologies.
Metrics in results.json describe CPU execution and fault detection only; they are not claims of STC fidelity or an autonomous agent repair score.

Level 1 LED, Level 2 Button+LED, Level 3 UART, Level 4 I2C synthetic OLED, Level 5 OLED ACK/command behavior are exercised. SPI/PWM/multi-device full-board tests are not implemented because no confirmed SPI slave/profile exists in this bring-up. Level 9 broken wiring is covered by five cases; Level 10 full-board bring-up remains PARTIAL.
