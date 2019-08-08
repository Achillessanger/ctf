for(int i = 0; i < 32; ++i){
	v0 = (int)(((int)(&i)) + i);  v0=v0+v1
	*((unsigned int)(((int)(&v1)) + i) ) = (unsigned char)(    ((int)(((unsigned char)(32 -((unsigned int)(((unsigned char)i)))))))     ^  ((int)(*(v0 + 4)))      )
	(int)(*((int)(&i) + i)+4)
}


v0 = 32 - v0
v0 = v1 ^ v0