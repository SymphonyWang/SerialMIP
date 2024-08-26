import cloudvolume as cv
import numpy as np
import tifffile as tiff
from tifffile import imread
import numpy as np
import os
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from skimage import color

# input_path_Ex445 = '/home/xiw4013/serialMIP/input/Ex445'
# input_path_Ex561 = '/home/xiw4013/serialMIP/input/Ex561'
input_path_Ex639 = '/mnt/d/Xiaoman/002_serialMIP/input/10_46_32_AZ10_SR4B18_A_Ex639'
save_path = '/mnt/d/Xiaoman/002_serialMIP/output/10_46_32_AZ10_SR4B18_A_Ex639'

# get the list of .tif files in input_path
tiff_files = sorted([f for f in os.listdir(input_path_Ex639) if f.endswith('.tif')])

# read the .tif files into numpy arrays and stack them
arr = np.stack([tiff.imread(os.path.join(input_path_Ex639, f)) for f in tiff_files], axis=0)
# print("Shape of arr_JH_1c:", arr_JH_1c.shape)
print("Shape of arr:", arr.shape)

# vol_JH_1c = cv.CloudVolume('https://wu-objstore-45d.med.cornell.edu/neuroglancer/AA4_JH_1c/Ex_561', mip=2)
# img_JH_1c = vol_JH_1c[:]
# arr_JH_1c = np.squeeze(img_JH_1c.T) # remove the first dimension of size 1 (channel dimension) (z,y,x)
# print("Shape of arr_JH_1c:", arr_JH_1c.shape)
# img_JH_1c_shape_x = arr_JH_1c.shape[2]
# img_JH_1c_shape_y = arr_JH_1c.shape[1]
img_shape_z = arr.shape[0]
print("img_shape_z:", img_shape_z)


# img_JH_1c_x = arr_JH_1c[:,:,0]
# img_JH_1c_y = arr_JH_1c.shape[1]
# img_JH_1c_z = arr[:,0,0]

# Map HSV colormap to grayscale image
# hue = np.zeros_like(arr_JH_1c)

def depth_to_hue_mapping(depth_range, hue_range):
    depth_values = np.arange(depth_range[0], depth_range[1])

    depth_ratios = (depth_values - depth_range[0]) / (depth_range[1] - depth_range[0])

    hue_values = np.interp(depth_ratios, [0, 1], hue_range)
    
    return hue_values

depth_range = [0, img_shape_z]
# hue_range = [0, 1]
hue_range = [0, 5/9]
# reverse the hue_range to make the colorbar consistent with the color of the image
hue_range.reverse()
hue_mapping = depth_to_hue_mapping(depth_range, hue_range)

print("hue_mapping_shape:", hue_mapping.shape)

# Normalize arr to the range [0,1]
normalizedarr = (arr - arr.min()) / (arr.max() - arr.min())
# z_depth = (img_JH_1c_z - img_JH_1c_z.min()) / (img_JH_1c_z.max() - img_JH_1c_z.min())
# print("z_depth.shape:", z_depth.shape)
# z_depth_expand = np.expand_dims(np.expand_dims(z_depth, axis=1), axis=1)
# print("z_depth_expand.shape:", z_depth_expand.shape)

# hue = z_depth * 360
# hue = np.clip(np.broadcast_to(z_depth_expand * 360, arr_JH_1c.shape), 0, 360)
# hue_value = map_depth_to_hue(z_depth_expand)
hue_mapping_reshaped = np.expand_dims(np.expand_dims(hue_mapping, axis=1), axis=1)
hue = np.broadcast_to(hue_mapping_reshaped, arr.shape)
print("hue_shape:", hue.shape)

saturation = np.ones_like(arr)

value = normalizedarr
print("value.shape:", value.shape)

hsv_image = np.stack((hue, saturation, value), axis=-1)
print("hsv_image_shape:", hsv_image.shape)

# Take the maximum value in the z direction to get the MIP
# mip = np.max(hsv_image, axis=0)
mip_index = np.argmax(hsv_image[..., 2], axis=0)
print("mip_index.shape:", mip_index.shape)
# hsv_image_2d = hsv_image[mip_index, :, :, :]
hsv_image_2d = hsv_image[mip_index, np.arange(hsv_image.shape[1])[:, None], np.arange(hsv_image.shape[2])]
print("hsv_image_2d.shape:", hsv_image_2d.shape)

# generate a color bar for the hue values and save it as a PNG file
fig, ax = plt.subplots()
fig.patch.set_facecolor('black')  # Set the background color to black

cmap = cm._colormaps['hsv']
cmap = cmap(np.linspace(0, 5/9, cmap.N))
# reverse the cmap to make the colorbar consistent with the color of the image
cmap = cmap[::-1]

cmap = cm.colors.ListedColormap(cmap)

norm = plt.Normalize(0, 6926)  # Set the normalization to the range of z-depth
cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
cb.set_label('z-depth (μm)', color='white')  # Set the color of the label to white
cb.ax.yaxis.set_tick_params(color='white')  # Set the color of the tick parameters to white
cb.outline.set_edgecolor('white')  # Set the color of the outline to white

# Change the color of the tick labels to white
for label in cb.ax.yaxis.get_ticklabels():
    label.set_color("white")

plt.savefig(os.path.join(save_path, '111.png'))


# Convert the HSV image to RGB
rgb_image = color.hsv2rgb(hsv_image_2d)
print("Shape of rgb_image:", rgb_image.shape)

# Save the RGB image as a TIFF file
tiff.imwrite(os.path.join(save_path, f'111.tif'), rgb_image)

