#    Copyright (C) <2018>  <Tamás Zolnai>    <zolnaitamas2000@gmail.com>

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

#!\\usr\\bin\\env python
# -*- coding: utf-8 -*-

import unittest

import os

import sys
# Add the local path to the main script so we can import it.
sys.path = [".."] + [os.path.join("..", "externals", "psychopy_mock")]  + sys.path

from psychopy import monitors, visual, core, logging
import asrt

import psychopy_visual_mock as pvm

# ignore warnings comming from psychopy
logging.console.setLevel(logging.ERROR)

class drawInstructionsTest(unittest.TestCase):

    def setUp(self):
        self.mywindow = None

    def tearDown(self):
        if self.mywindow is not None:
            self.mywindow.close()

    def initWindow(self):
        my_monitor = monitors.Monitor('myMon')
        my_monitor.setSizePix( [1366, 768] )
        my_monitor.setWidth(29)
        my_monitor.saveMon()

        self.mywindow = visual.Window(size = [1366, 768],
                                 pos = [0, 0],
                                 units = 'cm',
                                 fullscr = False,
                                 allowGUI = True,
                                 monitor = my_monitor,
                                 winType = 'pyglet',
                                 color = 'White')

    def constructFilePath(self, file_name):
        filepath = os.path.abspath(__file__)
        (inst_and_feedback_path, trail) = os.path.split(filepath)
        inst_and_feedback_path = os.path.join(inst_and_feedback_path, "data", "instr_and_feedback", file_name)
        return inst_and_feedback_path

    def testDisplaySingleText(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper._InstructionHelper__print_to_screen("Some string with sepcial characters (é,á,ú)", self.mywindow)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        instruction_text = drawing_list[0]
        self.assertTrue(isinstance(instruction_text, pvm.TextStim))
        # size
        self.assertAlmostEqual(instruction_text.height, 0.6, delta = 0.001)
        # pos
        self.assertAlmostEqual(instruction_text.pos[0], 0.0, delta = 0.001)
        self.assertAlmostEqual(instruction_text.pos[1], 0.0, delta = 0.001)
        # color
        self.assertEqual(instruction_text.color, "black")
        # text
        self.assertEqual(instruction_text.text, str("Some string with sepcial characters (é,á,ú)"))

    def testDisplaySingleInstruction(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper._InstructionHelper__show_message(instruction_helper.ending, self.mywindow, exp_settings)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        instruction_text = drawing_list[0]
        self.assertTrue(isinstance(instruction_text, pvm.TextStim))
        # size
        self.assertAlmostEqual(instruction_text.height, 0.6, delta = 0.001)
        # pos
        self.assertAlmostEqual(instruction_text.pos[0], 0.0, delta = 0.001)
        self.assertAlmostEqual(instruction_text.pos[1], 0.0, delta = 0.001)
        # color
        self.assertEqual(instruction_text.color, "black")
        # text
        self.assertEqual(instruction_text.text, str("\r\n\r\nA feladat végetért. Köszönjük a részvételt!\r\n\r\n"))

    def testQuitDisplay(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'

        visual_mock = pvm.PsychoPyVisualMock()
        visual_mock.setReturnKeyList(['q'])
        self.initWindow()
        with self.assertRaises(SystemExit):
            instruction_helper._InstructionHelper__show_message(instruction_helper.ending, self.mywindow, exp_settings)

    def testDisplayEmptyInstructionList(self):

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper = asrt.InstructionHelper()
        instruction_helper._InstructionHelper__show_message(instruction_helper.ending, self.mywindow, exp_settings)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 0)

    def testDisplayMoreInstructions(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper._InstructionHelper__show_message(instruction_helper.insts, self.mywindow, exp_settings)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 3)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nÜdvözlünk a feladatban!\r\n\r\n"
                                                "A képernyőn négy kör lesz, a kör egyikén megjelenik egy kutya.\r\n\r\n"
                                                "Az a feladatod, hogy a kutya megjelenési helyének megfelelő gombot nyomd meg.\r\n\r\n"
                                                "A további instrukciók megtekintéséhez nyomd meg valamelyik válaszgombot!\r\n\r\n")
        self.assertEqual(drawing_list[1].text, "\r\n\r\nA következő billenytűket kell használni: z, c, b, m\r\n\r\n"
                                                "Minél pontosabban és gyorsabban kövesd le a megjelenő ingereket!\r\n\r\n"
                                                "Ehhez mindkét kezedet használd, a középső és mutatóujjaidat.\r\n\r\n"
                                                "A kutya egymás után többször ugyanazon a helyen is megjelenhet.\r\n\r\n"
                                                "A további instrukciók megtekintéséhez nyomd meg valamelyik válaszgombot!\r\n\r\n")
        self.assertEqual(drawing_list[2].text, "\r\n\r\nKb. percenként fogsz visszajelzést kapni arról,\r\n"
                                                "hogy mennyire voltál gyors és pontos - ez alapján tudsz módosítani.\r\n\r\n"
                                                "A feladat indításához nyomd meg valamelyik válaszgombot!\r\n\r\n")

    def testShowInstruction(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper.show_instructions(self.mywindow, exp_settings)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 3)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nÜdvözlünk a feladatban!\r\n\r\n"
                                                "A képernyőn négy kör lesz, a kör egyikén megjelenik egy kutya.\r\n\r\n"
                                                "Az a feladatod, hogy a kutya megjelenési helyének megfelelő gombot nyomd meg.\r\n\r\n"
                                                "A további instrukciók megtekintéséhez nyomd meg valamelyik válaszgombot!\r\n\r\n")
        self.assertEqual(drawing_list[1].text, "\r\n\r\nA következő billenytűket kell használni: z, c, b, m\r\n\r\n"
                                                "Minél pontosabban és gyorsabban kövesd le a megjelenő ingereket!\r\n\r\n"
                                                "Ehhez mindkét kezedet használd, a középső és mutatóujjaidat.\r\n\r\n"
                                                "A kutya egymás után többször ugyanazon a helyen is megjelenhet.\r\n\r\n"
                                                "A további instrukciók megtekintéséhez nyomd meg valamelyik válaszgombot!\r\n\r\n")
        self.assertEqual(drawing_list[2].text, "\r\n\r\nKb. percenként fogsz visszajelzést kapni arról,\r\n"
                                                "hogy mennyire voltál gyors és pontos - ez alapján tudsz módosítani.\r\n\r\n"
                                                "A feladat indításához nyomd meg valamelyik válaszgombot!\r\n\r\n")

    def testShowUnexpectedQuit(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper.show_unexp_quit(self.mywindow, exp_settings)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nVáratlan kilépés történt a feladatból. Folytatás. A feladat indításához nyomd meg valamelyik válaszbillentyűt.")

    def testShowEnding(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper.show_ending(self.mywindow, exp_settings)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nA feladat végetért. Köszönjük a részvételt!\r\n\r\n")

    def testShowImplicitFeedbackNoWarning(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'
        exp_settings.whether_warning = False

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        return_value = instruction_helper.feedback_implicit("450.2", 92.123, "92.123", self.mywindow, exp_settings)

        self.assertEqual(return_value, "continue")

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nMost pihenhetsz egy kicsit.\r\n\r\n"
                                               "Pontosságod: 92.123 %\r\n"
                                               "Átlagos reakcióidőd: 450.2 másodperc\r\n\r\n\r\n")
                                               
    def testShowImplicitFeedbackQuit(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'
        exp_settings.whether_warning = True
        exp_settings.acc_warning = 90
        exp_settings.speed_warning = 94

        visual_mock = pvm.PsychoPyVisualMock()
        visual_mock.setReturnKeyList(['q'])
        self.initWindow()
        return_value = instruction_helper.feedback_implicit("450.2", 92.123, "92.123", self.mywindow, exp_settings)

        self.assertEqual(return_value, "quit")

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nMost pihenhetsz egy kicsit.\r\n\r\n"
                                               "Pontosságod: 92.123 %\r\n"
                                               "Átlagos reakcióidőd: 450.2 másodperc\r\n\r\n\r\n")

    def testShowImplicitFeedbackAccuracyWarning(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'
        exp_settings.whether_warning = True
        exp_settings.acc_warning = 90
        exp_settings.speed_warning = 94

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper.feedback_implicit("450.2", 52.123, "52.123", self.mywindow, exp_settings)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nMost pihenhetsz egy kicsit.\r\n\r\n"
                                               "Pontosságod: 52.123 %\r\n"
                                               "Átlagos reakcióidőd: 450.2 másodperc\r\n\r\n"
                                               "Legyél pontosabb!\r\n\r\n\r\n\r\n")

    def testShowImplicitFeedbackSpeedWarning(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'
        exp_settings.whether_warning = True
        exp_settings.acc_warning = 90
        exp_settings.speed_warning = 94

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper.feedback_implicit("450.2", 96.123, "96.123", self.mywindow, exp_settings)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nMost pihenhetsz egy kicsit.\r\n\r\n"
                                               "Pontosságod: 96.123 %\r\n"
                                               "Átlagos reakcióidőd: 450.2 másodperc\r\n\r\n"
                                               "Legyél gyorsabb!\r\n\r\n\r\n\r\n")

    def testShowExplicitFeedbackNoWarning(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'
        exp_settings.whether_warning = False

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        return_value = instruction_helper.feedback_explicit("450.2", "410.2", "90.123", 92.123, "92.123", self.mywindow, exp_settings)

        self.assertEqual(return_value, "continue")

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nMost pihenhetsz egy kicsit.\r\n\r\n"
                                               "Pontosságod általában: 92.123 %\r\n"
                                               "Átlagos reakcióidőd: 450.2 másodperc\r\n"
                                               "Pontosságod a bejósolható elemeknél: 90.123 %\r\n"
                                               "Átlagos reakcióidőd a bejósolható elemeknél: 410.2 másodperc\r\n\r\n\r\n")

    def testShowExplicitFeedbackQuit(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'
        exp_settings.whether_warning = False

        visual_mock = pvm.PsychoPyVisualMock()
        visual_mock.setReturnKeyList(['q'])
        self.initWindow()
        return_value = instruction_helper.feedback_explicit("450.2", "410.2", "90.123", 92.123, "92.123", self.mywindow, exp_settings)

        self.assertEqual(return_value, "quit")

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nMost pihenhetsz egy kicsit.\r\n\r\n"
                                               "Pontosságod általában: 92.123 %\r\n"
                                               "Átlagos reakcióidőd: 450.2 másodperc\r\n"
                                               "Pontosságod a bejósolható elemeknél: 90.123 %\r\n"
                                               "Átlagos reakcióidőd a bejósolható elemeknél: 410.2 másodperc\r\n\r\n\r\n")

    def testShowExplicitFeedbackAccuracyWarning(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'
        exp_settings.whether_warning = True
        exp_settings.acc_warning = 90
        exp_settings.speed_warning = 94

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper.feedback_explicit("450.2", "410.2", "90.123", 52.123, "52.123", self.mywindow, exp_settings)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nMost pihenhetsz egy kicsit.\r\n\r\n"
                                               "Pontosságod általában: 52.123 %\r\n"
                                               "Átlagos reakcióidőd: 450.2 másodperc\r\n"
                                               "Pontosságod a bejósolható elemeknél: 90.123 %\r\n"
                                               "Átlagos reakcióidőd a bejósolható elemeknél: 410.2 másodperc\r\n\r\n"                                               
                                               "Legyél pontosabb!\r\n\r\n\r\n\r\n")

    def testShowExplicitFeedbackSpeedWarning(self):
        inst_and_feedback_path = self.constructFilePath("default.txt")
        instruction_helper = asrt.InstructionHelper()
        instruction_helper.read_insts_from_file(inst_and_feedback_path)

        exp_settings = asrt.ExperimentSettings()
        exp_settings.key1 = 'z'
        exp_settings.key2 = 'c'
        exp_settings.key3 = 'b'
        exp_settings.key4 = 'm'
        exp_settings.key_quit = 'q'
        exp_settings.whether_warning = True
        exp_settings.acc_warning = 90
        exp_settings.speed_warning = 94

        visual_mock = pvm.PsychoPyVisualMock()
        self.initWindow()
        instruction_helper.feedback_explicit("450.2", "410.2", "90.123", 96.123, "96.123", self.mywindow, exp_settings)

        drawing_list = visual_mock.getListOfDrawings()
        self.assertEqual(len(drawing_list), 1)

        self.assertEqual(drawing_list[0].text, "\r\n\r\nMost pihenhetsz egy kicsit.\r\n\r\n"
                                               "Pontosságod általában: 96.123 %\r\n"
                                               "Átlagos reakcióidőd: 450.2 másodperc\r\n"
                                               "Pontosságod a bejósolható elemeknél: 90.123 %\r\n"
                                               "Átlagos reakcióidőd a bejósolható elemeknél: 410.2 másodperc\r\n\r\n"                                               
                                               "Legyél gyorsabb!\r\n\r\n\r\n\r\n")

if __name__ == "__main__":
    unittest.main() # run all tests 