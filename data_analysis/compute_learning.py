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

def calcEpochMedianRTsLearning(input_file, preparatory_trial_number):
    input_data_table = pandas.read_csv(input_file, sep='\t')

    RT_column = input_data_table["RT (ms)"]
    repetition_column = input_data_table["repetition"]
    trill_column = input_data_table["trill"]
    epoch_column = input_data_table["epoch"]
    trial_column = input_data_table["trial"]
    trial_type_column = input_data_table["high_low_learning"]

    previous_epoch = epoch_column[0]
    high_RT_list = []
    low_RT_list = []
    high_median_array = []
    low_median_array = []
    for i in range(len(RT_column) + 1):
        # End of the epoch -> calc median for low and high trials of the previous epoch.
        if i == len(RT_column) or previous_epoch != epoch_column[i]:
            assert(len(high_RT_list) > 0)
            assert(len(low_RT_list) > 0)
            high_median = numpy.median(high_RT_list)
            low_median = numpy.median(low_RT_list)

            high_median_array.append(floatToStr(high_median))
            high_RT_list = []
            low_median_array.append(floatToStr(low_median))
            low_RT_list = []

            # We are at the end of the data (actually we run out of the data range).
            # After we calculated the median RTs for the last epoch, we exit the loop.
            if i == len(RT_column):
                break

            previous_epoch = epoch_column[i]

        # we ignore the preparatory trials, repetitions and trills
        if trial_column[i] <= preparatory_trial_number or repetition_column[i] == "True" or trill_column[i] == "True":
            continue

        assert(repetition_column[i] == "False")
        assert(trill_column[i] == "False")

        # We collect the high and low reaction times.
        if trial_type_column[i] == 'high':
            high_RT_list.append(strToFloat(RT_column[i]))
        elif trial_type_column[i] == 'low':
            low_RT_list.append(strToFloat(RT_column[i]))

    if len(low_median_array) != 8 or len(high_median_array) != 8:
        raise Exception("Error: The input data should contain exactly 8 epochs for this data analysis.")
    return low_median_array, high_median_array

def computeStatisticalLearning(input_dir, output_file):
    learning_data = pandas.DataFrame(columns=['subject', 'epoch_1_low', 'epoch_2_low', 'epoch_3_low', 'epoch_4_low',
                                              'epoch_5_low', 'epoch_6_low', 'epoch_7_low', 'epoch_8_low',
                                              'epoch_1_high', 'epoch_2_high', 'epoch_3_high', 'epoch_4_high',
                                              'epoch_5_high', 'epoch_6_high', 'epoch_7_high', 'epoch_8_high'])

    parent_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    settings = ExperimentSettings(os.path.join(parent_folder, 'settings', 'settings'), "", True)
    try:
            settings.read_from_file()
    except:
        raise Exception('Error: Could not read settings file to get the number of preparatory trials.')

    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            subject = file.split('_')[1]

            print("Compute statistical learning for subject: " + subject)

            low_medians, high_medians = calcEpochMedianRTsLearning(input_file, settings.blockprepN)
            learning_data.loc[len(learning_data)] = [subject] + low_medians + high_medians
        break

    learning_data.to_csv(output_file, sep='\t', index=False)
