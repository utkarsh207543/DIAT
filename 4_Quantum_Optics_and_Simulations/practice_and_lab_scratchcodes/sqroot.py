# sqroot
import math

def sqroot(number):

    if number < 0:
        return "Cannot calculate the square root of a negative number"
    else:
        number = math.sqrt(number)
        return number
