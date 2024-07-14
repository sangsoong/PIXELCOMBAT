import math

class Circle:
    def __init__(self, a, b, radius):
        self.a = a
        self.b = b
        self.radius = radius

    def formula(self, x):
        y = math.sqrt(self.radius**2 - (x-self.a)**2) + self.b
        return (-1*y, y)

    def circle_area(self):
        return math.pi * (self.radius ** 2)

    def is_in_circle(self, x, y):
        if (x-self.a)**2 + (y-self.b)**2 <= self.radius ** 2:
            return True
        elif (x-self.a)**2 + (y-self.b)**2 > self.radius ** 2:
            return False

if __name__ == '__main__':
    circle1 = Circle(3, 4, 5)
    area = circle1.circle_area()
    isin = circle1.is_in_circle(4, 5)

    print(area, isin)