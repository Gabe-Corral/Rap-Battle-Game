import tkinter as tk
from client import Client

class StartClient:

    def __init__(self):
        self.root =  tk.Tk()
        self.root.geometry("500x100")
        self.ip_entry = tk.Entry(self.root, width=40)
        self.ip_entry.pack()
        self.ip_button = tk.Button(self.root, text="Connect",
        command=self.join)
        self.ip_button.pack()
        tk.mainloop()

    def join(self):
        self.ip = self.ip_entry.get()
        self.root.destroy()
        Client(self.ip)
        quit()

if __name__=="__main__":
    StartClient()
