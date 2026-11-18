#include "control.h"
#include <stdlib.h>
#include <string.h>
static int clamp(int x,int lo,int hi) { return x<lo?lo:(x>hi?hi:x); }
void control_init(Control *c) {
    memset(c,0,sizeof(*c)); c->target=3500; c->mode=MODE_AUTO; c->manual=40;
}
void control_step(Control *c,int temperature,int current,int estop) {
    c->temperature=temperature; c->current=current; c->estop=estop;
    if(estop) c->fault=FAULT_ESTOP;
    else if(temperature < -1000 || temperature>11000) c->fault=FAULT_SENSOR;
    else if(current>2000) c->fault=FAULT_STALL;
    else if(temperature>=7500 && c->fault==0) c->fault=FAULT_OVERHEAT;
    if(c->fault) { c->integral=0; c->duty=c->fault==FAULT_OVERHEAT?100:0; return; }
    if(c->mode==MODE_OFF) { c->duty=0; c->integral=0; }
    else if(c->mode==MODE_MANUAL) { c->duty=c->manual; c->integral=0; }
    else {
        int error=temperature-c->target;
        c->integral=clamp(c->integral+error,-10000,30000);
        c->duty=clamp(error/40+c->integral/600,0,100);
    }
}
int control_command(Control *c,const char *line) {
    if(!line || strlen(line)<3 || line[1]!=',' || line[2]<'0' || line[2]>'9') return 0;
    char *end; long value=strtol(line+2,&end,10);
    if(*end || value<0 || value>10000) return 0;
    if(line[0]=='R') {
        if(value || c->estop || c->temperature<0 || c->temperature>=6500 || c->current>2000) return 0;
        c->fault=0; c->integral=0; c->mode=MODE_AUTO; return 1;
    }
    if(c->fault) return 0;
    if(line[0]=='S' && value>=2500 && value<=5000) { c->target=(int)value; c->integral=0; return 1; }
    if(line[0]=='M' && value<=2) { c->mode=(int)value; c->integral=0; return 1; }
    if(line[0]=='D' && value<=100 && c->mode==MODE_MANUAL) { c->manual=(int)value; return 1; }
    return 0;
}
