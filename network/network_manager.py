#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter
import tkMessageBox
import ifconfig
import route
import socket
import subprocess


class NetworkSetupDialog:
    def __init__(self, info, on_save, on_cancel, on_close):
        self.win = Tkinter.Toplevel()
        self.win.title("Network Setup")
        self.win.protocol("WM_DELETE_WINDOW", on_close)
        self.on_save_callback = on_save

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

        self.address.insert(0, info["address"])
        self.netmask.insert(0, info["netmask"])
        self.gateway.insert(0, info["gateway"])

        entris.pack(side=Tkinter.LEFT)

        frame.pack(side=Tkinter.TOP)

        frame = Tkinter.Frame(form)
        button = Tkinter.Button(frame, text="Cancel", command=on_cancel)
        button.pack(side=Tkinter.RIGHT)
        button = Tkinter.Button(frame, text="Save", command=self.on_save)
        button.pack(side=Tkinter.RIGHT)
        frame.pack(side=Tkinter.TOP, anchor="e", pady=4)

        form.pack(padx=10, pady=4)

    def on_save(self):
        address = self.address.get()
        if not self.is_valid_ipv4_address(address):
            tkMessageBox.showerror("Input Error", "Address Field Format Error!")
            return
        netmask = self.netmask.get()
        if not self.is_valid_ipv4_address(netmask):
            tkMessageBox.showerror("Input Error", "Netmask Field Format Error!")
            return
        gateway = self.gateway.get()
        if not self.is_valid_ipv4_address(gateway):
            tkMessageBox.showerror("Input Error", "Gateway Field Format Error!")
            return
        self.on_save_callback()


    def is_valid_ipv4_address(self, address):
        try:
            addr= socket.inet_pton(socket.AF_INET, address)
        except AttributeError: # no inet_pton here, sorry
            try:
                addr= socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error: # not a valid address
            return False

        return True

    def destroy(self):
        self.win.destroy()


class NetworkStatusDialog:
    def __init__(self, info, on_edit, on_exit, on_close):
        self.win = Tkinter.Toplevel()
        self.win.title("Network Status")
        self.win.protocol("WM_DELETE_WINDOW", on_close)

        form = Tkinter.Frame(self.win)
        frame = Tkinter.Frame(form)

        labels = Tkinter.Frame(frame)
        Tkinter.Label(labels, text="Address:").pack(side=Tkinter.TOP, pady=4)
        Tkinter.Label(labels, text="Netmask:").pack(side=Tkinter.TOP, pady=4)
        Tkinter.Label(labels, text="Gateway:").pack(side=Tkinter.TOP, pady=4)
        Tkinter.Label(labels, text="MAC Addr:").pack(side=Tkinter.TOP, pady=4)
        labels.pack(side=Tkinter.LEFT)

        eth0 = ifconfig.findif("eth0")

        entris = Tkinter.Frame(frame)
        self.address = Tkinter.Label(entris, text=info["address"])
        self.address.pack(side=Tkinter.TOP, pady=4)
        self.netmask = Tkinter.Label(entris, text=info["netmask"])
        self.netmask.pack(side=Tkinter.TOP, pady=4)
        self.gateway = Tkinter.Label(entris, text=info["gateway"])
        self.gateway.pack(side=Tkinter.TOP, pady=4)
        self.macaddr = Tkinter.Label(entris, text=info["macaddr"])
        self.macaddr.pack(side=Tkinter.TOP, pady=4)
        entris.pack(side=Tkinter.LEFT)

        frame.pack(side=Tkinter.TOP)

        frame = Tkinter.Frame(form)
        button = Tkinter.Button(frame, text="Exit", command=on_exit)
        button.pack(side=Tkinter.RIGHT)
        button = Tkinter.Button(frame, text="Edit", command=on_edit)
        button.pack(side=Tkinter.RIGHT)
        frame.pack(side=Tkinter.TOP, anchor="e", pady=4)

        form.pack(padx=10, pady=4)

    def ping(self, ip):
        pingTest = "ping -c 1 " + ip
        process = subprocess.Popen(pingTest, shell=True, stdout=subprocess.PIPE)
        process.wait()
        returnCodeTotal = process.returncode
        print "ping result:", returnCodeTotal

    def destroy(self):
        self.win.destroy()


class App:
    def __init__(self, master):
        self.master = master
        self.master.withdraw()
        self.show_status_dialog()

    def get_network_info(self):
        info = {}
        eth0 = ifconfig.findif("eth0")
        info["address"] = eth0.get_ip()
        info["netmask"] = eth0.get_netmask_str()
        info["gateway"] = route.get_default_gw()
        info["macaddr"] = eth0.get_mac()
        return info

    def show_status_dialog(self):
        info = self.get_network_info()
        self.status_dialog = NetworkStatusDialog(info, self.on_edit_setup,
            self.on_exit, self.on_exit)

    def show_setup_dialog(self):
        info = self.get_network_info()
        self.setup_dialog = NetworkSetupDialog(info, self.on_save_setup,
            self.on_cancel_setup, self.on_cancel_setup)        

    def on_edit_setup(self):
        self.status_dialog.destroy()
        self.show_setup_dialog()

    def on_exit(self):
        self.quit()

    def on_save_setup(self):
        dialog = self.setup_dialog
        address = dialog.address.get()
        netmask = dialog.netmask.get()
        gateway = dialog.gateway.get()
        self.setup_dialog.destroy()

        print "Save %s, %s, %s" % (address, netmask, gateway)
        self.save_fixed_ip_config("/etc/network/interfaces", address, netmask, gateway)
        self.restart_network()
        self.show_status_dialog()

    def save_fixed_ip_config(self, pathname, address, netmask, gateway):
        try:
            # This will create a new file or **overwrite an existing file**.
            f = open(pathname, "w")
            try:
                f.write("auto lo\n")
                f.write("iface lo inet loopback\n")
                f.write("\n")
                f.write("auto eth0\n")
                f.write("iface eth0 inet static\n")
                f.write("address %s\n" % address)
                f.write("netmask %s\n" % netmask)
                f.write("gateway %s\n" % gateway)
            finally:
                f.close()
        except IOError:
            pass

    def restart_network(self):
        cmd = "sudo /etc/init.d/networking restart"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        process.wait()
        ret = process.returncode
        print "restart networking result:", ret

    def on_cancel_setup(self):
        self.setup_dialog.destroy()
        self.show_status_dialog()

    def quit(self):
        self.master.quit()


if __name__ == "__main__":
    root = Tkinter.Tk()
    app = App(root)
    Tkinter.mainloop()

