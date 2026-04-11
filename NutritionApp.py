from Config import dbFilePath
from UserInterface import uiMainWindow
from MacroDetermination import MacroDetermination
from TargetManager import TargetManager
from ClassifierModel import ClassifyItem
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
    def __init__(self):
        super().__init__()
        
        # Object instatiation
        self.db = myDatabase()
        self.macro = MacroDetermination(self.db)

        # Initialize UI
        self.setupUi(self)
        self.Get_Targets()
        self.Setup_Chart()
        self.Refresh_Chart()
        self.MyFunctions()

    def MyFunctions(self):
        self.comboBoxTimeframe.currentIndexChanged.connect(self.Refresh_Chart)
        self.pbTargets.clicked.connect(self.Set_Targets)
        self.pbLogFood.clicked.connect(self.Log_Food)

    def Setup_Chart(self):
        font = QFont('Arial', 12)
        fontBold = QFont('Arial', 12, QFont.Bold)

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
        timePeriod = self.comboBoxTimeframe.currentText()
        today = date.today()
        self.db.open(dbFilePath)
        if timePeriod in ['Today', 'This Week', 'This Month']:
            if timePeriod == 'This Week':
                periodStart = today - timedelta(days=today.weekday())
                periodEnd = periodStart + timedelta(days=6)
                strSql = f'SELECT * FROM ConsumptionHistory WHERE ConsDate BETWEEN "{periodStart}" AND "{periodEnd}"'
                periodLen = today.weekday() + 1
            elif timePeriod == 'This Month':
                _, numDays = calendar.monthrange(today.year, today.month)
                periodStart = today.replace(day=1)
                periodEnd = date(today.year, today.month, day=numDays)
                strSql = f'SELECT * FROM ConsumptionHistory WHERE ConsDate BETWEEN "{periodStart}" AND "{periodEnd}"'
                periodLen = today.day
            else:
                strSql = f'SELECT * FROM ConsumptionHistory WHERE ConsDate = "{today}"'
                periodLen = 1
            records = self.db.mySqlQuery(strSql)
        else:
            records = self.db.getTableDataSorted('ConsumptionHistory', 'ConsDate', 'ASC')
            startDate = datetime.strptime(records[0][1], '%Y-%m-%d')
            endDate = datetime.strptime(records[-1][1], '%Y-%m-%d')
            periodLen = (endDate - startDate).days + 1
        self.db.close()
        return records, periodLen

    def Calculate_Consumption_Totals(self, records, periodLen):
        netCarbKcal, proteinKcal, totalFatKcal, satFat_g, addedSugar_g = 0, 0, 0, 0, 0
        self.db.open(dbFilePath)
        for record in records:
            foodId = record[2]
            portionSize = float(record[3])
            nutritionData = self.db.queryColumnData('FoodItems', ['NutritionData'], 
                                                    [{'condition': f'FoodId = {foodId}', 'operator': ''}])
            if nutritionData:
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
            for i, (k,v) in enumerate(self.targets.items()):
                self.targetSet.replace(i, v.value if v.format == 'Percent' else 100)
            self.Refresh_Chart()

    def Get_Targets(self):
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
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('Select method')
        msg.setText('How do you want to log your item?')
        msg.addButton(QtWidgets.QPushButton('Enter Manually'), QtWidgets.QMessageBox.AcceptRole)
        msg.addButton(QtWidgets.QPushButton('Upload Photo'), QtWidgets.QMessageBox.AcceptRole)
        msg.addButton(QtWidgets.QPushButton('Cancel'), QtWidgets.QMessageBox.AcceptRole)
        importMode = msg.exec()
        if importMode == 0:
            foodItem, ok = QtWidgets.QInputDialog.getText(None, 'Item Name', 'Enter item name:')
            if not ok:
                return
        elif importMode == 1:
            fileDialog = QtWidgets.QFileDialog()
            fileDialog.setWindowTitle("Select a Photo")
            fileDialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
            fileDialog.setNameFilter("Images (*.png *.jpg *.jpeg);;All Files (*)")
            if fileDialog.exec():
                print(fileDialog.selectedFiles())
                foodItem = ClassifyItem(fileDialog.selectedFiles())
            else:
                return
        else:
            return
        # Macronutrient determination here
        self.macro.Handle_Item(foodItem)

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