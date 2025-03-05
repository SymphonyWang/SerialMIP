import os
import numpy as np
import tifffile as tiff
import ome_zarr
import zarr
from ome_zarr.io import parse_url
from ome_zarr.writer import write_image

input_path = '/mnt/d/Xiaoman/002_serialMIP/fixedbar/colorbar_jet_16_9600_crop550.tif'
output_path = '/mnt/d/Xiaoman/002_serialMIP/03_zarr/colorbar/colorbar_jet_16_9600_crop550.zarr'

# Read the .tif files and print the shape
image = tiff.imread(input_path)
print("Shape of arr:", image.shape)
# Shape of arr: (2059, 550, 3)
y = image.shape[0]
x = image.shape[1]

# Reshape the image to (1, 3, 1, y, x)
image = np.transpose(image, (2, 0, 1))  # Change to (4, 8817, 7433)
image = image[np.newaxis, :, np.newaxis, :, :]  # Add singleton dimensions to get (1, 3, 1, 8817, 7433)
print("New shape:", image.shape)
print("Data type:", image.dtype)

# Create a Zarr store
store = parse_url(output_path, mode='w').store

# Create a Zarr group
group = zarr.group(store)

# Recursively remove all existing data in the group if it exists
if len(group.keys()) > 0:
    for key in list(group.keys()):
        del group[key]  # Remove the entire key and its data

chunk_height, chunk_width = int(y/8), int(x/8)
chunks = (1, 3, 1, chunk_height, chunk_width)

# Write the image data to the Zarr store
write_image(
    image, 
    group, 
    axes=[{"name": "t", "type": "time"},
          {"name": "c", "type": "channel"},
          {"name": "z", "type": "space"},
          {"name": "y", "type": "space", "unit": "micrometer"},
          {"name": "x", "type": "space", "unit": "micrometer"}],
    coordinate_transformations=[
        [{"type": "scale", "scale": [1, 1, 1, 1.8, 1.8]}],  # Highest resolution (path 0)
        [{"type": "scale", "scale": [1, 1, 1, 3.6, 3.6]}],  # Downsampled by 2 (path 1)
        [{"type": "scale", "scale": [1, 1, 1, 7.2, 7.2]}],  # Downsampled by 4 (path 2)
        [{"type": "scale", "scale": [1, 1, 1, 14.4, 14.4]}],  # Downsampled by 8 (path 3)
        [{"type": "scale", "scale": [1, 1, 1, 28.8, 28.8]}],  # Downsampled by 16 (path 4)
    ],
    chunks=chunks
)



# Print the Zarr store tree and type
print(group.tree())
print(group.info)

print(f"Image successfully written to {output_path}")