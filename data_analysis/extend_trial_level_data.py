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

def computeRepetitionColumn(data_table):
    repetition_column = []
    stimulus_column = data_table["stimulus"]
    trial_column = data_table["trial"]

    # A trial is repetition if the previous trial has the same stimulus
    for i in range(len(stimulus_column)):
        # Can't calculate for the first trial of the block, because there is no previous trial.
        if trial_column[i] <= 1:
            repetition_column.append('none')
        elif stimulus_column[i] == stimulus_column[i - 1]:
            repetition_column.append(True)
        else:
            repetition_column.append(False)

    return repetition_column

def computeTrillColumn(data_table):
    trill_column = []
    stimulus_column = data_table["stimulus"]
    trial_column = data_table["trial"]

    # A trial is a trill if the first and third item of the current triplet has the same
    # stimulus, but the middle item of the triplet is different.
    for i in range(len(stimulus_column)):
        # Can't calculate for the first two trials of the block, because there is no triplet we can use.
        if trial_column[i] <= 2:
            trill_column.append('none')
        elif ( stimulus_column[i] != stimulus_column[i - 1] and
             stimulus_column[i] == stimulus_column[i - 2] ):
            trill_column.append(True)
        else:
            trill_column.append(False)

    return trill_column

def findLearningSequence(data_table):
    PCode_colum = data_table["PCode"]

    # We find the first valid PCode, that will be the learning sequence.
    for i in range(len(PCode_colum)):
        if str(PCode_colum[i]) != "noPattern":
            return str(PCode_colum[i])

    raise Exception("Error: Could not find a valid learning sequence in the data.")
    return ""

def computeHighLowBasedOnLearningSequence(data_table):
    high_low_column = []
    stimulus_column = data_table["stimulus"]
    trial_column = data_table["trial"]
    session_column = data_table["session"]
    pcode_column = data_table["PCode"]

    if session_column.nunique() == 1:
        # get the learning sequence
        learning_sequence = findLearningSequence(data_table)
        learning_sequence += learning_sequence[0]

        # We calculate whether the current triplet is a high or low triplet based on the learning sequence.
        for i in range(len(stimulus_column)):
            # Can't calculate for the first two trials of the block, because there is no triplet we can use.
            if trial_column[i] <= 2:
                high_low_column.append('none')
            elif (str(stimulus_column[i - 2]) + str(stimulus_column[i])) in learning_sequence:
                high_low_column.append('high')
            else:
                high_low_column.append('low')

        return high_low_column
    elif session_column.nunique() > 1:
        # get the learning sequence
        learning_sequence = pcode_column.unique()[1]

        # We calculate whether the current triplet is a high or low triplet based on the learning sequence.
        for i in range(len(stimulus_column)):
            # Can't calculate for the first two trials of the block, because there is no triplet we can use.
            if trial_column[i] <= 2:
                high_low_column.append('none')
            elif (str(stimulus_column[i - 2]) + str(stimulus_column[i])) in learning_sequence:
                high_low_column.append('high')
            else:
                high_low_column.append('low')

        return high_low_column

def computeAnticipationColumn(data_table):
    anticipation_column = []
    stimulus_column = data_table["stimulus"]
    last_AOI_column = data_table["last_AOI_before_stimulus"]
    trial_column = data_table["trial"]

    # We calculate wether the last AOI during the current RSI was different from the
    # AOI of the last trial. So the the eye was moved after the last trial.
    for i in range(len(stimulus_column)):
        # Can't calculate for the first trial of the block, because there is no previous trial.
        if trial_column[i] <= 1:
            anticipation_column.append('none')
        # There is no valid AOI data recorded during RSI.
        elif last_AOI_column[i] == 'none':
            anticipation_column.append(False)
        elif int(last_AOI_column[i]) != int(stimulus_column[i - 1]):
            anticipation_column.append(True)
        else:
            anticipation_column.append(False)

    return anticipation_column

def computeLearntAnticipationColumn(data_table):
    learnt_anticipation_data = []
    stimulus_column = data_table["stimulus"]
    last_AOI_column = data_table["last_AOI_before_stimulus"]
    trial_column = data_table["trial"]

    learning_sequence = findLearningSequence(data_table)
    learning_sequence += learning_sequence[0]

    for i in range(len(stimulus_column)):
        # Can't calculate for the first two trials of the block, because there is no triplet we can use.
        if trial_column[i] <= 2:
            learnt_anticipation_data.append('none')
        # There is no valid AOI data recorded during RSI.
        elif last_AOI_column[i] == 'none':
            learnt_anticipation_data.append(False)
        # No anticipation eye movement. Eye is in the same AOI where the previous stimulus was.
        elif int(last_AOI_column[i]) == int(stimulus_column[i - 1]):
            learnt_anticipation_data.append(False)
        # The last registered AOI during RSI follows the learning sequence.
        elif str(stimulus_column[i - 2]) + str(last_AOI_column[i]) in learning_sequence:
            learnt_anticipation_data.append(True)
        else:
            learnt_anticipation_data.append(False)

    return learnt_anticipation_data

def extendTrialLevelDataForOneSubject(input_file, output_file):
    data_table = pandas.read_csv(input_file, sep='\t')

    # previous trial has the stimulus at the same position -> repetition.
    repetition_data = computeRepetitionColumn(data_table)
    assert(len(repetition_data) == len(data_table.index))
    data_table["repetition"] = repetition_data

    # trill: first item and third item of trial triplet is the same: e.g. 1x1, 2x2, etc.
    trill_data = computeTrillColumn(data_table)
    assert(len(trill_data) == len(data_table.index))
    data_table["trill"] = trill_data

    # calculate frequency based on learning sequence
    high_low_data = computeHighLowBasedOnLearningSequence(data_table)
    assert(len(high_low_data) == len(data_table.index))
    data_table["high_low_learning"] = high_low_data

    # calculate whether anticipatory eye-movement has happened
    anticipation_data = computeAnticipationColumn(data_table)
    assert(len(anticipation_data) == len(data_table.index))
    data_table["has_anticipation"] = anticipation_data

    # calculate whether learning dependent anticipatory eye-movement has happened
    learnt_anticipation_data = computeLearntAnticipationColumn(data_table)
    assert(len(learnt_anticipation_data) == len(data_table.index))
    data_table["has_learnt_anticipation"] = learnt_anticipation_data

    data_table.to_csv(output_file, sep='\t', index=False)

def extendTrialLevelData(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for subject_file in files:
            subject = subject_file.split('_')[1]

            print("Extend trial level data with additional fields for subject: " + subject)

            input_file = os.path.join(input_dir, subject_file)
            output_file = os.path.join(output_dir, 'subject_' + subject + '__trial_extended_log.csv')
            extendTrialLevelDataForOneSubject(input_file, output_file)

        break