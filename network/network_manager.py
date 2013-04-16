#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter

class NetworkSetupDialog:
    def __init__(self, on_save, on_cancel, on_close):
        self.win = Tkinter.Toplevel()
        self.win.title("Network Config")
        self.win.protocol("WM_DELETE_WINDOW", on_close)

        form = Tkinter.Frame(self.win)
        frame = Tkinter.Frame(form)

        labels = Tkinter.Frame(frame)
        Tkinter.Label(labels, text="Address").pack(side=Tkinter.TOP, pady=4)
        Tkinter.Label(labels, text="Netmask").pack(side=Tkinter.TOP, pady=4)
        Tkinter.Label(labels, text="Gateway").pack(side=Tkinter.TOP, pady=4)
        labels.pack(side=Tkinter.LEFT)

        entris = Tkinter.Frame(frame)
        self.address = Tkinter.Entry(entris)
        self.address.pack(side=Tkinter.TOP, pady=4)
        self.netmask = Tkinter.Entry(entris)
        self.netmask.pack(side=Tkinter.TOP, pady=4)
        self.gateway = Tkinter.Entry(entris)
        self.gateway.pack(side=Tkinter.TOP, pady=4)
        entris.pack(side=Tkinter.LEFT)

        frame.pack(side=Tkinter.TOP)

        frame = Tkinter.Frame(form)
        button = Tkinter.Button(frame, text="Cancel", command=on_cancel)
        button.pack(side=Tkinter.RIGHT)
        button = Tkinter.Button(frame, text="Save", command=on_save)
        button.pack(side=Tkinter.RIGHT)
        frame.pack(side=Tkinter.TOP, anchor="e", pady=4)

        form.pack(padx=10, pady=4)

    def destroy(self):
        self.win.destroy()


class App:
    def __init__(self, master):
        self.master = master
        self.master.withdraw()
        self.dialog = NetworkSetupDialog(self.save_setup, self.cancel_setup, self.cancel_setup)

    def save_setup(self):
        dialog = self.dialog
        print "Save %s, %s, %s" % (dialog.address.get(), dialog.netmask.get(), dialog.gateway.get())
        self.dialog.destroy()
        self.quit()

    def cancel_setup(self):
        self.dialog.destroy()
        self.quit()

    def quit(self):
        self.master.quit()



if __name__ == "__main__":
    root = Tkinter.Tk()
    app = App(root)
    Tkinter.mainloop()

