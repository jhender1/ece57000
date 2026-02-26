from UserInterface import uiMainWindow
from PyQt5 import QtWidgets
from RecipeManager import RecipeManager
from ClassifierModel import ClassifyItem

from ctypes import windll

class NutritionApp(QtWidgets.QMainWindow, uiMainWindow.Ui_NutritionApp):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.MyFunctions()

    def MyFunctions(self):
        self.comboBoxTimeframe.currentIndexChanged.connect(self.RefreshChart)
        self.pbRecipe.clicked.connect(self.AddRecipe)
        self.pbLogFood.clicked.connect(self.LogFood)

    def RefreshChart(self):
        print('Called Refresh Chart')

    def AddRecipe(self):
        recipeDialog = QtWidgets.QDialog()
        RecipeObj = RecipeManager(recipeDialog)
        if recipeDialog.exec():
            print('Store Recipe in Database')
    
    def LogFood(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('Select method')
        msg.setText('How do you want to log your item?')
        msg.addButton(QtWidgets.QPushButton('Enter Manually'), QtWidgets.QMessageBox.AcceptRole)
        msg.addButton(QtWidgets.QPushButton('Upload Photo'), QtWidgets.QMessageBox.AcceptRole)
        msg.addButton(QtWidgets.QPushButton('Cancel'), QtWidgets.QMessageBox.AcceptRole)
        importMode = msg.exec()
        if importMode == 0:
            itemLabel, ok = QtWidgets.QInputDialog.getText(None, 'Item Name', 'Enter item name:')
            if not ok:
                return
        elif importMode == 1:
            fileDialog = QtWidgets.QFileDialog()
            fileDialog.setWindowTitle("Select a Photo")
            fileDialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
            fileDialog.setNameFilter("Images (*.png *.jpg *.jpeg);;All Files (*)")
            if fileDialog.exec():
                print(fileDialog.selectedFiles())
                itemLabel = ClassifyItem(fileDialog.selectedFiles())
            else:
                return
        else:
            return
        print(itemLabel)

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
    print(MainWindow.size())
    print(MainWindow.centralWidget().size())
    sys.exit(app.exec_())