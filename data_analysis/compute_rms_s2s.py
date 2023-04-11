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

# Add the local path to the main script and external scripts so we can import them.
sys.path = [".."] + sys.path
from asrt import ExperimentSettings

def getEyePos(data_table, i):
    left_gaze_validity = data_table["left_gaze_validity"][i]
    right_gaze_validity = data_table["right_gaze_validity"][i]
    left_gaze_data_X_PCMCS = data_table["left_gaze_data_X_PCMCS"][i]
    left_gaze_data_Y_PCMCS = data_table["left_gaze_data_Y_PCMCS"][i]
    right_gaze_data_X_PCMCS = data_table["right_gaze_data_X_PCMCS"][i]
    right_gaze_data_Y_PCMCS = data_table["right_gaze_data_Y_PCMCS"][i]

    # Calculate current eye pos based on the valid eye positions (hybrid computation).
    if bool(left_gaze_validity) and bool(right_gaze_validity):
        pos_X = (strToFloat(left_gaze_data_X_PCMCS) + strToFloat(right_gaze_data_X_PCMCS)) / 2.0
        pos_Y = (strToFloat(left_gaze_data_Y_PCMCS) + strToFloat(right_gaze_data_Y_PCMCS)) / 2.0
    elif bool(left_gaze_validity):
        pos_X = strToFloat(left_gaze_data_X_PCMCS)
        pos_Y = strToFloat(left_gaze_data_Y_PCMCS)
    elif bool(right_gaze_validity):
        pos_X = strToFloat(right_gaze_data_X_PCMCS)
        pos_Y = strToFloat(right_gaze_data_Y_PCMCS)
    else: # No valid data
        return 'none'

    return (pos_X, pos_Y)

def calcDistancesForFixation(j, k, data_table):

    all_distances = []
    # Check all samples with an index within j and k.
    for i in range(j, k):
        prev_pos = getEyePos(data_table, i)
        next_pos = getEyePos(data_table, i + 1)
        if prev_pos != 'none' and next_pos != 'none':
            # Distance in cm, based on psychopy coordinate system.
            distance = math.sqrt(pow(prev_pos[0] - next_pos[0], 2) + pow(prev_pos[1] - next_pos[1], 2))
            # Convert the distance in cm to a visual angle. It's more common to use visual angle values.
            all_distances.append(convertToAngle(distance))
    
    return all_distances

def computeRMSSampleToSampleImpl(input, preparatory_trial_number, fixation_duration_threshold):
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
        if trial_column[i] != trial_column[i + 1]:
            # Distance values for the fixation samples.
            all_distances = calcDistancesForFixation(i - fixation_duration_threshold + 1, i, data_table)
            if len(all_distances) > 0:
                current_epoch = int(epoch_column[i])

                # Calc RMS of all collected distances.
                new_RMS = calcRMS(all_distances)
                if current_epoch in epoch_rmss.keys():
                    epoch_rmss[current_epoch].append(new_RMS)
                else:
                    epoch_rmss[current_epoch] = [new_RMS]

    # We compute median RMS(S2S) for all epochs.
    epoch_summary = numpy.zeros(8).tolist()
    for epoch in epoch_rmss.keys():
        epoch_summary[epoch - 1] = floatToStr(numpy.median(epoch_rmss[epoch]))

    if len(epoch_summary) != 8:
        print("Error: The input data should contain exactly 8 epochs for this data analysis.")

    return epoch_summary

def computeRMSSampleToSample(input_dir, output_file):
    settings = ExperimentSettings(os.path.join('..', 'settings', 'settings'), "", True)
    try:
            settings.read_from_file()
    except:
        print('Error: Could not read settings file to get the number of preparatory trials.')
        return

    median_rmss = []
    subject_epochs = []
    for root, dirs, files in os.walk(input_dir):
        for subject_file in files:
            subject = subject_file.split('_')[1]

            print("Compute RMS(S2S) for subject: " + subject)
            input_file = os.path.join(root, subject_file)

            for i in range(1,9):
                subject_epochs.append("subject_" + subject + "_" + str(i))

            RMS = computeRMSSampleToSampleImpl(input_file, settings.blockprepN, settings.stim_fixation_threshold)
            median_rmss += RMS
        break

    RMS_S2S_data = pandas.DataFrame({'epoch' : subject_epochs, 'RMS(S2S)_median' : median_rmss})
    RMS_S2S_data.to_csv(output_file, sep='\t', index=False)