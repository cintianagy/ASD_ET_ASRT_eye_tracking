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
import sys
import shutil
import time

from compute_trial_level_data import computeTrialLevelData
from extend_trial_level_data import extendTrialLevelData
from compute_learning import computeStatisticalLearning
from compute_anticipatory import computeAnticipatoryData
from compute_interference import computeInterferenceData

from compute_missing_data_ratio import computeMissingDataRatio
from compute_distance import computeDistance
from compute_rms_s2s import computeRMSSampleToSample
from compute_rms_e2e import computeRMSEyeToEye

from validate_learning import validateLearning
from validate_anticipatory import validateAnticipatoryData
from validate_interference import validateInterferenceData
from validate_extended_data import validateExtendedTrialData
from validate_trial_data import validateTrialData

def setupOutputDir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        time.sleep(.001)

    os.makedirs(dir_path)
    if not os.path.isdir(dir_path):
        print("Could not make the output folder: " + dir_path)
        exit(1)

def extract_subject_id(subject_file_name):
    subject_id = subject_file_name[len('subject_'):]
    subject_id = subject_id[:subject_id.find('_')]
    return subject_id

def compute_trial_data(input_dir, output_dir):
    setupOutputDir(output_dir)

    for root, dirs, files in os.walk(input_dir):
        for subject_file in files:
            subject_id = extract_subject_id(subject_file)
            print("Compute trial level data for subject: " + subject_id)

            raw_data_path = os.path.join(root, subject_file)
            RT_data_path = os.path.join(output_dir, 'subject_' + subject_id + '__trial_log.csv')
            computeTrialLevelData(raw_data_path, RT_data_path)

        break

def validate_trial_data(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for subject_file in files:
            subject_id = extract_subject_id(subject_file)

            print("Validate trial level data for subject: " + subject_id)
            raw_data_path = os.path.join(root, subject_file)
            RT_data_path = os.path.join(output_dir, 'subject_' + subject_id + '__trial_log.csv')
            validateTrialData(raw_data_path, RT_data_path)

        break

def extend_trial_data(input_dir, output_dir):
    setupOutputDir(output_dir)

    for root, dirs, files in os.walk(input_dir):
        for subject_file in files:
            subject_id = extract_subject_id(subject_file)
            print("Extend trial level data with additional fields for subject: " + subject_id)

            input_file = os.path.join(input_dir, subject_file)
            output_file = os.path.join(output_dir, 'subject_' + subject_id + '__trial_extended_log.csv')
            extendTrialLevelData(input_file, output_file)

        break

def validate_extended_trial_data(input_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:

            input_file = os.path.join(input_dir, file)
            validateExtendedTrialData(input_file)

        break

def compute_statistical_learning(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'statistical_learning_RT.csv')
    computeStatisticalLearning(input_dir, output_file)

def validate_statistical_learning(input_dir, output_dir):

    output_file = os.path.join(output_dir, 'statistical_learning_RT.csv')
    validateLearning(input_dir, output_file)

def compute_interference_data(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'interference_HL_LL_LH.csv')
    computeInterferenceData(input_dir, output_file)

def validate_interference_data(input_dir, output_dir):
    output_file = os.path.join(output_dir, 'interference_HL_LL_LH.csv')
    validateInterferenceData(input_dir, output_file)

def compute_anticipatory_data(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'anticipatory_data.csv')
    computeAnticipatoryData(input_dir, output_file)

def validate_anticipatory_data(input_dir, output_dir):

    output_file = os.path.join(output_dir, 'anticipatory_data.csv')
    validateAnticipatoryData(input_dir, output_file)

def compute_missing_data_ratio(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'missing_data_ratio.csv')
    computeMissingDataRatio(input_dir, output_file)

def compute_distance(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'screen_eye_distance_data.csv')
    computeDistance(input_dir, output_file)

def compute_RMS_E2E(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'RMS(E2E)_data.csv')
    computeRMSEyeToEye(input_dir, output_file)

def compute_RMS_S2S(input_dir, output_dir):
    setupOutputDir(output_dir)

    output_file = os.path.join(output_dir, 'RMS(S2S)_data.csv')
    computeRMSSampleToSample(input_dir, output_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("You need to specify an input folder for raw data files.")
        exit(1)

    if not os.path.isdir(sys.argv[1]):
        print("The passed first parameter should be a valid directory path: " + sys.argv[1])
        exit(1)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    trial_data_dir = os.path.join(script_dir, 'data', 'trial_data')

    compute_trial_data(sys.argv[1], trial_data_dir)

    # validate_trial_data(sys.argv[1], trial_data_dir)
    
    extended_trial_data_dir = os.path.join(script_dir, 'data', 'trial_data_extended')

    extend_trial_data(trial_data_dir, extended_trial_data_dir)
    
    # validate_extended_trial_data(extended_trial_data_dir)

    statistical_learning_dir = os.path.join(script_dir, 'data', 'statistical_learning')

    compute_statistical_learning(extended_trial_data_dir, statistical_learning_dir)

    # validate_statistical_learning(extended_trial_data_dir, statistical_learning_dir)

    interference_dir = os.path.join(script_dir, 'data', 'interference')

    compute_interference_data(extended_trial_data_dir, interference_dir)

    # validate_interference_data(extended_trial_data_dir, interference_dir)

    anticipatory_dir = os.path.join(script_dir, 'data', 'anticipatory_movements')

    compute_anticipatory_data(extended_trial_data_dir, anticipatory_dir)

    # validate_anticipatory_data(extended_trial_data_dir, anticipatory_dir)

    missing_data_dir = os.path.join(script_dir, 'data', 'missing_data')

    compute_missing_data_ratio(sys.argv[1], missing_data_dir)

    distance_dir = os.path.join(script_dir, 'data', 'distance_data')

    compute_distance(sys.argv[1], distance_dir)

    RMS_E2E_dir = os.path.join(script_dir, 'data', 'RMS_E2E')

    compute_RMS_E2E(sys.argv[1], RMS_E2E_dir)

    RMS_S2S_dir = os.path.join(script_dir, 'data', 'RMS_S2S')

    compute_RMS_S2S(sys.argv[1], RMS_S2S_dir)
