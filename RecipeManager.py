from UserInterface import uiRecipeDialog

class RecipeManager(uiRecipeDialog.Ui_RecipeDialog):
    def __init__(self, dialog):
        self.setupUi(dialog)