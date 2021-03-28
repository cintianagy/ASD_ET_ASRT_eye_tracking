# !/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2019>  <Tamás Zolnai>  <zolnaitamas2000@gmail.com>

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
import math

def generateOutput(raw_file_name, new_file_name, RT_data):
    # use the input data headers
    input_data = pandas.read_csv(raw_file_name, sep='\t')
    output_data = pandas.DataFrame(columns=input_data.columns)

    # remove some useless fields
    output_data = output_data.drop(columns=['RSI_time', 'trial_phase', 'left_gaze_data_X_ADCS', 'left_gaze_data_Y_ADCS',
                      'right_gaze_data_X_ADCS', 'right_gaze_data_Y_ADCS', 'left_gaze_data_X_PCMCS',
                      'left_gaze_data_Y_PCMCS', 'right_gaze_data_X_PCMCS', 'right_gaze_data_Y_PCMCS',
                      'left_eye_distance', 'right_eye_distance', 'left_gaze_validity', 'right_gaze_validity',
                      'left_pupil_diameter', 'right_pupil_diameter', 'left_pupil_validity', 'right_pupil_validity',
                      'gaze_data_time_stamp', 'stimulus_1_position_X_PCMCS', 'stimulus_1_position_Y_PCMCS',
                      'stimulus_2_position_X_PCMCS', 'stimulus_2_position_Y_PCMCS', 'stimulus_3_position_X_PCMCS',
                      'stimulus_3_position_Y_PCMCS', 'stimulus_4_position_X_PCMCS', 'stimulus_4_position_Y_PCMCS', 'quit_log', 'Unnamed: 48'])

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

    output_data.to_csv(new_file_name, sep='\t', index=False)

def calcRTColumn(raw_file_name):
    input_data = pandas.read_csv(raw_file_name, sep='\t')

    last_trial = "1"
    start_time = 0
    end_time = 0
    start_time_found = False
    end_time_found = False
    RT_data = []
    previous_row = -1

    for index, row in input_data.iterrows():
        # we are at the end of the trial (actually at the first row of the next trial)
        if last_trial != str(row['trial']) or index == len(input_data.index) - 1:
            # we ignore 0 indexed blocks, which are calibration validation blocks.
            if isinstance(previous_row, pandas.Series) and str(previous_row['block']) != "0":
                # We calculate the elapsed time during the stimulus was on the screen.
                if start_time_found and end_time_found:
                    RT_data.append(str((end_time - start_time) / 1000.0).replace(".", ","))
                # if there is not endtime, then it means the software was fast enough to step
                # on to the next trial instantly after the stimulus was hidden.
                elif start_time_found:
                    end_time = int(previous_row['gaze_data_time_stamp'])
                    RT_data.append(str((end_time - start_time) / 1000.0).replace(".", ","))
                else:
                    RT_data.append("0")

            last_trial = str(row['trial'])
            start_time_found = False
            end_time_found = False

        # stimulus appears on the screen -> start time
        if row['trial_phase'] == "stimulus_on_screen" and not start_time_found:
            start_time = int(row['gaze_data_time_stamp'])
            start_time_found = True

        # stimulus disappear from the screen -> end time
        if row['trial_phase']== "after_reaction" and not end_time_found:
            end_time = int(previous_row['gaze_data_time_stamp'])
            end_time_found = True

        previous_row = row

    return RT_data

def computeTrialData(raw_file_name, new_file_name):
    RT_data = calcRTColumn(raw_file_name)
    generateOutput(raw_file_name, new_file_name, RT_data)