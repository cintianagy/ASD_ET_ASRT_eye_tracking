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
import psychopy_gui_mock as pgm


class allSettingsDefTest(unittest.TestCase):

    def tearDown(self):
        tempdir = os.path.abspath(__file__)
        (tempdir, trail) = os.path.split(tempdir)
        tempdir = os.path.join(tempdir, "data", "all_settings_def")

        # remove all temp files
        for file in os.listdir(tempdir):
            file_path = os.path.join(tempdir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)

    def setUp(self):
        tempdir = os.path.abspath(__file__)
        (tempdir, trail) = os.path.split(tempdir)
        tempdir = os.path.join(tempdir, "data", "all_settings_def")
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)

    def constructFilePath(self, file_name):
        filepath = os.path.abspath(__file__)
        (inst_and_feedback_path, trail) = os.path.split(filepath)
        inst_and_feedback_path = os.path.join(inst_and_feedback_path, "data")
        inst_and_feedback_path = os.path.join(
            inst_and_feedback_path, "all_settings_def")
        inst_and_feedback_path = os.path.join(
            inst_and_feedback_path, file_name)
        return inst_and_feedback_path

    def testSettingsDialogsDefaultValues(self):
        output_file = self.constructFilePath(
            "testSettingsDialogsDefaultValues")
        experiment = asrt.Experiment("")
        experiment.settings = asrt.ExperimentSettings(
            output_file, output_file + "_reminder.txt")

        gui_mock = pgm.PsychoPyGuiMock()
        experiment.all_settings_def()

        self.assertEqual(experiment.settings.experiment_type, 'reaction-time')
        self.assertEqual(experiment.settings.groups, ["", ""])
        self.assertEqual(experiment.settings.blockprepN, 5)
        self.assertEqual(experiment.settings.blocklengthN, 80)
        self.assertEqual(experiment.settings.block_in_epochN, 5)
        self.assertEqual(experiment.settings.epochN, 10)
        self.assertEqual(experiment.settings.epochs, [5, 5])
        self.assertEqual(experiment.settings.asrt_types, {1: 'noASRT', 2: 'implicit', 3: 'implicit', 4: 'implicit',
                                                          5: 'implicit', 6: 'noASRT', 7: 'implicit', 8: 'implicit', 9: 'implicit', 10: 'implicit'})
        self.assertEqual(experiment.settings.monitor_width, 34.2)
        self.assertEqual(experiment.settings.computer_name, "Laposka")
        self.assertEqual(experiment.settings.asrt_distance, 3)
        self.assertEqual(experiment.settings.asrt_size, 1)
        self.assertEqual(experiment.settings.asrt_rcolor, "DarkBlue")
        self.assertEqual(experiment.settings.asrt_pcolor, "Green")
        self.assertEqual(experiment.settings.asrt_background, "Ivory")
        self.assertEqual(experiment.settings.RSI_time, 0.12)
        self.assertEqual(experiment.settings.key1, 'y')
        self.assertEqual(experiment.settings.key2, 'c')
        self.assertEqual(experiment.settings.key3, 'b')
        self.assertEqual(experiment.settings.key4, 'm')
        self.assertEqual(experiment.settings.key_quit, 'q')
        self.assertEqual(experiment.settings.whether_warning, True)
        self.assertEqual(experiment.settings.speed_warning, 93)
        self.assertEqual(experiment.settings.acc_warning, 91)
        self.assertEqual(experiment.settings.get_maxtrial(), 4290)
        self.assertEqual(
            experiment.settings.get_session_starts(), [1, 2146, 4291])
        self.assertEqual(experiment.settings.get_block_starts(), [1, 21, 106, 191, 276, 361, 446, 531, 616, 701, 786, 871,
                                                                  956, 1041, 1126, 1211, 1296, 1381, 1466, 1551, 1636, 1721,
                                                                  1806, 1891, 1976, 2061, 2146, 2166, 2251, 2336, 2421, 2506,
                                                                  2591, 2676, 2761, 2846, 2931, 3016, 3101, 3186, 3271, 3356,
                                                                  3441, 3526, 3611, 3696, 3781, 3866, 3951, 4036, 4121, 4206,
                                                                  4291, 4376])
        self.assertEqual(experiment.settings.get_epoch_starts(), [446, 871, 1296, 1721, 2146, 2591, 3016, 3441, 3866, 4291])
        self.assertEqual(experiment.settings.validation_trialN, 20)

        # output file exists
        self.assertTrue(os.path.exists(output_file + ".dat") or os.path.exists(output_file))
        self.assertTrue(os.path.exists(output_file + "_reminder.txt"))

        # reload saved data
        experiment.settings = asrt.ExperimentSettings(output_file, "")
        experiment.all_settings_def()

        self.assertEqual(experiment.settings.experiment_type, 'reaction-time')
        self.assertEqual(experiment.settings.groups, ["", ""])
        self.assertEqual(experiment.settings.blockprepN, 5)
        self.assertEqual(experiment.settings.blocklengthN, 80)
        self.assertEqual(experiment.settings.block_in_epochN, 5)
        self.assertEqual(experiment.settings.epochN, 10)
        self.assertEqual(experiment.settings.epochs, [5, 5])
        self.assertEqual(experiment.settings.asrt_types, {1: 'noASRT', 2: 'implicit', 3: 'implicit', 4: 'implicit',
                                                          5: 'implicit', 6: 'noASRT', 7: 'implicit', 8: 'implicit', 9: 'implicit', 10: 'implicit'})
        self.assertEqual(experiment.settings.monitor_width, 34.2)
        self.assertEqual(experiment.settings.computer_name, "Laposka")
        self.assertEqual(experiment.settings.asrt_distance, 3)
        self.assertEqual(experiment.settings.asrt_size, 1)
        self.assertEqual(experiment.settings.asrt_rcolor, "DarkBlue")
        self.assertEqual(experiment.settings.asrt_pcolor, "Green")
        self.assertEqual(experiment.settings.asrt_background, "Ivory")
        self.assertEqual(experiment.settings.RSI_time, 0.12)
        self.assertEqual(experiment.settings.key1, 'y')
        self.assertEqual(experiment.settings.key2, 'c')
        self.assertEqual(experiment.settings.key3, 'b')
        self.assertEqual(experiment.settings.key4, 'm')
        self.assertEqual(experiment.settings.key_quit, 'q')
        self.assertEqual(experiment.settings.whether_warning, True)
        self.assertEqual(experiment.settings.speed_warning, 93)
        self.assertEqual(experiment.settings.acc_warning, 91)
        self.assertEqual(experiment.settings.get_maxtrial(), 4290)
        self.assertEqual(
            experiment.settings.get_session_starts(), [1, 2146, 4291])
        self.assertEqual(experiment.settings.get_block_starts(), [1, 21, 106, 191, 276, 361, 446, 531, 616, 701, 786, 871,
                                                                  956, 1041, 1126, 1211, 1296, 1381, 1466, 1551, 1636, 1721,
                                                                  1806, 1891, 1976, 2061, 2146, 2166, 2251, 2336, 2421, 2506,
                                                                  2591, 2676, 2761, 2846, 2931, 3016, 3101, 3186, 3271, 3356,
                                                                  3441, 3526, 3611, 3696, 3781, 3866, 3951, 4036, 4121, 4206,
                                                                  4291, 4376])
        self.assertEqual(experiment.settings.get_epoch_starts(), [446, 871, 1296, 1721, 2146, 2591, 3016, 3441, 3866, 4291])
        self.assertEqual(experiment.settings.validation_trialN, 20)

    def testSettingsDialogsCustomValues(self):
        output_file = self.constructFilePath("testSettingsDialogsCustomValues")
        experiment = asrt.Experiment("")
        experiment.settings = asrt.ExperimentSettings(
            output_file, output_file + "_reminder.txt")

        gui_mock = pgm.PsychoPyGuiMock()
        gui_mock.addFieldValues(['reakció idő', 1, 1, 10, 75, 7, 12, 2, 'implicit', 15, 29.1, "Alma", 4, 2, "Blue", "Red",
                                 "Yellow", 300, 'a', 's', 'd', 'f', 'g', False, 89, 78])
        experiment.all_settings_def()

        self.assertEqual(experiment.settings.experiment_type, 'reaction-time')
        self.assertEqual(experiment.settings.groups, ['nincsenek csoportok'])
        self.assertEqual(experiment.settings.blockprepN, 10)
        self.assertEqual(experiment.settings.blocklengthN, 75)
        self.assertEqual(experiment.settings.block_in_epochN, 7)
        self.assertEqual(experiment.settings.epochN, 12)
        self.assertEqual(experiment.settings.epochs, [12])
        self.assertEqual(experiment.settings.asrt_types, {1: 'noASRT', 2: 'noASRT', 3: 'implicit', 4: 'implicit', 5: 'implicit', 6: 'implicit', 7: 'implicit',
                                                          8: 'implicit', 9: 'implicit', 10: 'implicit', 11: 'implicit', 12: 'implicit'})
        self.assertEqual(experiment.settings.monitor_width, 29.1)
        self.assertEqual(experiment.settings.computer_name, "Alma")
        self.assertEqual(experiment.settings.asrt_distance, 4)
        self.assertEqual(experiment.settings.asrt_size, 2)
        self.assertEqual(experiment.settings.asrt_rcolor, "Blue")
        self.assertEqual(experiment.settings.asrt_pcolor, "Red")
        self.assertEqual(experiment.settings.asrt_background, "Yellow")
        self.assertEqual(experiment.settings.RSI_time, 0.3)
        self.assertEqual(experiment.settings.key1, 'a')
        self.assertEqual(experiment.settings.key2, 's')
        self.assertEqual(experiment.settings.key3, 'd')
        self.assertEqual(experiment.settings.key4, 'f')
        self.assertEqual(experiment.settings.key_quit, 'g')
        self.assertEqual(experiment.settings.whether_warning, False)
        self.assertEqual(experiment.settings.speed_warning, 89)
        self.assertEqual(experiment.settings.acc_warning, 78)
        self.assertEqual(experiment.settings.get_maxtrial(), 7155)
        self.assertEqual(experiment.settings.get_session_starts(), [1, 7156])
        self.assertEqual(experiment.settings.get_block_starts(), [1, 16, 101, 186, 271, 356, 441, 526, 611, 696, 781,
                                                                  866, 951, 1036, 1121, 1206, 1291, 1376, 1461, 1546,
                                                                  1631, 1716, 1801, 1886, 1971, 2056, 2141, 2226, 2311,
                                                                  2396, 2481, 2566, 2651, 2736, 2821, 2906, 2991, 3076,
                                                                  3161, 3246, 3331, 3416, 3501, 3586, 3671, 3756, 3841,
                                                                  3926, 4011, 4096, 4181, 4266, 4351, 4436, 4521, 4606,
                                                                  4691, 4776, 4861, 4946, 5031, 5116, 5201, 5286, 5371,
                                                                  5456, 5541, 5626, 5711, 5796, 5881, 5966, 6051, 6136,
                                                                  6221, 6306, 6391, 6476, 6561, 6646, 6731, 6816, 6901,
                                                                  6986, 7071, 7156, 7241])
        self.assertEqual(experiment.settings.get_epoch_starts(), [611, 1206, 1801, 2396, 2991, 3586, 4181, 4776, 5371, 5966, 6561, 7156])
        self.assertEqual(experiment.settings.validation_trialN, 15)

        # output file exists
        self.assertTrue(os.path.exists(output_file + ".dat") or os.path.exists(output_file))
        self.assertTrue(os.path.exists(output_file + "_reminder.txt"))

if __name__ == "__main__":
    unittest.main()  # run all tests
