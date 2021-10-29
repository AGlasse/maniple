#!/usr/bin/python
import os
from os import listdir
import win32api
from astropy.io import fits
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tooltip import Tooltip
from icon import Icon
from panel import Panel
from globals import Globals
import sys


class IoPanel(Panel):

    file_labels = []
    name_vars = []
    path_separator = None
    display_buffer = "A"

    def __init__(self, parent):
        Panel.__init__(self, parent)
        platform_name = sys.platform
        IoPanel.path_separator = '/'
        if platform_name == 'win32':
            IoPanel.path_separator = '\\'
            drives = win32api.GetLogicalDriveStrings()
            IoPanel.drives = drives.split('\000')[:-1]
            print(drives)
        run_dir = os.getcwd()
        self.path_file = run_dir + IoPanel.path_separator + 'pathfile.txt'
        font = self.LARGE_FONT
        self.pad = self.BUTTON_PAD
        self._make_load_widget(0, font, row=1)
        self._make_load_widget(1, font, row=2)
        tt = 'Save buffer A to fits file'
        lcom = lambda: self._launch_fits_dialogue('save')
        self.make_button(icon_name='io_saveFits', lcom=lcom, tt=tt, row=1, column=3)
        return

    def _display_buffer(self, buff_name):
        Globals.set_display_buffer(buff_name)

        self.display_buffer = buff_name
        print('Display buffer ' + buff_name)
        return

    def _make_load_widget(self, buffer_index, font, **kwargs):
        idxs = ['A', 'B']
        idx = idxs[buffer_index]
        row = kwargs.get('row', 1)
        icon_name = 'io_load' + idx
        icon = Icon(icon_name, height=self.ICON_HEIGHT)
        button = ttk.Button(self, image=icon.image,
                            command=lambda:
                            self._launch_fits_dialogue('load', buffer_id=idx))
        button.image = icon.image       # Keep image reference
        Tooltip(button, text='Load fits cube into buffer ' + idx,
                wraplength=200)
        button.grid(row=row, column=0, sticky=W,
                    padx=self.pad, pady=self.pad)
        name_var = StringVar()
        name_var.set('File ' + idx)
        file_label = ttk.Label(self, textvariable=name_var, font=font,
                               width=100)
        self.name_vars.append(name_var)
        file_label.grid(row=row, column=1, sticky=W,
                        padx=self.pad, pady=self.pad)
        self.file_labels.append(file_label)
        return

    def _launch_fits_dialogue(self, func, **kwargs):
        buffer_id = kwargs.get('buffer_id', 0)
        fits_dialogue = FitsDialogue(self, func, buffer_id)
        return

