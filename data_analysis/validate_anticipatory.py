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
import numpy
from utils import strToFloat, floatToStr

def computeAnticipationDataForOneSubject(input_file):
    input_data_table = pandas.read_csv(input_file, sep='\t')

    anticipation_column = input_data_table["has_anticipation"]
    learnt_anticipation_column = input_data_table["has_learnt_anticipation"]
    epoch_column = input_data_table["epoch"]
    trial_column = input_data_table["trial"]
    repetition_column = input_data_table["repetition"]
    trill_column = input_data_table["trill"]

    false_anticipation_ratios = []
    all_anticipation = 0.0
    false_anticipation = 0.0
    current_epoch = epoch_column[0]

    for i in range(len(anticipation_column) + 1):
        # end of the epoch -> calc summary data
        if i == len(anticipation_column) or current_epoch != epoch_column[i]:
            assert(false_anticipation <= all_anticipation)
            false_ratio = false_anticipation / all_anticipation * 100.0
            false_anticipation_ratios.append(false_ratio)
            all_anticipation = 0.0
            false_anticipation = 0.0

        if i == len(anticipation_column):
            break

        current_epoch = epoch_column[i]

        if trial_column[i] <= 5 or repetition_column[i] == "True" or trill_column[i] == "True":
            continue

        if str(anticipation_column[i]) == 'True':
            all_anticipation += 1

        if str(anticipation_column[i]) == 'True' and str(learnt_anticipation_column[i]) == 'False':
            false_anticipation += 1

    return false_anticipation_ratios

def checkAnticipationData(output_file, subject, false_anticipation_ratios):
    input_data = pandas.read_csv(output_file, sep='\t')

    for index, row in input_data.iterrows():
        if str(row["subject"]) == subject:
            subject_row = row
            break

    learnt_anticipation_ratios = []
    for i in range(0,8):
        learnt_anticipation_ratio_label = "epoch_" + str(i + 1) + "_learnt_anticip_ratio";
        learnt_anticipation_ratios += [strToFloat(subject_row[learnt_anticipation_ratio_label])]

    assert(len(learnt_anticipation_ratios) == len(false_anticipation_ratios))
    for i in range(len(learnt_anticipation_ratios)):
        assert(abs(learnt_anticipation_ratios[i] + false_anticipation_ratios[i] - 100.0) < 0.00000001)

def validateAnticipatoryData(input_dir, output_file):
    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            subject = file.split('_')[1]

            print("Validate anticipatory data for subject: " + subject)

            false_anticipation_ratios = computeAnticipationDataForOneSubject(input_file)
            checkAnticipationData(output_file, subject, false_anticipation_ratios)
        break
