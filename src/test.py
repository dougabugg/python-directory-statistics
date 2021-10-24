from tkinter import *
from tkinter.filedialog import askopenfilename

def NewFile():
    print("New File!")
def OpenFile():
    name = askopenfilename()
    print(name)
def About():
    print("This is a simple example of a menu")

root = Tk()
menu = Menu(root)
##root.config(menu=menu)
root['menu'] = menu
filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=NewFile)
filemenu.add_command(label="Open...", command=OpenFile)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)

helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=About)

mainloop()


"""from tkinter import *
from tkinter import ttk

root = Tk()
l = Listbox(root, height=5)
s = Scrollbar(root)
s['command'] = l.yview
l['yscrollcommand'] = s.set
l.grid(column=0, row=0, sticky=(N,W,E,S))
s.grid(column=1, row=0, sticky=(N,S))

ttk.Sizegrip().grid(column=1, row=1, sticky=(S,E))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
for i in range(1,101):
    l.insert('end', 'Line %d of 100' % i)
root.mainloop()
"""






















