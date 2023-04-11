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

import sys
import os
import pandas
from utils import strToFloat, floatToStr

# Add the local path to the main script and external scripts so we can import them.
sys.path = [".."] + sys.path
from asrt import ExperimentSettings

def computeAnticipationDataForOneSubject(input_file, preparatory_trial_number):
    input_data_table = pandas.read_csv(input_file, sep='\t')

    anticipation_column = input_data_table["has_anticipation"]
    correct_anticipation_column = input_data_table["has_learnt_anticipation"]
    epoch_column = input_data_table["epoch"]
    repetition_column = input_data_table["repetition"]
    trill_column = input_data_table["trill"]
    trial_column = input_data_table["trial"]

    learnt_anticipation_ratios = []
    all_anticipation = 0.0
    learnt_anticipation = 0.0
    current_epoch = epoch_column[0]
    for i in range(len(anticipation_column) + 1):
        # end of the epoch -> calc summary data
        if i == len(anticipation_column) or current_epoch != epoch_column[i]:
            assert(learnt_anticipation <= all_anticipation)

            learnt_ratio = learnt_anticipation / all_anticipation * 100.0
            learnt_anticipation_ratios.append(floatToStr(learnt_ratio))
            all_anticipation = 0.0
            learnt_anticipation = 0.0

        if i == len(anticipation_column):
            break

        current_epoch = epoch_column[i]

        # we ignore the first two trials, repetitions and trills
        if trial_column[i] <= preparatory_trial_number or repetition_column[i] == "True" or trill_column[i] == "True":
            continue

        assert(repetition_column[i] == "False")
        assert(trill_column[i] == "False")

        if str(anticipation_column[i]) == 'True':
            all_anticipation += 1

        if str(correct_anticipation_column[i]) == 'True':
            learnt_anticipation += 1

    if len(learnt_anticipation_ratios) != 8:
        print("Error: The input data should contain exactly 8 epochs for this data analysis.")
    return learnt_anticipation_ratios

def computeAnticipatoryData(input_dir, output_file):
    anticipation_data = pandas.DataFrame(columns=['subject',
                                                  'epoch_1_learnt_anticip_ratio', 'epoch_2_learnt_anticip_ratio', 'epoch_3_learnt_anticip_ratio', 'epoch_4_learnt_anticip_ratio',
                                                  'epoch_5_learnt_anticip_ratio', 'epoch_6_learnt_anticip_ratio', 'epoch_7_learnt_anticip_ratio', 'epoch_8_learnt_anticip_ratio'])

    settings = ExperimentSettings(os.path.join('..', 'settings', 'settings'), "", True)
    try:
            settings.read_from_file()
    except:
        print('Error: Could not read settings file to get the number of preparatory trials.')
        return

    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            subject = file.split('_')[1]

            print("Compute anticipatory data for subject: " + subject)

            learnt_anticipation_ratios = computeAnticipationDataForOneSubject(input_file, settings.blockprepN)
            anticipation_data.loc[len(anticipation_data)] = [subject] + learnt_anticipation_ratios
        break

    anticipation_data.to_csv(output_file, sep='\t', index=False)
