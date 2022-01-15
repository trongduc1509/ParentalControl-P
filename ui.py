from cgitb import text
from select import select
import tkinter as tk
from tkinter import CENTER, Button, Label, StringVar, ttk
from tkinter import messagebox

from threading import Event, Thread
import time

import datetime
from tokenize import String

from ggapis import APP_DATA_ID, TIME_CONFIG_ID, overwrite_cloud_file, read_data_file

def get_table_value(trv: ttk.Treeview):
    res = ''
    for line in trv.get_children():
        values = trv.item(line)['values']
        res += 'F'+values[0] + ' ' + 'T'+values[1]
        res += ' D'+str(values[2]) if str(values[2]) != '' else ''
        res += ' I'+str(values[3]) if str(values[3]) != '' else ''
        res += ' S'+str(values[4])+'\n' if str(values[4]) != '' else '\n'
    return res

def read_time_frame() -> list[tuple]:
    timeFrames = read_data_file(TIME_CONFIG_ID).splitlines()
    timeList=[]
    for single in timeFrames:
        tempDict = {}
        for item in map(lambda splittedStr: (splittedStr[0], splittedStr[1:]), single.split()):
            tempDict[item[0]] = item[1]
        timeList.append((tempDict['F'],tempDict['T'],tempDict['D'] if 'D' in tempDict else '',tempDict['I'] if 'I' in tempDict else '',tempDict['S'] if 'S' in tempDict else ''))
    return timeList

def update(trv: ttk.Treeview, is_terminate: Event):
    while not is_terminate.is_set():
        rows = read_time_frame()
        trv.delete(*trv.get_children())
        for i in rows:
            trv.insert('','end',values=i)
        time.sleep(60)

def table():
    root = tk.Tk()

    is_terminate = Event()
    t0 = StringVar()
    t1 = StringVar()
    t2 = StringVar()
    t3 = StringVar()
    t4 = StringVar()
    t5 = StringVar()

    wrapper1 = tk.LabelFrame(root, text="TimeFrame List")
    wrapper2 = tk.LabelFrame(root, text="TimeFrame Data")

    wrapper1.pack(fill="both",expand="yes",padx=20,pady=10)
    wrapper2.pack(fill="both",expand="yes",padx=20,pady=10)

    trv = ttk.Treeview(wrapper1, columns=(1,2,3,4,5),show="headings",height="6")
    trv.pack()

    vsb = tk.Scrollbar(wrapper1, orient="vertical", command=trv.yview)
    vsb.pack(side='right',fill='y')

    trv.configure(yscrollcommand=vsb.set)

    trv.heading(1, text="From")
    trv.column(1, width=140, stretch="NO", anchor=CENTER)
    trv.heading(2, text="To")
    trv.column(2, width=140, stretch="NO", anchor=CENTER)
    trv.heading(3, text="Duration")
    trv.column(3, width=140, stretch="NO", anchor=CENTER)
    trv.heading(4, text="Interrupt")
    trv.column(4, width=140, stretch="NO", anchor=CENTER)
    trv.heading(5, text="Sum")
    trv.column(5, width=140, stretch="NO", anchor=CENTER)

    def getRow(event):
        item = trv.item(trv.focus())
        t1.set(item['values'][0])
        t2.set(item['values'][1])
        t3.set(item['values'][2])
        t4.set(item['values'][3])
        t5.set(item['values'][4])

    trv.bind('<Double 1>', getRow)

    update_thread = Thread(target=update,args=(trv,is_terminate))
    update_thread.daemon = True
    update_thread.start()

    #user interface to data section
    ent0 = tk.Entry(wrapper2, textvariable=t0)

    lb1 = Label(wrapper2, text="FROM:")
    lb1.grid(row=0,column=0,padx=5,pady=3)
    ent1 = tk.Entry(wrapper2, textvariable=t1)
    ent1.grid(row=0,column=1,padx=5,pady=3)

    lb2 = Label(wrapper2, text="TO:")
    lb2.grid(row=1,column=0,padx=5,pady=3)
    ent2 = tk.Entry(wrapper2, textvariable=t2)
    ent2.grid(row=1,column=1,padx=5,pady=3)

    lb3 = Label(wrapper2, text="DURATION:")
    lb3.grid(row=2,column=0,padx=5,pady=3)
    ent3 = tk.Entry(wrapper2, textvariable=t3)
    ent3.grid(row=2,column=1,padx=5,pady=3)

    lb4 = Label(wrapper2, text="INTERRUPT:")
    lb4.grid(row=3,column=0,padx=5,pady=3)
    ent4 = tk.Entry(wrapper2, textvariable=t4)
    ent4.grid(row=3,column=1,padx=5,pady=3)

    lb5 = Label(wrapper2, text="SUM:")
    lb5.grid(row=4,column=0,padx=5,pady=3)
    ent5 = tk.Entry(wrapper2, textvariable=t5)
    ent5.grid(row=4,column=1,padx=5,pady=3)

    def writeTimeConfig():
        while read_data_file(APP_DATA_ID) == 'FLAG':
            time.sleep(10)
        else:
            overwrite_cloud_file(APP_DATA_ID,'FLAG')
            temp = get_table_value(trv)
            overwrite_cloud_file(TIME_CONFIG_ID,temp)
            overwrite_cloud_file(APP_DATA_ID,'')

    def updateTimeFrame():
        if trv.focus() != '':
            if t1.get() != '' and t2.get() != '':
                selected_item = trv.selection()[0]
                trv.delete(selected_item)
                trv.insert('','end',values=(t1.get(),t2.get(),int(t3.get()) if t3.get() != '' else '',int(t4.get()) if t4.get() != '' else '',int(t5.get()) if t5.get() != '' else ''))
                writeTimeConfig()

    def addTimeFrame():
        if t1.get() != '' and t2.get() != '':
            trv.insert('','end',values=(t1.get(),t2.get(),int(t3.get()) if t3.get() != '' else '',int(t4.get()) if t4.get() != '' else '',int(t5.get()) if t5.get() != '' else ''))
            writeTimeConfig()

    def delTimeFrame():
        selected_item = trv.selection()[0]
        trv.delete(selected_item)
        writeTimeConfig()

    updateBtn = Button(wrapper2, text="Update", command=updateTimeFrame)
    addBtn = Button(wrapper2, text="Add new", command=addTimeFrame)
    delBtn = Button(wrapper2, text="Delete", command=delTimeFrame)

    addBtn.grid(row=5,column=0,padx=5,pady=3)
    updateBtn.grid(row=5,column=1,padx=5,pady=3)
    delBtn.grid(row=5,column=2,padx=5,pady=3)


    root.title("ParentalControl-Parent")
    root.geometry("800x700")
    root.resizable(False,False)
    root.mainloop()


if __name__ == '__main__':
    table()