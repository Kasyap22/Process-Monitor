import tkinter as tk
import psutil
from datetime import datetime
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os
import signal


window = tk.Tk()
window.title('Process Monitor')
window.geometry("1500x900")

"""
Function that is called when the search entry box is clicked
to remove the placeholder text displayed before.
"""

def click(*args):
    search_entry.delete(0, 'end')

"""
Gives the sizes in more readable manner

"""
def get_size(bytes):
    """
    Returns size of bytes in a nice format
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

"""
Searches the treeview table for the string parameter and
highlights and jumps to the row it is at, if found.
If not found, displays a message box saying not found.
"""

def searchButtonCallback(searchStr):
    children = tree.get_children()
    flag=0
    for child in children:
        if flag==1:
           return True 
        rowData = tree.set(child)

        if rowData['pid']==(search_entry.get().lower()):

            tree.selection_set(child)
            tree.see(child)
            flag=1
        else:
            flag=0
    if flag==0 :
        tk.messagebox.showinfo("SEARCH FAILURE", "<" + searchStr +">" + " was not found in the PID column of the table.")
    else:
        return True

def killButtonCallback(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callabck function which is
    called as soon as a child terminates.
    """
    tk.messagebox.showinfo("KILL BUTTON","Kill Button killing : " + search_entry.get())
    if pid == os.getpid():
        raise RuntimeError("I refuse to kill myself")
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        p.send_signal(sig)
    gone, alive = psutil.wait_procs(children, timeout=timeout,callback=on_terminate)
    selection = tree.selection()[0]
    tree.delete(selection)
    update()
    return (gone, alive)

def suspendButtonCallback():
    tk.messagebox.showinfo("SUSPEND BUTTON","Suspend Button suspending : " + search_entry.get())
    some_pid = int(search_entry.get() )
    p = psutil.Process(some_pid)
    print("BEFORE SUSPEND : " + p.status())
    p.suspend()
    print("AFTER SUSPEND : " + p.status())
    update()
    
    
def resumeButtonCallback():
    tk.messagebox.showinfo("RESUME BUTTON","Resume Button resuming : " + search_entry.get())
    some_pid = int(search_entry.get() )
    p = psutil.Process(some_pid)
    print("BEFORE RESUME : " + p.status())
    p.resume()
    print("AFTER RESUME : " + p.status())
    update()
    
def refreshButtonCallback():
    tk.messagebox.showinfo("REFRESH BUTTON","Refresh Button refreshing list.")
    update()

"""
Makes the column headings for the treeview
"""

def createHeadings():
    tree.column('pid',width=100 ,anchor=CENTER)
    tree.column('name',width=200 ,anchor=CENTER)
    tree.column('cpu usage',width=75 ,anchor=CENTER)
    tree.column('memory usage',width=100 ,anchor=CENTER)
    tree.column('read bytes',width=100 ,anchor=CENTER)
    tree.column('written bytes',width=100 ,anchor=CENTER)
    tree.column('status',width=100 ,anchor=CENTER)
    tree.column('create time',width=200 ,anchor=CENTER)
    tree.column('priority',width=50 ,anchor=CENTER)
    tree.column('thread count',width=100 ,anchor=CENTER)
    tree.column('cores',width=50 ,anchor=CENTER)
    tree.column('username',width=150 ,anchor=CENTER)
    
    tree.heading('pid', text='PID')
    tree.heading('name', text='Name')
    tree.heading('cpu usage', text='CPU Usage')
    tree.heading('memory usage', text='Memory Usage')
    tree.heading('read bytes', text='Read Bytes')
    tree.heading('written bytes', text='Written Bytes')
    tree.heading('status', text='Status')
    tree.heading('create time', text='Create Time')
    tree.heading('priority', text='Priority')
    tree.heading('thread count', text='Thread Count')
    tree.heading('cores', text='Cores')
    tree.heading('username', text='Username')
    
"""    
Input a list.
In the format :
('first 1', 'last 1', 'email1@example.com', '1')
for however many columns we end up using
and in the same order as the column order, so
pid, name, cpu, memory, read, written, status, create time, priority, thread count, cores, username
"""

