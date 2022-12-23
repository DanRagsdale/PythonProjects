from tkinter import *

root = Tk()

height = 5
width = 5

for i in range(height):
    for j in range(width):
        b = Entry(root, text="")
        b.grid(row=i, column=j)

mainloop()