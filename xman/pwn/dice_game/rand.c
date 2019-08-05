#include<stdio.h>
#include<stdlib.h>

int main(){
	srand(1);
	for(int i = 0;i < 50 ;i ++)
		printf("%d,",rand()%6 + 1);
	printf("\n");
}