#!/usr/bin/python
from panel import Panel
from globals import Globals
import numpy as np


class MathsPanel(Panel):


    icons = ['maths_aplusb', 'maths_aminusb', 'maths_amultb', 'maths_adivb',
             'maths_aplusc', 'maths_aminusc', 'maths_amultc', 'maths_adivc',
             'maths_norm', 'maths_log', 'maths_collapse']
    tts = ['A + B', 'A - B', 'A x B', 'A / B',
           'A + c', 'A - c', 'A x c', 'A / c',
           'Normalise frame', 'Log10', 'Z average']
    norm_idx = len(tts) - 2
    log_idx = len(tts) - 2

    def __init__(self, maniple):
        Panel.__init__(self, maniple)
        self.maniple = maniple
        rows = [1, 1, 2, 2, 1, 1, 2, 2, 1, 2, 1]
        cols = [0, 1, 0, 1, 3, 4, 3, 4, 6, 6, 7]
        n_ops = len(self.icons)
        for i in range(0, n_ops):
            tooltip = self.tts[i]
            button = self.make_button(icon_name=self.icons[i], tt=tooltip,
                                      row=rows[i], column=cols[i])
            button.config(command=lambda ilam=i: self._oper(ilam))
        self.con_entry = self.make_entry(val=0.0, fmt='{:5.1f}',
                                         tt='Enter constant')
        self.con_entry.grid(row=1, column=5, rowspan=2)
        self.columnconfigure(1, minsize=100)
        return

    def _oper(self, op_idx):
        """ Implement maths operations A oper B -> A
        """
        print(op_idx)
        a = Globals.buffers['A'].get()
        z = a
        b = Globals.buffers['B'].get()
        c = int(float(self.con_entry.get()))
        max_bin_idx = 3
        idx = op_idx
        is_norm = op_idx is self.norm_idx
        is_log = op_idx is self.log_idx

        if is_norm or is_log:
            if is_norm:
                self._norm()
            if is_log:
                self._log()
        else:
            if op_idx > max_bin_idx:        # Trap unary operations
                idx = op_idx - 4
                b = c
            if op_idx == 10:
                z = np.average(a, axis=1, keepdims=True)
            if idx == 0:
                z = np.add(a, b)
            if idx == 1:
                z = np.subtract(a, b)
            if idx == 2:
                z = np.multiply(a, b)
            if idx == 3:            # Set divide by zero values to Nan
                if op_idx == 7:     # Divide by constant
                    idx_zero = b == 0
                    b[idx_zero] = 1.0
                    z = np.divide(a, b)
                    z[idx_zero] = np.NaN
                else:
                    z = np.divide(a, b)
            try:
                Globals.buffers['A'].set(z)
            except ValueError:
                print('mathsPanel._oper - Undefined function called !!')
        base = self.get_base()
        base.refresh()
        return

    def _norm(self):
        """ Normalise buffer by scaling the currently selected limits to run
        from 0 to 1.
        :return:
        """
        block = Globals.buffers['A'].block
        vmin, vmax = self.maniple.get_vlimits()
        vrange = vmax - vmin
        b = np.subtract(block, vmin)
        b = np.divide(b, vrange)
        Globals.buffers['A'].block = b
        # Globals.buffers['A'].set(b)
        base = self.get_base()
        base.refresh()
        return

    def _log(self):

        block = Globals.buffers['A'].block
        b = np.log10(block)
        Globals.buffers['A'].block = b
        base = self.get_base()
        base.refresh()
        return