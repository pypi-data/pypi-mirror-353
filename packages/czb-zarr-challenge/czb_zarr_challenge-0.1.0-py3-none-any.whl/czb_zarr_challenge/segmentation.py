import numpy as np
import argparse
from pathlib import Path
import zarr
import iohub
import iohub.ngff
from iohub import open_ome_zarr
from skimage.filters import threshold_otsu
from skimage.feature import blob_log
from skimage.segmentation import watershed
from scipy import ndimage as ndi
from tqdm import tqdm


def segment_nuclei(
    zarr_path: str | Path, # path to OME‑Zarr store (can be Plate or Position)
    nuclei_channel: str = "nuclei_DAPI", 
    label_name: str = "nuclei_labels", # dataset name under labels group that we'll write the mask to
):
    """Segment nuclei in nuclei_channel, and save as labels in the original Zarr store file"""

    with open_ome_zarr(zarr_path, mode="r+", layout="auto") as root: # use iohub read/write mode
        # if it's a Plate (both Datasets 1 and 2 are) then get all positions in it. If a Position, then just get that.
        positions = ([p for _, p in root.positions()] if isinstance(root, iohub.ngff.Plate) else [root])

        _, position = next(iter(root.positions()))
        num_timepoints, _, _, _, _ = position[position.metadata.multiscales[0].datasets[0].path].shape

        with tqdm(total=num_timepoints, desc="Segmenting nuclei", unit="timepoint") as pbar:
            for i, position in enumerate(positions):
                print(f"Segmenting position {i+1} of {len(positions)}")

                # select first multiscale image, then first resolution level for it,
                # then get path which is the name of the array holding the actual image data
                array_path = position.metadata.multiscales[0].datasets[0].path 
                image_array = position[array_path] # Zarr array (ImageArray), shape (T, C, Z, Y, X)

                nuclei_channel_idx = position.channel_names.index(nuclei_channel)
                label_shape = list(image_array.shape) # should be same shape as image except with just one channel dim
                label_shape[1] = 1 # just one channel dim for the labels

                # create where the labels will go with Zarr's create fn: https://zarr.readthedocs.io/en/stable/api/zarr/creation/index.html#zarr.creation.create 
                labels = zarr.create(shape=tuple(label_shape), chunks=image_array.chunks, dtype="uint16", fill_value=0)

                # ------------------------------- segmentation part! ------------------------------
                # might wanna put this in a separate function
                # basic threshold -> scikit-image's blob_log -> 3D watershed

                for t in range(image_array.shape[0]):  # loop over timepoints
                    # first get the full 3D volume, so go into the current timepoint and the nuclei channel
                    vol_3d = image_array[t, nuclei_channel_idx, :, :, :].astype(np.float32) # (Z, Y, X)

                    # then use global threshold (Otsu) to get a rough foreground mask
                    thresh = threshold_otsu(vol_3d) # just a scalar
                    mask3d = vol_3d > thresh # 3d boolean array

                    # 3D blob detection with LoG, https://scikit-image.org/docs/0.25.x/api/skimage.feature.html#skimage.feature.blob_log 
                    # Blobs are bright on dark or dark on bright regions in an image. More here: https://scikit-image.org/docs/0.25.x/auto_examples/features_detection/plot_blob.html#blob-detection
                    blobs = blob_log(vol_3d, min_sigma=3, max_sigma=6, num_sigma=4, threshold=0.03) # blobs[i] = (z_coord, y_coord, x_coord, sigma_estimate)

                    # build markers based on the blob centers
                    markers = np.zeros_like(vol_3d, dtype=np.int32)
                    for i, blob_i in enumerate(blobs, start=1):
                        zi, yi, xi, _ = blob_i # ith nucleus
                        zi, yi, xi = int(round(zi)), int(round(yi)), int(round(xi)) # round the floats to int
                        markers[zi, yi, xi] = i # labels need to start at 1 because 0 is background in scikit watershed
                    # now markers is a 3D array where each voxel either has value 0 (background) or positive int i (seed for nucleus i)

                    # for every voxel inside the cell–nuclei foreground, get the Euclidean distance to the nearest background. Inverting this gives a “basin” for watershed
                    dist = ndi.distance_transform_edt(mask3d)

                    # https://scikit-image.org/docs/0.25.x/api/skimage.segmentation.html#skimage.segmentation.watershed
                    # Pass in (1) negative distance as the “elevation map”, (2) the blob markers, and (3) the thresholding mask to restrict to foreground
                    labels_3d = watershed(-dist, markers, mask=mask3d).astype(np.uint16)  # returns shape (Z, Y, X). Values are 0 (background), or 1, 2, 3, ..., N (each nucleus has its own integer label)
                    labels[t, 0, :, :, :] = labels_3d 

                    pbar.update(1)

                # ---------------------------------------------------------------------------------

                # write to <position>/labels/<label_name>/0. This discussion shows how labels are stored in NGFF format under the "labels" group: https://github.com/ome/ngff/issues/14
                # create_group API ref here: https://zarr.readthedocs.io/en/stable/api/zarr/index.html#zarr.AsyncGroup.create_group

                print(f"Writing Position {i+1}'s labels into OME-Zarr store...")
                zarr_group = position.zgroup
                
                if "labels" in zarr_group:
                    lbl_root = zarr_group["labels"]
                else:
                    lbl_root = zarr_group.create_group("labels") # lbl_root is <position>/labels

                if label_name in lbl_root:
                    del lbl_root[label_name]
                lbl_group = lbl_root.create_group(label_name) # create subgroup "nuclei_labels" in labels

                # create dataset in /labels/<label_name>/0. This writes the entire 5D label volume with the same chunking and compressor as input image_array
                lbl_group.create_dataset(name="0", data=labels, chunks=image_array.chunks, dtype="uint16", compressor=image_array.compressor)

                print(f"Position {i+1}'s labels saved under '{zarr_path}{array_path}/labels/{label_name}/0'\n")


# ------------------------------------- CLI ----------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="segment nuclei from a DAPI channel and save the labels in a OME‑Zarr store")
    parser.add_argument("zarr_path", type=str, help="path to the OME‑Zarr store")
    parser.add_argument("--nuclei-channel", type=str, default="nuclei_DAPI", help="channel to segment (default: nuclei_DAPI)")
    parser.add_argument("--label-name", type=str, default="nuclei_labels", help="output label dataset name")

    args = parser.parse_args()

    segment_nuclei(zarr_path=args.zarr_path, nuclei_channel=args.nuclei_channel, label_name=args.label_name)

# Example usage:
# python main/src/segmentation.py data/20241107_infection.zarr \
#     --nuclei-channel nuclei_DAPI \
#     --label-name nuclei_labels
