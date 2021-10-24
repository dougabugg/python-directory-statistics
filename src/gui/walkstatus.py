from tkinter import *
from tkinter import ttk
from fstree.util import createSnapshot
from fstree.walkfs import BreakWalk,Inspector
import threading,queue,time
why = None
def demo():
    root = Tk()
    win = WalkStatusPopup(master=root,path="C:/")
    #root.mainloop()
    return win

class WalkStatusPopup(Toplevel):
    def __init__(self,master,*a,**k):
        super().__init__(master=master)
        self.transient(master)
        self.frame = frame = WalkStatusFrame(master=self,*a,**k)
        frame.grid()
        self.title("New Snapshot")
        self.wm_attributes("-toolwindow","true","-topmost","true")
        self.update()
        self.resizable(0,0)
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth()-width)/2
        y = (self.winfo_screenheight()-height)/2
        self.geometry("+{:.0f}+{:.0f}".format(x,y))
class WalkStatusFrame(ttk.Frame):
    def __init__(self,path,callback=None,maxItems=None,poll=200,*a,**k):
        super().__init__(*a,**k)
        self.path = path
        self.snapshot = None
        self.callback = callback
        self.maxItems = maxItems
        self.inspect = Inspector()
        self.poll = poll
        #setup label, progress bar, and cancel button
        self.status = status = StringVar()
        label = ttk.Label(master=self,textvariable=status)
        label.pack()
        if maxItems:
            self.progress = progress = IntVar()
            progressbar = ttk.Progressbar(master=self,length=150,variable=progress)
            progressbar.pack()
        self.startButton = startButton = ttk.Button(
            master=self,text="Start",command=self.start)
        startButton.pack(side="left")
        self.pauseButton = pauseButton = ttk.Button(
            master=self,text="Pause",command=self.pause)
        pauseButton.pack(side="right")
        #populate the label
        self.pollInspector()
    def pause(self):
        i = self.inspect
        if i.finished or not i.started:
            return
        if i.running:
            self.pauseButton["text"] = "Resume"
            self.inspect.pauseEvent.clear()
        else:
            self.pauseButton["text"] = "Pause"
            self.inspect.pauseEvent.set()
    def cancel(self):
        self.inspect.breakEvent.set()
    def start(self):
        self.startButton["text"] = "Cancel"
        self.startButton["command"] = self.cancel
        self.inspect = Inspector()
        self.t = threading.Thread(target=self.runThread)
        self.t.start()
        self.pollInspector()
    def pollInspector(self):
        i = self.inspect
        if i.finished:
            self.startButton["text"] = "Start"
            self.startButton["command"] = self.start
            if i.breakEvent.is_set():
                status = "Canceled by user"
            else:
                status = "Completed successfully"
        elif i.running:
            status = "Creating new snapshot..."
        else:
            status = "Paused by user"
        if i.started:
            self.after(self.poll,self.pollInspector)
        else:
            status = "Waiting to start"
        status += "\nProcessed {:.0f} ".format(i.progress)
        if self.maxItems:
            self.progress.set(i.progress/self.maxItems)
            status += "of {:.0f} ".format(self.maxItems)
        status += "items,\n" \
            "at {:.2f} items/second\n".format(i.rate)
        status += "Elapsed: {:.2f} seconds".format(i.elapsed)
        self.status.set(status)
        if i.finished and self.callback:
            self.callback(self.snapshot)
    def runThread(self):
        try:
            self.snapshot = createSnapshot(
                self.path,inspect=self.inspect)
        except BreakWalk:
            pass
    def putUpdate(self,status,progress):
        self.q.put([self.status,status])
        self.q.put([self.progress,progress])
    def destroy(self):
        self.cancel()
        super().destroy()

if __name__ == "__main__":
    demo()
