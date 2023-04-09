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
# Add the local path to the main script and external scripts so we can import them.
sys.path = [".."] + \
    [os.path.join("..", "externals", "psychopy_mock")] + sys.path

import unittest
import asrt
import shutil
import psychopy_gui_mock as pgm


class participantIDTest(unittest.TestCase):

    def tearDown(self):
        tempdir = os.path.abspath(__file__)
        (tempdir, trail) = os.path.split(tempdir)
        tempdir = os.path.join(tempdir, "data", "participant_id")

        # remove all temp files
        for file in os.listdir(tempdir):
            file_path = os.path.join(tempdir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    def constructFilePath(self, file_name):
        filepath = os.path.abspath(__file__)
        (filepath, trail) = os.path.split(filepath)
        filepath = os.path.join(filepath, "data", "participant_id", file_name)
        return filepath

    def testNoSettingsFile(self):
        gui_mock = pgm.PsychoPyGuiMock()
        gui_mock.addFieldValues(
            [10, 'kontrol', 'férfi', 25, '3rd', '2nd'])

        thispath = self.constructFilePath("NoSettingsFile")
        experiment = asrt.Experiment(thispath)
        experiment.settings = asrt.ExperimentSettings("", "")
        experiment.settings.groups = ["kontrol", "exp1"]
        experiment.settings.numsessions = 2
        experiment.settings.epochN = 3
        experiment.settings.epochs = [1, 2]
        experiment.settings.block_in_epochN = 2
        experiment.settings.blockprepN = 5
        experiment.settings.blocklengthN = 20
        experiment.settings.asrt_rcolor = "Orange"
        experiment.settings.asrt_pcolor = "Green"
        experiment.settings.asrt_types = {}
        experiment.settings.asrt_types[1] = "implicit"
        experiment.settings.asrt_types[2] = "implicit"
        experiment.settings.asrt_types[3] = "implicit"

        asrt.ensure_dir(os.path.join(thispath, "subject_settings"))

        experiment.participant_id()

        self.assertEqual(experiment.subject_group, 'kontrol')
        self.assertEqual(experiment.subject_number, 10)
        self.assertEqual(experiment.PCodes, {1: '3rd - 1324', 2: '3rd - 1324', 3: '2nd - 1243'})

        # Check person data handler's properties too
        self.assertEqual(experiment.person_data.subject_id,
                         "subject_10_kontrol")
        self.assertEqual(experiment.person_data.all_settings_file_path, os.path.join(
            thispath, "subject_settings", experiment.person_data.subject_id))
        self.assertEqual(experiment.person_data.all_IDs_file_path, os.path.join(
            thispath, "subject_settings", "participant_settings"))
        self.assertEqual(experiment.person_data.subject_list_file_path, os.path.join(
            thispath, "subject_settings", "participants_in_experiment.txt"))
        self.assertEqual(experiment.person_data.output_file_path, os.path.join(
            thispath, "logs", experiment.person_data.subject_id + "_log.txt"))

        # Some files were created
        self.assertTrue(os.path.isfile(experiment.person_data.all_settings_file_path + ".dat") or
                        os.path.isfile(experiment.person_data.all_settings_file_path))
        self.assertTrue(os.path.isfile(experiment.person_data.all_IDs_file_path + ".dat") or
                        os.path.isfile(experiment.person_data.all_IDs_file_path))
        self.assertTrue(os.path.isfile(
            experiment.person_data.subject_list_file_path))

    def testExistingSettingsFile(self):
        gui_mock = pgm.PsychoPyGuiMock()
        gui_mock.addFieldValues(
            [10, 'kontrol', 'nő', 30, '3rd', '2nd', 10, 'kontrol'])

        thispath = self.constructFilePath("NoSettingsFile")
        experiment = asrt.Experiment(thispath)
        experiment.settings = asrt.ExperimentSettings("", "")
        experiment.settings.groups = ["kontrol", "exp1"]
        experiment.settings.numsessions = 2
        experiment.settings.epochN = 3
        experiment.settings.epochs = [1, 2]
        experiment.settings.block_in_epochN = 2
        experiment.settings.blockprepN = 5
        experiment.settings.blocklengthN = 20
        experiment.settings.asrt_rcolor = "Orange"
        experiment.settings.asrt_pcolor = "Green"
        experiment.settings.asrt_types = {}
        experiment.settings.asrt_types[1] = "implicit"
        experiment.settings.asrt_types[2] = "implicit"
        experiment.settings.asrt_types[3] = "implicit"

        asrt.ensure_dir(os.path.join(thispath, "subject_settings"))

        # call once to get the participant settings
        experiment.participant_id()

        # let save participant settings after the first block
        experiment.last_N = 25
        experiment.person_data.save_person_settings(experiment)

        experiment.settings = asrt.ExperimentSettings("", "")
        experiment.settings.groups = ["kontrol", "exp1"]
        experiment.settings.epochN = 3
        experiment.settings.block_in_epochN = 2
        experiment.settings.blockprepN = 5
        experiment.settings.blocklengthN = 20
        experiment.settings.numsessions = 2
        experiment.settings.validation_trialN = 20

        # now load back the participant's settings with participant id function
        experiment.participant_id()

        self.assertEqual(experiment.subject_group, 'kontrol')
        self.assertEqual(experiment.subject_number, 10)
        self.assertEqual(experiment.PCodes, {1: '3rd - 1324', 2: '3rd - 1324', 3: '2nd - 1243'})
        self.assertEqual(experiment.stim_output_line, 0)

if __name__ == "__main__":
    unittest.main()  # run all tests
