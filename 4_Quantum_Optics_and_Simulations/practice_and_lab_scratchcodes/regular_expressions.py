import re


if re.search("ape", "The ap at the apx"):
    print("There's an ape")

all_apes = re.findall("ape", " ape in the apex")
for i in all_apes:
    print(i)

