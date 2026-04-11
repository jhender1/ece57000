import numpy as np
from UserInterface import uiTargetDialog
from PyQt5.QtWidgets import QDialogButtonBox

class TargetManager(uiTargetDialog.Ui_macroTargets):
    def __init__(self, dialog, targets):
        self.setupUi(dialog)
        self.dblCarbs.setValue(targets['Net Carbs'].value)
        self.dblProtein.setValue(targets['Protein'].value)
        self.dblFat.setValue(targets['Total Fat'].value)
        self.dblSatFat.setValue(targets['Saturated Fat'].value)
        self.dblSugar.setValue(targets['Added Sugar'].value)
        self.lblWarning.setVisible(False)

        self.myFunctions()

    def myFunctions(self):
        self.dblCarbs.valueChanged.connect(self.Validate_Percentages)
        self.dblProtein.valueChanged.connect(self.Validate_Percentages)
        self.dblFat.valueChanged.connect(self.Validate_Percentages)
    
    def Validate_Percentages(self):
        total = self.dblCarbs.value() + self.dblProtein.value() + self.dblFat.value()
        if np.isclose(total, 100):
            self.lblWarning.setVisible(False)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.lblWarning.setVisible(True)
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
