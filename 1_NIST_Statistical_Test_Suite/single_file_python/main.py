#module: Main.py

import os
import numpy as np
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile
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

class Main(Frame):

    def __init__(self, master=None):

        Frame.__init__(self, master=master)
        self._master = master
        self.init_variables()
        self.init_window()

    def init_variables(self):

        self._test_type = ['01. Frequency (Monobit) Test',
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
                            '16. Random Excursions Variant Test']


        self.__test_function = {
            0:ft.monobit_test,
            1:ft.block_frequency,
            2:rt.run_test,
            3:rt.longest_one_block_test,
            4:mt.binary_matrix_rank_text,
            5:st.spectral_test,
            6:tm.non_overlapping_test,
            7:tm.overlapping_patterns,
            8:ut.statistical_test,
            9:ct.linear_complexity_test,
            10:serial.serial_test,
            11:aet.approximate_entropy_test,
            12:cst.cumulative_sums_test,
            13:cst.cumulative_sums_test,
            14:ret.random_excursions_test,
            15:ret.variant_test
        }

        self._test_result = []
        self._test_string = []

    def init_window(self):
        frame_title = 'NIST 800-200 DRDO DIAT v1.0'
        title_label = LabelTag(self.master, frame_title, 0, 5, 1260)
        # Setup LabelFrame for Input
        input_label_frame = LabelFrame(self.master, text="Input Data")
        input_label_frame.config(font=("Calibri", 14))
        input_label_frame.propagate(0)
        input_label_frame.place(x=20, y=30, width=1260, height=125)
        self.__binary_input = Input(input_label_frame, 'Binary Data', 10, 5)
        self.__binary_data_file_input = Input(input_label_frame, 'Binary Data File', 10, 35, True,
                                              self.select_binary_file, button_xcoor=1060, button_width=160)
        self.__string_data_file_input = Input(input_label_frame, 'String Data File', 10, 65, True,
                                              self.select_data_file, button_xcoor=1060, button_width=160)

        # Setup LabelFrame for Randomness Test
        self._stest_selection_label_frame = LabelFrame(self.master, text="Randomness Testing", padx=5, pady=5)
        self._stest_selection_label_frame.config(font=("Calibri", 14))
        self._stest_selection_label_frame.place(x=20, y=155, width=1260, height=450)

        test_type_label_01 = LabelTag(self._stest_selection_label_frame, 'Test Type', 10, 5, 250, 11, border=2,
                                   relief="groove")
        p_value_label_01 = LabelTag(self._stest_selection_label_frame, 'P-Value', 265, 5, 235, 11, border=2,
                                 relief="groove")
        result_label_01 = LabelTag(self._stest_selection_label_frame, 'Result', 505, 5, 110, 11, border=2,
                                relief="groove")

        test_type_label_02 = LabelTag(self._stest_selection_label_frame, 'Test Type', 620, 5, 250, 11, border=2,
                                      relief="groove")
        p_value_label_02 = LabelTag(self._stest_selection_label_frame, 'P-Value', 875, 5, 235, 11, border=2,
                                    relief="groove")
        result_label_02 = LabelTag(self._stest_selection_label_frame, 'Result', 1115, 5, 110, 11, border=2,
                                   relief="groove")

        self._test = []

        self._monobit = TestItem(self._stest_selection_label_frame, self._test_type[0], 10, 35, p_value_x_coor=265, p_value_width=235, result_x_coor=505, result_width=110, font_size=11)
        self._test.append(self._monobit)

        self._block = TestItem(self._stest_selection_label_frame, self._test_type[1], 620, 35, p_value_x_coor=875, p_value_width=235, result_x_coor=1115, result_width=110, font_size=11)
        self._test.append(self._block)

        self._run = TestItem(self._stest_selection_label_frame, self._test_type[2], 10, 60, p_value_x_coor=265, p_value_width=235, result_x_coor=505, result_width=110, font_size=11)
        self._test.append(self._run)

        self._long_run = TestItem(self._stest_selection_label_frame, self._test_type[3], 620, 60, p_value_x_coor=875, p_value_width=235, result_x_coor=1115, result_width=110, font_size=11)
        self._test.append(self._long_run)

        self._rank = TestItem(self._stest_selection_label_frame, self._test_type[4], 10, 85, p_value_x_coor=265, p_value_width=235, result_x_coor=505, result_width=110, font_size=11)
        self._test.append(self._rank)

        self._spectral = TestItem(self._stest_selection_label_frame, self._test_type[5], 620, 85, p_value_x_coor=875, p_value_width=235, result_x_coor=1115, result_width=110, font_size=11)
        self._test.append(self._spectral)

        self._non_overlappong = TestItem(self._stest_selection_label_frame, self._test_type[6], 10, 110, p_value_x_coor=265, p_value_width=235, result_x_coor=505, result_width=110, font_size=11)
        self._test.append(self._non_overlappong)

        self._overlapping = TestItem(self._stest_selection_label_frame, self._test_type[7], 620, 110, p_value_x_coor=875, p_value_width=235, result_x_coor=1115, result_width=110, font_size=11)
        self._test.append(self._overlapping)

        self._universal = TestItem(self._stest_selection_label_frame, self._test_type[8], 10, 135, p_value_x_coor=265, p_value_width=235, result_x_coor=505, result_width=110, font_size=11)
        self._test.append(self._universal)

        self._linear = TestItem(self._stest_selection_label_frame, self._test_type[9], 620, 135, p_value_x_coor=875, p_value_width=235, result_x_coor=1115, result_width=110, font_size=11)
        self._test.append(self._linear)

        self._serial = TestItem(self._stest_selection_label_frame, self._test_type[10], 10, 160, serial=True, p_value_x_coor=265, p_value_width=235, result_x_coor=505, result_width=110, font_size=11, two_columns=True)
        self._test.append(self._serial)

        self._entropy = TestItem(self._stest_selection_label_frame, self._test_type[11], 10, 185, p_value_x_coor=265, p_value_width=235, result_x_coor=505, result_width=110, font_size=11)
        self._test.append(self._entropy)

        self._cusum_f = TestItem(self._stest_selection_label_frame, self._test_type[12], 10, 210, p_value_x_coor=265, p_value_width=235, result_x_coor=505, result_width=110, font_size=11)
        self._test.append(self._cusum_f)

        self._cusum_r = TestItem(self._stest_selection_label_frame, self._test_type[13], 620, 210, p_value_x_coor=875, p_value_width=235, result_x_coor=1115, result_width=110, font_size=11)
        self._test.append(self._cusum_r)

        self._excursion = RandomExcursionTestItem(self._stest_selection_label_frame, self._test_type[14], 10, 235,
                                                   ['-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4'], font_size=11)
        self._test.append(self._excursion)

        self._variant = RandomExcursionTestItem(self._stest_selection_label_frame, self._test_type[15], 10, 325,
                                                 ['-9.0', '-8.0', '-7.0', '-6.0', '-5.0', '-4.0', '-3.0', '-2.0',
                                                  '-1.0',
                                                  '+1.0', '+2.0', '+3.0', '+4.0', '+5.0', '+6.0', '+7.0', '+8.0',
                                                  '+9.0'], variant=True, font_size=11)
        self._test.append(self._variant)

        self._result_field = [
            self._monobit,
            self._block,
            self._run,
            self._long_run,
            self._rank,
            self._spectral,
            self._non_overlappong,
            self._overlapping,
            self._universal,
            self._linear,
            self._serial,
            self._entropy,
            self._cusum_f,
            self._cusum_r
        ]

        select_all_button = CustomButton(self.master, 'Select All Test', 20, 615, 100, self.select_all)
        deselect_all_button = CustomButton(self.master, 'De-Select All Test', 125, 615, 150, self.deselect_all)
        execute_button = CustomButton(self.master, 'Execute Test', 280, 615, 100, self.execute)
        save_button = CustomButton(self.master, 'Save as Text File', 385, 615, 100, self.save_result_to_file)
        reset_button = CustomButton(self.master, 'Reset', 490, 615, 100, self.reset)
        exit = CustomButton(self.master, 'Exit Program', 595, 615, 100, self.exit)

    def select_binary_file(self):
        """
        Called tkinter.askopenfilename to give user an interface to select the binary input file and perform the following:
        1.  Clear Binary Data Input Field. (The textfield)
        2.  Set selected file name to Binary Data File Input Field.
        3.  Clear String Data file input field.

        :return: None
        """
        print('Select Binary File')
        self.__file_name = askopenfilename(initialdir=os.getcwd(), title="Select Binary Input File.")
        if self.__file_name:
            self.__binary_input.set_data('')
            self.__binary_data_file_input.set_data(self.__file_name)
            self.__string_data_file_input.set_data('')
            self.__is_binary_file = True
            self.__is_data_file = False

    def select_data_file(self):
        """
        Called tkinter.askopenfilename to give user an interface to select the string input file and perform the following:
        1.  Clear Binary Data Input Field. (The textfield)
        2.  Clear Binary Data File Input Field.
        3.  Set selected file name to String Data File Input Field.

        :return: None
        """
        print('Select Data File')
        self.__file_name = askopenfilename(initialdir=os.getcwd(), title="Select Data File.")
        if self.__file_name:
            self.__binary_input.set_data('')
            self.__binary_data_file_input.set_data('')
            self.__string_data_file_input.set_data(self.__file_name)
            self.__is_binary_file = False
            self.__is_data_file = True



    def select_all(self):
        """
        Select all test type displayed in the GUI. (Check all checkbox)

        :return: None
        """
        print('Select All Test')
        for item in self._test:
            item.set_check_box_value(1)

    def deselect_all(self):
        """
        Unchecked all checkbox

        :return: None
        """
        print('Deselect All Test')
        for item in self._test:
            item.set_check_box_value(0)

    def execute(self):
        """
        Execute the tests and display the result in the GUI

        :return: None
        """
        print('Execute')

        if len(self.__binary_input.get_data().strip().rstrip()) == 0 and\
                len(self.__binary_data_file_input.get_data().strip().rstrip()) == 0 and\
                len(self.__string_data_file_input.get_data().strip().rstrip()) == 0:
            messagebox.showwarning("Warning",
                                   'You must input the binary data or read the data from from the file.')
            return None
        elif len(self.__binary_input.get_data().strip().rstrip()) > 0 and\
                len(self.__binary_data_file_input.get_data().strip().rstrip()) > 0 and\
                len(self.__string_data_file_input.get_data().strip().rstrip()) > 0:
            messagebox.showwarning("Warning",
                                   'You can either input the binary data or read the data from from the file.')
            return None

        input = []

        if not len(self.__binary_input.get_data()) == 0:
            input.append(self.__binary_input.get_data())
        elif not len(self.__binary_data_file_input.get_data()) == 0:
            temp = []
            if self.__file_name:
                handle = open(self.__file_name)
            for data in handle:
                temp.append(data.strip().rstrip())
            test_data = ''.join(temp)
            input.append(test_data[:1000000])
        elif not len(self.__string_data_file_input.get_data()) == 0:
            data = []
            count = 1
            if self.__file_name:
                handle = open(self.__file_name)
            for item in handle:
                if item.startswith('http://'):
                    url = Tools.url_to_binary(item)
                    data.append(Tools.string_to_binary(url))
                else:
                    data.append(Tools.string_to_binary(item))
                count += 1
            print(data)
            input.append(''.join(data))

            #print(data)
            #self.__test_data = Options(self.__stest_selection_label_frame, 'Input Data', data, 10, 5, 900)

        try:
            for test_data in input:
                count = 0
                results = [(), (), (), (), (), (), (), (), (), (), (), (), (), (), (), ()]
                for item in self._test:
                    if item.get_check_box_value() == 1:
                        print(self._test_type[count], 'selected.', self.__test_function[count](test_data))
                        if count == 13:
                            results[count] = self.__test_function[count](test_data, mode=1)
                        else:
                            results[count] = self.__test_function[count](test_data)
                    count += 1
                self._test_result.insert(0, results)

            self.write_results(self._test_result[0])
            messagebox.showinfo("Execute", "Test Complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            print(e)

    def write_results(self, results):
        """
        Write the result in the GUI

        :param results: result of the randomness test
        :return: None
        """
        count = 0
        for result in results:
            if len(result) == 0:
                if count == 10:
                    self._result_field[count].set_p_value('')
                    self._result_field[count].set_result_value('')
                    self._result_field[count].set_p_value_02('')
                    self._result_field[count].set_result_value_02('')
                elif count == 14:
                    self._excursion.set_results('')
                elif count == 15:
                    self._variant.set_results('')
                else:
                    self._result_field[count].set_p_value('')
                    self._result_field[count].set_result_value('')
            else:
                if count == 10:
                    self._result_field[count].set_p_value(result[0][0])
                    self._result_field[count].set_result_value(self.get_result_string(result[0][1]))
                    self._result_field[count].set_p_value_02(result[1][0])
                    self._result_field[count].set_result_value_02(self.get_result_string(result[1][1]))
                elif count == 14:
                    print(result)
                    self._excursion.set_results(result)
                elif count == 15:
                    print(result)
                    self._variant.set_results(result)
                else:
                    self._result_field[count].set_p_value(result[0])
                    self._result_field[count].set_result_value(self.get_result_string(result[1]))


            count += 1

    def save_result_to_file(self):
        print('Save to File')
        print(self._test_result)
        if not len(self.__binary_input.get_data()) == 0:
            output_file = asksaveasfile(mode='w', defaultextension=".txt")
            output_file.write('Test Data:' + self.__binary_input.get_data() + '\n\n\n')
            result = self._test_result[0]
            output_file.write('%-50s\t%-20s\t%-10s\n' % ('Type of Test', 'P-Value', 'Conclusion'))
            self.write_result_to_file(output_file, result)
            output_file.close()
            messagebox.showinfo("Save",  "File save finished.  You can check the output file for complete result.")
        elif not len(self.__binary_data_file_input.get_data()) == 0:
            output_file = asksaveasfile(mode='w', defaultextension=".txt")
            output_file.write('Test Data File:' + self.__binary_data_file_input.get_data() + '\n\n\n')
            result = self._test_result[0]
            output_file.write('%-50s\t%-20s\t%-10s\n' % ('Type of Test', 'P-Value', 'Conclusion'))
            self.write_result_to_file(output_file, result)
            output_file.close()
            messagebox.showinfo("Save",  "File save finished.  You can check the output file for complete result.")
        elif not len(self.__string_data_file_input.get_data()) == 0:
            output_file = asksaveasfile(mode='w', defaultextension=".txt")
            output_file.write('Test Data File:' + self.__string_data_file_input.get_data() + '\n\n')
            #count = 0
            #for item in self.__test_string:
            #    output_file.write('Test ' + str(count+1) + ':\n')
            #    output_file.write('String to be tested: %s' % item)
            #    output_file.write('Binary of the given String: %s\n\n' % Tools.string_to_binary(item))
            #    output_file.write('Result:\n')
            #    output_file.write('%-50s\t%-20s\t%-10s\n' % ('Type of Test', 'P-Value', 'Conclusion'))
            #    self.write_result_to_file(output_file, self._test_result[count])
            #    output_file.write('\n\n')
            #    count += 1
            result = self._test_result[0]
            output_file.write('%-50s\t%-20s\t%-10s\n' % ('Type of Test', 'P-Value', 'Conclusion'))
            self.write_result_to_file(output_file, result)
            output_file.close()
            messagebox.showinfo("Save",  "File save finished.  You can check the output file for complete result.")

    def write_result_to_file(self, output_file, result):
        for count in range(16):
            if self._test[count].get_check_box_value() == 1:
                if count == 10:
                    output_file.write(self._test_type[count] + ':\n')
                    output = '\t\t\t\t\t\t\t\t\t\t\t\t\t%-20s\t%s\n' % (
                    str(result[count][0][0]), self.get_result_string(result[count][0][1]))
                    output_file.write(output)
                    output = '\t\t\t\t\t\t\t\t\t\t\t\t\t%-20s\t%s\n' % (
                    str(result[count][1][0]), self.get_result_string(result[count][1][1]))
                    output_file.write(output)
                    pass
                elif count == 14:
                    output_file.write(self._test_type[count] + ':\n')
                    output = '\t\t\t\t%-10s\t%-20s\t%-20s\t%s\n' % ('State ', 'Chi Squared', 'P-Value', 'Conclusion')
                    output_file.write(output)
                    for item in result[count]:
                        output = '\t\t\t\t%-10s\t%-20s\t%-20s\t%s\n' % (
                        item[0], item[2], item[3], self.get_result_string(item[4]))
                        output_file.write(output)
                elif count == 15:
                    output_file.write(self._test_type[count] + ':\n')
                    output = '\t\t\t\t%-10s\t%-20s\t%-20s\t%s\n' % ('State ', 'COUNTS', 'P-Value', 'Conclusion')
                    output_file.write(output)
                    for item in result[count]:
                        output = '\t\t\t\t%-10s\t%-20s\t%-20s\t%s\n' % (
                        item[0], item[2], item[3], self.get_result_string(item[4]))
                        output_file.write(output)
                else:
                    output = '%-50s\t%-20s\t%s\n' % (
                    self._test_type[count], str(result[count][0]), self.get_result_string(result[count][1]))
                    output_file.write(output)
            count += 1

    #def change_data(self):
    #    index = int(self.__test_data.get_selected().split(' ')[0])
    #    print(self.__test_result[index-1])
    #    self.write_results(self.__test_result[index-1])

    def reset(self):
        """
        Reset the GUI:
        1.  Clear all input in the textfield.
        2.  Unchecked all checkbox

        :return: None
        """
        print('Reset')
        self.__binary_input.set_data('')
        self.__binary_data_file_input.set_data('')
        self.__string_data_file_input.set_data('')
        self.__is_binary_file = False
        self.__is_data_file = False
        self._monobit.reset()
        self._block.reset()
        self._run.reset()
        self._long_run.reset()
        self._rank.reset()
        self._spectral.reset()
        self._non_overlappong.reset()
        self._overlapping.reset()
        self._universal.reset()
        self._linear.reset()
        self._serial.reset()
        self._entropy.reset()
        self._cusum_f.reset()
        self._cusum_r.reset()
        self._excursion.reset()
        self._variant.reset()
        #self.__test_data = Options(self.__stest_selection_label_frame, 'Input Data', [''], 10, 5, 900)
        self._test_result = []
        self._test_string = []

    def exit(self):
        """
        Exit this program normally

        :return: None
        """
        print('Exit')
        exit(0)

    def get_result_string(self, result):
        """
        Interpret the result and return either 'Random' or 'Non-Random'

        :param result: Result of the test (either True or False)
        :return: str (Either 'Random' for True and 'Non-Random' for False
        """
        if result:
            return 'Random'
        else:
            return 'Non-Random'

if __name__ == '__main__':
    np.seterr('raise') # Make exceptions fatal, otherwise GUI might get inconsistent
    root = Tk()
    root.resizable(0, 0)
    root.geometry("%dx%d+0+0" % (1300, 650))
    title = 'Test Suite for NIST Random Numbers'
    root.title(title)
    app = Main(root)
    app.focus_displayof()
    app.mainloop()

#module: ApproximateEntropy.py

from math import log as log
from numpy import zeros as zeros
from scipy.special import gammaincc as gammaincc

class ApproximateEntropy:

    @staticmethod
    def approximate_entropy_test(binary_data:str, verbose=False, pattern_length=10):
        """
        from the NIST documentation http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf

        As with the Serial test of Section 2.11, the focus of this test is the frequency of all possible
        overlapping m-bit patterns across the entire sequence. The purpose of the test is to compare
        the frequency of overlapping blocks of two consecutive/adjacent lengths (m and m+1) against the
        expected result for a random sequence.

        :param      binary_data:        a binary string
        :param      verbose             True to display the debug message, False to turn off debug message
        :param      pattern_length:     the length of the pattern (m)
        :return:    ((p_value1, bool), (p_value2, bool)) A tuple which contain the p_value and result of serial_test(True or False)
        """
        length_of_binary_data = len(binary_data)

        # Augment the n-bit sequence to create n overlapping m-bit sequences by appending m-1 bits
        # from the beginning of the sequence to the end of the sequence.
        # NOTE: documentation says m-1 bits but that doesnt make sense, or work.
        binary_data += binary_data[:pattern_length + 1:]

        # Get max length one patterns for m, m-1, m-2
        max_pattern = ''
        for i in range(pattern_length + 2):
            max_pattern += '1'

        # Keep track of each pattern's frequency (how often it appears)
        vobs_01 = zeros(int(max_pattern[0:pattern_length:], 2) + 1)
        vobs_02 = zeros(int(max_pattern[0:pattern_length + 1:], 2) + 1)

        for i in range(length_of_binary_data):
            # Work out what pattern is observed
            vobs_01[int(binary_data[i:i + pattern_length:], 2)] += 1
            vobs_02[int(binary_data[i:i + pattern_length + 1:], 2)] += 1

        # Calculate the test statistics and p values
        vobs = [vobs_01, vobs_02]

        sums = zeros(2)
        for i in range(2):
            for j in range(len(vobs[i])):
                if vobs[i][j] > 0:
                    sums[i] += vobs[i][j] * log(vobs[i][j] / length_of_binary_data)
        sums /= length_of_binary_data
        ape = sums[0] - sums[1]

        xObs = 2.0 * length_of_binary_data * (log(2) - ape)

        p_value = gammaincc(pow(2, pattern_length - 1), xObs / 2.0)

        if verbose:
            print('Approximate Entropy Test DEBUG BEGIN:')
            print("\tLength of input:\t\t\t", length_of_binary_data)
            print('\tLength of each block:\t\t', pattern_length)
            print('\tApEn(m):\t\t\t\t\t', ape)
            print('\txObs:\t\t\t\t\t\t', xObs)
            print('\tP-Value:\t\t\t\t\t', p_value)
            print('DEBUG END.')

        return (p_value, (p_value >= 0.01))


#module: BinaryMatrix.py

from copy import copy as copy

class BinaryMatrix:

    def __init__(self, matrix, rows, cols):
        """
        This class contains the algorithm specified in the NIST suite for computing the **binary rank** of a matrix.
        :param matrix: the matrix we want to compute the rank for
        :param rows: the number of rows
        :param cols: the number of columns
        :return: a BinaryMatrix object
        """
        self.M = rows
        self.Q = cols
        self.A = matrix
        self.m = min(rows, cols)

    def compute_rank(self, verbose=False):
        """
        This method computes the binary rank of self.matrix
        :param verbose: if this is true it prints out the matrix after the forward elimination and backward elimination
        operations on the rows. This was used to testing the method to check it is working as expected.
        :return: the rank of the matrix.
        """
        if verbose:
            print("Original Matrix\n", self.A)

        i = 0
        while i < self.m - 1:
            if self.A[i][i] == 1:
                self.perform_row_operations(i, True)
            else:
                found = self.find_unit_element_swap(i, True)
                if found == 1:
                    self.perform_row_operations(i, True)
            i += 1

        if verbose:
            print("Intermediate Matrix\n", self.A)

        i = self.m - 1
        while i > 0:
            if self.A[i][i] == 1:
                self.perform_row_operations(i, False)
            else:
                if self.find_unit_element_swap(i, False) == 1:
                    self.perform_row_operations(i, False)
            i -= 1

        if verbose:
            print("Final Matrix\n", self.A)

        return self.determine_rank()

    def perform_row_operations(self, i, forward_elimination):
        """
        This method performs the elementary row operations. This involves xor'ing up to two rows together depending on
        whether or not certain elements in the matrix contain 1's if the "current" element does not.
        :param i: the current index we are are looking at
        :param forward_elimination: True or False.
        """
        if forward_elimination:
            j = i + 1
            while j < self.M:
                if self.A[j][i] == 1:
                    self.A[j, :] = (self.A[j, :] + self.A[i, :]) % 2
                j += 1
        else:
            j = i - 1
            while j >= 0:
                if self.A[j][i] == 1:
                    self.A[j, :] = (self.A[j, :] + self.A[i, :]) % 2
                j -= 1

    def find_unit_element_swap(self, i, forward_elimination):
        """
        This given an index which does not contain a 1 this searches through the rows below the index to see which rows
        contain 1's, if they do then they swapped. This is done on the forward and backward elimination
        :param i: the current index we are looking at
        :param forward_elimination: True or False.
        """
        row_op = 0
        if forward_elimination:
            index = i + 1
            while index < self.M and self.A[index][i] == 0:
                index += 1
            if index < self.M:
                row_op = self.swap_rows(i, index)
        else:
            index = i - 1
            while index >= 0 and self.A[index][i] == 0:
                index -= 1
            if index >= 0:
                row_op = self.swap_rows(i, index)
        return row_op

    def swap_rows(self, i, ix):
        """
        This method just swaps two rows in a matrix. Had to use the copy package to ensure no memory leakage
        :param i: the first row we want to swap and
        :param ix: the row we want to swap it with
        :return: 1
        """
        temp = copy(self.A[i, :])
        self.A[i, :] = self.A[ix, :]
        self.A[ix, :] = temp
        return 1

    def determine_rank(self):
        """
        This method determines the rank of the transformed matrix
        :return: the rank of the transformed matrix
        """
        rank = self.m
        i = 0
        while i < self.M:
            all_zeros = 1
            for j in range(self.Q):
                if self.A[i][j] == 1:
                    all_zeros = 0
            if all_zeros == 1:
                rank -= 1
            i += 1
        return rank

#module: Complexity.py

from copy import copy as copy
from numpy import dot as dot
from numpy import histogram as histogram
from numpy import zeros as zeros
from scipy.special import gammaincc as gammaincc

class ComplexityTest:

    @staticmethod
    def linear_complexity_test(binary_data:str, verbose=False, block_size=500):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of this test is the length of a linear feedback shift register (LFSR). The purpose of this test is to
        determine whether or not the sequence is complex enough to be considered random. Random sequences are
        characterized by longer LFSRs. An LFSR that is too short implies non-randomness.

        :param      binary_data:    a binary string
        :param      verbose         True to display the debug messgae, False to turn off debug message
        :param      block_size:     Size of the block
        :return:    (p_value, bool) A tuple which contain the p_value and result of frequency_test(True or False)

        """

        length_of_binary_data = len(binary_data)

        # The number of degrees of freedom;
        # K = 6 has been hard coded into the test.
        degree_of_freedom = 6

        #  π0 = 0.010417, π1 = 0.03125, π2 = 0.125, π3 = 0.5, π4 = 0.25, π5 = 0.0625, π6 = 0.020833
        #  are the probabilities computed by the equations in Section 3.10
        pi = [0.01047, 0.03125, 0.125, 0.5, 0.25, 0.0625, 0.020833]

        t2 = (block_size / 3.0 + 2.0 / 9) / 2 ** block_size
        mean = 0.5 * block_size + (1.0 / 36) * (9 + (-1) ** (block_size + 1)) - t2

        number_of_block = int(length_of_binary_data / block_size)

        if number_of_block > 1:
            block_end = block_size
            block_start = 0
            blocks = []
            for i in range(number_of_block):
                blocks.append(binary_data[block_start:block_end])
                block_start += block_size
                block_end += block_size

            complexities = []
            for block in blocks:
                complexities.append(ComplexityTest.berlekamp_massey_algorithm(block))

            t = ([-1.0 * (((-1) ** block_size) * (chunk - mean) + 2.0 / 9) for chunk in complexities])
            vg = histogram(t, bins=[-9999999999, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 9999999999])[0][::-1]
            im = ([((vg[ii] - number_of_block * pi[ii]) ** 2) / (number_of_block * pi[ii]) for ii in range(7)])

            xObs = 0.0
            for i in range(len(pi)):
                xObs += im[i]

            # P-Value = igamc(K/2, xObs/2)
            p_value = gammaincc(degree_of_freedom / 2.0, xObs / 2.0)

            if verbose:
                print('Linear Complexity Test DEBUG BEGIN:')
                print("\tLength of input:\t", length_of_binary_data)
                print('\tLength in bits of a block:\t', )
                print("\tDegree of Freedom:\t\t", degree_of_freedom)
                print('\tNumber of Blocks:\t', number_of_block)
                print('\tValue of Vs:\t\t', vg)
                print('\txObs:\t\t\t\t', xObs)
                print('\tP-Value:\t\t\t', p_value)
                print('DEBUG END.')


            return (p_value, (p_value >= 0.01))
        else:
            return (-1.0, False)

    @staticmethod
    def berlekamp_massey_algorithm(block_data):
        """
        An implementation of the Berlekamp Massey Algorithm. Taken from Wikipedia [1]
        [1] - https://en.wikipedia.org/wiki/Berlekamp-Massey_algorithm
        The Berlekamp–Massey algorithm is an algorithm that will find the shortest linear feedback shift register (LFSR)
        for a given binary output sequence. The algorithm will also find the minimal polynomial of a linearly recurrent
        sequence in an arbitrary field. The field requirement means that the Berlekamp–Massey algorithm requires all
        non-zero elements to have a multiplicative inverse.
        :param block_data:
        :return:
        """
        n = len(block_data)
        c = zeros(n)
        b = zeros(n)
        c[0], b[0] = 1, 1
        l, m, i = 0, -1, 0
        int_data = [int(el) for el in block_data]
        while i < n:
            v = int_data[(i - l):i]
            v = v[::-1]
            cc = c[1:l + 1]
            d = (int_data[i] + dot(v, cc)) % 2
            if d == 1:
                temp = copy(c)
                p = zeros(n)
                for j in range(0, l):
                    if b[j] == 1:
                        p[j + i - m] = 1
                c = (c + p) % 2
                if l <= 0.5 * i:
                    l = i + 1 - l
                    m = i
                    b = temp
            i += 1
        return l

#module: CumulativeSums.py

from numpy import abs as abs
from numpy import array as array
from numpy import floor as floor
from numpy import max as max
from numpy import sqrt as sqrt
from numpy import sum as sum
from numpy import zeros as zeros
from scipy.stats import norm as norm

class CumulativeSums:

    @staticmethod
    def cumulative_sums_test(binary_data:str, mode=0, verbose=False):
        """
        from the NIST documentation http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf

        The focus of this test is the maximal excursion (from zero) of the random walk defined by the cumulative sum of
        adjusted (-1, +1) digits in the sequence. The purpose of the test is to determine whether the cumulative sum of
        the partial sequences occurring in the tested sequence is too large or too small relative to the expected
        behavior of that cumulative sum for random sequences. This cumulative sum may be considered as a random walk.
        For a random sequence, the excursions of the random walk should be near zero. For certain types of non-random
        sequences, the excursions of this random walk from zero will be large.

        :param      binary_data:    a binary string
        :param      mode            A switch for applying the test either forward through the input sequence (mode = 0)
                                    or backward through the sequence (mode = 1).
        :param      verbose         True to display the debug messgae, False to turn off debug message
        :return:    (p_value, bool) A tuple which contain the p_value and result of frequency_test(True or False)

        """

        length_of_binary_data = len(binary_data)
        counts = zeros(length_of_binary_data)

        # Determine whether forward or backward data
        if not mode == 0:
            binary_data = binary_data[::-1]

        counter = 0
        for char in binary_data:
            sub = 1
            if char == '0':
                sub = -1
            if counter > 0:
                counts[counter] = counts[counter -1] + sub
            else:
                counts[counter] = sub

            counter += 1
        # Compute the test statistic z =max1≤k≤n|Sk|, where max1≤k≤n|Sk| is the largest of the
        # absolute values of the partial sums Sk.
        abs_max = max(abs(counts))

        start = int(floor(0.25 * floor(-length_of_binary_data / abs_max) + 1))
        end = int(floor(0.25 * floor(length_of_binary_data / abs_max) - 1))

        terms_one = []
        for k in range(start, end + 1):
            sub = norm.cdf((4 * k - 1) * abs_max / sqrt(length_of_binary_data))
            terms_one.append(norm.cdf((4 * k + 1) * abs_max / sqrt(length_of_binary_data)) - sub)

        start = int(floor(0.25 * floor(-length_of_binary_data / abs_max - 3)))
        end = int(floor(0.25 * floor(length_of_binary_data / abs_max) - 1))

        terms_two = []
        for k in range(start, end + 1):
            sub = norm.cdf((4 * k + 1) * abs_max / sqrt(length_of_binary_data))
            terms_two.append(norm.cdf((4 * k + 3) * abs_max / sqrt(length_of_binary_data)) - sub)

        p_value = 1.0 - sum(array(terms_one))
        p_value += sum(array(terms_two))

        if verbose:
            print('Cumulative Sums Test DEBUG BEGIN:')
            print("\tLength of input:\t", length_of_binary_data)
            print('\tMode:\t\t\t\t', mode)
            print('\tValue of z:\t\t\t', abs_max)
            print('\tP-Value:\t\t\t', p_value)
            print('DEBUG END.')

        return (p_value, (p_value >= 0.01))

#module: FrequencyTest.py

from math import fabs as fabs
from math import floor as floor
from math import sqrt as sqrt
from scipy.special import erfc as erfc
from scipy.special import gammaincc as gammaincc

class FrequencyTest:

    @staticmethod
    def monobit_test(binary_data:str, verbose=False):
        """
        The focus of the test is the proportion of zeroes and ones for the entire sequence.
        The purpose of this test is to determine whether the number of ones and zeros in a sequence are approximately
        the same as would be expected for a truly random sequence. The test assesses the closeness of the fraction of
        ones to 陆, that is, the number of ones and zeroes in a sequence should be about the same.
        All subsequent tests depend on the passing of this test.

        if p_value < 0.01, then conclude that the sequence is non-random (return False).
        Otherwise, conclude that the the sequence is random (return True).

        :param      binary_data         The seuqnce of bit being tested
        :param      verbose             True to display the debug messgae, False to turn off debug message
        :return:    (p_value, bool)     A tuple which contain the p_value and result of frequency_test(True or False)

        """

        length_of_bit_string = len(binary_data)

        # Variable for S(n)
        count = 0
        # Iterate each bit in the string and compute for S(n)
        for bit in binary_data:
            if bit == '0':
                # If bit is 0, then -1 from the S(n)
                count -= 1
            elif bit == '1':
                # If bit is 1, then +1 to the S(n)
                count += 1

        # Compute the test statistic
        sObs = count / sqrt(length_of_bit_string)

        # Compute p-Value
        p_value = erfc(fabs(sObs) / sqrt(2))

        if verbose:
            print('Frequency Test (Monobit Test) DEBUG BEGIN:')
            print("\tLength of input:\t", length_of_bit_string)
            print('\t# of \'0\':\t\t\t', binary_data.count('0'))
            print('\t# of \'1\':\t\t\t', binary_data.count('1'))
            print('\tS(n):\t\t\t\t', count)
            print('\tsObs:\t\t\t\t', sObs)
            print('\tf:\t\t\t\t\t',fabs(sObs) / sqrt(2))
            print('\tP-Value:\t\t\t', p_value)
            print('DEBUG END.')

        # return a p_value and randomness result
        return (p_value, (p_value >= 0.01))

    @staticmethod
    def block_frequency(binary_data:str, block_size=128, verbose=False):
        """
        The focus of the test is the proportion of ones within M-bit blocks.
        The purpose of this test is to determine whether the frequency of ones in an M-bit block is approximately M/2,
        as would be expected under an assumption of randomness.
        For block size M=1, this test degenerates to test 1, the Frequency (Monobit) test.

        :param      binary_data:        The length of each block
        :param      block_size:         The seuqnce of bit being tested
        :param      verbose             True to display the debug messgae, False to turn off debug message
        :return:    (p_value, bool)     A tuple which contain the p_value and result of frequency_test(True or False)
        """

        length_of_bit_string = len(binary_data)


        if length_of_bit_string < block_size:
            block_size = length_of_bit_string

        # Compute the number of blocks based on the input given.  Discard the remainder
        number_of_blocks = floor(length_of_bit_string / block_size)

        if number_of_blocks == 1:
            # For block size M=1, this test degenerates to test 1, the Frequency (Monobit) test.
            return FrequencyTest.monobit_test(binary_data[0:block_size])

        # Initialized variables
        block_start = 0
        block_end = block_size
        proportion_sum = 0.0

        # Create a for loop to process each block
        for counter in range(number_of_blocks):
            # Partition the input sequence and get the data for block
            block_data = binary_data[block_start:block_end]

            # Determine the proportion 蟺i of ones in each M-bit
            one_count = 0
            for bit in block_data:
                if bit == '1':
                    one_count += 1
            # compute π
            pi = one_count / block_size

            # Compute Σ(πi -½)^2.
            proportion_sum += pow(pi - 0.5, 2.0)

            # Next Block
            block_start += block_size
            block_end += block_size

        # Compute 4M Σ(πi -½)^2.
        result = 4.0 * block_size * proportion_sum

        # Compute P-Value
        p_value = gammaincc(number_of_blocks / 2, result / 2)

        if verbose:
            print('Frequency Test (Block Frequency Test) DEBUG BEGIN:')
            print("\tLength of input:\t", length_of_bit_string)
            print("\tSize of Block:\t\t", block_size)
            print('\tNumber of Blocks:\t', number_of_blocks)
            print('\tCHI Squared:\t\t', result)
            print('\t1st:\t\t\t\t', number_of_blocks / 2)
            print('\t2nd:\t\t\t\t', result / 2)
            print('\tP-Value:\t\t\t', p_value)
            print('DEBUG END.')

        return (p_value, (p_value >= 0.01))

#module: RandomExcursions.py

from math import isnan as isnan
from numpy import abs as abs
from numpy import append as append
from numpy import array as array
from numpy import clip as clip
from numpy import cumsum as cumsum
from numpy import ones as ones
from numpy import sqrt as sqrt
from numpy import sum as sum
from numpy import transpose as transpose
from numpy import where as where
from numpy import zeros as zeros
from scipy.special import erfc as erfc
from scipy.special import gammaincc as gammaincc

class RandomExcursions:

    @staticmethod
    def random_excursions_test(binary_data:str, verbose=False, state=1):
        """
        from the NIST documentation http://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-22r1a.pdf

        The focus of this test is the total number of times that a particular state is visited (i.e., occurs) in a
        cumulative sum random walk. The purpose of this test is to detect deviations from the expected number
        of visits to various states in the random walk. This test is actually a series of eighteen tests (and
        conclusions), one test and conclusion for each of the states: -9, -8, …, -1 and +1, +2, …, +9.

        :param      binary_data:    a binary string
        :param      verbose         True to display the debug messgae, False to turn off debug message
        :return:    (p_value, bool) A tuple which contain the p_value and result of frequency_test(True or False)
        """

        length_of_binary_data = len(binary_data)
        # Form the normalized (-1, +1) sequence X in which the zeros and ones of the input sequence (ε)
        # are converted to values of –1 and +1 via X = X1, X2, … , Xn, where Xi = 2εi – 1.
        sequence_x = zeros(length_of_binary_data)
        for i in range(len(binary_data)):
            if binary_data[i] == '0':
                sequence_x[i] = -1.0
            else:
                sequence_x[i] = 1.0

        # Compute partial sums Si of successively larger subsequences, each starting with x1. Form the set S
        cumulative_sum = cumsum(sequence_x)

        # Form a new sequence S' by attaching zeros before and after the set S. That is, S' = 0, s1, s2, … , sn, 0.
        cumulative_sum = append(cumulative_sum, [0])
        cumulative_sum = append([0], cumulative_sum)

        # These are the states we are going to look at
        x_values = array([-4, -3, -2, -1, 1, 2, 3, 4])
        index = x_values.tolist().index(state)

        # Identify all the locations where the cumulative sum revisits 0
        position = where(cumulative_sum == 0)[0]
        # For this identify all the cycles
        cycles = []
        for pos in range(len(position) - 1):
            # Add this cycle to the list of cycles
            cycles.append(cumulative_sum[position[pos]:position[pos + 1] + 1])
        num_cycles = len(cycles)

        state_count = []
        for cycle in cycles:
            # Determine the number of times each cycle visits each state
            state_count.append(([len(where(cycle == state)[0]) for state in x_values]))
        state_count = transpose(clip(state_count, 0, 5))

        su = []
        for cycle in range(6):
            su.append([(sct == cycle).sum() for sct in state_count])
        su = transpose(su)

        pi = ([([RandomExcursions.get_pi_value(uu, state) for uu in range(6)]) for state in x_values])
        inner_term = num_cycles * array(pi)
        xObs = sum(1.0 * (array(su) - inner_term) ** 2 / inner_term, axis=1)
        p_values = ([gammaincc(2.5, cs / 2.0) for cs in xObs])

        if verbose:
            print('Random Excursion Test DEBUG BEGIN:')
            print("\tLength of input:\t", length_of_binary_data)
            count = 0
            print('\t\t STATE \t\t\t xObs \t\t\t\t\t\t p_value  \t\t\t\t\t Result')
            for item in p_values:
                print('\t\t', repr(x_values[count]).rjust(2), ' \t\t ', xObs[count],' \t\t ', repr(item).rjust(21), ' \t\t\t ', (item >= 0.01))
                count += 1
            print('DEBUG END.')

        states = ['-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4',]
        result = []
        count = 0
        for item in p_values:
            result.append((states[count], x_values[count], xObs[count], item, (item >= 0.01)))
            count += 1

        return result

    @staticmethod
    def variant_test(binary_data:str, verbose=False):
        """
        from the NIST documentation http://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-22r1a.pdf

        :param binary_data:
        :param verbose:
        :return:
        """
        length_of_binary_data = len(binary_data)
        int_data = zeros(length_of_binary_data)

        for count in range(length_of_binary_data):
            int_data[count] = int(binary_data[count])

        sum_int = (2 * int_data) - ones(len(int_data))
        cumulative_sum = cumsum(sum_int)

        li_data = []
        index = []
        for count in sorted(set(cumulative_sum)):
            if abs(count) <= 9:
                index.append(count)
                li_data.append([count, len(where(cumulative_sum == count)[0])])

        j = RandomExcursions.get_frequency(li_data, 0) + 1

        p_values = []
        for count in (sorted(set(index))):
            if not count == 0:
                den = sqrt(2 * j * (4 * abs(count) - 2))
                p_values.append(erfc(abs(RandomExcursions.get_frequency(li_data, count) - j) / den))

        count = 0
        # Remove 0 from li_data so the number of element will be equal to p_values
        for data in li_data:
            if data[0] == 0:
                li_data.remove(data)
                index.remove(0)
                break
            count += 1

        if verbose:
            print('Random Excursion Variant Test DEBUG BEGIN:')
            print("\tLength of input:\t", length_of_binary_data)
            print('\tValue of j:\t\t', j)
            print('\tP-Values:')
            print('\t\t STATE \t\t COUNTS \t\t P-Value \t\t Conclusion')
            count = 0
            for item in p_values:
                print('\t\t', repr(li_data[count][0]).rjust(4), '\t\t', li_data[count][1], '\t\t', repr(item).ljust(14), '\t\t', (item >= 0.01))
                count += 1
            print('DEBUG END.')


        states = []
        for item in index:
            if item < 0:
                states.append(str(item))
            else:
                states.append('+' + str(item))

        result = []
        count = 0
        for item in p_values:
            result.append((states[count], li_data[count][0], li_data[count][1], item, (item >= 0.01)))
            count += 1

        return result

    @staticmethod
    def get_pi_value(k, x):
        """
        This method is used by the random_excursions method to get expected probabilities
        """
        if k == 0:
            out = 1 - 1.0 / (2 * abs(x))
        elif k >= 5:
            out = (1.0 / (2 * abs(x))) * (1 - 1.0 / (2 * abs(x))) ** 4
        else:
            out = (1.0 / (4 * x * x)) * (1 - 1.0 / (2 * abs(x))) ** (k - 1)
        return out

    @staticmethod
    def get_frequency(list_data, trigger):
        """
        This method is used by the random_excursions_variant method to get frequencies
        """
        frequency = 0
        for (x, y) in list_data:
            if x == trigger:
                frequency = y
        return frequency

#module: RunTest.py

from math import fabs as fabs
from math import floor as floor
from math import sqrt as sqrt
from scipy.special import erfc as erfc
from scipy.special import gammaincc as gammaincc
from numpy import zeros as zeros

class RunTest:

    @staticmethod
    def run_test(binary_data:str, verbose=False):
        """
        The focus of this test is the total number of runs in the sequence,
        where a run is an uninterrupted sequence of identical bits.
        A run of length k consists of exactly k identical bits and is bounded before
        and after with a bit of the opposite value. The purpose of the runs test is to
        determine whether the number of runs of ones and zeros of various lengths is as
        expected for a random sequence. In particular, this test determines whether the
        oscillation between such zeros and ones is too fast or too slow.

        :param      binary_data:        The seuqnce of bit being tested
        :param      verbose             True to display the debug messgae, False to turn off debug message
        :return:    (p_value, bool)     A tuple which contain the p_value and result of frequency_test(True or False)
        """
        one_count = 0
        vObs = 0
        length_of_binary_data = len(binary_data)

        # Predefined tau = 2 / sqrt(n)
        # TODO Confirm with Frank about the discrepancy between the formula and the sample of 2.3.8
        tau = 2 / sqrt(length_of_binary_data)

        # Step 1 - Compute the pre-test proportion πof ones in the input sequence: π = Σjεj / n
        one_count = binary_data.count('1')

        pi = one_count / length_of_binary_data

        # Step 2 - If it can be shown that absolute value of (π - 0.5) is greater than or equal to tau
        # then the run test need not be performed.
        if abs(pi - 0.5) >= tau:
            ##print("The test should not have been run because of a failure to pass test 1, the Frequency (Monobit) test.")
            return (0.0000, False)
        else:
            # Step 3 - Compute vObs
            for item in range(1, length_of_binary_data):
                if binary_data[item] != binary_data[item - 1]:
                    vObs += 1
            vObs += 1

            # Step 4 - Compute p_value = erfc((|vObs − 2nπ * (1−π)|)/(2 * sqrt(2n) * π * (1−π)))
            p_value = erfc(abs(vObs - (2 * (length_of_binary_data) * pi * (1 - pi))) / (2 * sqrt(2 * length_of_binary_data) * pi * (1 - pi)))

        if verbose:
            print('Run Test DEBUG BEGIN:')
            print("\tLength of input:\t\t\t\t", length_of_binary_data)
            print("\tTau (2/sqrt(length of input)):\t", tau)
            print('\t# of \'1\':\t\t\t\t\t\t', one_count)
            print('\t# of \'0\':\t\t\t\t\t\t', binary_data.count('0'))
            print('\tPI (1 count / length of input):\t', pi)
            print('\tvObs:\t\t\t\t\t\t\t', vObs)
            print('\tP-Value:\t\t\t\t\t\t', p_value)
            print('DEBUG END.')

        return (p_value, (p_value > 0.01))

    @staticmethod
    def longest_one_block_test(binary_data:str, verbose=False):
        """
        The focus of the test is the longest run of ones within M-bit blocks. The purpose of this test is to determine
        whether the length of the longest run of ones within the tested sequence is consistent with the length of the
        longest run of ones that would be expected in a random sequence. Note that an irregularity in the expected
        length of the longest run of ones implies that there is also an irregularity in the expected length of the
        longest run of zeroes. Therefore, only a test for ones is necessary.

        :param      binary_data:        The sequence of bits being tested
        :param      verbose             True to display the debug messgae, False to turn off debug message
        :return:    (p_value, bool)     A tuple which contain the p_value and result of frequency_test(True or False)
        """
        length_of_binary_data = len(binary_data)
        # print('Length of binary string: ', length_of_binary_data)

        # Initialized k, m. n, pi and v_values
        if length_of_binary_data < 128:
            # Not enough data to run this test
            return (0.00000, False, 'Error: Not enough data to run this test')
        elif length_of_binary_data < 6272:
            k = 3
            m = 8
            v_values = [1, 2, 3, 4]
            pi_values = [0.21484375, 0.3671875, 0.23046875, 0.1875]
        elif length_of_binary_data < 750000:
            k = 5
            m = 128
            v_values = [4, 5, 6, 7, 8, 9]
            pi_values = [0.1174035788, 0.242955959, 0.249363483, 0.17517706, 0.102701071, 0.112398847]
        else:
            # If length_of_bit_string > 750000
            k = 6
            m = 10000
            v_values = [10, 11, 12, 13, 14, 15, 16]
            pi_values = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]

        number_of_blocks = floor(length_of_binary_data / m)
        block_start = 0
        block_end = m
        xObs = 0
        # This will intialized an array with a number of 0 you specified.
        frequencies = zeros(k + 1)

        # print('Number of Blocks: ', number_of_blocks)

        for count in range(number_of_blocks):
            block_data = binary_data[block_start:block_end]
            max_run_count = 0
            run_count = 0

            # This will count the number of ones in the block
            for bit in block_data:
                if bit == '1':
                    run_count += 1
                    max_run_count = max(max_run_count, run_count)
                else:
                    max_run_count = max(max_run_count, run_count)
                    run_count = 0

            max(max_run_count, run_count)

            #print('Block Data: ', block_data, '. Run Count: ', max_run_count)

            if max_run_count < v_values[0]:
                frequencies[0] += 1
            for j in range(k):
                if max_run_count == v_values[j]:
                    frequencies[j] += 1
            if max_run_count > v_values[k - 1]:
                frequencies[k] += 1

            block_start += m
            block_end += m

        # print("Frequencies: ", frequencies)
        # Compute xObs
        for count in range(len(frequencies)):
            xObs += pow((frequencies[count] - (number_of_blocks * pi_values[count])), 2.0) / (
                    number_of_blocks * pi_values[count])

        p_value = gammaincc(float(k / 2), float(xObs / 2))

        if verbose:
            print('Run Test (Longest Run of Ones in a Block) DEBUG BEGIN:')
            print("\tLength of input:\t\t\t\t", length_of_binary_data)
            print("\tSize of each Block:\t\t\t\t", m)
            print('\tNumber of Block:\t\t\t\t', number_of_blocks)
            print("\tValue of K:\t\t\t\t\t\t", k)
            print('\tValue of PIs:\t\t\t\t\t', pi_values)
            print('\tFrequencies:\t\t\t\t\t', frequencies)
            print('\txObs:\t\t\t\t\t\t\t', xObs)
            print('\tP-Value:\t\t\t\t\t\t', p_value)
            print('DEBUG END.')

        return (p_value, (p_value > 0.01))

#module: Serial.py

from numpy import zeros as zeros
from scipy.special import gammaincc as gammaincc
class Serial:

    @staticmethod
    def serial_test(binary_data:str, verbose=False, pattern_length=16):
        """
        From the NIST documentation http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf

        The focus of this test is the frequency of all possible overlapping m-bit patterns across the entire
        sequence. The purpose of this test is to determine whether the number of occurrences of the 2m m-bit
        overlapping patterns is approximately the same as would be expected for a random sequence. Random
        sequences have uniformity; that is, every m-bit pattern has the same chance of appearing as every other
        m-bit pattern. Note that for m = 1, the Serial test is equivalent to the Frequency test of Section 2.1.

        :param      binary_data:        a binary string
        :param      verbose             True to display the debug message, False to turn off debug message
        :param      pattern_length:     the length of the pattern (m)
        :return:    ((p_value1, bool), (p_value2, bool)) A tuple which contain the p_value and result of serial_test(True or False)
        """
        length_of_binary_data = len(binary_data)
        binary_data += binary_data[:(pattern_length -1):]

        # Get max length one patterns for m, m-1, m-2
        max_pattern = ''
        for i in range(pattern_length + 1):
            max_pattern += '1'

        # Step 02: Determine the frequency of all possible overlapping m-bit blocks,
        # all possible overlapping (m-1)-bit blocks and
        # all possible overlapping (m-2)-bit blocks.
        vobs_01 = zeros(int(max_pattern[0:pattern_length:], 2) + 1)
        vobs_02 = zeros(int(max_pattern[0:pattern_length - 1:], 2) + 1)
        vobs_03 = zeros(int(max_pattern[0:pattern_length - 2:], 2) + 1)

        for i in range(length_of_binary_data):
            # Work out what pattern is observed
            vobs_01[int(binary_data[i:i + pattern_length:], 2)] += 1
            vobs_02[int(binary_data[i:i + pattern_length - 1:], 2)] += 1
            vobs_03[int(binary_data[i:i + pattern_length - 2:], 2)] += 1

        vobs = [vobs_01, vobs_02, vobs_03]

        # Step 03 Compute for ψs
        sums = zeros(3)
        for i in range(3):
            for j in range(len(vobs[i])):
                sums[i] += pow(vobs[i][j], 2)
            sums[i] = (sums[i] * pow(2, pattern_length - i) / length_of_binary_data) - length_of_binary_data

        # Cimpute the test statistics and p values
        #Step 04 Compute for ∇
        nabla_01 = sums[0] - sums[1]
        nabla_02 = sums[0] - 2.0 * sums[1] + sums[2]

        # Step 05 Compute for P-Value
        p_value_01 = gammaincc(pow(2, pattern_length - 1) / 2, nabla_01 / 2.0)
        p_value_02 = gammaincc(pow(2, pattern_length - 2) / 2, nabla_02 / 2.0)

        if verbose:
            print('Serial Test DEBUG BEGIN:')
            print("\tLength of input:\t", length_of_binary_data)
            print('\tValue of Sai:\t\t', sums)
            print('\tValue of Nabla:\t\t', nabla_01, nabla_02)
            print('\tP-Value 01:\t\t\t', p_value_01)
            print('\tP-Value 02:\t\t\t', p_value_02)
            print('DEBUG END.')

        return ((p_value_01, p_value_01 >= 0.01), (p_value_02, p_value_02 >= 0.01))

#module: Spectral.py

from math import fabs as fabs
from math import floor as floor
from math import log as log
from math import sqrt as sqrt
from numpy import where as where
from scipy import fftpack as sff
from scipy.special import erfc as erfc

class SpectralTest:

    @staticmethod
    def spectral_test(binary_data:str, verbose=False):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of this test is the peak heights in the Discrete Fourier Transform of the sequence. The purpose of
        this test is to detect periodic features (i.e., repetitive patterns that are near each other) in the tested
        sequence that would indicate a deviation from the assumption of randomness. The intention is to detect whether
        the number of peaks exceeding the 95 % threshold is significantly different than 5 %.

        :param      binary_data:        The seuqnce of bit being tested
        :param      verbose             True to display the debug messgae, False to turn off debug message
        :return:    (p_value, bool)     A tuple which contain the p_value and result of frequency_test(True or False)
        """
        length_of_binary_data = len(binary_data)
        plus_one_minus_one = []

        # Step 1 - The zeros and ones of the input sequence (ε) are converted to values of –1 and +1
        # to create the sequence X = x1, x2, …, xn, where xi = 2εi – 1.
        for char in binary_data:
            if char == '0':
                plus_one_minus_one.append(-1)
            elif char == '1':
                plus_one_minus_one.append(1)

        # Step 2 - Apply a Discrete Fourier transform (DFT) on X to produce: S = DFT(X).
        # A sequence of complex variables is produced which represents periodic
        # components of the sequence of bits at different frequencies
        spectral = sff.fft(plus_one_minus_one)

        # Step 3 - Calculate M = modulus(S´) ≡ |S'|, where S´ is the substring consisting of the first n/2
        # elements in S, and the modulus function produces a sequence of peak heights.
        slice = floor(length_of_binary_data / 2)
        modulus = abs(spectral[0:slice])

        # Step 4 - Compute T = sqrt(log(1 / 0.05) * length_of_string) the 95 % peak height threshold value.
        # Under an assumption of randomness, 95 % of the values obtained from the test should not exceed T.
        tau = sqrt(log(1 / 0.05) * length_of_binary_data)

        # Step 5 - Compute N0 = .95n/2. N0 is the expected theoretical (95 %) number of peaks
        # (under the assumption of randomness) that are less than T.
        n0 = 0.95 * (length_of_binary_data / 2)

        # Step 6 - Compute N1 = the actual observed number of peaks in M that are less than T.
        n1 = len(where(modulus < tau)[0])

        # Step 7 - Compute d = (n_1 - n_0) / sqrt (length_of_string * (0.95) * (0.05) / 4)
        d = (n1 - n0) / sqrt(length_of_binary_data * (0.95) * (0.05) / 4)

        # Step 8 - Compute p_value = erfc(abs(d)/sqrt(2))
        p_value = erfc(fabs(d) / sqrt(2))

        if verbose:
            print('Discrete Fourier Transform (Spectral) Test DEBUG BEGIN:')
            print('\tLength of Binary Data:\t', length_of_binary_data)
            print('\tValue of T:\t\t\t\t', tau)
            print('\tValue of n1:\t\t\t', n1)
            print('\tValue of n0:\t\t\t', n0)
            print('\tValue of d:\t\t\t\t', d)
            print('\tP-Value:\t\t\t\t', p_value)
            print('DEBUG END.')

        return (p_value, (p_value >= 0.01))

#module: TemplateMatching.py

from math import floor as floor
from numpy import array as array
from numpy import exp as exp
from numpy import zeros as zeros
from scipy.special import gammaincc as gammaincc
from scipy.special import hyp1f1 as hyp1f1


class TemplateMatching:

    @staticmethod
    def non_overlapping_test(binary_data:str, verbose=False, template_pattern='000000001', block=8):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of this test is the number of occurrences of pre-specified target strings. The purpose of this
        test is to detect generators that produce too many occurrences of a given non-periodic (aperiodic) pattern.
        For this test and for the Overlapping Template Matching test of Section 2.8, an m-bit window is used to
        search for a specific m-bit pattern. If the pattern is not found, the window slides one bit position. If the
        pattern is found, the window is reset to the bit after the found pattern, and the search resumes.
        :param      binary_data:        The seuqnce of bit being tested
        :param      template_pattern:   The pattern to match to
        :param      verbose             True to display the debug messgae, False to turn off debug message
        :param      block               The number of independent blocks. Has been fixed at 8 in the test code.
        :return:    (p_value, bool)     A tuple which contain the p_value and result of frequency_test(True or False)
        """

        length_of_binary = len(binary_data)
        pattern_size = len(template_pattern)
        block_size = floor(length_of_binary / block)
        pattern_counts = zeros(block)

        # For each block in the data
        for count in range(block):
            block_start = count * block_size
            block_end = block_start + block_size
            block_data = binary_data[block_start:block_end]
            # Count the number of pattern hits
            inner_count = 0
            while inner_count < block_size:
                sub_block = block_data[inner_count:inner_count+pattern_size]
                if sub_block == template_pattern:
                    pattern_counts[count] += 1
                    inner_count += pattern_size
                else:
                    inner_count += 1

            # Calculate the theoretical mean and variance
            # Mean - µ = (M-m+1)/2m
            mean = (block_size - pattern_size + 1) / pow(2, pattern_size)
            # Variance - σ2 = M((1/pow(2,m)) - ((2m -1)/pow(2, 2m)))
            variance = block_size * ((1 / pow(2, pattern_size)) - (((2 * pattern_size) - 1) / (pow(2, pattern_size * 2))))

        # Calculate the xObs Squared statistic for these pattern matches
        xObs = 0
        for count in range(block):
            xObs += pow((pattern_counts[count] - mean), 2.0) / variance

        # Calculate and return the p value statistic
        p_value = gammaincc((block / 2), (xObs / 2))

        if verbose:
            print('Non-Overlapping Template Test DEBUG BEGIN:')
            print("\tLength of input:\t\t", length_of_binary)
            print('\tValue of Mean (µ):\t\t', mean)
            print('\tValue of Variance(σ):\t', variance)
            print('\tValue of W:\t\t\t\t', pattern_counts)
            print('\tValue of xObs:\t\t\t', xObs)
            print('\tP-Value:\t\t\t\t', p_value)
            print('DEBUG END.')

        return (p_value, (p_value >= 0.01))

    @staticmethod
    def overlapping_patterns(binary_data:str, verbose=False, pattern_size=9, block_size=1032):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of the Overlapping Template Matching test is the number of occurrences of pre-specified target
        strings. Both this test and the Non-overlapping Template Matching test of Section 2.7 use an m-bit
        window to search for a specific m-bit pattern. As with the test in Section 2.7, if the pattern is not found,
        the window slides one bit position. The difference between this test and the test in Section 2.7 is that
        when the pattern is found, the window slides only one bit before resuming the search.

        :param      binary_data:    a binary string
        :param      verbose         True to display the debug messgae, False to turn off debug message
        :param      pattern_size:   the length of the pattern
        :param      block_size:     the length of the block
        :return:    (p_value, bool) A tuple which contain the p_value and result of frequency_test(True or False)
        """
        length_of_binary_data = len(binary_data)
        pattern = ''
        for count in range(pattern_size):
            pattern += '1'

        number_of_block = floor(length_of_binary_data / block_size)

        # λ = (M-m+1)/pow(2, m)
        lambda_val = float(block_size - pattern_size + 1) / pow(2, pattern_size)
        # η = λ/2
        eta = lambda_val / 2.0

        pi = [TemplateMatching.get_prob(i, eta) for i in range(5)]
        diff = float(array(pi).sum())
        pi.append(1.0 - diff)

        pattern_counts = zeros(6)
        for i in range(number_of_block):
            block_start = i * block_size
            block_end = block_start + block_size
            block_data = binary_data[block_start:block_end]
            # Count the number of pattern hits
            pattern_count = 0
            j = 0
            while j < block_size:
                sub_block = block_data[j:j + pattern_size]
                if sub_block == pattern:
                    pattern_count += 1
                j += 1
            if pattern_count <= 4:
                pattern_counts[pattern_count] += 1
            else:
                pattern_counts[5] += 1

        xObs = 0.0
        for i in range(len(pattern_counts)):
            xObs += pow(pattern_counts[i] - number_of_block * pi[i], 2.0) / (number_of_block * pi[i])

        p_value = gammaincc(5.0 / 2.0, xObs / 2.0)

        if verbose:
            print('Overlapping Template Test DEBUG BEGIN:')
            print("\tLength of input:\t\t", length_of_binary_data)
            print('\tValue of Vs:\t\t\t', pattern_counts)
            print('\tValue of xObs:\t\t\t', xObs)
            print('\tP-Value:\t\t\t\t', p_value)
            print('DEBUG END.')


        return (p_value, (p_value >= 0.01))

    @staticmethod
    def get_prob(u, x):
        out = 1.0 * exp(-x)
        if u != 0:
            out = 1.0 * x * exp(2 * -x) * (2 ** -u) * hyp1f1(u + 1, 2, x)
        return out

#module: Universal.py

from math import floor as floor
from math import log as log
from math import sqrt as sqrt
from numpy import zeros as zeros
from scipy.special import erfc as erfc

class Universal:

    @staticmethod
    def statistical_test(binary_data:str, verbose=False):
        """
        Note that this description is taken from the NIST documentation [1]
        [1] http://csrc.nist.gov/publications/nistpubs/800-22-rev1a/SP800-22rev1a.pdf
        The focus of this test is the number of bits between matching patterns (a measure that is related to the
        length of a compressed sequence). The purpose of the test is to detect whether or not the sequence can be
        significantly compressed without loss of information. A significantly compressible sequence is considered
        to be non-random. **This test is always skipped because the requirements on the lengths of the binary
        strings are too high i.e. there have not been enough trading days to meet the requirements.

        :param      binary_data:    a binary string
        :param      verbose             True to display the debug messgae, False to turn off debug message
        :return:    (p_value, bool) A tuple which contain the p_value and result of frequency_test(True or False)
        """
        length_of_binary_data = len(binary_data)
        pattern_size = 5
        if length_of_binary_data >= 387840:
            pattern_size = 6
        if length_of_binary_data >= 904960:
            pattern_size = 7
        if length_of_binary_data >= 2068480:
            pattern_size = 8
        if length_of_binary_data >= 4654080:
            pattern_size = 9
        if length_of_binary_data >= 10342400:
            pattern_size = 10
        if length_of_binary_data >= 22753280:
            pattern_size = 11
        if length_of_binary_data >= 49643520:
            pattern_size = 12
        if length_of_binary_data >= 107560960:
            pattern_size = 13
        if length_of_binary_data >= 231669760:
            pattern_size = 14
        if length_of_binary_data >= 496435200:
            pattern_size = 15
        if length_of_binary_data >= 1059061760:
            pattern_size = 16

        if 5 < pattern_size < 16:
            # Create the biggest binary string of length pattern_size
            ones = ""
            for i in range(pattern_size):
                ones += "1"

            # How long the state list should be
            num_ints = int(ones, 2)
            vobs = zeros(num_ints + 1)

            # Keeps track of the blocks, and whether were are initializing or summing
            num_blocks = floor(length_of_binary_data / pattern_size)
            # Q = 10 * pow(2, pattern_size)
            init_bits = 10 * pow(2, pattern_size)

            test_bits = num_blocks - init_bits

            # These are the expected values assuming randomness (uniform)
            c = 0.7 - 0.8 / pattern_size + (4 + 32 / pattern_size) * pow(test_bits, -3 / pattern_size) / 15
            variance = [0, 0, 0, 0, 0, 0, 2.954, 3.125, 3.238, 3.311, 3.356, 3.384, 3.401, 3.410, 3.416, 3.419, 3.421]
            expected = [0, 0, 0, 0, 0, 0, 5.2177052, 6.1962507, 7.1836656, 8.1764248, 9.1723243,
                        10.170032, 11.168765, 12.168070, 13.167693, 14.167488, 15.167379]
            sigma = c * sqrt(variance[pattern_size] / test_bits)

            cumsum = 0.0
            # Examine each of the K blocks in the test segment and determine the number of blocks since the
            # last occurrence of the same L-bit block (i.e., i – Tj). Replace the value in the table with the
            # location of the current block (i.e., Tj= i). Add the calculated distance between re-occurrences of
            # the same L-bit block to an accumulating log2 sum of all the differences detected in the K blocks
            for i in range(num_blocks):
                block_start = i * pattern_size
                block_end = block_start + pattern_size
                block_data = binary_data[block_start: block_end]
                # Work out what state we are in
                int_rep = int(block_data, 2)

                # Initialize the state list
                if i < init_bits:
                    vobs[int_rep] = i + 1
                else:
                    initial = vobs[int_rep]
                    vobs[int_rep] = i + 1
                    cumsum += log(i - initial + 1, 2)

            # Compute the statistic
            phi = float(cumsum / test_bits)
            stat = abs(phi - expected[pattern_size]) / (float(sqrt(2)) * sigma)

            # Compute for P-Value
            p_value = erfc(stat)

            if verbose:
                print('Maurer\'s Universal Statistical Test DEBUG BEGIN:')
                print("\tLength of input:\t\t", length_of_binary_data)
                print('\tLength of each block:\t', pattern_size)
                print('\tNumber of Blocks:\t\t', init_bits)
                print('\tValue of phi:\t\t\t', phi)
                print('\tP-Value:\t\t\t\t', p_value)
                print('DEBUG END.')

            return (p_value, (p_value>=0.01))
        else:
            return (-1.0, False)

#module: Tools.py

class Tools:

    @staticmethod
    def string_to_binary(input:str):
        binary = []
        for char in input:
            temp = bin(ord(char))[2:]
            while(len(temp) < 8):
                temp = '0' + temp
            binary.append(temp)

        return ''.join(binary)

    @staticmethod
    def string_to_binary_no_concat(input: str):
        binary = []
        for char in input:
            binary.append(bin(ord(char))[2:])

        return ''.join(binary)

    @staticmethod
    def url_to_binary(input:str):
        binary = []
        url = input.split('/')[-1].split('.')[0]

        return url


#module: Gui.py

from tkinter import Button
from tkinter import Canvas
from tkinter import Checkbutton
from tkinter import DISABLED
from tkinter import Entry
from tkinter import Frame
from tkinter import IntVar
from tkinter import Label
from tkinter import LabelFrame
from tkinter import OptionMenu
from tkinter import Scrollbar
from tkinter import StringVar

class CustomButton:

    def __init__(self, master, title, x_coor, y_coor, width, action=None):
        button = Button(master, text=title, command=action)
        button.config(font=("Calibri", 10))
        button.place(x=x_coor, y=y_coor, width=width, height=25)

class Input:

    def __init__(self, master, title, x_coor, y_coor, has_button=False, action=None, state='disabled', button_xcoor=1050, button_width=180):
        # Setup Labels
        label = Label(master, text=title)
        label.config(font=("Calibri", 12))
        label.place(x=x_coor, y=y_coor, height=25)

        self.__data = StringVar()
        self.__data_entry = Entry(master, textvariable=self.__data)
        self.__data_entry.place(x=150, y=y_coor, width=900, height=25)

        if has_button:
            self.__data_entry.config(state='disabled')
            button_title = 'Select ' + title
            button = Button(master, text=button_title, command=action)
            button.config(font=("Calibri", 10))
            button.place(x=button_xcoor, y=y_coor, width=180, height=25)

    def set_data(self, value):
        self.__data.set(value)

    def get_data(self):
        return self.__data.get()

    def change_state(self, state):
        self.__data_entry.config(state=state)

class LabelTag:

    def __init__(self, master, title, x_coor, y_coor, width, font_size=18, border=0, relief='flat'):
        label = Label(master, text=title, borderwidth=border, relief=relief)
        label.config(font=("Calibri", font_size))
        label.place(x=x_coor, y=y_coor, width=width, height=25)

class Options:

    def __init__(self, master, title, data, x_coor, y_coor, width):

        self.__selected = StringVar()
        label = Label(master, text=title)
        label.config(font=("Calibri", 12))
        self.__selected.set(data[0])
        label.place(x=x_coor, y=y_coor, height=25, width=100)
        self.__option = OptionMenu(master, self.__selected, *data)
        self.__option.place(x=150, y=y_coor, height=25, width=width)

    def set_selected(self, data):
        self.__selected.set(data)

    def get_selected(self):
        return self.__selected.get()

    def update_data(self, data):
        self.__option.option_clear()
        self.__option.option_add(data, '')
        self.__option.update()

class TestItem:

    def __init__(self, master, title, x_coor, y_coor, serial=False, p_value_x_coor=365, p_value_width=500, result_x_coor=870, result_width=350, font_size=12, two_columns=False):
        self.__chb_var = IntVar()
        self.__p_value = StringVar()
        self.__result = StringVar()
        self.__p_value_02 = StringVar()
        self.__result_02 = StringVar()
        checkbox = Checkbutton(master, text=title, variable=self.__chb_var)
        checkbox.config(font=("Calibri", font_size))
        checkbox.place(x=x_coor, y=y_coor)

        p_value_entry = Entry(master, textvariable=self.__p_value)
        p_value_entry.config(state=DISABLED)
        p_value_entry.place(x=p_value_x_coor, y=y_coor, width=p_value_width, height=25)

        result_entry = Entry(master, textvariable=self.__result)
        result_entry.config(state=DISABLED)
        result_entry.place(x=result_x_coor, y=y_coor, width=result_width, height=25)

        if serial and two_columns:
            p_value_entry_02 = Entry(master, textvariable=self.__p_value_02)
            p_value_entry_02.config(state=DISABLED)
            p_value_entry_02.place(x=875, y=y_coor, width=235, height=25)

            result_entry_02 = Entry(master, textvariable=self.__result_02)
            result_entry_02.config(state=DISABLED)
            result_entry_02.place(x=1115, y=y_coor, width=110, height=25)
        elif serial and not two_columns:
            p_value_entry_02 = Entry(master, textvariable=self.__p_value_02)
            p_value_entry_02.config(state=DISABLED)
            p_value_entry_02.place(x=365, y=y_coor+25, width=500, height=25)

            result_entry_02 = Entry(master, textvariable=self.__result_02)
            result_entry_02.config(state=DISABLED)
            result_entry_02.place(x=870, y=y_coor+25, width=350, height=25)

    def get_check_box_value(self):
        return self.__chb_var.get()

    def set_check_box_value(self, value):
        self.__chb_var.set(value)

    def set_p_value(self, value):
        self.__p_value.set(value)

    def set_result_value(self, value):
        self.__result.set(value)

    def set_p_value_02(self, value):
        self.__p_value_02.set(value)

    def set_result_value_02(self, value):
        self.__result_02.set(value)

    def set_values(self, values):
        self.__p_value.set(values[0])
        self.__result.set(self.__get_result_string(values[1]))

    def set_p_2_values(self, values):
        self.__p_value_02(values[0])
        self.__result_02(self.__get_result_string(values[1]))

    def reset(self):
        self.set_check_box_value(0)
        self.set_p_value('')
        self.set_result_value('')
        self.set_p_value_02('')
        self.set_result_value_02('')

    def __get_result_string(self, result):
        if result == True:
            return 'Random'
        else:
            return 'Non-Random'

class RandomExcursionTestItem:

    def __init__(self, master, title, x_coor, y_coor, data, variant=False, font_size=11):
        self.__chb_var = IntVar()
        self.__state = StringVar()
        self.__count = StringVar()
        self.__xObs = StringVar()
        self.__p_value = StringVar()
        self.__result = StringVar()
        self.__results = []
        self.__variant = variant

        checkbox = Checkbutton(master, text=title, variable=self.__chb_var)
        checkbox.config(font=("Calibri", font_size))
        checkbox.place(x=x_coor, y=y_coor)

        state_label = LabelTag(master, 'State', (x_coor + 60), (y_coor + 30), width=100, font_size=font_size, border=2, relief='groove')
        if variant:
            self.__state.set('-1.0')
        else:
            self.__state.set('+1')
        state_option = OptionMenu(master, self.__state, *data)
        state_option.place(x=(x_coor + 60), y=(y_coor + 60), height=25, width=100)
        self.__state.trace("w", self.update)
        if not variant:
            xObs_label = LabelTag(master, 'Chi^2', (x_coor + 165), (y_coor + 30), width=350, font_size=font_size, border=2,
                                   relief='groove')
            xObs_Entry = Entry(master, textvariable=self.__xObs)
            xObs_Entry.config(state=DISABLED)
            xObs_Entry.place(x=(x_coor + 165), y=(y_coor + 60), width=350, height=25)
        else:
            count_label = LabelTag(master, 'Count', (x_coor + 165), (y_coor + 30), width=350, font_size=font_size,
                                  border=2, relief='groove')
            count_Entry = Entry(master, textvariable=self.__count)
            count_Entry.config(state=DISABLED)
            count_Entry.place(x=(x_coor + 165), y=(y_coor + 60), width=350, height=25)
            pass
        p_value_label = LabelTag(master, 'P-Value', (x_coor + 520), (y_coor + 30), width=350, font_size=font_size, border=2,
                               relief='groove')
        p_value_Entry = Entry(master, textvariable=self.__p_value)
        p_value_Entry.config(state=DISABLED)
        p_value_Entry.place(x=(x_coor + 520), y=(y_coor + 60), width=350, height=25)
        conclusion_label = LabelTag(master, 'Result', (x_coor + 875), (y_coor + 30), width=150, font_size=font_size, border=2,
                               relief='groove')
        conclusion_Entry = Entry(master, textvariable=self.__result)
        conclusion_Entry.config(state=DISABLED)
        conclusion_Entry.place(x=(x_coor + 875), y=(y_coor + 60), width=150, height=25)

    def get_check_box_value(self):
        return self.__chb_var.get()

    def set_check_box_value(self, value):
        self.__chb_var.set(value)

    def set_results(self, results):
        self.__results = results
        self.update()

    def update(self, *_):
        match = False
        for result in self.__results:
            if result[0] == self.__state.get():
                if self.__variant:
                    self.__count.set(result[2])
                else:
                    self.__xObs.set(result[2])

                self.__p_value.set(result[3])
                self.__result.set(self.get_result_string(result[4]))
                match = True

        if not match:
            if self.__variant:
                self.__count.set('')
            else:
                self.__xObs.set('')

            self.__p_value.set('')
            self.__result.set('')

    def get_result_string(self, result):
        if result == True:
            return 'Random'
        else:
            return 'Non-Random'

    def reset(self):
        self.__chb_var.set('0')
        if self.__variant:
            self.__state.set('-1.0')
            self.__count.set('')
        else:
            self.__state.set('+1')
            self.__xObs.set('')

        self.__p_value.set('')
        self.__result.set('')

class ScrollLabelFrame(LabelFrame):
    def __init__(self, parent, label):
        super().__init__(master=parent, text=label, padx=5, pady=5)
        self._canvas = Canvas(self, background="#ffffff")
        self.inner_frame = Frame(self._canvas, background="#ffffff")
        self._scroll_bar = Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scroll_bar.set)
        self._scroll_bar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._canvas_window = self._canvas.create_window((4,4), window=self.inner_frame, anchor="nw",            #add view port frame to canvas
                                  tags="self.inner_frame")

        self.inner_frame.bind("<Configure>", self.onFrameConfigure)  # bind an event whenever the size of the viewPort frame changes.
        self._canvas.bind("<Configure>", self.onCanvasConfigure)  # bind an event whenever the size of the viewPort frame changes.

        self.onFrameConfigure(None)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self._canvas.configure(scrollregion=self._canvas.bbox(
            "all"))  # whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self._canvas.itemconfig(self._canvas_window, width=canvas_width)
