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

def validateRepetition(data_table):

    repetition_column = []
    stimulus_column = data_table["stimulus"]
    trial_column = data_table["trial"]
    repetition_column = data_table["repetition"]

    for i in range(len(stimulus_column)):
        if repetition_column[i] == 'none':
            assert(trial_column[i] == 1)
        elif repetition_column[i] == 'True':
            assert(stimulus_column[i - 1] == stimulus_column[i])
        else:
            assert(repetition_column[i] == "False")
            assert(stimulus_column[i - 1] != stimulus_column[i])

def validateTrill(data_table):

    stimulus_column = data_table["stimulus"]
    trial_column = data_table["trial"]
    trill_column = data_table["trill"]

    for i in range(len(stimulus_column)):
        if trill_column[i] == 'none':
            assert(trial_column [i] <= 2)
        elif trill_column[i] == 'True':
            assert(stimulus_column[i - 2] == stimulus_column[i])
            assert(stimulus_column[i - 1] != stimulus_column[i])
        else:
            assert(trill_column[i] == 'False')
            assert(stimulus_column[i - 2] != stimulus_column[i] or stimulus_column[i - 1] == stimulus_column[i])

def findLearningSequence(data_table):
    PCode_colum = data_table["PCode"]

    # We find the first valid PCode, that will be the learning sequence.
    for i in range(len(PCode_colum)):
        if str(PCode_colum[i]) != "noPattern":
            return str(PCode_colum[i])

    raise Exception("Error: Could not find a valid learning sequence in the data.")
    return ""

def validateHighLowBasedOnLearningSequence(data_table):

    high_low_column = []
    stimulus_column = data_table["stimulus"]
    trial_column = data_table["trial"]
    high_low_column = data_table["high_low_learning"]

    # get the learning sequence
    learning_sequence = findLearningSequence(data_table)
    learning_sequence += learning_sequence[0]

    for i in range(len(stimulus_column)):
        if high_low_column[i] == 'none':
            assert(trial_column[i] <= 2)
        elif high_low_column[i] == "high":
            assert(str(stimulus_column[i - 2]) + str(stimulus_column[i]) in learning_sequence)
        else:
            assert(high_low_column[i] == "low")
            assert(str(stimulus_column[i - 2]) + str(stimulus_column[i]) not in learning_sequence)         

def validateAnticipationColumn(data_table):

    anticipation_column = data_table["has_anticipation"]
    stimulus_column = data_table["stimulus"]
    last_AOI_column = data_table["last_AOI_before_stimulus"]
    trial_column = data_table["trial"]

    for i in range(len(stimulus_column)):
        if anticipation_column[i] == 'none':
            assert(trial_column[i] <= 1)
        elif anticipation_column[i] == 'True':
            assert(trial_column[i] >= 1)
            assert(int(last_AOI_column[i]) != int(stimulus_column[i - 1]))
        else:
            assert(anticipation_column[i] == 'False')
            assert(trial_column[i] >= 1)
            assert(trial_column[i] >= 1)
            assert(last_AOI_column[i] == 'none' or int(last_AOI_column[i]) == int(stimulus_column[i - 1]))

def validateLearntAnticipationColumn(data_table):

    learnt_anticipation_column = data_table["has_learnt_anticipation"]
    stimulus_column = data_table["stimulus"]
    last_AOI_column = data_table["last_AOI_before_stimulus"]
    anticipation_column = data_table["has_anticipation"]
    trial_column = data_table["trial"]

    # get the learning sequence
    learning_sequence = findLearningSequence(data_table)
    learning_sequence += learning_sequence[0]

    for i in range(len(stimulus_column)):
        if learnt_anticipation_column[i] == 'none':
            assert(trial_column[i] <= 2)
        elif learnt_anticipation_column[i] == 'True':
            assert(trial_column[i] >= 2)
            assert(anticipation_column[i] == 'True')
            assert(str(stimulus_column[i - 2]) + str(last_AOI_column[i]) in learning_sequence)
        else:
            assert(learnt_anticipation_column[i] == 'False')
            assert(trial_column[i] >= 2)
            assert(anticipation_column[i] == 'False' or
                   str(stimulus_column[i - 2]) + str(last_AOI_column[i]) not in learning_sequence)

def validateExtendedTrialData(input_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)

            subject = os.path.basename(input_file).split('_')[1]
            print("Validate trial level data extension for subject: " + subject)

            data_table = pandas.read_csv(input_file, sep='\t')
            validateRepetition(data_table)
            validateTrill(data_table)
            validateHighLowBasedOnLearningSequence(data_table)
            validateAnticipationColumn(data_table)
            validateLearntAnticipationColumn(data_table)

        break
