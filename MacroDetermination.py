from datetime import date
from Config import dbFilePath #, API_KEY, nutrientIds
from PyQt5 import QtWidgets
from FoodSearch import FoodSearch

class MacroDetermination:
    def __init__(self, db):
        self.db = db
    
    def Handle_Item(self, foodItem):
        self.db.open(dbFilePath)
        result = self.db.RecordExists('FoodItems', {'key':'ClassLabel','idx':foodItem})
        if result:
            queryCondition = f'ClassLabel = "{foodItem}"'
            foodId = self.db.queryColumnData('FoodItems', ['FoodId'], [{'condition': queryCondition,'operator': ''}])[0][0]
            self.Log_Consumption(foodItem, foodId)
        else:
            fsDialog = QtWidgets.QDialog()
            fs = FoodSearch(fsDialog, foodItem)
            if fsDialog.exec():
                fields = tuple(['ClassLabel','FdcId','FdcDescription', 'ServingSize','NutritionData'])
                data = tuple([foodItem, 
                              fs.currentFood.fdc_id, 
                              fs.currentFood.description, 
                              fs.servingSize, 
                              fs.Nutrients_to_JSON()])
                foodId = self.db.addRecord('FoodItems', fields, data)
                self.Log_Consumption(foodItem, foodId)
            else:
                pass
        self.db.close()

    def Log_Consumption(self, foodItem, foodId):
        portionSize, ok = QtWidgets.QInputDialog.getText(None, 'Portion Size', f'Logging item: {foodItem} \r\nEnter portion size:')
        if not ok:
            return
        fields = tuple(['FoodItem', 'PortionSize', 'ConsDate'])
        data = tuple([foodId, portionSize, date.today().isoformat()])
        self.db.addRecord('ConsumptionHistory', fields, data)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    macro = MacroDetermination()
    macro.Handle_Item('pork chop')