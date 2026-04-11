from UserInterface import uiFoodSearch
from PyQt5 import QtWidgets
from Config import nutrientIds, API_KEY
from usda_fdc import FdcClient
import json

class FoodSearch(uiFoodSearch.Ui_FoodSearchDialog):
    def __init__(self, dialog, foodItem):
        # Initialize variables
        self.foodItem = foodItem
        self.servingSize = 100
        self.currentRow = -1
        self.searchPage = 1
        self.searchList = []

        # Initialize UI
        self.setupUi(dialog)
        self.checkBoxes = [
            (self.cbFoundation,'Foundation'),
            (self.cbSrLegacy,'SR Legacy'),
            (self.cbBranded,'Branded')]
        nutrientsRows = 9
        self.foodListRows = 20
        self.dblSvgSize.setValue(self.servingSize)
        self.tableNutrients.setVerticalHeaderLabels(list(nutrientIds.keys()))
        self.tableNutrients.setFixedHeight(self.tableNutrients.verticalHeader().defaultSectionSize() * nutrientsRows
                     + self.tableNutrients.horizontalHeader().height()
                     + self.tableNutrients.frameWidth() * 2)
        self.tableList.setFixedHeight(self.tableList.verticalHeader().defaultSectionSize() * self.foodListRows
                     + self.tableNutrients.frameWidth() * 2)
        self.cbFoundation.setChecked(True)
        self.cbSrLegacy.setChecked(False)
        self.cbBranded.setChecked(False)
        
        # Object instatiation & additional functions
        self.fdc = FdcClient(API_KEY)
        self.myFunctions()
        self.Update_List()
    
    def myFunctions(self):
        self.pbMore.clicked.connect(self.Get_More_Items)
        self.tableList.cellClicked.connect(self.Update_Food)
        self.dblSvgSize.valueChanged.connect(self.Update_Serving_Size)
    
    def Get_More_Items(self):
        self.searchPage += 1
        self.searchPage = 1 if self.searchPage > self.curSearchList.total_pages else self.searchPage
        self.Update_List()

    def Update_List(self):
        self.tableList.clearContents()
        self.tableList.clearSelection()
        self.tableNutrients.clearContents()
        oldSearchList = self.searchList
        self.searchList = [label for cb, label in self.checkBoxes if cb.isChecked()]
        self.searchPage = self.searchPage if self.searchList == oldSearchList else 1
        self.currentRow = -1
        if self.searchList:
            self.curSearchList = self.fdc.search(self.foodItem, data_type = self.searchList, 
                                                 page_size=self.foodListRows, page_number=self.searchPage)
            for row, value in enumerate(self.curSearchList.foods):
                self.tableList.setItem(row, 0, QtWidgets.QTableWidgetItem(value.description))
            self.tableList.resizeColumnsToContents()

    def Update_Food(self):
        self.servingSize = 100
        self.dblSvgSize.setValue(self.servingSize)
        self.currentRow = self.tableList.selectedItems()[0].row()
        self.currentFood = self.fdc.get_food(self.curSearchList.foods[self.currentRow].fdc_id, 
                                                  format='full', nutrients=list(nutrientIds.values()))
        self.Update_Nutrients()

    def Update_Serving_Size(self):
        self.servingSize = self.dblSvgSize.value()
        if self.currentRow >= 0:
            self.Update_Nutrients()

    def Update_Nutrients(self):
        self.tableNutrients.clearContents()
        for i, (_, value) in enumerate(nutrientIds.items()):
            for nutrient in self.currentFood.nutrients:
                if int(nutrient.nutrient_nbr) == value:
                    amt = self.servingSize / 100 * nutrient.amount
                    cellValue = f'{amt:.2f} {nutrient.unit_name}'
                    self.tableNutrients.setItem(i, 0, QtWidgets.QTableWidgetItem(cellValue))

    def Nutrients_to_JSON(self):
        nutrientDict = {}
        for row in range(self.tableNutrients.rowCount()):
            key = self.tableNutrients.verticalHeaderItem(row).text().strip()
            item = self.tableNutrients.item(row,0)
            value = float(item.text().split(' ')[0]) if item else 0
            nutrientDict[key] = value
        return json.dumps(nutrientDict)