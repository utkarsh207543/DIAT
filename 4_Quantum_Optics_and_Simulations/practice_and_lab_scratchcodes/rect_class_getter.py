import sys
import math
import random
import threading
import time

class rect:
    def __init__(self, height = "0", width = "0"):
        self.height = height
        self.width = width
    @property
    def height(self):
        print("calling height")
        return self.__height

    @height.setter
    def height(self, value):
        if value.isdigit():
            self.__height = value
        else:
            print("NUMBERS ONLY")

    @property
    def width(self):
        print("calling width")
        return self.__width

    @width.setter
    def width(self, value):
        if value.isdigit():
            self.__width = value
        else:
            print("Enter Only Numbersa")

    def area(self):
        return int(self.__height) * int(self.__width)

    def perimeter(self):
        return 2 * (int(self.__width) + int(self.__height))


    def is_square(self):
        return int(self.__width) == int(self.__height)

    def __str__(self):
        return f"Rectangle: Width = {int(self.__width)}, Height = {int(self.__height)}"


a = input("Enter Height: ")
b = input("Enter Width: ")
rectangle = rect(a, b)
print(rectangle)
print(f"Area: {rectangle.area()}")
print(f"Perimeter: {rectangle.perimeter()}")
print(f"Is square? {rectangle.is_square()}")