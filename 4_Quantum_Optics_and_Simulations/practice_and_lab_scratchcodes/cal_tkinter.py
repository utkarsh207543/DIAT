import tkinter as tk


def on_button_click(event):
    text = event.widget.cget("text")

    if text == "=":
        try:
            result = str(eval(screen.get()))
            screen.set(result)
        except Exception as e:
            screen.set("Error")
    elif text == "C":
        screen.set("")
    else:
        screen.set(screen.get() + text)


root = tk.Tk()
root.title("Calculator")

screen = tk.StringVar()
entry = tk.Entry(root, textvar=screen, font="Helvetica 24", justify="right")
entry.pack(fill=tk.BOTH, ipadx=8, ipady=8, padx=10, pady=10)

button_frame = tk.Frame(root)
button_frame.pack()

button_labels = [
    "7", "8", "9", "+",
    "4", "5", "6", "-",
    "1", "2", "3", "*",
    "C", "0", "=", "/"
]

row, col = 0, 0
for label in button_labels:
    button = tk.Button(button_frame, text=label, font="Helvetica 18", width=5, height=2)
    button.grid(row=row, column=col, padx=5, pady=5)
    button.bind("<Button-1>", on_button_click)
    col += 1
    if col > 3:
        col = 0
        row += 1

root.mainloop()