def tableData(content_list):
    for i in tree.get_children():
        tree.delete(i)
    for content in content_list:
        tree.insert('', tk.END, values=content)

columns = ('pid', 'name', 'cpu usage', 'memory usage', 'read bytes', 'written bytes', 'status', 'create time', 'priority','thread count', 'cores', 'username')

style=ttk.Style()
style.theme_use('clam')
tree = ttk.Treeview(window, columns=columns, show='headings', height=23)

"""
Generates data for the UI
"""
def data_generation():
    contacts = []
    for process in psutil.process_iter():
            # get the process id
        with process.oneshot():
            pid = process.pid
            if pid == 0:
                # System Idle Process for Windows NT, useless to see anyways
                continue
            # get the name of the file executed
            name = process.name()
            # get the time the process was spawned
            try:
                create_time = datetime.fromtimestamp(process.create_time())
            except OSError:
                # system processes, using boot time instead
                create_time = datetime.fromtimestamp(psutil.boot_time())
            try:
                # get the number of CPU cores that can execute this process
                cores = len(process.cpu_affinity())
            except psutil.AccessDenied:
                cores = 0
            # get the CPU usage percentage
            cpu_usage = process.cpu_percent()
             # get the status of the process (running, idle, etc.)
            status = process.status()
            try:
                # get the process priority (a lower value means a more prioritized process)
                nice = int(process.nice())
            except psutil.AccessDenied:
                nice = 0
            try:
                # get the memory usage in bytes
                memory_usage = process.memory_full_info().uss
            except psutil.AccessDenied:
                memory_usage = 0
             # total process read and written bytes
            memory_usage = get_size(memory_usage)
            io_counters = process.io_counters()
            read_bytes = io_counters.read_bytes
            read_bytes = get_size(read_bytes)
            write_bytes = io_counters.write_bytes
            write_bytes = get_size(write_bytes)
             # get the number of total threads spawned by this process
            n_threads = process.num_threads()
              # get the username of user spawned the process
            try:
                username = process.username()
            except psutil.AccessDenied:
                username = "N/A"
            contacts.append((f'{pid}', f'{name}', f'{cpu_usage}', f'{memory_usage}', f'{read_bytes}', f'{write_bytes}', f'{status}', f'{create_time}',f'{nice}', f'{n_threads}', f'{cores}', f'{username}'))
                #print(contacts)
    return contacts

"""data gets updated every 10sec by default"""

def update():
    updated_data=[]
    updated_data = data_generation()
    tableData(updated_data)
    window.after(10000,update) 

"""
Makes the search text box to enter PID.
"""

search_entry=Entry(window)
search_entry.grid(row=0,column=0,sticky='w',padx=10)
search_entry.insert(0,"Enter PID to search")
search_entry.bind("<Button-1>", click)

tree.grid(row=1, column=0, sticky='nsew',padx=10)

"""
Adds a scrollbar to the table
and assigns it a position on the grid.
"""

scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=1, column=1, sticky='ns')

"""
Makes the search, kill, suspend, resume and refresh buttons
and assigns their positions on the grid.
"""

searchButton = Button(window,text="Search",command = lambda : searchButtonCallback(search_entry.get()))
searchButton.grid(row=2,column=0,pady=5,padx=10,sticky='w')

killButton = Button(window,text="Kill", command = lambda : killButtonCallback(int(search_entry.get())))
killButton.grid(row=3,column=0,pady=5,padx=10,sticky='w')

suspendButton = Button(window, text="Suspend", command = lambda : suspendButtonCallback() )
suspendButton.grid(row=4,column=0,pady=5,padx=10,sticky='w')

resumeButton = Button(window, text = "Resume", command = lambda : resumeButtonCallback() )
resumeButton.grid(row=5, column=0,pady=5,padx=10,sticky='w')

refreshButton = Button(window, text = "Refresh", command = lambda : refreshButtonCallback() )
refreshButton.grid(row=6, column=0,pady=5,padx=10,sticky='w')


# run the app
#update()
if __name__=="__main__":
    """
    Creating table headings and inserting data
    """  
    createHeadings()
    data = data_generation()
    tableData(data)
    window.mainloop()