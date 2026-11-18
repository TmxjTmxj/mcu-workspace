#include "protocol.h"
int protocol_byte(LineParser *p,unsigned char b) {
    if(b=='\r')return 0;
    if(b=='\n') {
        p->line[p->used]=0;int result=p->discard?-1:1;p->used=p->discard=0;return result;
    }
    if(b<32 || b>126) p->discard=1;
    else if(p->used<sizeof(p->line)-1 && !p->discard) p->line[p->used++]=(char)b;
    else p->discard=1;
    return 0;
}
