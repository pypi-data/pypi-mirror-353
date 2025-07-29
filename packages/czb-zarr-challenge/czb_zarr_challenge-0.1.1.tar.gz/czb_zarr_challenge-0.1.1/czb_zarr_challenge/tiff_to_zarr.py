## -------------- Convert  OME-TIFF to OME-Zarr using iohub, used on Dataset 1 --------------

# https://czbiohub-sf.github.io/iohub/main/api/mm_converter.html

from iohub.convert import TIFFConverter

tiff_path = "data/KazanskyStar/Kazansky_MMStack.ome.tif"
zarr_path = "data/KazanskyStar_converted.zarr"

converter = TIFFConverter(tiff_path, zarr_path)
converter()
