# Base class (superclass)
class Shape:
    def __init__(self, name):
        self.name = name

    def area(self):
        pass  # This method will be overridden in the derived classes

    def perimeter(self):
        pass  # This method will be overridden in the derived classes

    def description(self):
        return f"This is a {self.name}."

# Derived class 1
class Circle(Shape):
    def __init__(self, name, radius):
        super().__init__(name)
        self.radius = radius

    def area(self):
        return 3.14159265359 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159265359 * self.radius

# Derived class 2
class Rectangle(Shape):
    def __init__(self, name, width, height):
        super().__init__(name)
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

# Example usage
circle = Circle("circle", 5)
print(circle.description())
print(f"Area: {circle.area()}")
print(f"Perimeter: {circle.perimeter()}")

rectangle = Rectangle("rectangle", 4, 6)
print(rectangle.description())
print(f"Area: {rectangle.area()}")
print(f"Perimeter: {rectangle.perimeter()}")
