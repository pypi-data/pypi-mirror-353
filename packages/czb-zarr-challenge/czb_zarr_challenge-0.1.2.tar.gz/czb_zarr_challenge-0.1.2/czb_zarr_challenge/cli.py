import argparse
import sys
from czb_zarr_challenge.get_metadata import get_metadata, save_metadata_as_txt
from czb_zarr_challenge.inference import profile_inference
from czb_zarr_challenge.segmentation import segment_nuclei
from czb_zarr_challenge.segmentation_parallelized import segment_nuclei_dask
from czb_zarr_challenge.visualize import visualize_infection

# -----------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="czb-zarr-challenge",
        description="unified CLI for OME‐Zarr metadata, inference, segmentation, visualization, etc.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ------------ to extract metadata ------------
    """ 
    Example usage:
    czb-zarr-challenge metadata -data/KazanskyStar_converted.zarr metadata1.txt
    czb-zarr-challenge metadata -data/20241107_infection.zarr metadata2.txt
    """

    metadata_parser = subparsers.add_parser("metadata", help="extract metadata from an OME-Zarr store and save as txt file")
    metadata_parser.add_argument("--zarr_path", type=str, help="input Zarr dataset path")
    metadata_parser.add_argument("--output_path", type=str, help="output metadata text file path")
    metadata_parser.set_defaults(func=_handle_metadata)

    # ------------ inference with custom Dataloader and ResNet ------------
    """ 
    Example usage:
    czb-zarr-challenge run_inference data/20241107_infection.zarr
    """
    inference_parser = subparsers.add_parser("run_inference", help="profile data loading & inference times (ResNet18) on an OME-Zarr dataset")
    inference_parser.add_argument("--zarr_path", help="Path to input OME-Zarr store")
    inference_parser.set_defaults(func=_handle_inference)

    # ------------ segment nuclei (original) ------------
    """ 
    Example usage:
    czb-zarr-challenge segment data/20241107_infection.zarr \
        --nuclei-channel nuclei_DAPI \
        --label-name nuclei_labels
    """
    seg_parser = subparsers.add_parser("segment", description="segment nuclei from a DAPI channel and save the labels in a OME‑Zarr store")
    seg_parser.add_argument("zarr_path", type=str, help="path to the OME‑Zarr store")
    seg_parser.add_argument("--nuclei-channel", type=str, default="nuclei_DAPI", help="channel to segment (default: nuclei_DAPI)")
    seg_parser.add_argument("--label-name", type=str, default="nuclei_labels", help="output label dataset name")
    seg_parser.set_defaults(func=_handle_segmentation)

    # ------------ segment nuclei (profile parallelization) ------------
    """ 
    Example usage:
    czb-zarr-challenge segment_p data/20241107_infection.zarr \
        --nuclei-channel nuclei_DAPI \
        --label-name nuclei_labels \
        --profile
    """
    seg_parallel_parser = subparsers.add_parser("segment_p", description="segment nuclei from a DAPI channel with parallelization, and save the labels in a OME‑Zarr store")
    seg_parallel_parser.add_argument("zarr_path", type=str, help="path to the OME‑Zarr store")
    seg_parallel_parser.add_argument("--nuclei-channel", type=str, default="nuclei_DAPI", help="channel to segment (default: nuclei_DAPI)")
    seg_parallel_parser.add_argument("--label-name", type=str, default="nuclei_labels", help="output label dataset name")
    seg_parallel_parser.add_argument("--profile", action="store_true", help=("this will run segmentation twice (once on single worker and once on eight workers), print elapsed times for comparison"))
    seg_parallel_parser.set_defaults(func=_profile_parallel_segmentation)

    # ------------ visualization! ------------
    """ 
    Example usage:
    czb-zarr-challenge visualize data/20241107_infection.zarr \
        main/output \
        --no-segmentation

    czb-zarr-challenge visualize data/20241107_infection.zarr \
        main/output

    czb-zarr-challenge visualize data/20241107_infection.zarr \
        main/output \
        --show-infection \
        --intensity-increase 2.0 \
        --count-increase 20

    """
    vis_parser = subparsers.add_parser("visualize",description="visualize cell infection with channel and optional segmentation overlay")
    vis_parser.add_argument("zarr_path", type=str)
    vis_parser.add_argument("output_dir", type=str, help="PNGs and GIF will be saved here")
    vis_parser.add_argument("--timepoints", type=int, nargs="+", default=None, help="timepoints to visualize (default: all)")
    vis_parser.add_argument("--z-slice", type=int, default=None, help="Z index to visualize (default: middle slice)")
    vis_parser.add_argument("--no-segmentation", dest="plot_segmentation", action="store_false", help="no segmentation contours (default is to have them)")
    vis_parser.add_argument("--show-infection", dest="show_infection", action="store_true", help="recolor nuclei in magenta once virus volume crosses threshold")
    vis_parser.set_defaults(show_infection=False)
    vis_parser.add_argument("--intensity-increase", dest="intensity_increase", type=float, default=2.0, help="fold-change threshold for infection onset")
    vis_parser.add_argument("--count-increase", dest="count_increase", type=int, default=20,
        help="Absolute voxel‐count increase threshold for infection onset (default = 20)"
    )
    vis_parser.set_defaults(plot_segmentation=True)
    vis_parser.set_defaults(func=_handle_visualization)

    # ------
    args = parser.parse_args()
    return args.func(args)
    # ------

# -----------------------------------------------------------------

def _handle_metadata(args):
    metadata = get_metadata(args.zarr_path)
    print("\n--- Metadata ---")
    for key, value in metadata.items():
        print(f"{key}: {value}")
    save_metadata_as_txt(metadata, args.output_path)
    sys.exit(0)

def _handle_inference(args):
    print(f"\n--- Profiling inference for Zarr store: {args.zarr_path} ---")
    profile_inference(zarr_path=args.zarr_path)
    sys.exit(0)

def _handle_segmentation(args):
    segment_nuclei(zarr_path=args.zarr_path, nuclei_channel=args.nuclei_channel, label_name=args.label_name)
    sys.exit(0)

def _profile_parallel_segmentation(args):
    segment_nuclei_dask(zarr_path=args.zarr_path, nuclei_channel=args.nuclei_channel, label_name=args.label_name, profile=args.profile,)
    sys.exit(0)

def _handle_visualization(args):
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
    sys.exit(0)

# -----------------------------------------------------------------

if __name__ == "__main__":
    main()