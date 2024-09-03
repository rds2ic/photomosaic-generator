import pickle, glob, os
from PIL import Image
import numpy as np
from constants import *

# PHOTO RESIZER

# Change PATH to name of folder containing source files
PATH = "./mosaic_images"
# Change newpath to name of folder containing output files
newpath = "./resized_mosaics_" + str(PXSIZE)
if not os.path.exists(newpath):
    print("Resizing source images")
    os.makedirs(newpath)

    i = 0
    for filename in glob.glob(os.path.join(PATH, '*.jpg')):
        im = Image.open(filename)
        im = im.resize((PXSIZE, PXSIZE))
        im.save(f"./{newpath}/{i}.jpg")
        i += 1

    for filename in glob.glob(os.path.join(PATH, '*.JPEG')):
        im = Image.open(filename)
        im = im.resize((PXSIZE, PXSIZE))
        im.save(f"./{newpath}/{i}.jpg")
        i += 1

# AVERAGE COLOUR FINDER
print("Finding average colour sizes")
if not os.path.exists("avg_colour_" + str(PXSIZE) + '.pkl'):
    average_values = {}
    PATH = "./resized_mosaics_" + str(PXSIZE)
    for filename in glob.glob(os.path.join(PATH, '*.jpg')):
        im = Image.open(filename)
        im.convert('RGB')
        image_array = np.array(im)

        average_r, average_g, average_b = 0, 0, 0
        for row in image_array:
            for pixel in row:
                average_r += pixel[0]
                average_g += pixel[1]
                average_b += pixel[2]
        average_colours_arr = (average_r // (PXSIZE*PXSIZE), average_g // (PXSIZE*PXSIZE), average_b // (PXSIZE*PXSIZE))
        average_values[filename] = average_colours_arr
        with open("avg_colour_" + str(PXSIZE) + '.pkl', 'wb') as f:
            pickle.dump(average_values, f)

print("Constructing Image")
image = Image.open(PICTURE)
image.convert('RGB')
# Need to resize image dimensions to multiples of 50 as mosaic pictures are 50x50 squares
image = image.resize(((image.size[0] - (image.size[0] % PXSIZE)), (image.size[1] - (image.size[1] % PXSIZE))))

# Creating the array which stores the pixel RGB values
image_arr = np.asarray(image)
# Averages array has to be in divisions of the pixel size
averages_arr = [[() for _ in range(len(image_arr[0]) // PXSIZE)] for _ in range(len(image_arr) // PXSIZE)]

# Loop through the rows of the array in pixel size divisions at a time
for i in range(0, len(image_arr), PXSIZE):
    # At each pixel size division of rows we need to loop a square for the whole row in the size of the pixel dimensions
    col = 0
    avg_r, avg_g, avg_b = 0,0,0
    # This is for it to be able to loop until the end of the row
    while col < len(image_arr[0]):
        # Looping each unit in the pixel sized subdivision of rows
        for j in range(0, PXSIZE):
            # Looping in only a pixel size amound of columns to the right
            for u in range(col, col + PXSIZE):
                # Adding all the RGB values respectively to their total
                pixel = image_arr[i+j][u]
                avg_r += pixel[0]
                avg_g += pixel[1]
                avg_b += pixel[2]

        # Adding the averages of each square to the averages array
        averages_arr[i // PXSIZE][col // PXSIZE] = (avg_r // (PXSIZE*PXSIZE), avg_g // (PXSIZE*PXSIZE), avg_b // (PXSIZE*PXSIZE))
        avg_r, avg_g, avg_b = 0,0,0

        # Incrementing the column starting count for the next square
        col += PXSIZE

with open(f'avg_colour_{PXSIZE}.pkl', 'rb') as f:
    average_values = pickle.load(f)

def compare_colours(colour1, colour2) -> int:
    r1, g1, b1 = colour1
    r2, g2, b2 = colour2

    return np.sqrt(np.square(r2-r1) + np.square(g2-g1) + np.square(b2-b1))

# Need to create a canvas image to paste all other images onto
average_image = Image.new('RGB', size=(image.size[0], image.size[1]))
for i in range(len(averages_arr)):
    for j in range(len(averages_arr[0])):
        
        pixel = averages_arr[i][j]
        min_key = ""
        min_val = np.inf

        for key in average_values:
            val = compare_colours(pixel, average_values[key])
            if val < min_val:
                min_key = key
                min_val = val

        im = Image.open(min_key)
        # Paste each pixel onto the canvas one
        # im = Image.new('RGB', (PXSIZE, PXSIZE), averages_arr[i][j])

        # Need to invert j and i otherwise image is reflected in y=-x
        average_image.paste(im, (j * PXSIZE, i * PXSIZE))
average_image.show()
average_image.save(f'mosaic_{PXSIZE}_{PICTURE}')
