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
import pandas
from utils import strToFloat, floatToStr

def validateMedianData(input_file, epochs_data):
    input_data_table = pandas.read_csv(input_file, sep='\t')

    RT_column = input_data_table["RT (ms)"]
    repetition_column = input_data_table["repetition"]
    trill_column = input_data_table["trill"]
    epoch_column = input_data_table["epoch"]
    trial_column = input_data_table["trial"]
    trial_type_column = input_data_table["high_low_learning"]

    current_epoch = epoch_column[0]
    current_epoch_median = epochs_data[current_epoch]
    smaller_low_count = 0
    bigger_low_count = 0
    smaller_high_count = 0
    bigger_high_count = 0
    for i in range(len(RT_column) + 1):
        # end of the epoch -> calc maximum / minimum for low and high trials
        if i == len(RT_column) or current_epoch != epoch_column[i]:
            assert(abs(smaller_high_count - bigger_high_count) <= 1)
            assert(abs(smaller_low_count - bigger_low_count) <= 1)

            smaller_low_count = 0
            bigger_low_count = 0
            smaller_high_count = 0
            bigger_high_count = 0

            if i == len(RT_column):
                break

            current_epoch = epoch_column[i]
            current_epoch_median = epochs_data[current_epoch]

        # we ignore the five trials, repetitions and trills
        if trial_column[i] <= 5 or repetition_column[i] == "True" or trill_column[i] == "True":
            continue

        RT = strToFloat(RT_column[i])
        if trial_type_column[i] == 'high':
            if RT < current_epoch_median[0]:
                smaller_high_count += 1
            elif RT > current_epoch_median[0]:
                bigger_high_count += 1

        elif trial_type_column[i] == 'low':
            if RT < current_epoch_median[1]:
                smaller_low_count += 1
            elif RT > current_epoch_median[1]:
                bigger_low_count += 1

def readEpochMedianData(input_file, subject):

    input_data = pandas.read_csv(input_file, sep='\t')

    for index, row in input_data.iterrows():
        if row["subject"] == subject:
            subject_row = row
            break

    epochs_data = {}
    for i in range(0,8):
        high_column_label = "epoch_" + str(i + 1) + "_high";
        high_value = strToFloat(subject_row[high_column_label])
        low_column_label = "epoch_" + str(i + 1) + "_low";
        low_value = strToFloat(subject_row[low_column_label])

        epochs_data[i + 1] = [high_value, low_value]
    
    assert(len(epochs_data) == 8)
    return epochs_data

def validateLearning(input_dir, output_file):
    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            subject = int(file.split('_')[1])

            print("Validate statistical learning data for subject: " + str(subject))

            epochs_data = readEpochMedianData(output_file, subject)
            validateMedianData(input_file, epochs_data)
        break
