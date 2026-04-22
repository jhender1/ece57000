"""
File:           TargetManager.py
Author:         Joshua Henderson
Date Created:   2026-03-28
Last Modified:  2026-04-22

Course:         ECE 57000
Instructor:     Chaoyue Liu
Assignment:     Course Project

Description:
    TargetManager.py presents the user with a dialog box that allows specification of the macronutrient targets for the 
    user's preferred diet.  The specified target values are then stored in the local database.

Dependencies: see dependencies.txt

Usage: TargetManager.py is not intended to be executed directly.  For testing purposes, the TargetManager class was 
tested in conjunction with NutritionApp.py
"""

import numpy as np
from UserInterface import uiTargetDialog
from PyQt5.QtWidgets import QDialogButtonBox

class TargetManager(uiTargetDialog.Ui_macroTargets):
    def __init__(self, dialog, targets):
        # Initialize UI, 'targets' contains the current target values stored in the database
        self.setupUi(dialog)
        self.dblCarbs.setValue(targets['Net Carbs'].value)
        self.dblProtein.setValue(targets['Protein'].value)
        self.dblFat.setValue(targets['Total Fat'].value)
        self.dblSatFat.setValue(targets['Saturated Fat'].value)
        self.dblSugar.setValue(targets['Added Sugar'].value)
        self.lblWarning.setVisible(False)

        self.myFunctions()

    def myFunctions(self):
        """Connect all GUI events to their corresponding handler functions"""
        self.dblCarbs.valueChanged.connect(self.Validate_Percentages)
        self.dblProtein.valueChanged.connect(self.Validate_Percentages)
        self.dblFat.valueChanged.connect(self.Validate_Percentages)
    
    def Validate_Percentages(self):
        # The total percentages for carbohydrates, total fat, and protein must sum to 100%.  
        # Validate user input each time a value is changed.
        total = self.dblCarbs.value() + self.dblProtein.value() + self.dblFat.value()
        if np.isclose(total, 100):
            # Percentages total 100%, hide warning and enable the OK button
            self.lblWarning.setVisible(False)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            # Percentages do not total 100%, show warning and disable the OK button
            self.lblWarning.setVisible(True)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
