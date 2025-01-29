# This script converts MIP TIFF files to colored MIP Zarr files (whole MIP and multilayers MIP).

import numpy as np
import os
import tifffile as tiff
import matplotlib.pyplot as plt
import zarr
from ome_zarr.io import parse_url
from ome_zarr.writer import write_image
import subprocess

# Set input and output paths
input_path = '/mnt/d/Xiaoman/002_serialMIP/00_input/AZ4_DB2d_Ex561'
wholemip_tif_save_path = '/mnt/d/Xiaoman/002_serialMIP/02_tif/AZ4_DB2d_Ex561/AZ4_DB2d_Ex561_wholemip.tif'
wholemip_zarr_save_path = '/mnt/d/Xiaoman/002_serialMIP/03_zarr/AZ4_DB2d_Ex561/AZ4_DB2d_Ex561_wholemip.zarr'

# Constants
MIP_NUM_MAX = 16

# Helper function to normalize an array
def normalize_array(arr):
    return (arr - arr.min()) / (arr.max() - arr.min())

# Helper function to create a colormap
def generate_colormap(num_layers, cmap_name='jet'):
    cmap = plt.get_cmap(cmap_name).reversed()
    z_levels = np.linspace(0, 1, MIP_NUM_MAX)
    fixed_rgb_colors = cmap(z_levels)[:, :3]
    mapped_levels = np.linspace(0, num_layers / MIP_NUM_MAX, num_layers)
    actual_rgb_colors = np.zeros((num_layers, 3))
    for i in range(3):
        actual_rgb_colors[:, i] = np.interp(mapped_levels, z_levels, fixed_rgb_colors[:, i])
    return actual_rgb_colors

# Generate RGBA image
def create_rgba_image(arr, rgb_colors):

    # Broadcast RGB colors across the image width and height
    rgb_image = np.zeros((arr.shape[0], arr.shape[1], arr.shape[2], 3))
    for z in range(arr.shape[0]):
        rgb_image[z] = rgb_colors[z]

    rgba_image = np.zeros((arr.shape[0], arr.shape[1], arr.shape[2], 4))
    rgba_image[..., :3] = rgb_image
    rgba_image[..., 3] = normalize_array(arr)
    return rgba_image

# Save TIFF
def save_tiff(path, image):
    tiff.imwrite(path, image)
    print(f"TIFF image successfully saved to {path}")

# Convert TIFF to Zarr
def convert_tif_to_zarr(input_path, output_path, compression='zlib', compression_level=9, resolutions=5):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cmd = [
        'bioformats2raw',
        input_path,
        output_path,
        '--compression', compression,
        '--compression-properties', f'level={compression_level}',
        '--resolutions', str(resolutions)
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully converted {input_path} to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        raise

# Whole MIP Processing
def process_whole_mip():
    tiff_files = sorted([f for f in os.listdir(input_path) if f.endswith('.tif')])[:MIP_NUM_MAX]
    arr = np.stack([tiff.imread(os.path.join(input_path, f)) for f in tiff_files], axis=0)
    rgb_colors = generate_colormap(arr.shape[0])
    rgba_image = create_rgba_image(arr, rgb_colors)

    # Generate MIP
    mip_index = np.argmax(rgba_image[..., 3], axis=0)
    rgba_mip = np.zeros((rgba_image.shape[1], rgba_image.shape[2], 4))
    for i in range(rgba_mip.shape[0]):
        for j in range(rgba_mip.shape[1]):
            rgba_mip[i, j, :] = rgba_image[mip_index[i, j], i, j, :]

    # Scale and save
    rgba_mip[..., :3] = np.clip(rgba_mip[..., :3] * 255, 0, 255).astype(np.uint8)
    rgba_mip[..., 3] = (np.clip(rgba_mip[..., 3], 0, 1) * 65535).astype(np.uint16)
    # Create an empty array for the final image with uint16 dtype
    final_rgba_mip = np.zeros((rgba_mip.shape[0], rgba_mip.shape[1], 4), dtype=np.uint16)
    final_rgba_mip[..., :3] = rgba_mip[..., :3]  # Keep RGB as uint8
    final_rgba_mip[..., 3] = rgba_mip[..., 3]

    save_tiff(wholemip_tif_save_path, final_rgba_mip)

    # Save to Zarr
    image = tiff.imread(wholemip_tif_save_path)
    image = np.transpose(image, (2, 0, 1))[np.newaxis, :, np.newaxis, :, :]
    store = parse_url(wholemip_zarr_save_path, mode='w').store
    group = zarr.group(store)
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
             [{"type": "scale", "scale": [1, 1, 1, 28.8, 28.8]}], # Downsampled by 16 (path 4)
        ],
        chunks=(1, 4, 1, rgba_mip.shape[0] // 8, rgba_mip.shape[1] // 8))
    print(f"Whole MIP Zarr successfully saved to {wholemip_zarr_save_path}")

# Single Layer MIP Processing
def process_single_layer_mip():
    tiff_files = sorted([f for f in os.listdir(input_path) if f.endswith('.tif')])[:MIP_NUM_MAX]
    num_layers = len(tiff_files)

    multilayersmip_tif_save_path = f'/mnt/d/Xiaoman/002_serialMIP/02_tif/AZ4_DB2d_Ex561/AZ4_DB2d_Ex561_multilayersmip_{num_layers}.tif'
    multilayersmip_zarr_save_path = f'/mnt/d/Xiaoman/002_serialMIP/03_zarr/AZ4_DB2d_Ex561/AZ4_DB2d_Ex561_multilayersmip_{num_layers}.zarr'

    image = np.stack([tiff.imread(os.path.join(input_path, f)) for f in tiff_files], axis=0)[None, :, None]
    save_tiff(multilayersmip_tif_save_path, image)
    convert_tif_to_zarr(multilayersmip_tif_save_path, multilayersmip_zarr_save_path)

# Run processing
process_whole_mip()
process_single_layer_mip()
