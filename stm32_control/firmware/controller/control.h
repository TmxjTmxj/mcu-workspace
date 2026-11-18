#ifndef CONTROL_H
#define CONTROL_H
#include <stdint.h>
enum { MODE_OFF=0, MODE_AUTO=1, MODE_MANUAL=2 };
enum { FAULT_NONE=0, FAULT_SENSOR=1, FAULT_OVERHEAT=2, FAULT_STALL=3, FAULT_ESTOP=4 };
typedef struct {
    int target, temperature, current;
    int integral, duty, manual, mode, fault, estop;
} Control;
void control_init(Control *c);
void control_step(Control *c, int temperature, int current, int estop);
int control_command(Control *c, const char *line);
#endif
