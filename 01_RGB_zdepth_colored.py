import numpy as np
import os
import tifffile as tiff
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PIL import Image
import colorcet as cc

# Set input and output paths
input_path = '/mnt/d/Xiaoman/002_serialMIP/input/12_52_12_AZ10_SR4B1_A_Ex639'
save_path = '/mnt/d/Xiaoman/002_serialMIP/output/12_52_12_AZ10_SR4B1_A_Ex639/finial/rgba_output/jet'

# Get the list of .tif files in the input path
tiff_files = sorted([f for f in os.listdir(input_path) if f.endswith('.tif')])

# Read the .tif files and stack them into a 3D array
arr = np.stack([tiff.imread(os.path.join(input_path, f)) for f in tiff_files], axis=0)
print("Shape of arr:", arr.shape)

# Get z-axis levels and map them to corresponding RGB colors
z_levels = np.linspace(0, 1, arr.shape[0])
rgb_cmap = plt.get_cmap('jet')
# rgb_cmap = cc.cm['bmw']
rgb_colors = rgb_cmap(z_levels)[:, :3]  # Get RGB colors, ignoring the alpha channel
print("Shape of rgb_colors:", rgb_colors.shape)

# Broadcast RGB colors across the image width and height
rgb_image = np.zeros((arr.shape[0], arr.shape[1], arr.shape[2], 3))
for z in range(arr.shape[0]):
    rgb_image[z] = rgb_colors[z]

# Map signal intensity to the alpha channel
normalized_arr = (arr - arr.min()) / (arr.max() - arr.min())  # Normalize to [0, 1]
rgba_image = np.zeros((arr.shape[0], arr.shape[1], arr.shape[2], 4))
rgba_image[..., :3] = rgb_image  # Assign RGB colors
rgba_image[..., 3] = normalized_arr  # Assign normalized intensity as the alpha channel

# Generate maximum intensity projection (MIP) image
mip_index = np.argmax(rgba_image[..., 3], axis=0)  # Get the index of the maximum alpha value
rgba_mip = np.zeros((rgba_image.shape[1], rgba_image.shape[2], 4))  # Shape: (height, width, 4)
for i in range(rgba_mip.shape[0]):
    for j in range(rgba_mip.shape[1]):
        rgba_mip[i, j, :] = rgba_image[mip_index[i, j], i, j, :]

# separate the alpha channel from the RGB channels
rgb_mip = rgba_mip[..., :3]
alpha_mip = rgba_mip[..., 3]

# apply the alpha channel to the RGB channels
rgba_mip = rgb_mip * alpha_mip[..., None]

# save as RGB image
output_file = os.path.join(save_path, 'rgb_mip_output_jet.tif')
tiff.imwrite(output_file, rgba_mip)



