grades ={
        "George": 93,
        "Fred": 88,
        "Davina": 78
        }
grades["Charles"] = 95
grades["Steve"] = 88

print("All grades:", grades)
print("George's grade:", grades["George"])
print("Davina's grade:", grades.get("Davina"))

words = ["rock", "tree", "branch", "leaf", "twig", "bark"]
count = {}
for word in words:
    count[word] = count.get(word, 0) + 1
print("Word counts:", count)
