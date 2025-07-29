import numpy as np
import matplotlib.pyplot as plt
import imageio
import os
import zarr
import argparse
import iohub
from skimage import measure
from pathlib import Path
from iohub import open_ome_zarr
import imageio.v2 as imageio
from skimage.exposure import rescale_intensity # for 3D normalizing, does vol_norm = (vol - vol.min()) / (vol.max() - vol.min())
from infection_dynamics import compute_infection_onset, compute_nuclear_virus_volumes
from utils import hex_to_rgb01 
import dask.array as da 


def visualize_infection(
    zarr_path,
    output_dir="../output",
    timepoints=None,
    z_slice=None,
    plot_segmentation=True,
    show_infection=False,
    intensity_increase=2.0,
    count_increase=20,
):
    print(f"Creating visualization for {zarr_path}")
    """
    - visualizes the 3-channel image (and segmentation if desired) for a Zarr store, saves PNGs and a GIF in output_dir
    - if we pass a Plate path, e.g. 20241107_infection.zarr, we visualize the first Position within it. If we pass a Position path, e.g. 20241107_infection.zarr/C/2/000001/0, then we directly use that.
    """
    root = open_ome_zarr(store_path=zarr_path, mode="r", layout="auto") # Plate or Position
    if isinstance(root, iohub.ngff.Plate):
        _, position = next(iter(root.positions()))
    else:
        position = root

    array_path = position.metadata.multiscales[0].datasets[0].path
    image_array = position[array_path] # 5D numpy array, [T, C, Z, Y, X]
    shape = image_array.shape
    # dask_img5d = da.from_array(image_array, chunks=image_array.chunks) # parallelization!
    print(shape)
    T, C, Z, Y, X = shape

    # -----------
    ch_meta = position.metadata.omero.channels
    colors_hex = [ch.color for ch in ch_meta]  # ["FFFFFF","0000FF","FF00FF"]
    colors_rgb = [hex_to_rgb01(h) for h in colors_hex]
    # -----------

    seg_arr = None
    if plot_segmentation or show_infection:
        seg_arr = position.zgroup["labels"]["nuclei_labels"]["0"]

    onset_times = {}
    if show_infection:
        volumes, label_ids = compute_nuclear_virus_volumes(image_array, seg_arr, virus_channel_idx=2)
        onset_times = compute_infection_onset(volumes, label_ids, intensity_increase, count_increase)
        print("Computed infection onset times for each nucleus")

    if timepoints is None: # if timepoints aren't specified, do all of them
        timepoints = list(range(T))
    if z_slice is None: # middle slice if not specified
        z_slice = Z // 2

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    png_paths = []
    
    for t in timepoints: # get each channel at the z_slice
        print("timepoint ", t)
        phase3d = image_array[t, 0, z_slice, :, :].astype(np.float32) # 2d image array
        nuclei = image_array[t, 1, z_slice, :, :].astype(np.float32)
        virus = image_array[t, 2, z_slice, :, :].astype(np.float32)
    
        p_norm = rescale_intensity(phase3d, in_range='image', out_range=(0.0, 1.0)) * 0.7
        n_norm = rescale_intensity(nuclei, in_range='image', out_range=(0.0, 1.0))
        v_norm = rescale_intensity(virus, in_range='image', out_range=(0.0, 1.0)) * 0.2

        # building rgb composite! 
        rgb = np.zeros((Y, X, 3), dtype=np.float32) # all black
        phase_color = colors_rgb[0] # (1.0, 1.0, 1.0)
        rgb[..., 0] = p_norm * phase_color[0] # red channel
        rgb[..., 1] = p_norm * phase_color[1] # green
        rgb[..., 2] = p_norm * phase_color[2] # blue
        nuclei_color = colors_rgb[1] # (0.0, 0.0, 1.0)
        rgb[..., 0] = np.maximum(rgb[..., 0], n_norm * nuclei_color[0])
        rgb[..., 1] = np.maximum(rgb[..., 1], n_norm * nuclei_color[1])
        rgb[..., 2] = np.maximum(rgb[..., 2], n_norm * nuclei_color[2]) # only this contributes since nuclei are blue

        if show_infection:
            virus_color = colors_rgb[2] # (1.0, 0.0, 1.0)
            rgb[..., 0] += v_norm * virus_color[0] # red, contributes to magenta
            rgb[..., 1] += v_norm * virus_color[1]
            rgb[..., 2] += v_norm * virus_color[2] # blue, contributes to magenta

        rgb = np.clip(rgb, 0.0, 1.0)

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(rgb, interpolation='nearest')

        # ---------------------
        if plot_segmentation:
            seg_arr = position.zgroup["labels"]["nuclei_labels"]["0"]
            mask3d = seg_arr[t, 0, :, :, :]
            mask = mask3d[z_slice]

            # https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.find_contours 
            contours = measure.find_contours(mask, 0.5) 
            for contour in contours: # each contour is a ndarray of (row, column) coordinates
                ax.plot(contour[:, 1], contour[:, 0], linewidth=1.0, color='lime')

            if show_infection:
                seg_slice = seg_arr[t, 0, z_slice, :, :]
                unique_labels = np.unique(seg_slice)
                unique_labels = unique_labels[unique_labels != 0]  # drop background

                for L in unique_labels:
                    t_inf = onset_times.get(int(L), np.inf)
                    if t >= t_inf:
                        ys, xs = np.where(seg_slice == L) # all y,x pixels belonging to this nucleus label in this slice
                        y_centroid = ys.mean()
                        x_centroid = xs.mean()
                        ax.plot(x_centroid, y_centroid, marker="x", color="magenta", markersize=3)
        # ---------------------

    # --- png and gif creation with the help of ChatGPT ---
        ax.axis('off')
        ax.set_title(f"T={t}, Z={z_slice}")

        png_path = output_dir / f"vis_t{t:03d}_z{z_slice:02d}.png"
        fig.savefig(png_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        png_paths.append(str(png_path))

    # make GIF
    images = [imageio.imread(p) for p in png_paths]
    gif_path = output_dir / "timeseries.gif"
    imageio.mimsave(gif_path, images, fps=2)
    print(f"GIF is saved in {gif_path}")
    # ------------------------------------------------------


# ------------------------------------- CLI ----------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="visualize cell infection with channel and optional segmentation overlay")
    parser.add_argument("zarr_path", type=str)
    parser.add_argument("output_dir", type=str, help="PNGs and GIF will be saved here")
    parser.add_argument("--timepoints", type=int, nargs="+", default=None, help="timepoints to visualize (default: all)")
    parser.add_argument("--z-slice", type=int, default=None, help="Z index to visualize (default: middle slice)")
    parser.add_argument("--no-segmentation", dest="plot_segmentation", action="store_false", help="no segmentation contours (default is to have them)")
    parser.add_argument(
        "--show-infection", dest="show_infection", action="store_true",
        help="If set, recolor nuclei in magenta once virus volume crosses threshold"
    )
    parser.set_defaults(show_infection=False)

    parser.add_argument(
        "--intensity-increase", dest="intensity_increase", type=float, default=2.0,
        help="Fold-change threshold for nuclear infection onset (default = 2.0)"
    )
    parser.add_argument(
        "--count-increase", dest="count_increase", type=int, default=20,
        help="Absolute voxel‐count increase threshold for infection onset (default = 20)"
    )
    parser.set_defaults(plot_segmentation=True)

    args = parser.parse_args()

    visualize_infection(
        zarr_path=args.zarr_path,
        output_dir=args.output_dir,
        timepoints=args.timepoints,
        z_slice=args.z_slice,
        plot_segmentation=args.plot_segmentation,
        show_infection=args.show_infection,
        intensity_increase=args.intensity_increase,
        count_increase=args.count_increase,
    )

# Example usage:

# python main/src/visualize.py \
#     data/20241107_infection.zarr \
#     main/output \
#     --no-segmentation

# python main/src/visualize.py \
#     data/20241107_infection.zarr \
#     main/output

# python main/src/visualize.py \
#     data/20241107_infection.zarr \
#     main/output \
#     --show-infection \
#     --intensity-increase 2.0 \
#     --count-increase 20
