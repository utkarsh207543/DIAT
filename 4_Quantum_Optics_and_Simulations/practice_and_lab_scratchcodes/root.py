# main.py
import sqroot

# Input a number for which you want to find the square root
user_input = float(input("Enter a number: "))

# Call the find_square_root function from the square_root module
result = sqroot.sqroot(user_input)

# Display the result
print(f"The square root of {user_input} is: {result}")
