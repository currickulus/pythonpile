pet_list = ["cats", "dogs", "fish", "lizards"]

pet_list.append("snakes")

pet_list.remove("lizards")

pet_list[1] = "dogs subsitute"

print("Pet list:", pet_list)

print("Number of pet types:", len(pet_list))

for item in pet_list:

    print("buy:", item)
