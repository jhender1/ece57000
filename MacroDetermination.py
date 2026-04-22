"""
File:           MacroDetermination.py
Author:         Joshua Henderson
Date Created:   2026-03-22
Last Modified:  2026-04-22

Course:         ECE 57000
Instructor:     Chaoyue Liu
Assignment:     Course Project

Description:
    MacroDetermination.py is used to determine the correct macronutrient composition for the food item being logged to 
    the local database.  The class checks first to see if the nutrient information has already been stored locally, to 
    avoid unnecessarily prompting the user to specify the nutritional content for the food item.  If nutritional content
    is not found, MacroDetermination uses the FoodSearch class to assist the user with determining the correct 
    nutritional content for the food item.  Once the correct nutritional content has been determined, the class logs the
    new nutritional content information to the local database.

Dependencies: see dependencies.txt

Usage: FOR TESTING PURPOSES ONLY
    1. Edit the item label for the food to be classified (Line 84)
    2. From a Windows Powershell terminal, navigate to the project root directory.
    3. Execute .\.venv\Scripts\Activate.ps1
    4. Execute .\.venv\scripts\python.exe NutritionApp.py
"""

from datetime import date
from Config import dbFilePath
from PyQt5 import QtWidgets
from FoodSearch import FoodSearch

class MacroDetermination:
    def __init__(self, db):
        # Instantiate the local database
        self.db = db
    
    def Handle_Item(self, foodItem):
        """Identify the nutritional content for the specified foodItem"""
        self.db.open(dbFilePath)
        
        # Search for the food item in the local database
        result = self.db.RecordExists('FoodItems', {'key':'ClassLabel','idx':foodItem})
        if result:
            # Nutrition content found for the specified food item, log the item to the consumption history table
            queryCondition = f'ClassLabel = "{foodItem}"'
            foodId = self.db.queryColumnData('FoodItems', ['FoodId'], [{'condition': queryCondition,'operator': ''}])[0][0]
            self.Log_Consumption(foodItem, foodId)
        else:
            # Item not found, use FoodSearch dialog to determine the nutrition content for the specified food item
            fsDialog = QtWidgets.QDialog()
            fs = FoodSearch(fsDialog, foodItem)
            if fsDialog.exec():
                # User selected nutrition content for the food item, store the nutrition content in the local database 
                # and log the item to the consumption history table
                fields = tuple(['ClassLabel','FdcId','FdcDescription', 'ServingSize','NutritionData'])
                data = tuple([foodItem, 
                              fs.currentFood.fdc_id, 
                              fs.currentFood.description, 
                              fs.servingSize, 
                              fs.Nutrients_to_JSON()])
                foodId = self.db.addRecord('FoodItems', fields, data)
                self.Log_Consumption(foodItem, foodId)
            else:
                # user cancelled, do not log
                pass
        self.db.close()

    def Log_Consumption(self, foodItem, foodId):
        """Log the food item in the consumption history table"""
        # Prompt the user for the portion size of the food that was consumed
        portionSize, ok = QtWidgets.QInputDialog.getText(None, 'Portion Size', f'Logging item: {foodItem} \r\nEnter portion size:')
        if not ok:
            # User cancelled, do not log
            return
        fields = tuple(['FoodItem', 'PortionSize', 'ConsDate'])
        data = tuple([foodId, portionSize, date.today().isoformat()])
        self.db.addRecord('ConsumptionHistory', fields, data)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    macro = MacroDetermination()
    macro.Handle_Item('pork chop')