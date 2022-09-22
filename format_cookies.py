import os
import json


files = os.listdir("cookies")
for items in files:
    data = json.load(open(f"cookies/{items}"))
    with open("formated.txt", "a+",) as file:
        file.write(f"""{"".join(f"{items['name']}={items['value']}; " for items in data['cookies'])}\n""")
