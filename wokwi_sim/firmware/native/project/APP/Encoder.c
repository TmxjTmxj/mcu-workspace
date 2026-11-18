//#include	"type_def.h"
#include	"Encoder.h"
#include	"stdio.h"


u16 encoderTemp;

void SendEncoder(void)
{
	printf("Encoder = %d\n\r", encoderTemp);
}