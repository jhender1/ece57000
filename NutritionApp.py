"""
File:           NutritionApp.py
Author:         Joshua Henderson
Date Created:   2026-02-26
Last Modified:  2026-04-22

Course:         ECE 57000
Instructor:     Chaoyue Liu
Assignment:     Course Project

Description:
    NutritionApp.py contains the class definition for the NutritionApp class.  NutritionApp is the top level food 
    journal application.  When executed, the class presents the top level GUI to the user and handles data visualization
    and user interactions.  The class inherits QMainWindow and Ui_NutritionApp.  Ui_NutritionApp is an auto-generated 
    class that is compiled from a UI created using QT Designer.

Dependencies: see dependencies.txt

Usage:
    1. From a Windows Powershell terminal, navigate to the project root directory.
    2. Execute .\.venv\Scripts\Activate.ps1
    3. Execute .\.venv\scripts\python.exe NutritionApp.py
"""

from Model import ClassifierModel
from Config import dbFilePath
from UserInterface import uiMainWindow
from MacroDetermination import MacroDetermination
from TargetManager import TargetManager
from Database.Database import myDatabase
from PyQt5 import QtWidgets
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QFont
from ctypes import windll
from datetime import datetime, date, timedelta
import calendar
import json
import numpy as np

FAT_KCAL_PER_GRAM = 9
PROTEIN_KCAL_PER_GRAM = 4
CARB_KCAL_PER_GRAM = 4

class NutritionTarget:
    dbkey = 0
    value = 0
    format = 'Amount'

