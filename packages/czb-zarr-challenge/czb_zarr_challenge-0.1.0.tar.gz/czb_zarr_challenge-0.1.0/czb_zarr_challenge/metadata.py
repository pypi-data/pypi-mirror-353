# Inspect the converted OME-Zarr and retrieve key metadata using iohub (i.e, array 
# shapes, scale, channel names, chunk sizes, etc). Tell us what method you used and 
# save them in a text file.

# iohub.open_ome_zarr returns a Plate, Position, or TiledPosition object depending on the Zarr dataset layout
# ex. for KazanskyStar it's a Plate object

# iohub/ngff/nodes.py shows how iohub defines object types within a Zarr group

import iohub.ngff
import numpy as np
import iohub
from iohub import open_ome_zarr
import argparse

# open_ome_zarr function definition: https://czbiohub-sf.github.io/iohub/main/api/ngff.html#iohub.open_ome_zarr
def get_metadata(zarr_path):
    with open_ome_zarr(store_path=zarr_path, 
                       mode="r", # just need read-only
                       layout="auto",
                       ) as dataset:
        
        if isinstance(dataset, iohub.ngff.Plate): # iterate wells, select one explicitly
            position = next(iter(dataset.positions())) # from Plate class, this gives [str, Position]: Path and position object
            position = position[1] # get the actual Position object
        else: # already a single Position or TiledPosition
            position = dataset

        # metadata.multiscales is from .zattrs["multiscales"], select the first multiscale image
        # then select the first resolution level for that image
        # then get path which is the name of the array holding the actual image data
        array_path = position.metadata.multiscales[0].datasets[0].path 
        image_array = position[array_path]

        metadata = {
            "Layout": type(dataset).__name__,
            "Shape": image_array.shape,
            "Chunk size": image_array.chunks,
            "Dtype": str(image_array.dtype),
            "Scale": position.scale,
            "Channel names": position.channel_names,
        }
        dataset.print_tree()
    return metadata

# --- code block generated with the help of ChatGPT ---
def save_metadata_as_txt(metadata, output_path):
    with open(output_path, "w") as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    print(f"Metadata saved to {output_path}")
# -----------------------------------------------------

# CLI!
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("zarr_path", type=str, help="input Zarr dataset path")
    parser.add_argument("output_path", type=str, help="output metadata text file path")

    args = parser.parse_args()
    metadata = get_metadata(args.zarr_path)

    print("\n--- Metadata ---")
    for key, value in metadata.items():
        print(f"{key}: {value}")

    save_metadata_as_txt(metadata, args.output_path)

    # example usage:
    # python main/src/get_metadata.py ../../../data/KazanskyStar_converted.zarr metadata1.txt
    # python main/src/get_metadata.py ../../../data/20241107_infection.zarr metadata2.txt