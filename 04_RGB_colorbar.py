import matplotlib.pyplot as plt
import matplotlib.cm as cm
import tifffile as tiff
import os
import numpy as np
import colorcet as cc

save_path = '/mnt/d/Xiaoman/002_serialMIP/fixedbar'

# z-axis numbers
mip_num = 16

# Get z-axis levels and map them to corresponding RGB colors
z_levels = np.linspace(0, 1, mip_num)
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

norm = plt.Normalize(0, 9600)  # Set the normalization to the range of z-depth
cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
cb.set_label('z-depth (μm)', color='white')  # Set the color of the label to white
cb.ax.yaxis.set_tick_params(color='white')  # Set the color of the tick parameters to white
cb.outline.set_edgecolor('white')  # Set the color of the outline to white

# Invert the y-axis of the colorbar
cb.ax.invert_yaxis()

# Set custom tick labels
tick_positions = np.arange(0, 9601, 1200)
print(tick_positions)
cb.set_ticks(tick_positions)
cb.set_ticklabels([str(int(tick)) for tick in tick_positions])

# Change the color of the tick labels to white
for label in cb.ax.yaxis.get_ticklabels():
    label.set_color("white")

plt.savefig(os.path.join(save_path, 'colorbar_jet_16_9600.tif'))

