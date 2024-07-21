list1 = [1, 2, 3, 4, 5, 6, 7, 8]
for i in list1:
    print(i)

for idx, item in enumerate(list1):
    print(idx, item)

for dan, gop in enumerate(list1):
    print(f"{dan+1} x {gop+1} = {(dan+1)*(gop+1)}")