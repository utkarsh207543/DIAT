import os
import numpy as np
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter import messagebox

from GUI import CustomButton
from GUI import Input
from GUI import LabelTag
from GUI import RandomExcursionTestItem
from GUI import TestItem
from Tools import Tools

from ApproximateEntropy import ApproximateEntropy as aet
from Complexity import ComplexityTest as ct
from CumulativeSum import CumulativeSums as cst
from FrequencyTest import FrequencyTest as ft
from Matrix import Matrix as mt
from RandomExcursions import RandomExcursions as ret
from RunTest import RunTest as rt
from Serial import Serial as serial
from Spectral import SpectralTest as st
from TemplateMatching import TemplateMatching as tm
from Universal import Universal as ut

class Main(tb.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('NIST 800-200 DRDO DIAT v1.0')
        self.master.geometry("1300x650")
        self.master.resizable(0, 0)
        self.pack(fill=BOTH, expand=True)

        self._test_type = [
            '01. Frequency (Monobit) Test',
            '02. Frequency Test within a Block',
            '03. Runs Test',
            '04. Test for the Longest Run of Ones in a Block',
            '05. Binary Matrix Rank Test',
            '06. Discrete Fourier Transform (Spectral) Test',
            '07. Non-overlapping Template Matching Test',
            '08. Overlapping Template Matching Test',
            '09. Maurer\'s "Universal Statistical" Test',
            '10. Linear Complexity Test',
            '11. Serial Test',
            '12. Approximate Entropy Test',
            '13. Cumulative Sums Test (Forward)',
            '14. Cumulative Sums Test (Backward)',
            '15. Random Excursions Test',
            '16. Random Excursions Variant Test'
        ]

        self._test_function = {
            0: ft.monobit_test,
            1: ft.block_frequency,
            2: rt.run_test,
            3: rt.longest_one_block_test,
            4: mt.binary_matrix_rank_text,
            5: st.spectral_test,
            6: tm.non_overlapping_test,
            7: tm.overlapping_patterns,
            8: ut.statistical_test,
            9: ct.linear_complexity_test,
            10: serial.serial_test,
            11: aet.approximate_entropy_test,
            12: cst.cumulative_sums_test,
            13: cst.cumulative_sums_test,
            14: ret.random_excursions_test,
            15: ret.variant_test
        }

        self._test_result = []
        self._test_string = []

        self.init_window()

    def init_window(self):
        title_label = tb.Label(self.master, text='NIST 800-200 DRDO DIAT v1.0', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=10)

        input_label_frame = tb.LabelFrame(self.master, text="Input Data", bootstyle="primary")
        input_label_frame.place(x=20, y=50, width=1260, height=125)

        self.__binary_input = Input(input_label_frame, 'Binary Data', 10, 5)
        self.__binary_data_file_input = Input(input_label_frame, 'Binary Data File', 10, 35, True,
                                              self.select_binary_file, button_xcoor=1060, button_width=160)
        self.__string_data_file_input = Input(input_label_frame, 'String Data File', 10, 65, True,
                                              self.select_data_file, button_xcoor=1060, button_width=160)

        # Buttons
        tb.Button(self.master, text='Select All Test', bootstyle='success', command=self.select_all).place(x=20, y=600, width=120)
        tb.Button(self.master, text='De-Select All Test', bootstyle='warning', command=self.deselect_all).place(x=150, y=600, width=150)
        tb.Button(self.master, text='Execute Test', bootstyle='primary', command=self.execute).place(x=310, y=600, width=120)
        tb.Button(self.master, text='Save as Text File', bootstyle='info', command=self.save_result_to_file).place(x=440, y=600, width=150)
        tb.Button(self.master, text='Reset', bootstyle='secondary', command=self.reset).place(x=600, y=600, width=100)
        tb.Button(self.master, text='Exit Program', bootstyle='danger', command=self.exit).place(x=710, y=600, width=120)

    def select_binary_file(self):
        self.__file_name = askopenfilename(initialdir=os.getcwd(), title="Select Binary Input File.")
        if self.__file_name:
            self.__binary_input.set_data('')
            self.__binary_data_file_input.set_data(self.__file_name)
            self.__string_data_file_input.set_data('')
            self.__is_binary_file = True
            self.__is_data_file = False

    def select_data_file(self):
        self.__file_name = askopenfilename(initialdir=os.getcwd(), title="Select Data File.")
        if self.__file_name:
            self.__binary_input.set_data('')
            self.__binary_data_file_input.set_data('')
            self.__string_data_file_input.set_data(self.__file_name)
            self.__is_binary_file = False
            self.__is_data_file = True

    def select_all(self):
        print('Select All Test')
        for item in self._test:
            item.set_check_box_value(1)

    def deselect_all(self):
        print('Deselect All Test')
        for item in self._test:
            item.set_check_box_value(0)

    def execute(self):
        if len(self.__binary_input.get_data().strip()) == 0 and\
           len(self.__binary_data_file_input.get_data().strip()) == 0 and\
           len(self.__string_data_file_input.get_data().strip()) == 0:
            messagebox.showwarning("Warning", 'You must input the binary data or select a file.')
            return

        input_data = []

        if len(self.__binary_input.get_data().strip()) > 0:
            input_data.append(self.__binary_input.get_data().strip())
        elif len(self.__binary_data_file_input.get_data().strip()) > 0:
            with open(self.__file_name, 'r') as handle:
                input_data.append(''.join([line.strip() for line in handle])[:1000000])
        elif len(self.__string_data_file_input.get_data().strip()) > 0:
            with open(self.__file_name, 'r') as handle:
                data = [Tools.string_to_binary(line.strip()) for line in handle]
                input_data.append(''.join(data))

        try:
            for test_data in input_data:
                results = []
                for i in range(16):
                    if i == 13:
                        res = self._test_function[i](test_data, mode=1)
                    else:
                        res = self._test_function[i](test_data)
                    results.append(res)
                self._test_result.append(results)
                messagebox.showinfo("Success", "All tests executed successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_result_to_file(self):
        if not self._test_result:
            messagebox.showinfo("Info", "No result to save.")
            return

        output_file = asksaveasfile(mode='w', defaultextension=".txt")
        if output_file:
            for result in self._test_result[0]:
                output_file.write(str(result) + '\n')
            output_file.close()
            messagebox.showinfo("Saved", "Results saved successfully.")

    def reset(self):
        self.__binary_input.set_data('')
        self.__binary_data_file_input.set_data('')
        self.__string_data_file_input.set_data('')
        self._test_result = []

    def exit(self):
        self.master.destroy()

if __name__ == '__main__':
    np.seterr('raise')
    root = tb.Window(themename="flatly")
    app = Main(master=root)
    root.mainloop()