import subprocess

# Define variables
bucket = 's3://neuroglancer'
profile = 'CAC'
# endpoint_url = 'https://redcloud.cac.cornell.edu:8443/'
endpoint_url = 'https://wulab.cac.cornell.edu:8443/'

source_path = '/mnt/d/Xiaoman/002_serialMIP/03_zarr'
target_name = 'AZ4_DB2d_Ex561'
wholemip_source_path = f'{source_path}/{target_name}/{target_name}_wholemip.zarr'
print(wholemip_source_path)
multilayersmip_source_path = f'{source_path}/{target_name}/{target_name}_multilayersmip_14.zarr'# change the number for each target
print(multilayersmip_source_path)


# Construct the destination path
destination_path_wholemip = f'{bucket}/{target_name}_mip/{target_name}_wholemip_zarr/'
print(destination_path_wholemip)
destination_path_multilayersmip = f'{bucket}/{target_name}_mip/{target_name}_multilayersmip_zarr/'

# Execute the command
subprocess.run([
    'aws', '--endpoint-url', endpoint_url, 
    's3', '--profile', profile, 
    'cp', '--recursive', wholemip_source_path, destination_path_wholemip
])
print(f"Successfully copied {wholemip_source_path} to {destination_path_wholemip}")

subprocess.run([
    'aws', '--endpoint-url', endpoint_url, 
    's3', '--profile', profile, 
    'cp', '--recursive', multilayersmip_source_path, destination_path_multilayersmip
])

print(f"Successfully copied {multilayersmip_source_path} to {destination_path_multilayersmip}")


