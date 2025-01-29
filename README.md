# README

This repository contains a set of Python scripts designed to process image data into Maximum Intensity Projection (MIP) formats, convert them into Zarr files, upload them to an S3 bucket, and prepare them for visualization in Neuroglancer. Below is a description of each script and how they should be used.

---

## Scripts Overview

### 01_convert.py

**Purpose**:  
Processes multi-layer TIFF images into both RGBA TIFF and Zarr formats. It generates colormaps, creates RGBA images, saves them as TIFF files, and converts these to Zarr format for efficient storage.

**Key Functions**:
- `generate_colormap()`: Generates RGB colors for each layer based on fixed RGB values.  
- `create_rgba_image()`: Combines the grayscale image with generated RGB colors and adds an alpha channel for transparency.  
- `save_tiff()`: Saves the processed image as a TIFF file.  
- `convert_tif_to_zarr()`: Converts the TIFF file to Zarr format using bioformats2raw.  
- `process_whole_mip()` and `process_single_layer_mip()`: Processes images into whole MIPs or single-layer MIPs, respectively.

---

### 02_upload.py

**Purpose**:  
Uploads the generated Zarr files from local storage to an S3 bucket using AWS CLI.

**Key Steps**:
1. Constructs source and destination paths for both WholeMIP and MultiLayerMIP files.  
2. Uses `aws s3 cp --recursive` to upload all files in the specified directories.

---

### 03_url.py

**Purpose**:  
Modifies a Neuroglancer JSON template to point to the uploaded Zarr files, enabling visualization in Neuroglancer.

**Key Steps**:
1. Reads the structure of the Zarr file and extracts dimensions (x, y).  
2. Modifies the template JSON file to include the correct filenames and URLs for visualization layers.  
3. Saves the modified JSON file locally, which can then be uploaded to S3.

---

## Requirements

### Dependencies
- Python  
- NumPy  
- Tiff  
- Zarr 
- Bioformats2raw  
- AWS CLI  

### Other Requirements
- Access to an S3 bucket with appropriate credentials.  
- Neuroglancer setup for visualization.

---

## Setup Instructions

### Install Dependencies

```bash
pip install numpy tifffile zarr bioformats2raw
