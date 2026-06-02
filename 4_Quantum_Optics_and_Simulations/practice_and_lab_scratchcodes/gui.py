import tkinter as tk

# Create a function to update the label text
def update_label_text():
    label.config(text="Hello, Fuck you")

# Create the main application window
root = tk.Tk()
root.title("Fucker Loop")

# Create a label widget
label = tk.Label(root, text="Fuck you")
label.pack(pady=10)

# Create a button widget
button = tk.Button(root, text="Fuck off,", command=update_label_text)
button.pack()

# Start the tkinter main loop
root.mainloop()
