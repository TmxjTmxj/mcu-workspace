#ifndef PROTOCOL_H
#define PROTOCOL_H
typedef struct { char line[24]; unsigned used,discard; } LineParser;
/* 0 waiting, 1 valid complete ASCII line, -1 rejected complete line. */
int protocol_byte(LineParser *p,unsigned char byte);
#endif
