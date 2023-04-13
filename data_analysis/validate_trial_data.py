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
from utils import strToFloat, floatToStr

def calcRTUpperLimits(raw_file_name):
    input_data = pandas.read_csv(raw_file_name, sep='\t',
                                 usecols=['block', 'trial', 'gaze_data_time_stamp'])

    last_trial = 1
    start_time = 0
    RT_data = []
    previous_row = -1
    start_time_set = False

    for index, row in input_data.iterrows():
        if not start_time_set and row['trial'] == 1 and row['block'] == 1:
            start_time = int(row['gaze_data_time_stamp'])
            start_time_set = True

        # we are at the end of the trial (actually at the first row of the next trial)
        if last_trial != row['trial'] or index == len(input_data.index) - 1:
            if isinstance(previous_row, pandas.Series) and str(previous_row['block']) != "0": # validation blocks
                if index == len(input_data.index) - 1:
                    end_time = row['gaze_data_time_stamp']
                else:
                    end_time = previous_row['gaze_data_time_stamp']
                RT_data.append((end_time - start_time) / 1000.0)

                last_trial = row['trial']
                start_time = previous_row['gaze_data_time_stamp']

        previous_row = row

    # 85 trial * 5 block * 8 epoch
    assert(len(RT_data) == 3400)
    return RT_data

def validateRTOutput(trial_file_name, RT_upper_limits):
    trial_data = pandas.read_csv(trial_file_name, sep='\t')

    assert(len(trial_data.index) == len(RT_upper_limits))

    for index, row in trial_data.iterrows():
        actual_RT = strToFloat(row["RT (ms)"])
        assert(actual_RT < (RT_upper_limits[index] - 380.0))

def getAOI(left_gaze_validity, right_gaze_validity, left_gaze_X, left_gaze_Y,
           right_gaze_X, right_gaze_Y):

    if left_gaze_validity and right_gaze_validity:
        X = (left_gaze_X + right_gaze_X) / 2.0
        Y = (left_gaze_Y + right_gaze_Y) / 2.0
    elif left_gaze_validity:
        X = left_gaze_X
        Y = left_gaze_Y
    elif right_gaze_validity:
        X = right_gaze_X
        Y = right_gaze_Y
    else:
        return -1

    if X <= 0.0 and Y >= 0.0:
        return 1
    elif X >= 0.0 and Y >= 0.0:
        return 2
    elif X <= 0.0 and Y <= 0.0:
        return 3
    else:
        return 4

def calcLastAOIs(raw_file_name):
    data_table = pandas.read_csv(raw_file_name, sep='\t',
                                usecols=['block', 'trial', 'trial_phase', 'left_gaze_validity', 'right_gaze_validity',
                                         'left_gaze_data_X_PCMCS', 'left_gaze_data_Y_PCMCS', 'right_gaze_data_X_PCMCS', 'right_gaze_data_Y_PCMCS'])

    anticipation_data = []
    trial_column = data_table["trial"]
    block_column = data_table["block"]
    trial_phase_column = data_table["trial_phase"]
    left_gaze_validity_column = data_table["left_gaze_validity"]
    right_gaze_validity_column = data_table["right_gaze_validity"]
    left_gaze_data_X_column = data_table["left_gaze_data_X_PCMCS"]
    left_gaze_data_Y_column = data_table["left_gaze_data_Y_PCMCS"]
    right_gaze_data_X_column = data_table["right_gaze_data_X_PCMCS"]
    right_gaze_data_Y_column = data_table["right_gaze_data_Y_PCMCS"]

    last_AOI = -1
    last_AOI_found = False
    for i in range(len(trial_column) - 2, -1, -1):
        # we reached the next trial's last data (we compute the previous trial's last visited AOI).
        if i == 0:
            reached_next_trial = False
        else:
            reached_next_trial = trial_column[i] != trial_column[i + 1]
        if reached_next_trial:
            # we don't compute last AOI data for 0 indexed blocks, which are calibration validation blocks.
            if str(block_column[i + 1]) != "0":
                if last_AOI == -1:
                    anticipation_data.append('none')
                else:
                    anticipation_data.append(last_AOI)
            last_AOI = -1
            last_AOI_found = False

        # get AOI during RSI
        if trial_phase_column[i] == 'before_stimulus' and not last_AOI_found:
            current_AOI = getAOI(bool(left_gaze_validity_column[i]), bool(right_gaze_validity_column[i]),
                                 strToFloat(left_gaze_data_X_column[i]), strToFloat(left_gaze_data_Y_column[i]),
                                 strToFloat(right_gaze_data_X_column[i]), strToFloat(right_gaze_data_Y_column[i]))
            if current_AOI != -1:
                last_AOI = current_AOI
                last_AOI_found = True

        # we need to handle the last trial differently at the end of the data file.
        if (i == 0):
            if str(block_column[i + 1]) != "0":
                if last_AOI == -1:
                    anticipation_data.append('none')
                else:
                    anticipation_data.append(last_AOI)
            last_AOI = -1

    anticipation_data = anticipation_data[::-1]
    return anticipation_data

def validateLastAOIs(trial_file_name, last_AOIs):
    trial_data = pandas.read_csv(trial_file_name, sep='\t')


    assert(len(trial_data.index) == len(last_AOIs))

    checked_items = 0
    failed_items = 0
    for index, row in trial_data.iterrows():
        actual_last_AOI = row["last_AOI_before_stimulus"]
        assert(actual_last_AOI == last_AOIs[index])

def validateTrialData(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for subject_file in files:
            subject = subject_file.split('_')[1]

            print("Validate trial level data for subject: " + subject)

            raw_data_path = os.path.join(root, subject_file)
            RT_data_path = os.path.join(output_dir, 'subject_' + subject + '__trial_log.csv')

            RT_upper_limits = calcRTUpperLimits(raw_data_path)
            validateRTOutput(RT_data_path, RT_upper_limits)
            last_AOIs = calcLastAOIs(raw_data_path)
            validateLastAOIs(RT_data_path, last_AOIs)

        break