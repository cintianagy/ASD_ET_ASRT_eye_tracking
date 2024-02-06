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

import sys
import os
import pandas
from utils import strToFloat, floatToStr

# Add the local path to the main script so we can import some class from it.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from asrt import ExperimentSettings

def computeAnticipationDataForOneSubject(input_file, preparatory_trial_number):
    input_data_table = pandas.read_csv(input_file, sep='\t')

    anticipation_column = input_data_table["has_anticipation"]
    correct_anticipation_column = input_data_table["has_learnt_anticipation"]
    epoch_column = input_data_table["epoch"]
    repetition_column = input_data_table["repetition"]
    trill_column = input_data_table["trill"]
    trial_column = input_data_table["trial"]
    trial_type_pr = input_data_table["trial_type_pr"]

    learnt_anticipation_ratios = []
    all_anticipation = 0.0
    learnt_anticipation = 0.0
    current_epoch = epoch_column[0]
    epoch_number = epoch_column.max()
    for i in range(len(anticipation_column) + 1):
        # end of the epoch -> calc summary data
        if i == len(anticipation_column) or current_epoch != epoch_column[i]:
            assert(learnt_anticipation <= all_anticipation)

            if all_anticipation == 0:
                learnt_ratio = float('nan')
                print("Warning: No anticipatory eye-movements were found in epoch " + str(current_epoch) + ".")
            else:
                learnt_ratio = learnt_anticipation / all_anticipation * 100.0

            learnt_anticipation_ratios.append(floatToStr(learnt_ratio))
            all_anticipation = 0.0
            learnt_anticipation = 0.0

        if i == len(anticipation_column):
            break

        current_epoch = epoch_column[i]

        # we ignore the preparatory trials, repetitions and trills
        if trial_column[i] <= preparatory_trial_number or repetition_column[i] == "True" or trill_column[i] == "True":
            continue

        assert(repetition_column[i] == "False")
        assert(trill_column[i] == "False")

        if str(anticipation_column[i]) == 'True':
            all_anticipation += 1

        if str(correct_anticipation_column[i]) == 'True':
            learnt_anticipation += 1

    # we do not need this
    # if len(learnt_anticipation_ratios) != 8:
    #     raise Exception("Error: The input data should contain exactly 8 epochs for this data analysis.")
    return learnt_anticipation_ratios, epoch_number

def get_number_of_epochs(input_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)

            input_data_table = pandas.read_csv(input_file, sep='\t')
            epoch_column = input_data_table["epoch"]
            epoch_number = epoch_column.max()

    return epoch_number

def computeAnticipatoryData(input_dir, output_file):
    epoch_number = get_number_of_epochs(input_dir)
    column_names = ['subject'] + [f'epoch_{i}_learnt_anticip_ratio' for i in range(1, epoch_number + 1)]
    anticipation_data = pandas.DataFrame(columns=column_names)

    parent_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    settings = ExperimentSettings(os.path.join(parent_folder, 'settings', 'settings'), "", True)
    try:
            settings.read_from_file()
    except:
        raise Exception('Error: Could not read settings file to get the number of preparatory trials.')

    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            subject = file.split('_')[1]

            print("Compute anticipatory data for subject: " + subject)

            learnt_anticipation_ratios = computeAnticipationDataForOneSubject(input_file, settings.blockprepN)
            anticipation_data.loc[len(anticipation_data)] = [subject] + learnt_anticipation_ratios
        break

    anticipation_data.to_csv(output_file, sep='\t', index=False)
