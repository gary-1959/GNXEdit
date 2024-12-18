
# number pack

v =[]
n = 10
while n > 0:
    d = n % 256
    v.append(d)
    n = (n // 256)

if len(v) > 0:
    v.append(0b10000000 | len(v))   # signals multi-byte number

#reverse the order
print(v)
v = v[::-1]

print(v)