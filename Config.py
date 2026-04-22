"""
File:           Config.py
Author:         Joshua Henderson
Date Created:   2026-03-22
Last Modified:  2026-04-22

Course:         ECE 57000
Instructor:     Chaoyue Liu
Assignment:     Course Project

Description:
    Config.py contains helper variables used by the application.

Dependencies: None

Usage: Config.py is not intended to be executed directly.
"""

# Location of the local database
dbFilePath = './Database/FoodLog.db'

# Dictionary mapping nutrient friendly names to the ID used by the USDA FDC database
nutrientIds = {
    'Protein': 203,
    'Total Fat': 204,
    '     Saturated Fat': 606,
    '     Trans Fat': 605,
    '     Monounsaturated Fat': 645,
    '     Polyunsaturated Fat': 646,
    'Total Carbohydrates': 205,
    '     Added Sugar': 539,
    '     Dietary Fiber': 291
}

# Image normalization parameters determined during model training.
# These must be manually updated when new training iterations are performed AND dataset modifications have been made
imageMean = [0.5857, 0.4723, 0.3584]
imageStd = [0.2231, 0.2377, 0.2436]

# Class Labels used by the Image Classifier model
classLabels = [
    'almond',
    'apple',
    'apple_pie',
    'avocado',
    'baby_back_ribs',
    'banana',
    'caesar_salad',
    'carrot_cake',
    'cherry_tomato',
    'chicken_curry',
    'chicken_wings',
    'donuts',
    'fish_and_chips',
    'grape',
    'grapefruit',
    'grilled_salmon',
    'hamburger',
    'ice_cream',
    'lasagna',
    'macaroni_and_cheese',
    'omelette',
    'orange',
    'pad_thai',
    'pistachio',
    'pizza',
    'pulled_pork_sandwich',
    'raspberry',
    'steak',
    'tacos',
    'waffles']