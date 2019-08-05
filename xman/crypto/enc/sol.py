import libnum
f = open('zero_one','r')
s = f.read()
output = ''
for i in s.split():
	if('ZERO' == i):
		output += '0'
	if('ONE' == i):
		output += '1'
output = int(output,2)
print output
print libnum.n2s(output)