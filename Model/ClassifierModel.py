"""
File:           ClassifierModel.py
Author:         Joshua Henderson
Date Created:   2026-02-26
Last Modified:  2026-04-22

Course:         ECE 57000
Instructor:     Chaoyue Liu
Assignment:     Course Project

Description:
    ClassifierModel.py contains the instantiation of the ResNet-50 Image Classification model.  The class contains a 
    single function, Classify_Item, which executes the forward function of the model and returns the output class label.

Dependencies: see dependencies.txt

Usage: FOR TESTING PURPOSES ONLY
    1. Edit the absolute path to the image to be classified (Line 71)
    2. From a Windows Powershell terminal, navigate to the project root directory.
    3. Execute .\venv\Scripts\Activate.ps1
    4. Execute .\venv\scripts\python.exe ClassifierModel.py
"""

import torch
import torch.nn as nn
from PIL import Image
import pillow_heif
from torchvision.models import resnet50
import torchvision.transforms as transforms
from Config import imageMean, imageStd, classLabels

class ClassifierModel:
    def __init__(self):
        # Instantiate model and load parameter weights obtained from model training.  Update final model layer to match
        # the number of output classes
        self.model = resnet50()
        self.model.fc = nn.Linear(2048,30)
        self.model.load_state_dict(torch.load(r'model\custom_ds_weights.pth', map_location=torch.device('cpu')))
        
        # The transforms ensure that the images size matches the model input, that the image data structure is correct
        # and that pixel color values are normalized according to the dataset statistics computed during training
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=imageMean, std=imageStd)
        ])
        # Needed to convert .HEIC images to RGB format
        pillow_heif.register_heif_opener()

    def Classify_Item(self, imageFile):
        # Ensure model is not in training mode
        self.model.eval()
        
        # Read the image from the provided location
        image = Image.open(imageFile).convert("RGB")
        image = self.transform(image).unsqueeze(0)
        
        # Model forward function
        output = self.model(image)
        
        # Classify model output and return the label
        predicted_class = torch.argmax(output, dim=1).item()
        return classLabels[predicted_class]

if __name__ == "__main__":
    import os
    print(os.getcwd())
    cm = ClassifierModel()
    
    # photo path
    imageFile = r'C:\git\ece57000\Photos\screenshot12.jpg'
    label = cm.Classify_Item(imageFile)
    print(label)