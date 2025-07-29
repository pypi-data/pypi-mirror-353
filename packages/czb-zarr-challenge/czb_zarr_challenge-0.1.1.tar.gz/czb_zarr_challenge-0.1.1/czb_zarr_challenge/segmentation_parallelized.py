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
import dask
import dask.array as da
from dask.diagnostics import ProgressBar
import dask.multiprocessing
from functools import partial
import time

# ------------------------------

def _segment_one_timepoint(dapi_vol_t):
    """
    dapi_vol_t is the 3d nparray of the nuclei_dapi channel for time t
    Returns a 3d label array (labels are different nuclei integer IDs)
    """
    Z, Y, X = dapi_vol_t.shape
    label_vol = np.zeros((Z, Y, X), dtype=np.uint16)

    thresh = threshold_otsu(dapi_vol_t)
    mask3d = dapi_vol_t > thresh

    dist = ndi.distance_transform_edt(mask3d)
    blobs = blob_log(mask3d.astype(np.uint8), min_sigma=3, max_sigma=6, threshold=0.03)
    markers = np.zeros_like(dapi_vol_t, dtype=np.int32)
    for i, blob_i in enumerate(blobs, start=1):
        zi, yi, xi, _ = blob_i
        zi, yi, xi = int(round(zi)), int(round(yi)), int(round(xi))
        markers[zi, yi, xi] = i

    markers, _ = ndi.label(markers > 0)
    label_vol = watershed(-dist, markers, mask=mask3d)

    return label_vol

# ------------------------------

def segment_nuclei_dask(zarr_path, nuclei_channel="nuclei_DAPI", label_name="nuclei_labels", profile=False):
    root = open_ome_zarr(zarr_path, mode="r+", layout="auto")

    positions = ([p for _, p in root.positions()] if isinstance(root, iohub.ngff.Plate) else [root])

    for pos in positions:
        array_path = pos.metadata.multiscales[0].datasets[0].path

        ch_meta = pos.metadata.omero.channels
        channels = [ch.label for ch in ch_meta]
        c_idx = channels.index(nuclei_channel)

        image_data = pos[array_path] # Zarr array (ImageArray), shape (T, C, Z, Y, X)
        dask_data = da.from_array(image_data, chunks=image_data.chunks)
        dapi_dask = dask_data[:, c_idx]

        zarr_group = pos.zgroup

        if "labels" in zarr_group:
            lbl_root = zarr_group["labels"]
        else:
            lbl_root = zarr_group.create_group("labels")
            
        if label_name in lbl_root:
            del lbl_root[label_name]
        lbl_group = lbl_root.create_group(label_name)
        lbl_chunks = (image_data.chunks[0], 1, image_data.chunks[2], image_data.chunks[3], image_data.chunks[4])

        T, C, Z, Y, X = image_data.shape
        lbl_group = lbl_group.create_dataset(name="0", shape=(T, 1, Z, Y, X), chunks=lbl_chunks, dtype="uint16", compressor=image_data.compressor)

        seg_tasks = []
        for t in range(T):
            task_t = dask.delayed(_segment_one_timepoint)(dapi_dask[t].compute()) # compute() brings a (Z,Y,X) 3d numpy volume to CPU
            seg_tasks.append(task_t)

        if profile:
            print("Profiling segmentation tasks")

            # single‐worker (like no parallelization) to get baseline
            single_mp = partial(dask.multiprocessing.get, num_workers=1)
            with ProgressBar():
                t0 = time.perf_counter()
                volumes_1 = dask.compute(*seg_tasks, scheduler=single_mp)
                t1 = time.perf_counter()
            elapsed_1 = t1 - t0
            print(f"1-worker (multiprocessing): {elapsed_1:.2f} s")

            # 8‐worker multiprocessing
            eight_mp = partial(dask.multiprocessing.get, num_workers=8)
            with ProgressBar():
                t0 = time.perf_counter()
                volumes_8 = dask.compute(*seg_tasks, scheduler=eight_mp)
                t1 = time.perf_counter()
            elapsed_8 = t1 - t0
            print(f"8-worker (multiprocessing): {elapsed_8:.2f} s")

            print(f"Speedup ≈ {elapsed_1 / elapsed_8:.2f}×")
            label_volumes = volumes_8 # just use this one to write back, no need for volumes_1 (just compute to get speed)

        else: # don't profile and just compute with thread‐based scheduler auto-using all cores
            label_volumes = dask.compute(*seg_tasks, scheduler="threads")

        for t_idx, lbl_vol_t in enumerate(tqdm(label_volumes)):
            lbl_group[t_idx, 0, :, :, :] = lbl_vol_t # (Z, Y, X) -> (1, 1, Z, Y, X)

        print(f"We're done segmenting all {T} timepoints")

# ------------------------------------- CLI ----------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="segment nuclei from a DAPI channel with parallelization, and save the labels in a OME‑Zarr store")
    parser.add_argument("zarr_path", type=str, help="path to the OME‑Zarr store")
    parser.add_argument("--nuclei-channel", type=str, default="nuclei_DAPI", help="channel to segment (default: nuclei_DAPI)")
    parser.add_argument("--label-name", type=str, default="nuclei_labels", help="output label dataset name")
    parser.add_argument("--profile", action="store_true", help=("this will run segmentation twice (once on single worker and once on eight workers), print elapsed times for comparison"))

    args = parser.parse_args()
    segment_nuclei_dask(
        zarr_path=args.zarr_path,
        nuclei_channel=args.nuclei_channel,
        label_name=args.label_name,
        profile=args.profile,
    )

# Example usage:
# python main/src/segmentation_parallelized.py \
#     data/20241107_infection.zarr \
#     --nuclei-channel nuclei_DAPI \
#     --label-name nuclei_labels \
#     --profile