#include "control.h"
#include "protocol.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
    LineParser parser={0};
    const unsigned char binary[]={'M',',','2',0,'x','\n'};
    int result=0;for(unsigned i=0;i<sizeof(binary);i++) result=protocol_byte(&parser,binary[i]);
    assert(result==-1);
    for(unsigned i=0;i<100;i++) protocol_byte(&parser,'S');
    assert(protocol_byte(&parser,'\n')==-1);
    const char *valid="S,4000\n";while(*valid)result=protocol_byte(&parser,(unsigned char)*valid++);
    assert(result==1);
    Control c; control_init(&c);
    control_step(&c,4500,400,0);
    assert(c.mode==MODE_AUTO && c.duty>0 && c.fault==0);
    assert(control_command(&c,"S,3600") && c.target==3600);
    assert(!control_command(&c,"S,9999") && c.target==3600);
    assert(!control_command(&c,"S,3600junk"));
    assert(!control_command(&c,"D,-1"));
    assert(!control_command(&c,"D,100")); /* only in manual mode */
    assert(control_command(&c,"M,2") && control_command(&c,"D,42"));
    control_step(&c,4500,400,0); assert(c.duty==42);
    control_step(&c,9000,400,0); assert(c.fault==FAULT_OVERHEAT && c.duty==100);
    assert(!control_command(&c,"M,2"));
    assert(!control_command(&c,"R,0"));
    control_step(&c,3500,400,0);
    assert(control_command(&c,"R,0") && c.fault==0);
    control_step(&c,-9999,400,0); assert(c.fault==FAULT_SENSOR && c.duty==0);
    control_step(&c,3500,400,0); assert(c.fault==FAULT_SENSOR);
    assert(control_command(&c,"R,0"));
    control_step(&c,4500,3000,0); assert(c.fault==FAULT_STALL && c.duty==0);
    control_step(&c,3500,400,0); assert(control_command(&c,"R,0"));
    control_step(&c,4500,400,1); assert(c.fault==FAULT_ESTOP && c.duty==0);
    puts("CONTROL_TEST_PASS"); return 0;
}
