
import logging
import argparse
import os
from PIL import Image, ImageFont, ImageDraw


logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(message)s')

parser = argparse.ArgumentParser(description='Tool to generate tile images')
parser.add_argument('--baseImage', type=str, help='Base image to draw tiles on top of', default =
        'Wood-Tile')
parser.add_argument('--suffix', type=str, help='Any string to append to the base tile', 
        default = None)
parser.add_argument('--fontSize', type=int, help='Size of the font to put onto the tile', 
        default = 80)
parser.add_argument('--fontFile', type=str, help='Font filename to use', 
        default = os.path.join("..", "fonts", "Exo2-Bold.otf"))
parser.add_argument('--xOffset', type=int, help='Additional offset on the x Axis for the letter', 
        default = 10)
parser.add_argument('--yOffset', type=int, help='Additional offset on the y Axis for the letter', 
        default = 0)
config = parser.parse_args()

fontFilename = os.path.join("..", "fonts", "Exo2-Bold.otf")
logging.info("Going to get font; file: %s, size: %d", config.fontFile, config.fontSize)
font = ImageFont.truetype(config.fontFile, config.fontSize)

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

baseImage = Image.open(config.baseImage + ".png")
for i in alphabet:
    letterImage = baseImage.copy()
    draw = ImageDraw.Draw(letterImage)
    w, h = draw.textsize(i, font=font)
    draw.text(((100-w)/2 + config.xOffset, (100-h)/2 + config.yOffset), i, font=font, 
            outline="black", fill="White")
    if config.suffix:
        letterFilename = "{}-{}-{}.png".format(config.baseImage, i, config.suffix)
    else:
        letterFilename = "{}-{}.png".format(config.baseImage, i)
    logging.info("Going to save resulting image;  letter: %s, filename: %s", i, letterFilename) 
    letterImage.save(letterFilename, "PNG") 
