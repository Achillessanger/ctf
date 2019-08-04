def caesar_encrypt(m,k):
r=""
for i in m:
r+=chr((ord(i)+k)%128)
return r

from secret import m,k
print caesar_encrypt(m,k).encode("base64")

#output:bXNobgJyaHB6aHRwdGgE
#k从0-128爆破找有没有flag这个特征