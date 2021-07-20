from tkinter import *
from tkinter import ttk
from tkinter import messagebox
class pavan():
    
    def __init__(self,master):
        
        self.master=master
        self.master.title("pavan")
        self.master.geometry("1350x700+0+0")
        loginbutton=Button(self.master,text="Login", width=15, font=("times new roman",14,"bold"),bg="pink", fg="red", command= self.logbutton).grid(row=3,column=1,pady=10)

    def logbutton(self):
        messagebox.showinfo("kdsj","slkdjf")
        self.window=Toplevel(self.master)
        self.o=kumar(self.window)

    

    def new_window(self):
        self.window=Toplevel(self.master)
        self.o=kumar(self.window)


class kumar:
    def __init__(self,master):
        
        self.master=master
        self.master.title("kumar")
        self.master.geometry("1350x700+0+0")

        butt=Button(self.master,text="click", width=15, font=("times new roman",14,"bold"),bg="blue", fg="red", command= self.click).grid(row=3,column=1,pady=10)

    def click(self):
        self.window=Toplevel(self.master)
        self.o=kumar(self.window)
        messagebox.showinfo("sldkf","slkdhjf")
        




        
root=Tk()
o=pavan(root)
#k=kumar(o)
root.mainloop()
