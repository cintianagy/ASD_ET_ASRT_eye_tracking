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

def generateOutput(raw_file_name, new_file_name, RT_data, last_AOI_data):
    # use a subset of the input data headers
    input_data = pandas.read_csv(raw_file_name, sep='\t',
                                usecols=['computer_name', 'monitor_width_pixel', 'monitor_height_pixel', 'subject_group',
                                          'subject_number', 'subject_sex', 'subject_age', 'asrt_type', 'PCode', 'session',
                                          'epoch', 'block', 'trial', 'frame_rate', 'frame_time', 'frame_sd', 'stimulus_color',
                                          'trial_type_pr', 'triplet_type_hl', 'stimulus'],
                                dtype={'PCode': 'str' })
    output_data = pandas.DataFrame(columns=input_data.columns)

    output_index = 0
    last_trial = "0"
    for index, row in input_data.iterrows():
        # we ignore 0 indexed blocks, which are calibration validation blocks.
        if str(row['block']) == "0":
            continue

        # insert one row of each trial data
        if row['trial'] != last_trial:
            last_trial = row['trial']
            output_data.loc[output_index] = row
            output_index += 1

    # reaction time of the trial
    assert(len(output_data.index) == len(RT_data))
    output_data['RT (ms)'] = RT_data

    # Last AOI during RSI (useful for anticipation data calculation)
    assert(len(output_data.index) == len(last_AOI_data))
    output_data['last_AOI_before_stimulus'] = last_AOI_data

    output_data.to_csv(new_file_name, sep='\t', index=False)

def calcRTTrial(start_time_found, start_time, end_time_found, end_time, last_time_stamp_of_trial):
    # We calculate the elapsed time during the stimulus was on the screen.
    if start_time_found and end_time_found:
        RT_ms = (end_time - start_time) / 1000.0
        return floatToStr(RT_ms)

    # If there is no end time, then it means the software was fast enough to step
    # on to the next trial instantly after the stimulus was hidden. In this case
    # we use the last row of the given trial.
    elif start_time_found:
        end_time = last_time_stamp_of_trial
        RT_ms = (end_time - start_time) / 1000.0
        return floatToStr(RT_ms)

    # The stimulus disappeared instantly.
    else:
        return "0"

def calcRTColumn(raw_file_name):
    data_table = pandas.read_csv(raw_file_name, sep='\t',
                                usecols=['block', 'trial', 'trial_phase', 'gaze_data_time_stamp'])

    RT_data = []
    trial_column = data_table["trial"]
    block_column = data_table["block"]
    trial_phase_column = data_table["trial_phase"]
    time_stamp_column = data_table["gaze_data_time_stamp"]

    start_time = 0
    end_time = 0
    start_time_found = False
    end_time_found = False

    for i in range(len(trial_column)):

        # we reached the next trial's first data (we compute the previous trial's reaction time).
        if i == 0:
            reached_next_trial = False
        else:
            reached_next_trial = trial_column[i] != trial_column[i - 1]
        if reached_next_trial:
            # we don't compute RT for 0 indexed blocks, which are calibration validation blocks.
            if str(block_column[i - 1]) != "0":
                RT_data.append(calcRTTrial(start_time_found, start_time, end_time_found, end_time, int(time_stamp_column[i - 1])))

            start_time_found = False
            end_time_found = False

        # stimulus appears on the screen -> start time
        if trial_phase_column[i] == "stimulus_on_screen" and not start_time_found:
            start_time = int(time_stamp_column[i])
            start_time_found = True

        # stimulus disappear from the screen -> end time
        if trial_phase_column[i] == "after_reaction" and not end_time_found:
            end_time = int(time_stamp_column[i - 1])
            end_time_found = True

        # we need to handle the last trial differently at the end of the data file.
        reached_end_of_file = (i == len(trial_column) - 1)
        if reached_end_of_file:
            # we don't compute RT for 0 indexed blocks, which are calibration validation blocks.
            if str(block_column[i - 1]) != "0":
                RT_data.append(calcRTTrial(start_time_found, start_time, end_time_found, end_time, int(time_stamp_column[i])))

    return RT_data

def getAOI(left_gaze_validity, right_gaze_validity, left_gaze_X, left_gaze_Y, right_gaze_X, right_gaze_Y):
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

    if X <= 0.5 and Y <= 0.5:
        return 1
    elif X >= 0.5 and Y <= 0.5:
        return 2
    elif X <= 0.5 and Y >= 0.5:
        return 3
    else:
        return 4

def calcLastAOIColumn(raw_file_name):
    data_table = pandas.read_csv(raw_file_name, sep='\t',
                                usecols=['block', 'trial', 'trial_phase', 'left_gaze_validity', 'right_gaze_validity',
                                         'left_gaze_data_X_ADCS', 'left_gaze_data_Y_ADCS', 'right_gaze_data_X_ADCS', 'right_gaze_data_Y_ADCS'])

    anticipation_data = []
    trial_column = data_table["trial"]
    block_column = data_table["block"]
    trial_phase_column = data_table["trial_phase"]
    left_gaze_validity_column = data_table["left_gaze_validity"]
    right_gaze_validity_column = data_table["right_gaze_validity"]
    left_gaze_data_X_column = data_table["left_gaze_data_X_ADCS"]
    left_gaze_data_Y_column = data_table["left_gaze_data_Y_ADCS"]
    right_gaze_data_X_column = data_table["right_gaze_data_X_ADCS"]
    right_gaze_data_Y_column = data_table["right_gaze_data_Y_ADCS"]

    last_AOI = -1
    for i in range(len(trial_column)):
        # we reached the next trial's first data (we compute the previous trial's last visited AOI).
        if i == 0:
            reached_next_trial = False
        else:
            reached_next_trial = trial_column[i] != trial_column[i - 1]
        if reached_next_trial:
            # we don't compute last AOI data for 0 indexed blocks, which are calibration validation blocks.
            if str(block_column[i - 1]) != "0":
                if last_AOI == -1:
                    anticipation_data.append('none')
                else:
                    anticipation_data.append(last_AOI)
            last_AOI = -1

        # get AOI during RSI
        if trial_phase_column[i] == 'before_stimulus':
            current_AOI = getAOI(bool(left_gaze_validity_column[i]), bool(right_gaze_validity_column[i]),
                                 strToFloat(left_gaze_data_X_column[i]), strToFloat(left_gaze_data_Y_column[i]),
                                 strToFloat(right_gaze_data_X_column[i]), strToFloat(right_gaze_data_Y_column[i]))
            if current_AOI != -1:
                last_AOI = current_AOI

        # we need to handle the last trial differently at the end of the data file.
        reached_end_of_file = (i == len(trial_column) - 1)
        if reached_end_of_file:
            # we don't compute last AOI data for 0 indexed blocks, which are calibration validation blocks.
            if str(block_column[i - 1]) != "0":
                if last_AOI == -1:
                    anticipation_data.append('none')
                else:
                    anticipation_data.append(last_AOI)
                last_AOI = -1

    return anticipation_data

def computeTrialLevelData(input_dir, output_dir):

    for root, dirs, files in os.walk(input_dir):
        for subject_file in files:
            subject = subject_file.split('_')[1]

            print("Compute trial level data for subject: " + subject)

            raw_data_path = os.path.join(root, subject_file)
            RT_data_path = os.path.join(output_dir, 'subject_' + subject + '__trial_log.csv')
            RT_data = calcRTColumn(raw_data_path)
            last_AOI_data = calcLastAOIColumn(raw_data_path)
            generateOutput(raw_data_path, RT_data_path, RT_data, last_AOI_data)

        break
