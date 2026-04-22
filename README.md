# ECE 57000 Final Project

The source code for the CV-Enabled Food Journal Application is divided into two distinct parts. The first part consists of a Jupyter notebook used to perform model evaluation and training. The second part consists of the Python code used to deploy the model and implement the application.  Separate instructions for each part are included below.

# Model Training
Both the training algorithm and dataset can be accessed from the following folder in Google Drive:
[Link](https://drive.google.com/drive/folders/1fSF1zko7vLK-xOSIYfB1jrv_9Nx2bY1m?usp=sharing)

## Code structure
Project/<br>
|--- food-101: Contains the curated Food-101 used to train the Image Classifier model<br>
|--- my-dataset: Contains the final dataset with the Food-101 and VegFru datasets merged into a single dataset<br>
|--- Custom-Dataset-Classifier-Final.ipynb: File containing the final training algorithm used to train the Image Classifier Model<br>
|--- Food101-Classifier-Final.ipynb: File containing the final training algorithm used to train the model on the Food-101 dataset<br>
|--- Food101-Classifier-CP1.ipynb: File containing the training algorithm at Project Checkpoint 1<br>
|--- Food101-Classifier-CP2.ipynb: File containing the training algorithm at Project Checkpoint 2<br>

## Dependencies:
-google.colab.drive<br>
-google.colab.files<br>
-matplotlib.pyplot<br>
-numpy<br>
-torch<br>
-torchvision<br>
-torch.utils.data.random_split<br>
-torch.nn<br>
-torchvision.models.resnet50<br>
-torch.optim<br>
-shutil<br>

## Execution Instructions
Instructions to run the training algorithm from a Windows PC using Google Colab:
1. Copy my-dataset to a Google Drive location which the user can access from Google Colab
2. Open Custom-Dataset-Classifier-Final.ipynb in the Google Colab environment
3. In Cell #4, update the source_path with the location where the dataset was copied in Step #1
4. Recommended, not required: Connect to a GPU-based runtime environment: 
    a. runtime > Change runtime type
    b. Select the desired runtime type.  Most training iterations were performed using a T4 GPU.
    c. Click "Save"
5. Click Run all to execute the full training algorithm
6. When execution of the training algorithm completes, the updated model weights will automatically be downloaded.  Copy 'custom_ds_weights.pth' to the following location in the Prototype Application file structure: <Root>/Model/custom_ds_weights.pth

## Code Reuse
Parts of the code written by the author: (Line numbers correspond to Custom-Dataset-Classifier-Final.ipynb)<br>
The training algorithm was adapted from CIFAR10 tutorial.  See the Final Report document for citation/URL.<br>
Specific lines modified/written by the author:<br>
Cell #1 (Import Statements): Lines 1,2,5,6,7,8,9,10<br>
Cell #2 (GPU Setup): Entire cell written by the author<br>
Cell #3 (Unmount Google Drive): Entire cell written by the author<br>
Cell #4 (Mount Google Drive): Entire cell written by the author<br>
Cell #5 (Load Dataset): All lines modified by the author except lines 20-23<br>
Cell #6 (Visualize Images): No lines modified by the author<br>
Cell #7 (Create Model): Entire cell written by the author<br>
Cell #8 (CreateLoss Function, Optimizer): Lines 4,5<br>
Cell #9 (Training Loop): Lines 1,2,6,9,10,15,22,23,<br>
Cell #10 (Model Evaluation): Lines 1,9,10,<br>
Cell #11 (Save model weights): Entire cell written by the author<br>

# Prototype Application

## Code Structure
root/<br>
|--- .vscode: contains launch.json which defines debug launch configurations used by VS Code<br>
|--- Database<br>
|---|--- Database.py: Python class for interfacing with the local repository; imported by NutritionApp.py<br>
|---|--- FoodLog.db: Local repository, sqlite database<br>
|--- Model<br>
|---|--- ClassifierModel.py: Image Classifier python class; imported by NutritionApp.py<br>
|---|--- custom_ds_weights.pth: Image Classifier Model Weights, loaded upon model instantiation<br>
|---|--- food101_weights.pth: Image Classifer Model Weights obtained by training the Food-101 dataset only; not used in final implementation<br>
|--- Photos: Directory containing sample images used to test the top level application<br>
|--- UserInterface<br>
|---|--- CompileUi.bat: script used to compile the QT Designer files into Python source<br>
|---|--- uiFoodSearch.ui: QT Designer source file for the FoodSearch GUI<br>
|---|--- uiFoodSearch.py: Python source file for the FoodSearch GUI; imported by FoodSearch.py<br>
|---|--- uiMainWindow.ui: QT Designer source file for the top level GUI<br>
|---|--- uiMainWindow.py: Python source file for the top level GUI; imported by NutritionApp.py<br>
|---|--- uiRecipeDialog.ui: QT Designer source file for the RecipeManager GUI; not used in the final implementation<br>
|---|--- uiRecipeDialog.py: Python source file for the RecipeManager GUI; not used in the final implementation<br>
|---|--- uiTargetDialog.ui: QT Designer source file for the TargetDialog GUI<br>
|---|--- uiTargetDialog.py: Python source file for the TargetDialog GUI; imported by TargetManager.py<br>
|--- .gitignore: git configuration file<br>
|--- Config.py: contains helper variables used by the app; imported by NutritionApp.py, ClassifierModel.py, MacroDetermination.py, FoodSearch.py<br>
|--- dependencies.txt: list of all Python dependencies required by the food journal application
|--- FoodSearch.py: Class to assist the user with searching the USDA FDC database; imported by MacroDetermination.py<br>
|--- MacroDetermination.py: Class for determining macronutrient composition; imported by NutritionApp.py.<br>
|--- NutritionApp.py: Top-level application<br>
|--- README.md: project documentation<br>
|--- TargetManager.py: Class for obtaining nutrient targets from the user via Dialog box; imported by NutritionApp.py.<br>

## Dependencies
See dependencies.txt located in the project root directory<br>
Additional dependencies not listed in dependencies.txt include torch and torchvision.<br>

## Execution Instructions
The prototype application should be executed from a Python virtual environment on a Windows 11 PC.  Instructions for creating the Python virtual environment are included in the following subsections.

### Clone Repo and Configure Python Environment
The following instructions assume that Python 3.11.9 is already installed on the target machine.<br>
1. Navigate to the project site on github: [Link](https://github.com/jhender1/ece57000)
2. Select Code > Clone > HTTPS and copy the provided web URL.
3. Open a git bash terminal window and navigate to the desired directory.
4. Execute `git clone <url>` using the url obtained in Step 2.
5. Open a PowerShell terminal and navigate to the project root directory.
6. Follow the steps below to create the Python virtual environment and install the required dependencies.<br>
    a. From PowerShell, execute `py -3.11 -m venv .venv`<br>
    b. Activate the virtual environment: `.\.venv\Scripts\Acivate.ps1`<br>
    c. Install the required dependencies:  `pip install -r dependencies.txt`<br>
    d. torch and torchvision must be installed separately: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`<br>

### Obtain USDA FDC API Key
Execution of the prototype application requires an API key for the USDA FoodData Central database.  Follow the instructions below to create an API key and store the key in the project directory.<br>
1. Navigate to the USDA FDC registration page: [Link](https://fdc.nal.usda.gov/api-key-signup)
2. Enter the required information and click 'Sign up'
3. Check the provided email address for an email containing the API key
4. Create a file called `ConfigFdc.py` in the project root directory.  
5. Add the following line to the file then save and close the file: `API_KEY = "<key>"` where <key> is the API Key received via email.

### Run the Application
The steps to configure the Python environment and obtain a USDA FDC API Key must be performed prior to running the application.<br>
1. From a Windows Powershell terminal, navigate to the project root directory.
2. Execute .\.venv\Scripts\Activate.ps1
3. Execute .\.venv\scripts\python.exe NutritionApp.py

## Code Reuse
All code for the prototype application was written by the other with the exceptions listed below:<br>
1. Database.py was written by the author prior to the start of the ECE 57000 course.  Specific lines that were modified: Lines 78,79
2. All Python files located in `root/UserInterface` were automatically compiled using the CompileUi.bat script located in the same subdirectory.