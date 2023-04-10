# !/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2019-2021>  <Tamás Zolnai>  <zolnaitamas2000@gmail.com>

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
import numpy
from utils import strToFloat, floatToStr

def computeMissingDataRatioImpl(input):
    data_table = pandas.read_csv(input, sep='\t')

    trial_column = data_table["trial"]
    block_column = data_table["block"]
    epoch_column = data_table["epoch"]
    left_gaze_validity = data_table["left_gaze_validity"]
    right_gaze_validity = data_table["right_gaze_validity"]

    epoch_all = {}
    epoch_missing = {}
    for i in range(len(trial_column)):
        if int(trial_column[i]) > 2 and int(block_column[i]) > 0:
            current_epoch = int(epoch_column[i])
            if current_epoch in epoch_all.keys():
                epoch_all[current_epoch] += 1
            else:
                epoch_all[current_epoch] = 1

            if not bool(left_gaze_validity[i]) and not bool(right_gaze_validity[i]):
                if current_epoch in epoch_missing.keys():
                    epoch_missing[current_epoch] += 1
                else:
                    epoch_missing[current_epoch] = 1

    epoch_summary = numpy.zeros(8).tolist()
    for epoch in epoch_all.keys():
        epoch_summary[epoch - 1] = floatToStr((epoch_missing[epoch] / epoch_all[epoch]) * 100.0)

    return epoch_summary

def computeMissingDataRatio(input_dir, output_file):

    missing_data_ratios = []
    epochs_phases = []
    for root, dirs, files in os.walk(input_dir):
        for subject in dirs:
            if subject.startswith('.'):
                continue

            print("Compute missing data ratio for subject(ASRT): " + subject)
            input_file = os.path.join(root, subject, 'subject_' + subject + '__log.txt')

            for i in range(1,9):
                epochs_phases.append("subject_" + subject + "_" + str(i))

            result = computeMissingDataRatioImpl(input_file)

            missing_data_ratios += result
        break

    missing_data = pandas.DataFrame({'epoch' : epochs_phases, 'missing_data_ratio' : missing_data_ratios})
    missing_data.to_csv(output_file, sep='\t', index=False)
