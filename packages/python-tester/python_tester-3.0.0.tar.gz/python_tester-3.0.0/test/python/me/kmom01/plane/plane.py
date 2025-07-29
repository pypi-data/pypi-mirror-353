#!/usr/bin/evn python3

"""
Program som tar emot värden av en enhetstyp och omvandlar till motsvarande
värde av en annan.
"""
# raise ValueError("hejhejhej")
# raise StopIteration("hejhejhej")
print("Hello and welcome to the unit converter!")

hight = float(input("Enter current hight in meters over sea, and press enter: "))
speed = float(input("Enter current velocity in km/h, and press enter: "))
temp = float(input("Enter current outside temperature in °C, and press enter: "))
# temp = float(input("Enter current outside temperature in °C, and press enter: "))

h = str(round(hight * 3.28084, 2))
s = str(round(speed * 0.62137, 2))
t = str(round(temp * 9 / 5 + 32, 2))

print(str(hight) + " meters over sea is equivalent to " + h + " feet over sea.")
print(str(speed) + " km/h is equivalent to " + s + " mph")
print(str(temp) + " °C is equivalent to " + t + "  °F")
