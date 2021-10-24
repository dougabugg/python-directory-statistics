from tkinter import *

import threading # should use the threading module instead!
import queue

import os

class ThreadSafeConsole(Text):
    def __init__(self, master, **options):
        Text.__init__(self, master, **options)
        self.queue = queue.Queue()
        self.update_me()
    def write(self, line):
        self.queue.put(line)
    def clear(self):
        self.queue.put(None)
    def update_me(self):
        try:
            while 1:
                line = self.queue.get_nowait()
                if line is None:
                    pass#self.delete(1.0, END)
                else:
                    self.insert(END, str(line))
                self.see(END)
                self.update_idletasks()
        except queue.Empty:
            pass
        self.after(100, self.update_me)

# this function pipes input to an widget
def pipeToWidget(i, widget):
    widget.clear()
    while 1:
        line = i.readline()
        if not line:
            break
        widget.write(line)

def funcThread(widget):
    i = os.popen('dir', 'r')
    pipeToWidget(i, widget)

# uber-main
root = Tk()
widget = ThreadSafeConsole(root)
widget.pack(side=TOP, expand=YES, fill=BOTH)
for i in range(5):
    threading.Thread(target=funcThread, args=[widget]).start()
root.mainloop()