class NutritionApp(QtWidgets.QMainWindow, uiMainWindow.Ui_NutritionApp):
    # NutritionApp is the top level class that presents the top level GUI and handles user interactions
    def __init__(self):
        super().__init__()
        
        # Object instatiation
        self.db = myDatabase()
        self.macro = MacroDetermination(self.db)
        self.cm = ClassifierModel.ClassifierModel()

        # Initialize UI
        self.setupUi(self)
        self.Get_Targets()
        self.Setup_Chart()
        self.Refresh_Chart()
        self.MyFunctions()

    def MyFunctions(self):
        """Connect all GUI events to their corresponding handler functions"""
        self.comboBoxTimeframe.currentIndexChanged.connect(self.Refresh_Chart)
        self.pbTargets.clicked.connect(self.Set_Targets)
        self.pbLogFood.clicked.connect(self.Log_Food)

    def Setup_Chart(self):
        """Initialize the consumption history chart"""
        font = QFont('Arial', 12)
        fontBold = QFont('Arial', 12, QFont.Bold)

        #[Net Carbs, Protein, Total Fat, Saturated Fat, Added Sugar]
        values = [0,0,0,0,0]
        targets = [target.value if target.format == 'Percent' else 100 for target in self.targets.values()]

        self.valueSet = QBarSet('Amount Consumed')
        self.targetSet = QBarSet('Target')

        self.valueSet.append(values)
        self.targetSet.append(targets)

        series = QBarSeries()
        series.append(self.valueSet)
        series.append(self.targetSet)

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(font)

        axisX = QBarCategoryAxis()
        axisX.append(self.targets.keys())
        axisX.setLabelsFont(fontBold)
        axisX.setLabelsAngle(-45)
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        self.axisYLeft = QValueAxis()
        self.axisYLeft.setLabelFormat('%.0f%%')
        self.axisYLeft.setTitleText('percent (%)')
        self.axisYLeft.setRange(0, 100)
        self.axisYLeft.setTitleFont(fontBold)
        self.axisYLeft.setLabelsFont(font)
        chart.addAxis(self.axisYLeft, Qt.AlignLeft)
        series.attachAxis(self.axisYLeft)

        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)
        self.chartWidget.setChart(chart)
        self.chartWidget.setRenderHint(QPainter.Antialiasing)

    def Refresh_Chart(self):
        """Update the consumption history chart whenever data needs to be changed"""
        records, periodLen = self.Get_Consumption_Records()
        chartTotals, avgKcal = self.Calculate_Consumption_Totals(records, periodLen)
        for i, v in enumerate(chartTotals):
            self.valueSet.replace(i, v)
        self.dblAvgKcal.setValue(avgKcal)
        chartValues = [self.valueSet.at(i) for i in range(self.valueSet.count())] + \
        [self.targetSet.at(i) for i in range(self.targetSet.count())]
        chartMax = np.ceil(max(chartValues)*1.1/25)*25 if max(chartValues) > 0 else 100
        self.axisYLeft.setRange(0, chartMax)
        self.axisYLeft.setTickCount(int(chartMax / 25)+1)
    
    def Get_Consumption_Records(self):
        """Gets consumption history records from the database that match the user selected timeframe"""
        timePeriod = self.comboBoxTimeframe.currentText()
        today = date.today()
        self.db.open(dbFilePath)

        # Build the appropriate database query string based on the user selected time period
        if timePeriod in ['Today', 'This Week', 'This Month']:
            if timePeriod == 'This Week':
                # Get records for the current week, beginning on the previous Monday
                periodStart = today - timedelta(days=today.weekday())
                periodEnd = periodStart + timedelta(days=6)
                strSql = f'SELECT * FROM ConsumptionHistory WHERE ConsDate BETWEEN "{periodStart}" AND "{periodEnd}"'
                periodLen = today.weekday() + 1
            elif timePeriod == 'This Month':
                # Get records for the current month
                _, numDays = calendar.monthrange(today.year, today.month)
                periodStart = today.replace(day=1)
                periodEnd = date(today.year, today.month, day=numDays)
                strSql = f'SELECT * FROM ConsumptionHistory WHERE ConsDate BETWEEN "{periodStart}" AND "{periodEnd}"'
                periodLen = today.day
            else:
                # Get records for today
                strSql = f'SELECT * FROM ConsumptionHistory WHERE ConsDate = "{today}"'
                periodLen = 1
            # No helper functions for date/time window based queries.  Build the query string manually and then execute.
            records = self.db.mySqlQuery(strSql)
        else:
            # Get all records in the database
            records = self.db.getTableDataSorted('ConsumptionHistory', 'ConsDate', 'ASC')
            startDate = datetime.strptime(records[0][1], '%Y-%m-%d')
            endDate = datetime.strptime(records[-1][1], '%Y-%m-%d')
            periodLen = (endDate - startDate).days + 1
        self.db.close()
        return records, periodLen

    def Calculate_Consumption_Totals(self, records, periodLen):
        """Iterate through a set of consumption history records and aggregate the nutritional information by nutrient 
        type"""
        netCarbKcal, proteinKcal, totalFatKcal, satFat_g, addedSugar_g = 0, 0, 0, 0, 0
        self.db.open(dbFilePath)
        # For each record in the input parameter set
        for record in records:
            foodId = record[2]
            portionSize = float(record[3])
            # Get the nutrition information for the food item
            nutritionData = self.db.queryColumnData('FoodItems', ['NutritionData'], 
                                                    [{'condition': f'FoodId = {foodId}', 'operator': ''}])
            # Validate database query
            if nutritionData:
                # Nutrition data for the item was found in the database
                nd = json.loads(nutritionData[0][0])
                netCarbKcal += (nd['Total Carbohydrates'] - nd['Dietary Fiber']) * portionSize * CARB_KCAL_PER_GRAM
                proteinKcal += nd.get('Protein', 0) * portionSize * PROTEIN_KCAL_PER_GRAM
                totalFatKcal += nd.get('Total Fat', 0) * portionSize * FAT_KCAL_PER_GRAM
                satFat_g += nd.get('Saturated Fat', 0) * portionSize
                addedSugar_g += nd.get('Added Sugar', 0) * portionSize
        self.db.close()

        # Convert macronutrient totals to percentage of total calories
        values = np.array([netCarbKcal, proteinKcal, totalFatKcal])
        totalKcal = values.sum()
        avgKcal = totalKcal / periodLen
        values = values / totalKcal * 100 if totalKcal > 0 else np.zeros_like(values)

        # Convert saturated fat and added sugar to percentage of their upper limits
        satFatPct = satFat_g / periodLen / self.targets['Saturated Fat'].value * 100
        addedSugarPct = addedSugar_g /periodLen / self.targets['Added Sugar'].value * 100
        return [values[0], values[1], values[2], satFatPct, addedSugarPct], avgKcal

    def Set_Targets(self):
        """Promt the user to enter their target amounts for each nutrient type and store the result in the database"""
        dialog = QtWidgets.QDialog()
        targetManager = TargetManager(dialog, self.targets)
        if dialog.exec():
            self.db.open(dbFilePath)
            self.targets['Net Carbs'].value = targetManager.dblCarbs.value()
            self.targets['Protein'].value = targetManager.dblProtein.value()
            self.targets['Total Fat'].value = targetManager.dblFat.value()
            self.targets['Saturated Fat'].value = targetManager.dblSatFat.value()
            self.targets['Added Sugar'].value = targetManager.dblSugar.value()
            self.db.updateRecord({'key': 'id', 'idx': self.targets['Net Carbs'].dbkey}, 
                                 'Targets', ['TargetValue'], [targetManager.dblCarbs.value()])
            self.db.updateRecord({'key': 'id', 'idx': self.targets['Protein'].dbkey}, 
                                 'Targets', ['TargetValue'], [targetManager.dblProtein.value()])
            self.db.updateRecord({'key': 'id', 'idx': self.targets['Total Fat'].dbkey}, 
                                 'Targets', ['TargetValue'], [targetManager.dblFat.value()])
            self.db.updateRecord({'key': 'id', 'idx': self.targets['Saturated Fat'].dbkey}, 
                                 'Targets', ['TargetValue'], [targetManager.dblSatFat.value()])
            self.db.updateRecord({'key': 'id', 'idx': self.targets['Added Sugar'].dbkey}, 
                                 'Targets', ['TargetValue'], [targetManager.dblSugar.value()])
            self.db.close()
            
            # For adverse nutrient types, the target is an upper limi which is set to 100% for display purposes 
            for i, (k,v) in enumerate(self.targets.items()):
                self.targetSet.replace(i, v.value if v.format == 'Percent' else 100)
            # Refresh the chart with the the updated targets 
            self.Refresh_Chart()

    def Get_Targets(self):
        """Gets nutrient target records from the database"""
        self.db.open(dbFilePath)
        self.targets = {}
        targets = self.db.getTableData('Targets')
        for record in targets:
            obj = NutritionTarget()
            key = record[1]
            obj.dbkey = record[0]
            obj.value = record[2]
            obj.format = record[3]
            self.targets[key] = obj
        self.db.close()

    def Log_Food(self):
        """Add a new food to the consumption history table.  First, prompt the user for the logging method.  Users can 
        either type the class label manually or upload a photo of the food item.  Photos are handled by the classifier 
        model while for manual label entry the function bypasses the classifier model and proceeds directly to 
        macronutrient determination"""
        
        # Prompt the user to select an update method
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('Select method')
        msg.setText('How do you want to log your item?')
        msg.addButton(QtWidgets.QPushButton('Enter Manually'), QtWidgets.QMessageBox.AcceptRole)
        msg.addButton(QtWidgets.QPushButton('Upload Photo'), QtWidgets.QMessageBox.AcceptRole)
        msg.addButton(QtWidgets.QPushButton('Cancel'), QtWidgets.QMessageBox.AcceptRole)
        importMode = msg.exec()
        
        # Handle user response
        if importMode == 0:
            # User selected 'Enter Manually'
            foodItem, ok = QtWidgets.QInputDialog.getText(None, 'Item Name', 'Enter item name:')
            if not ok:
                return
        elif importMode == 1:
            # User selected 'Upload Photo'
            fileDialog = QtWidgets.QFileDialog()
            fileDialog.setWindowTitle("Select a Photo")
            fileDialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
            fileDialog.setNameFilter("Images (*.png *.jpg *.jpeg);;All Files (*)")
            if fileDialog.exec():
                foodItem = self.cm.Classify_Item(fileDialog.selectedFiles()[0])
            else:
                return
        else:
            # User cancelled, do nothing
            return
        
        # Macronutrient determination here
        self.macro.Handle_Item(foodItem)
        self.Refresh_Chart()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # Hide the Python terminal window when app is launched
    GetConsoleWindow = windll.kernel32.GetConsoleWindow
    ShowWindow = windll.user32.ShowWindow
    console_window_handle = GetConsoleWindow()
    ShowWindow(console_window_handle, 0)

    # Start the app
    MainWindow = NutritionApp()
    MainWindow.show()
    sys.exit(app.exec_())