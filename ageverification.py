name = input("What's your name?: ")
print("Hello dear", name)
age = int(input("how old are you ?: "))
age_required = 14
if age < age_required:
    print("You're to young.")
elif age == age_required:
    print("Welcome")
    email = input("What's your e-mail?: ")
    print("Thank you. We will send more information to",email)
else:
    print("You're to old.")