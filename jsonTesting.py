import json 

#JSON READ:
with open("test.json", "r", encoding="utf-8") as file:
    data = json.load(file)

print(len(data["top_10_colonias"]))

for i in range(10):
    data_col = data["top_10_colonias"][i]["nombre_colonia"]
    print(data_col)
