from recordclass import dataobject

class Point(dataobject):
    x:int
    y:int

    def __init__(self, x, y):
        self.x = x
        self.y = y


print(Point.__text_signature__)

p = Point()
print(p.x, p.y)
