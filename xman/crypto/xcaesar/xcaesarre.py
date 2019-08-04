output = 'bXNobgJyaHB6aHRwdGgE'
for i in range(128):
	output2=''
	for j in output.decode('base64'):
		output2 += chr((ord(j)+i)%128)
	if 'flag' in output2:
		print output2
		
	