class FitsDialogue(Toplevel):
    """ Dialogue which extends 'Toplevel' to select a fits file, display its
        structure and allow the selection of which extensions and images to
        load or save. Set dir to 'load' or 'save'.
    """
    def __init__(self, parent, func, buffer_id):
        self.parent = parent
        Toplevel.__init__(self, parent)
        font = parent.LARGE_FONT
        func_select = 'Load ' if func == 'load' else 'Save '
        title = func_select + ' fits image(s)'
        self.title(title)
        self.buffer_id = buffer_id
        self.transient(parent)
        self.parent = parent
        self.navbox_var = StringVar()
        self.navbox_label = ttk.Label(self, textvariable=self.navbox_var)
        self.navbox_label.grid(row=0, column=0, columnspan=3)
        self.navbox = tk.Listbox(self, font=font, width=50)
        self.navbox.grid(row=1, column=0, columnspan=3)
        self.navbox.bind("<Double-Button-1>", self.changedir)
        text = 'Double click on folder to navigate '
        Tooltip(self.navbox, text=text, wraplength=200)
        filebox_label = ttk.Label(self, text='FITS file')
        filebox_label.grid(row=2, column=0, columnspan=3)
        self.filebox = tk.Listbox(self, font=font, width=50)    # Display files
        self.filebox.grid(row=3, column=0, columnspan=3)
        text = 'Click on file to show data units'
        Tooltip(self.filebox, text=text, wraplength=200)
        load_path, save_path = self._load_persistent_paths()

        # If loading, prevent file overwriting and display HDU parameters
        if func == 'load':
            try:
                os.chdir(load_path)
            except Exception:
                os.chdir('..')
            self.filebox.bind("<Button-1>", self.inspect)
        if func == 'save':                          # Include file name entry
            os.chdir(save_path)
            self.fits_name = StringVar()
            self.fits_name.set('newfile.fits')
            fits_name_entry = ttk.Entry(self, textvariable=self.fits_name,
                                        width=10, justify=RIGHT, font=font)
            fits_name_entry.grid(row=4, column=1)
            fits_name_entry.bind("<Double-Button-1>", self.ok_save)
        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
        body.grid(row=5, column=0, padx=5, pady=5)
        self.buttonbox(func)
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))
        self.initial_focus.focus_set()
        self.refresh()
        return

    def _load_persistent_paths(self):
        try:
            f = open(self.parent.path_file, "r")
            paths = f.read().split('\n')
            load_path = paths[0]
            save_path = paths[1]
            return load_path, save_path
        except IOError:
            self._save_persistent_paths(load_path='..', save_path='..')
        return

    def _save_persistent_paths(self, **kwargs):
        load_path, save_path = self._load_persistent_paths()
        lp = kwargs.get('load_path', load_path)
        sp = kwargs.get('save_path', save_path)
        path_record = lp + '\n' + sp
        f = open(self.parent.path_file, "w")
        f.write(path_record)
        return

    def refresh(self):
        self.navbox.delete(0, END)
        ps = IoPanel.path_separator
        cwd = os.getcwd()
        sub_folders = [d.path for d in os.scandir(cwd) if d.is_dir()]
        self.navbox.insert(tk.END, '..')
        for sub_folder in sub_folders:
            tokens = sub_folder.split(ps)
            folder = tokens[len(tokens)-1]  # + ps
            self.navbox.insert(tk.END, folder)
        text = ''
        nchars = len(cwd)
        p2 = 0
        more_text = True
        while more_text:
            p1 = p2
            p2 = nchars if nchars - p1 < 40 else p1 + 40
            text += cwd[p1: p2]
            text += '\n'
            more_text = p2 < nchars

        self.navbox_var.set('Folder - ' + text)
        for drive in IoPanel.drives:
            self.navbox.insert(tk.END, drive)
        self.filebox.delete(0, END)
        file_list = [f for f in listdir(cwd) if f.endswith('.fits')]
        for f in file_list:
            self.filebox.insert(tk.END, f)
        return

    def _print_header(self, hdu):
        header = hdu.header
        for card in header.cards:
            print(card)
        self.destroy()
        return

    def inspect(self, event):
        file = self.filebox.get(tk.ACTIVE)
        cwd = os.getcwd()
        ps = IoPanel.path_separator
        path = cwd + ps + file
        hdu_list = fits.open(path, mode='readonly')
        hdu_panel = HDUPanel(self, hdu_list)
        hdu_panel.grid(row=1, column=4)
        self.refresh()
        return

    def changedir(self, event):
        """ Change working directory.
        """
        cwd = os.getcwd()
        ps = IoPanel.path_separator
        folder = self.navbox.get(tk.ACTIVE)
        wd = folder
        if folder == '..':
            idx = cwd.rfind(ps)
            wd = cwd[0:idx]
        print(wd)
        os.chdir(wd)
        self.refresh()

    def body(self, master):
        """ Create dialog body.  return widget that should have initial focus.
            This method should be overridden
        """
        pass

    def buttonbox(self, func):
        """ Add standard button box.
        """
        box = ttk.Frame(self)
        row = 0
        if func == 'save':
            w = ttk.Button(box, text="OK", width=10, command=self.ok_save)
            self.bind("<Return>", self.ok_save)
            w.grid(row=row, column=0, padx=5, pady=5)
            row = row + 1
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.grid(row=row, column=0, padx=5, pady=5)
        self.bind("<Escape>", self.cancel)
        box.grid()
        return

    def ok_save(self):
        file = self.fits_name.get()
        print(file)
        cwd = os.getcwd()
        self._save_persistent_paths(save_path=cwd)
        path = cwd + '/' + file
        hdu = self.parent.maniple.buffers['A'].get()
        fits.writeto(path, hdu, header=None, overwrite=True)
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return
        self.destroy()

    def load_hdu(self, hdu_name):
        import numpy as np
        from globals import Globals

        file = self.filebox.get(tk.ACTIVE)
        cwd = os.getcwd()
        self._save_persistent_paths(load_path=cwd)
        path = cwd + '/' + file
        image_name = path.split('/')[-1] + ", " + hdu_name
        if self.buffer_id == 'A':
            self.parent.name_vars[0].set(image_name)
        else:
            self.parent.name_vars[1].set(image_name)

        hdu_list = fits.open(path, mode='readonly')
        for hdu in hdu_list:
            if hdu_name == hdu.name:
                datacube = hdu.data
                shape = datacube.shape
                ndim = len(shape)
                for dim in range(ndim, 4):        # eg single frame y, x, -> int,frame,y,x
                    datacube = np.expand_dims(datacube, axis=0)
                print("Writing {:s} to buffer {:s}".format(file, self.buffer_id))
                Globals.load_buffer(self.buffer_id, datacube)
                base = self.parent.get_base()
                base.reset()
                base.refresh()
                self.destroy()
                return
        return

    def cancel(self):       # , event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    @staticmethod
    def validate():
        return 1  # override

    def apply(self):
        pass  # override


class HDUPanel(Panel):

    def __init__(self, parent, hdu_list):
        Panel.__init__(self, parent)
        row = 1
        for hdu in hdu_list:
            hdu_label = ttk.Label(self, text=hdu.name)
            hdu_label.grid(row=row, column=4, padx=5, pady=5)
            header_button = ttk.Button(self, text="Header", width=10,
                                       command=lambda hdu_=hdu: parent._print_header(hdu_))
            header_button.grid(row=row, column=5, padx=5, pady=5)
            if hdu.data is not None:
                datacube = hdu.data
                shape = datacube.shape
                size_text = ""
                for s in shape:
                    size_text = size_text + "{:5d} x".format(s)
                size_label = ttk.Label(self, text=size_text[:-2])
                size_label.grid(row=row, column=6, padx=5, pady=5)
                image_button = ttk.Button(self, text="Load Image", width=10)
                hdu_name = hdu.name
                image_button.bind("<ButtonRelease>", lambda event, hdu_name_=hdu_name: parent.load_hdu(hdu_name_))
                image_button.grid(row=row, column=7, padx=5, pady=5)
            row = row + 1
        return
