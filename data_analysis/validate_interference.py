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

def validateSubjectInterferenceData(input_file, high_low_median, low_low_median, low_high_median):
    input_data_table = pandas.read_csv(input_file, sep='\t')

    RT_column = input_data_table["RT (ms)"]
    repetition_column = input_data_table["repetition"]
    trill_column = input_data_table["trill"]
    epoch_column = input_data_table["epoch"]
    trial_column = input_data_table["trial"]
    trial_type_learning_column = input_data_table["high_low_learning"]
    trial_type_hl_column = input_data_table["triplet_type_hl"]

    smaller_low_low_count = 0
    bigger_low_low_count = 0
    smaller_high_low_count = 0
    bigger_high_low_count = 0
    smaller_low_high_count = 0
    bigger_low_high_count = 0
    for i in range(len(RT_column)):
        # we calculate only with the seven epoch
        if epoch_column[i] != 7:
            continue

        # we ignore the five trials, repetitions and trills
        if trial_column[i] <= 5 or repetition_column[i] == "True" or trill_column[i] == "True":
            continue

        RT = strToFloat(RT_column[i])
        if trial_type_learning_column[i] == 'high':
            if trial_type_hl_column[i] == 'low':
                if RT < high_low_median:
                    smaller_high_low_count += 1
                elif RT > high_low_median:
                    bigger_high_low_count += 1

        elif trial_type_learning_column[i] == 'low':
            if trial_type_hl_column[i] == 'low':
                if RT < low_low_median:
                    smaller_low_low_count += 1
                elif RT > low_low_median:
                    bigger_low_low_count += 1
            elif trial_type_hl_column[i] == 'high':
                if RT < low_high_median:
                    smaller_low_high_count += 1
                elif RT > low_high_median:
                    bigger_low_high_count += 1

    assert(abs(smaller_low_low_count - bigger_low_low_count) <= 1)
    assert(abs(smaller_high_low_count - bigger_high_low_count) <= 1)
    assert(abs(smaller_low_high_count - bigger_low_high_count) <= 1)

def readEpochMedianData(input_file, subject):

    input_data = pandas.read_csv(input_file, sep='\t')

    for index, row in input_data.iterrows():
        if row["subject"] == subject:
            subject_row = row
            break

    high_low_median = strToFloat(subject_row["epoch_7_high_low"])
    low_low_median = strToFloat(subject_row['epoch_7_low_low'])
    low_high_median = strToFloat(subject_row['epoch_7_low_high'])

    return high_low_median, low_low_median, low_high_median

def validateInterferenceData(input_dir, output_file):
    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            subject = int(file.split('_')[1])

            print("Validate interference data for subject: " + str(subject))

            high_low_median, low_low_median, low_high_median = readEpochMedianData(output_file, subject)
            validateSubjectInterferenceData(input_file, high_low_median, low_low_median, low_high_median)
        break
