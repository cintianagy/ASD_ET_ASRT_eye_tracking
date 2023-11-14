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
import math
from utils import strToFloat, floatToStr, calcRMS, convertToAngle

# Add the local path to the main script so we can import some class from it.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from asrt import ExperimentSettings

def calcDistancesForFixation(j, k, data_table):

    all_eye_to_eye_distances = []
    left_gaze_validity = data_table["left_gaze_validity"]
    right_gaze_validity = data_table["right_gaze_validity"]
    left_gaze_data_X_PCMCS = data_table["left_gaze_data_X_PCMCS"]
    left_gaze_data_Y_PCMCS = data_table["left_gaze_data_Y_PCMCS"]
    right_gaze_data_X_PCMCS = data_table["right_gaze_data_X_PCMCS"]
    right_gaze_data_Y_PCMCS = data_table["right_gaze_data_Y_PCMCS"]

    for i in range(j, k + 1):
        eye_to_eye_distance = -1.0
        if bool(left_gaze_validity[i]) and bool(right_gaze_validity[i]):
            left_X = strToFloat(left_gaze_data_X_PCMCS[i])
            left_Y = strToFloat(left_gaze_data_Y_PCMCS[i])
            right_X = strToFloat(right_gaze_data_X_PCMCS[i])
            right_Y = strToFloat(right_gaze_data_Y_PCMCS[i])
            X_distance = abs(left_X - right_X)
            Y_distance = abs(left_Y - right_Y)
            eye_to_eye_distance = math.sqrt(pow(X_distance, 2) + pow(Y_distance, 2))

        if eye_to_eye_distance > 0.0:
            all_eye_to_eye_distances.append(convertToAngle(eye_to_eye_distance))

    return all_eye_to_eye_distances

def computeRMSEyeToEyeImpl(input, preparatory_trial_number, fixation_duration_threshold):
    data_table = pandas.read_csv(input, sep='\t',
                                 usecols=['block', 'trial', 'epoch', 'left_gaze_validity', 'right_gaze_validity',
                                          'left_gaze_data_X_PCMCS', 'left_gaze_data_Y_PCMCS', 'right_gaze_data_X_PCMCS', 'right_gaze_data_Y_PCMCS'])

    trial_column = data_table["trial"]
    block_column = data_table["block"]
    epoch_column = data_table["epoch"]

    epoch_rmss= {}
    for i in range(len(trial_column) - 1):
        # We ignore preparatory trials.
        if int(trial_column[i]) <= preparatory_trial_number:
            continue

        # We ignore calibration validation blocks.
        if str(block_column[i]) == '0':
            continue

        # end of trial -> check samples of the last fixation (duration threshold shows the number of samples)
        if trial_column[i] != trial_column[i + 1] or i + 1 == len(trial_column) - 1:
            # Distance values for the fixation samples.
            if i + 1 == len(trial_column) - 1:
                all_distances = calcDistancesForFixation(i - fixation_duration_threshold + 2, i + 1, data_table)
            else:
                all_distances = calcDistancesForFixation(i - fixation_duration_threshold + 1, i, data_table)

            if len(all_distances) > 0:
                current_epoch = int(epoch_column[i])

                # Calc RMS of all collected distances.
                new_RMS = calcRMS(all_distances)
                if current_epoch in epoch_rmss.keys():
                    epoch_rmss[current_epoch].append(new_RMS)
                else:
                    epoch_rmss[current_epoch] = [new_RMS]

    # We compute median RMS(E2E) for all epochs.
    epoch_summary = numpy.zeros(8).tolist()
    for epoch in epoch_rmss.keys():
        epoch_summary[epoch - 1] = floatToStr(numpy.median(epoch_rmss[epoch]))

    if len(epoch_summary) != 8:
        raise Exception("Error: The input data should contain exactly 8 epochs for this data analysis.")

    return epoch_summary

def computeRMSEyeToEye(input_dir, output_file):
    parent_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    settings = ExperimentSettings(os.path.join(parent_folder, 'settings', 'settings'), "", True)
    try:
            settings.read_from_file()
    except:
        raise Exception('Error: Could not read settings file to get the number of preparatory trials.')

    median_rms = []
    subject_epochs = []
    for root, dirs, files in os.walk(input_dir):
        for subject_file in files:
            subject = subject_file.split('_')[1]

            print("Compute RMS(E2E) for subject:  " + subject)
            input_file = os.path.join(root, subject_file)

            for i in range(1,9):
                subject_epochs.append("subject_" + subject + "_" + str(i))

            result = computeRMSEyeToEyeImpl(input_file, settings.blockprepN, settings.stim_fixation_threshold)
            median_rms += result
        break

    RMS_E2E_data = pandas.DataFrame({'epoch' : subject_epochs, 'RMS(E2E)_median' : median_rms})
    RMS_E2E_data.to_csv(output_file, sep='\t', index=False)