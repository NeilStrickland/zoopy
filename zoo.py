import numpy as np
# tkinter is the main library for making graphical user interfaces in Python
import tkinter as tk
import tkinter.font as tkf
import customtkinter as ctk 
# PIL is the main library used for processing images in Python
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageEnhance

# We now define a new class called Marker.  Each marker is represented by an
# object of this class.  We need to keep track of various information about
# each marker, such as its position, velocity and age.  This information 
# is stored in the attributes of the Marker object.
class Marker():
    # The __init__ method is called when a new Marker object is created. 
    # All that the method does is to store the given arguments as attributes
    # of the new object.
    def __init__(self, x, y, dx, dy, text, age=0, img=None, obj=None):
        self.x = x          # current x coordinate
        self.y = y          # current y coordinate
        self.dx = dx        # change in x for each time step
        self.dy = dy        # change in y for each time step
        self.text = text    # a single unicode emoji character 
        self.age = age      # number of time steps since creation
        self.img = img      # PIL image object
        self.obj = obj      # tkinter object

# By writing Zoo(tk.Tk), we declare that the new class Zoo is a subclass of tk.Tk
# This means that Zoo inherits all the methods and attributes of tk.Tk
class Zoo(tk.Tk):
    def __init__(self):
        # We first do the standard initialization of a tk.Tk object
        tk.Tk.__init__(self)
        # Then we define the additional attributes that we want to add to the Zoo class
        self.animals = '🐜🦋🐪🐬🐘🐸🐐🐹🍧🎃🐨🐞🐭📔🐙🐧🐮🦏🐍🐯🐢🦀🐋🐌🐝🦉'
        self.font = ImageFont.truetype("seguiemj.ttf", size=int(24))
        self.size = 32         # size of marker images in pixels
        self.max_age = 8000    # number of time steps before markers disappear
        self.markers = []      # list of Marker objects
        self.is_frozen = False 
        self.canvas = tk.Canvas(self, width=500, height=500)
        self.canvas.pack()

        # The next line means that when the left mouse button is clicked, 
        # the method self.onclick will be called
        self.canvas.bind("<Button-1>", self.onclick)
        # The next line means that when a key is pressed, the method 
        # self.onkey will be called
        self.bind("<KeyPress>", self.onkey)
        # The main purpose of the update() method is to update the 
        # positions of the markers.  At the moment there are no markers so
        # there is nothing to do.  However, the update() method also 
        # sets a timer to call itself again after 100 milliseconds.  Thus,
        # by calling update() now, we ensure that the markers will be
        # updated every 100 milliseconds from now on.
        self.update()

    def add_marker(self, x, y, dx, dy, text):
        """Add a new marker to the canvas at position (x, y) with velocity (dx, dy) and text."""
        # Because emojis are just strings, we could add them to the 
        # canvas using the create_text method.  However, they would then
        # just be black and white, because tkinter does not support 
        # mulicolored text.  Instead, we will use the PIL library to
        # create a colored image of the emoji and then add the image to
        # the canvas.

        # The approach used here is taken from 
        # https://stackoverflow.com/questions/66183690/how-to-display-colored-emojis-in-tkinter
        
        m = Marker(x, y, dx, dy, text)
        # Create a PIL image
        m.img = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
        # Create an object that can be used to draw on the image
        m.draw = ImageDraw.Draw(m.img)
        m.draw.text((self.size/2, self.size/2), m.text,
                    embedded_color=True, font=self.font, anchor="mm")
        # For technical reasons we now need to convert the PIL image to a
        # slightly different form.
        m.img = ImageTk.PhotoImage(m.img)
        # Now we can add the image to the canvas
        m.obj = self.canvas.create_image(m.x, m.y, image=m.img)
        # Finally, we add the new marker to the list of markers
        self.markers.append(m)
        return m
        
    def onclick(self, event):
        # This method is called when the left mouse button is clicked
        # The argument event is an object that contains information about
        # the click.  All that we need are the attributes event.x and
        # event.y, which give the x and y coordinates of the click.

        # Choose a random animal.
        i = np.random.randint(0, len(self.animals))
        a = self.animals[i]

        # Choose a random velocity.
        dx = (np.random.random() - 0.5) * 10
        dy = (np.random.random() - 0.5) * 10

        # Add a new marker at the position of the click with the chosen
        # velocity and the chosen animal.
        self.add_marker(event.x, event.y, dx, dy, a)

    def onkey(self, event):
        # This method is called when a key is pressed.  The argument event
        # is an object that contains information about the key press.  All
        # that we need is the attribute event.char, which gives the
        # character that was pressed.

        c = event.char.lower()
        if c == '+':
            self.accelerate(1.3)
        elif c == '-':
            self.accelerate(0.7)
        elif c == '.':
            self.is_frozen = not self.is_frozen
        elif c == '#':
            self.clear()
        # Under unusual circumstances, such as when many keys are pressed in
        # quick succession, event.char may be an empty string.  If so, the 
        # test 'elif c' will fail and the following code will not be executed.
        # This is a good thing, because ord(c) will give an error if c is empty.
        elif c:
            i = ord(c) - ord('a')
            if 0 <= i < len(self.animals):
                # If we get here, then the key that was pressed was a letter

                # Choose a random position.
                x = np.random.randint(10, 490)
                y = np.random.randint(10, 490)

                # Choose a random velocity.
                dx = (np.random.random() - 0.5) * 10
                dy = (np.random.random() - 0.5) * 10

                # Add a new marker at the chosen position with the chosen
                # velocity and the animal corresponding to the key that was
                # pressed.
                self.add_marker(x, y, dx, dy, self.animals[i])

    def clear(self):
        """Remove all markers from the canvas."""
        for m in self.markers:
            self.canvas.delete(m.obj)
        self.markers = []

    def accelerate(self, f):
        """Multiply the velocity of all markers by f."""
        for m in self.markers:
            m.dx *= f  # This is shorthand for m.dx = m.dx * f
            m.dy *= f  # This is shorthand for m.dy = m.dy * f

    def update(self):
        """Update the positions of the markers and remove old markers."""
        # This method is called every 100 milliseconds.

        if not self.is_frozen:
            for m in self.markers:
                # Move the marker
                m.x += m.dx # This is shorthand for m.x = m.x + m.dx
                m.y += m.dy # This is shorthand for m.y = m.y + m.dy
                self.canvas.coords(m.obj, m.x, m.y)
                # If the marker reaches the edge of the canvas, make it bounce
                if m.x < 10 or m.x > 490:
                    m.dx *= -1
                if m.y < 10 or m.y > 490:
                    m.dy *= -1
                # Update the age of the marker
                m.age += 1
                # The next few lines make the marker fade away as it gets older
                img0 = ImageTk.getimage(m.img)
                alpha = img0.split()[3]
                o = 1 - np.minimum(1,np.maximum(0, m.age / self.max_age))
                alpha = ImageEnhance.Brightness(alpha).enhance(o)
                img0.putalpha(alpha)
                m.img.paste(img0)
                # If the marker is too old, remove it
                if m.age > self.max_age:
                    self.canvas.delete(m.obj)
                    self.markers.remove(m)
                
        # Set a timer to call this method again after 100 milliseconds
        self.after(100, self.update)
        
# Create a new Zoo object
zoo = Zoo()

# We now call the method mainloop().  This is a method of the tk.Tk class,
# and Zoo is a subclass of tk.Tk, so it inherits the method mainloop().
# The effect is to create the window and start the event loop, which 
# listens for events such as key presses and mouse clicks.
zoo.mainloop()

