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

# Add the local path to the main script and external scripts so we can import them.
sys.path = [".."] + sys.path
from asrt import ExperimentSettings

def computeMissingDataRatioImpl(input, preparatory_trial_number):
    data_table = pandas.read_csv(input, sep='\t',
                                 usecols=['block', 'trial', 'epoch', 'left_gaze_validity', 'right_gaze_validity'])

    trial_column = data_table["trial"]
    block_column = data_table["block"]
    epoch_column = data_table["epoch"]
    left_gaze_validity = data_table["left_gaze_validity"]
    right_gaze_validity = data_table["right_gaze_validity"]

    epoch_all_data = {}
    epoch_missing_data = {}
    for i in range(len(trial_column)):
        # We ignore preparatory trials.
        if int(trial_column[i]) <= preparatory_trial_number:
            continue

        # We ignore calibration validation blocks.
        if str(block_column[i]) == '0':
            continue

        current_epoch = int(epoch_column[i])

        # We count all eye-tracking samples for the current epoch.
        if current_epoch in epoch_all_data.keys():
            epoch_all_data[current_epoch] += 1.0
        else:
            epoch_all_data[current_epoch] = 1.0

        # We count all missing eye-tracking data for the current epoch.
        if not bool(left_gaze_validity[i]) and not bool(right_gaze_validity[i]):
            if current_epoch in epoch_missing_data.keys():
                epoch_missing_data[current_epoch] += 1.0
            else:
                epoch_missing_data[current_epoch] = 1.0

    # We compute missing data ratio for all epochs.
    epoch_summary = numpy.zeros(8).tolist()
    for epoch in epoch_all_data.keys():
        epoch_summary[epoch - 1] = floatToStr((epoch_missing_data[epoch] / epoch_all_data[epoch]) * 100.0)

    if len(epoch_summary) != 8:
        print("Error: The input data should contain exactly 8 epochs for this data analysis.")

    return epoch_summary

def computeMissingDataRatio(input_dir, output_file):
    settings = ExperimentSettings(os.path.join('..', 'settings', 'settings'), "", True)
    try:
            settings.read_from_file()
    except:
        print('Error: Could not read settings file to get the number of preparatory trials.')
        return

    missing_data_ratios = []
    subject_epochs = []
    for root, dirs, files in os.walk(input_dir):
        for subject_file in files:
            subject = int(subject_file.split('_')[1])

            print("Compute missing data ratio for subject: " + str(subject))
            input_file = os.path.join(root, subject_file)

            for i in range(1,9):
                subject_epochs.append("subject_" + str(subject) + "_" + str(i))

            result = computeMissingDataRatioImpl(input_file, settings.blockprepN)

            missing_data_ratios += result
        break

    missing_data = pandas.DataFrame({'epoch' : subject_epochs, 'missing_data_ratio' : missing_data_ratios})
    missing_data.to_csv(output_file, sep='\t', index=False)
