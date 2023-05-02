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

def computeDistanceImpl(input, preparatory_trial_number):
    data_table = pandas.read_csv(input, sep='\t',
                                 usecols=['block', 'trial', 'epoch', 'left_gaze_validity', 'right_gaze_validity',
                                          'left_eye_distance', 'right_eye_distance'])

    trial_column = data_table["trial"]
    epoch_column = data_table["epoch"]
    left_gaze_validity = data_table["left_gaze_validity"]
    right_gaze_validity = data_table["right_gaze_validity"]
    left_eye_distance = data_table["left_eye_distance"]
    right_eye_distance = data_table["right_eye_distance"]
    block_column = data_table["block"]

    epoch_distances = {}
    for i in range(len(trial_column)):
        # We ignore preparatory trials.
        if int(trial_column[i]) <= preparatory_trial_number:
            continue

        # We ignore calibration validation blocks.
        if str(block_column[i]) == '0':
            continue

        # Use the distance from the valid eye data. If there is two, we use average.
        distance_mm = -1.0
        if bool(left_gaze_validity[i]) and bool(right_gaze_validity[i]):
            distance_mm = (strToFloat(left_eye_distance[i]) + strToFloat(right_eye_distance[i])) / 2.0
        elif bool(left_gaze_validity[i]):
            distance_mm = strToFloat(left_eye_distance[i])
        elif bool(right_gaze_validity[i]):
            distance_mm = strToFloat(right_eye_distance[i])

        # Collect all distances of all epochs,
        if distance_mm > 0.0:
            distance_cm = distance_mm / 10.0
            current_epoch = int(epoch_column[i])
            if current_epoch in epoch_distances.keys():
                epoch_distances[current_epoch].append(distance_cm)
            else:
                epoch_distances[current_epoch] = [distance_cm]

    # Compute median distance of subject eyes for all epochs.
    epoch_summary = numpy.zeros(8).tolist()
    for epoch in epoch_distances.keys():
        epoch_summary[epoch - 1] = floatToStr(numpy.median(epoch_distances[epoch]))

    if len(epoch_summary) != 8:
        print("Error: The input data should contain exactly 8 epochs for this data analysis.")

    return epoch_summary

def computeDistance(input_dir, output_file):
    parent_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    settings = ExperimentSettings(os.path.join(parent_folder, 'settings', 'settings'), "", True)
    try:
            settings.read_from_file()
    except:
        print('Error: Could not read settings file to get the number of preparatory trials.')
        return

    median_distances = []
    subject_epochs = []
    for root, dirs, files in os.walk(input_dir):
        for subject_file in files:
            subject = subject_file.split('_')[1]

            print("Compute eye-screen distance data for subject: " + subject)
            input_file = os.path.join(root, subject_file)

            for i in range(1,9):
                subject_epochs.append("subject_" + subject + "_" + str(i))

            epoch_medians = computeDistanceImpl(input_file, settings.blockprepN)
            median_distances += epoch_medians
        break

    distance_data = pandas.DataFrame({'epoch' : subject_epochs, 'median_distance_cm' : median_distances})
    distance_data.to_csv(output_file, sep='\t', index=False)