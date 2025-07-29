import dask
import numpy as np
from scipy import stats
from skimage.filters import threshold_otsu
from iohub import open_ome_zarr
import dask.array as da 


def compute_nuclear_virus_volumes(img5d, seg_arr, virus_channel_idx=2):
    """
    seg_arr is a 5D label array of shape (T, 1, Z, Y, X). Each voxel is either a nucleus integer ID or 0 for background.
    For each nucleus label in seg_arr, compute volumes[t, label_id] = the total # of voxels inside that nucleus (across all Z) where virus_mCherry > threshold
    Returns volumes, nparray of shape (T, max_label+1). It is a time x label matrix where each entry is infected nucleus voxel count. We also return a list of all the integer nucleus labels.
    """
    T, C, Z, Y, X = img5d.shape
    virus_vol = img5d[:, virus_channel_idx, :, :, :].astype(np.float32) # (T, Z, Y, X) 

    all_labels = np.unique(seg_arr) # all nuclei labels, unique values in seg_arr
    all_labels = all_labels[all_labels != 0] # drop background
    volumes = np.zeros((T, int(all_labels.max()) + 1), dtype=np.int32) # time x label matrix. Each entry is voxel count

    for t in range(T):
        virus_t = virus_vol[t] # virus_mCherry intensity for this timepoint, (Z, Y, X) 
        seg_t = seg_arr[t, 0] # nucleus segmentation map for this timepoint, (Z, Y, X)

        thresh = threshold_otsu(virus_t.flatten())
        virus_binary_3d = virus_t > thresh # binary mask of virus voxels
 
        for label_id in all_labels: # for each nucleus
            mask3d = (seg_t == label_id) & virus_binary_3d # 1 if nucleus AND AND virus_mCherry above threshold
            volumes[t, label_id] = np.count_nonzero(mask3d) # total number of voxels within nucleus label_id at time t where virus_mCherry intensity above threshold

    return volumes, all_labels

# ------------------------------------------
# PARALLELIZED

def _compute_one_timepoint(virus_t, seg_t, all_labels):

    # for timepoint t, count per label how many voxels are in (seg_t == label) AND (virus_t > threshold)
    volumes_t = np.zeros((int(all_labels.max()) + 1), dtype=np.int32) # time x label matrix

    thresh = threshold_otsu(virus_t.flatten())
    virus_binary_3d = virus_t > thresh

    for label_id in all_labels:
        mask3d = (seg_t == label_id) & virus_binary_3d
        volumes_t[label_id] = np.count_nonzero(mask3d)

    return volumes_t

# --------------

def compute_nuclear_virus_volumes_dask(zarr_path: str, virus_channel_idx: int = 2):

    root = open_ome_zarr(zarr_path, mode="r", layout="auto")
    if hasattr(root, "positions"):
        _, position = next(iter(root.positions()))
    else:
        position = root

    array_path = position.metadata.multiscales[0].datasets[0].path
    zarr_img = position[array_path]

    dask_img5d = da.from_array(zarr_img, chunks=zarr_img.chunks)
    seg_path = f"{array_path}/labels/nuclei_labels/0"
    zarr_seg5d = position[seg_path]
    dask_seg5d = da.from_array(zarr_seg5d, chunks=zarr_seg5d.chunks)

    all_labels = np.array(da.unique(dask_seg5d[:, 0].ravel()).compute())
    all_labels = all_labels[all_labels != 0]

    T = dask_img5d.shape[0]
    tasks = []
    for t in range(T):
        # a slice is dask_img5d[t, virus_channel_idx] and is exactly one 3d chunk (10,800,1100)
        virus_chunk = dask_img5d[t, virus_channel_idx].compute()
        seg_chunk   = dask_seg5d[t, 0].compute()

        # wrap the function for counting infected voxels per nuclei in a delayed task
        task = dask.delayed(_compute_one_timepoint)(virus_chunk, seg_chunk, all_labels)
        tasks.append(task)

    results = dask.compute(*tasks, scheduler="threads") # launches up to 8 threads = 8 logical cores on my MacBook
    # results is tuple of length 14. Each item is a 1D nparray containing the infected voxel counts for each nuclei
    volumes = np.stack(results, axis=0)
    return volumes, all_labels

# ------------------------------------------

def compute_infection_onset(volumes, label_ids, intensity_increase=2.0, count_increase=20):
    """
    Computes the earliest timepoint at which each nucleus becomes infected, based on how nuclear virus count evolves over time
    Returns onset_times dictionary, {label_id: first time t that meets criteria or infinity if never meets criteria}
    A nucleus is infected at timepoint t if it has both:
        1. absolute change: virus voxel count has increased by at least count_increase
        2. relative change: virus voxel count has increased by at least intensity_increase × baseline at time 0
        (volumes[t, id] >= volumes[0, id] + absolute_delta) AND (volumes[t, id] >= fold_change * volumes[0, id])
    """
    T, _ = volumes.shape
    onset_times = {}

    for label_id in label_ids:
        baseline = int(volumes[0, label_id]) # virus level at starting timepoint 0 for this nucleus
        onset_time_t = np.inf
        for t in range(1, T):
            virus_voxel_count_t = int(volumes[t, label_id])
            if (virus_voxel_count_t >= baseline + count_increase) and (virus_voxel_count_t >= intensity_increase * max(baseline, 1)):
                onset_time_t = t
                break
        onset_times[label_id] = onset_time_t

    return onset_times