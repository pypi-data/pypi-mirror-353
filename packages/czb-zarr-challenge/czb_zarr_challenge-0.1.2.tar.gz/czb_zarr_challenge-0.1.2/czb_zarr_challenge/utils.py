import iohub
import iohub.ngff
from iohub import open_ome_zarr


# --- code block generated with the help of ChatGPT ---
def hex_to_rgb01(hexstr): 
    # converts a 6-character hex string (RRGGBB) to float RGB triple in [0,1]
    # used for converting channel colors from .zattrs
    r = int(hexstr[0:2], 16) / 255.0
    g = int(hexstr[2:4], 16) / 255.0
    b = int(hexstr[4:6], 16) / 255.0
    return (r, g, b)
# -----------------------------------------------------


def load_position_and_metadata(zarr_path):
    """
    If we pass a Plate path, we select the first Position within it. If we pass a Position path, use that directly.
    Returns (position, img5d, colors_rgb):
      - position: iohub.ngff.Position
      - img5d: 5D Zarr array of shape (T, C, Z, Y, X)
      - colors_rgb: list of length C of (r, g, b) floats from .omero channels
    """
    root = open_ome_zarr(store_path=zarr_path, mode="r", layout="auto")

    if isinstance(root, iohub.ngff.Plate):
        _, position = next(iter(root.positions()))
    else:
        position = root

    array_path = position.metadata.multiscales[0].datasets[0].path
    img5d = position[array_path] # (T, C, Z, Y, X)

    omero_meta = position.metadata.omero
    colors_rgb = [hex_to_rgb01(ch.color) for ch in omero_meta.channels]

    return position, img5d, colors_rgb
