# !/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2019-2023>  <Tamás Zolnai>  <zolnaitamas2000@gmail.com>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import pandas
import numpy
from utils import strToFloat, floatToStr

# Add the local path to the main script so we can import some class from it.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from asrt import ExperimentSettings

def computeInterferenceOneSubject(input_file, preparatory_trial_number):
    input_data_table = pandas.read_csv(input_file, sep='\t')

    RT_column = input_data_table["RT (ms)"]
    repetition_column = input_data_table["repetition"]
    trill_column = input_data_table["trill"]
    epoch_column = input_data_table["epoch"]
    block_column = input_data_table["block"]
    trial_column = input_data_table["trial"]
    trial_type_column = input_data_table["high_low_learning"]
    trial_type_interference_column = input_data_table["triplet_type_hl"]

    high_low_list = []
    low_low_list = []
    low_high_list = []
    for i in range(len(RT_column)):

        # we ignore the preparatory trials, repetitions and trills
        if trial_column[i] <= preparatory_trial_number or repetition_column[i] == "True" or trill_column[i] == "True":
            continue

        assert(repetition_column[i] == "False")
        assert(trill_column[i] == "False")

        # we calculate only with the sevens epoch (interference epoch).
        if epoch_column[i] == 7:
            if trial_type_column[i] == 'high' and trial_type_interference_column[i] == 'low':
                high_low_list.append(strToFloat(RT_column[i]))
            elif trial_type_column[i] == 'low' and trial_type_interference_column[i] == 'low':
                low_low_list.append(strToFloat(RT_column[i]))
            elif trial_type_column[i] == 'low' and trial_type_interference_column[i] == 'high':
                low_high_list.append(strToFloat(RT_column[i]))

    return numpy.median(high_low_list), numpy.median(low_low_list), numpy.median(low_high_list)

def computeInterferenceData(input_dir, output_file):
    learning_data = pandas.DataFrame(columns=['subject', 'epoch_7_high_low', 'epoch_7_low_low', 'epoch_7_low_high'])

    parent_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    settings = ExperimentSettings(os.path.join(parent_folder, 'settings', 'settings'), "", True)
    try:
            settings.read_from_file()
    except:
        print('Error: Could not read settings file to get the number of preparatory trials.')
        return

    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            subject = file.split('_')[1]

            print("Compute interference measures for subject: " + subject)

            high_low_median, low_low_median, low_high_median = computeInterferenceOneSubject(input_file, settings.blockprepN)
            learning_data.loc[len(learning_data)] = [subject, floatToStr(high_low_median), floatToStr(low_low_median), floatToStr(low_high_median)]
        break

    learning_data.to_csv(output_file, sep='\t', index=False)
