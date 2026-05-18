attendants = ["George", "Ben", "Cynthia", "Chris", "Julian"]

unique_attendants = set(attendants)

print("Unique attendants:", unique_attendants)

print("Is Ben coming?", "Ben" in unique_attendants)

players1 = {"George", "Ben", "Dave"}

players2 ={"Ben", "Chris", "Julian"}

print("Players on both teams:", players1 & players2)

print("Players at event:", players1 | players2)
