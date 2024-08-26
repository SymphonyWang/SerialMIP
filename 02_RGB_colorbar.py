import matplotlib.pyplot as plt
import matplotlib.cm as cm
import tifffile as tiff
import os
import numpy as np
import colorcet as cc

input_path = '/mnt/d/Xiaoman/002_serialMIP/input/12_52_12_AZ10_SR4B1_A_Ex639'
save_path = '/mnt/d/Xiaoman/002_serialMIP/output/12_52_12_AZ10_SR4B1_A_Ex639/finial/rgba_output/jet'

# Get the list of .tif files in the input path
tiff_files = sorted([f for f in os.listdir(input_path) if f.endswith('.tif')])

# Read the .tif files and stack them into a 3D array
arr = np.stack([tiff.imread(os.path.join(input_path, f)) for f in tiff_files], axis=0)
print("Shape of arr:", arr.shape)

# Get z-axis levels and map them to corresponding RGB colors
z_levels = np.linspace(0, 1, arr.shape[0])
# rgb_cmap = cc.cm['bmw']
rgb_cmap = plt.get_cmap('jet')
rgb_colors = rgb_cmap(z_levels)[:, :3]


# generate a color bar for the hue values and save it as a PNG file
fig, ax = plt.subplots()
fig.patch.set_facecolor('black')  # Set the background color to black

cmap = rgb_colors
# reverse the cmap to make the colorbar consistent with the color of the image
cmap = cmap[::-1]

cmap = cm.colors.ListedColormap(cmap)

norm = plt.Normalize(0, 7000)  # Set the normalization to the range of z-depth
cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
cb.set_label('z-depth (μm)', color='white')  # Set the color of the label to white
cb.ax.yaxis.set_tick_params(color='white')  # Set the color of the tick parameters to white
cb.outline.set_edgecolor('white')  # Set the color of the outline to white

# Set custom tick labels
# tick_positions = np.arange(0, 7000, 500)
# cb.set_ticks(tick_positions)
# cb.set_ticklabels([str(int(tick)) for tick in tick_positions])

# Change the color of the tick labels to white
for label in cb.ax.yaxis.get_ticklabels():
    label.set_color("white")

plt.savefig(os.path.join(save_path, 'rgb_colorbar_jet.png'))