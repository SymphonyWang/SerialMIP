import os
import json

def modify_template_json(template_path, input_path, output_path):
    # 1) Identify zarr file and sample name
    zarr_file = os.listdir(input_path)[0]
    zarr_file_name = os.path.splitext(zarr_file)[0]
    sample_name = '_'.join(zarr_file_name.split('_')[:-2])
    zarr_file_num = int(zarr_file_name.split('_')[-1])

    # 2) Read .zarray for x,y
    zarray_path = os.path.join(input_path, f"{sample_name}_wholemip.zarr", "0", ".zarray")
    with open(zarray_path, 'r') as zf:
        info = json.load(zf)
    y_size, x_size = info["shape"][-2], info["shape"][-1]

    # 3) Load template
    with open(template_path, 'r') as f:
        data = json.load(f)

    # 4) Filter depth layers (keep "depth1" to "depthN", then last two layers)
    keep_depths = [f"depth{i}" for i in range(1, zarr_file_num + 1)]
    *mid, last1, last2 = data["layers"]
    data["layers"] = [l for l in mid if l.get("name") in keep_depths] + [last1, last2]

    # 5) Update "position" with half x,y
    data["position"][0] = x_size / 2
    data["position"][1] = y_size / 2
    data["position"][2] = 0
    data["position"][3] = 0

    # 6) Recursively replace "filename" with sample_name
    def replace_filename_recursive(obj):
        if isinstance(obj, dict):
            return {k: replace_filename_recursive(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [replace_filename_recursive(i) for i in obj]
        if isinstance(obj, str):
            return obj.replace("filename", sample_name)
        return obj
    data = replace_filename_recursive(data)

    # 7) Update colorbar matrix
    for layer in data["layers"]:
        src = layer.get("source", {})
        if "colorbar_jet_16_crop550.zarr" in src.get("url", ""):
            mat = src["transform"]["matrix"]
            mat[3][-1] = y_size - 2059
            mat[4][-1] = x_size

    # 8) Save final
    out_json = os.path.join(output_path, f"{sample_name}.json")
    with open(out_json, 'w') as out:
        json.dump(data, out, indent=2)
    print("Modified JSON saved to:", out_json)

if __name__ == "__main__":
    template = "/mnt/d/Xiaoman/002_serialMIP/04_json/template.json"
    input_dir = "/mnt/d/Xiaoman/002_serialMIP/03_zarr/AZ4_DB2b_Ex561"
    output_dir = "/mnt/d/Xiaoman/002_serialMIP/04_json/test"
    modify_template_json(template, input_dir, output_dir)

# after running the script, the modified json file will be saved to the output directory
# Use aws command to upload the json file to the s3 bucket
# aws --endpoint-url https://wulab.cac.cornell.edu:8443/ s3 --profile CAC cp /mnt/d/Xiaoman/002_serialMIP/04_json/AZ4_DB2d_Ex561.json s3://neuroglancer/AZ4_DB2d_Ex561_mip/AZ4_DB2d_Ex561.json
# finnal url like:
# https://ngapp.mab3d-atlas.com/#!https://wulab.cac.cornell.edu:8443/swift/v1/neuroglancer/AZ4_DB2b_Ex561_mip/AZ4_DB2b_Ex561.json
