"""
File:           FoodSearch.py
Author:         Joshua Henderson
Date Created:   2026-03-28
Last Modified:  2026-04-22

Course:         ECE 57000
Instructor:     Chaoyue Liu
Assignment:     Course Project

Description:
    FoodSearch.py contains Logic to assist the user with selecting the correct nutrition information for foods that do 
    not exist in the local repository.  The FoodSearch class issues search queries to the USDA FDC database, parses the 
    search results and displays them to the user, and returns the nutritional content selected by by the user.

Dependencies: see dependencies.txt

Usage: FoodSearch.py is not intended to be executed directly.  For testing purposes, the FoodSearch class was tested in 
conjunction with MacroDetermination.py
"""

from UserInterface import uiFoodSearch
from PyQt5 import QtWidgets
from Config import nutrientIds
from ConfigFdc import API_KEY
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
        self.labelFoodItem.setText(self.labelFoodItem.text().replace('***',self.foodItem))
        
        # Object instatiation & additional functions
        self.fdc = FdcClient(API_KEY)
        self.myFunctions()
        self.Update_List()
    
    def myFunctions(self):
        """Connect all GUI events to their corresponding handler functions"""
        self.pbMore.clicked.connect(self.Get_More_Items)
        self.tableList.cellClicked.connect(self.Update_Food)
        self.dblSvgSize.valueChanged.connect(self.Update_Serving_Size)
    
    def Get_More_Items(self):
        """Get the next page of search results from the database query and update the search result list in the GUI.  
        Return to the first search result page after reaching the last search result page."""
        self.searchPage += 1
        self.searchPage = 1 if self.searchPage > self.curSearchList.total_pages else self.searchPage
        self.Update_List()

    def Update_List(self):
        """Update the search result list whenever the list needs to be refreshed."""
        
        self.tableList.clearContents()
        self.tableList.clearSelection()
        self.tableNutrients.clearContents()
        oldSearchList = self.searchList
        # USDA FDC contains several databases that can be queried.  searchList contains the list of databases the user 
        # wants to search 
        self.searchList = [label for cb, label in self.checkBoxes if cb.isChecked()]
        
        # If the search list has changed, issue a new query and present the first page of search results
        self.searchPage = self.searchPage if self.searchList == oldSearchList else 1
        
        # Clear the active row selected by the user
        self.currentRow = -1
        
        # Nothing to do if the user did not select any databases to query
        if self.searchList:
            # User selected at least one database, perform query
            searchTerm = self.foodItem.replace('_', ' ')
            self.curSearchList = self.fdc.search(searchTerm, data_type = self.searchList, 
                                                 page_size=self.foodListRows, page_number=self.searchPage)
            # Refresh the search list in the GUI
            for row, value in enumerate(self.curSearchList.foods):
                self.tableList.setItem(row, 0, QtWidgets.QTableWidgetItem(value.description))
            self.tableList.resizeColumnsToContents()

    def Update_Food(self):
        """Display the nutrition information for the item selected by the user"""
        self.servingSize = 100
        self.dblSvgSize.setValue(self.servingSize)
        self.currentRow = self.tableList.selectedItems()[0].row()
        
        # Query the USDA FDC database to get the nutrition information for the selected food
        self.currentFood = self.fdc.get_food(self.curSearchList.foods[self.currentRow].fdc_id, 
                                                  format='full', nutrients=list(nutrientIds.values()))
        
        # Update_Nutrients parses the query response and displays the updated nutrition information to the user
        self.Update_Nutrients()

    def Update_Serving_Size(self):
        """USDA FDC nutrition information is normalized to a serving size of 100g.  Normalize all nutrient amounts 
        if the user specifies a different serving size."""
        self.servingSize = self.dblSvgSize.value()
        if self.currentRow >= 0:
            self.Update_Nutrients()

    def Update_Nutrients(self):
        """Parses the query response and displays the updated nutrition information to the user"""
        self.tableNutrients.clearContents()
        # Iterate through each nutrient ID tracked by the app
        for i, (_, value) in enumerate(nutrientIds.items()):
            # Iterate through each nutrient ID included in the USDA FDC database query response
            for nutrient in self.currentFood.nutrients:
                if int(nutrient.nutrient_nbr) == value:
                    # Nutrient ID's match, refresh GUI
                    amt = self.servingSize / 100 * nutrient.amount
                    cellValue = f'{amt:.2f} {nutrient.unit_name}'
                    self.tableNutrients.setItem(i, 0, QtWidgets.QTableWidgetItem(cellValue))

    def Nutrients_to_JSON(self):
        """Format the nutrient information for writing to the local database.  Nutrient information is flattened to a 
        JSON string for storage in the sqlite database"""
        nutrientDict = {}
        for row in range(self.tableNutrients.rowCount()):
            key = self.tableNutrients.verticalHeaderItem(row).text().strip()
            item = self.tableNutrients.item(row,0)
            value = float(item.text().split(' ')[0]) if item else 0
            nutrientDict[key] = value
        return json.dumps(nutrientDict)