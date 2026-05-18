numbers = []
min_val = float('inf')
max_val = float('-inf')

# input loop + min/max  in single pass
for i in range(10):
    num = int(input("Enter a number: "))
    numbers.append(num)
    if num < min_val:
        min_val = num
    if num > max_val:
        max_val = num

print(f"Max is {max_val}")
print(f"Min is {min_val}")

# find duplicates in another pass
duplicates = []
seen = []

for i in range(10):
    num = numbers[i]
    if num in seen:
        if num not in duplicates:
            duplicates.append(num)
    else:
        seen.append(num)

#output duplicates
print("Duplicates: ", end="")
if duplicates:
    for i in range(len(duplicates)):
        print(duplicates[i], end="")
        if i < len(duplicates) - 1:
            print(" ", end="")
        print()
else:
    print("No duplicates")

