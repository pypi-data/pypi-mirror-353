# CZB-zarr-challenge

## Getting started
### Installation

1. **Clone and install locally**  
   ```bash
   git clone https://github.com/audreychun/czb-zarr-challenge.git
   cd czb-zarr-challenge
   pip install -e .
   ```

2. **Install from PyPI**  
   ```bash
   pip install czb-zarr-challenge
   ```

### Data Downloads
 
> Download or place your OME-Zarr datasets (e.g., `KazanskyStar_converted.zarr` or `20241107_infection.zarr`) into `data/` before running any commands.

- **KazanskyStar dataset:** [link](https://public.czbiohub.org/comp.micro/SWE_2025/KazanskyStar/)

- **20241107 dataset:** [link](https://public.czbiohub.org/comp.micro/SWE_2025/20241107_infection.zarr/)
  - This one can be downloaded using `wget -m -np -nH --cut-dirs=2 -R "index.html*" https://public.czbiohub.org/comp.micro/SWE_2025/20241107_infection.zarr/`.

### iohub Installation

To get the latest iohub (v0.3.0), clone and install manually:

```bash
git clone https://github.com/czbiohub-sf/iohub.git
pip install ./iohub
```

## OME-TIFF → OME-Zarr Conversion

Use the provided `tiff_to_zarr.py` script. This leverages IOHub’s `TiffConverter` to convert a Micromanager OME-TIFF to OME-Zarr. For Task 1, running the following command will convert Dataset 1 (Micromanager OME-TIFF layout) to OME-Zarr in the same /data folder.

```bash
python tiff_to_zarr.py
```

## Metadata Extraction

To generate a metadata `.txt` file with key information (shape, chunk size, dtype, scale, channel names) from a Zarr store:

```bash
czb-zarr-challenge metadata   --zarr_path /path/to/YourData.zarr   --output_path ./example_metadata.txt
```

### Examples

```bash
czb-zarr-challenge metadata   --zarr_path data/KazanskyStar_converted.zarr   --output_path metadata_KazanskyStar.txt

czb-zarr-challenge metadata   --zarr_path data/20241107_infection.zarr   --output_path metadata_20241107.txt
```

> Code for this metadata extraction is found in `get_metadata.py`. It uses IOHub’s `open_ome_zarr(...)` to open the store and IOHub’s node objects to navigate Plate → Position → ImageArray. The script prints the full OME-Zarr hierarchy to stdout and writes a human-readable `.txt` containing:
>
> - **Layout** (Plate / Position / TiledPosition)  
> - **Shape** (e.g., `(T, C, Z, Y, X)`)  
> - **Chunk size** (e.g., `(1, 1, 10, 512, 512)`)  
> - **Dtype** (e.g., `float32`)  
> - **Scale** (e.g., `(1.0, 0.5, 0.5)`)  
> - **Channel names** (e.g., `['Plate3D', 'nuclei_DAPI', 'virus_mCherry']`)

## Inference Profiling

The custom PyTorch `DataLoader` (in `dataloader.py`) uses ioub and OME-Zarr to read 5D volumes from Dataset 2. We profile both data-loading and inference times using a pretrained ResNet-18.

```bash
czb-zarr-challenge run_inference   --zarr_path data/20241107_infection.zarr
```

This will print a tqdm progress bar and then report:

```
Average batch loading time:   X.XXXX s
Average inference time:       Y.YYYY s
```

> - The `run_inference` subcommand calls `profile_inference(...)` in `inference.py`.  
> - It takes the center Z slice of each 5D batch, resizes to 224×224, normalizes (ImageNet stats), and runs a forward pass on ResNet-18.

## Nuclei Segmentation

To segment nuclei on the DAPI channel and save labels back into the same OME-Zarr store:

```bash
czb-zarr-challenge segment   data/20241107_infection.zarr   --nuclei-channel nuclei_DAPI   --label-name nuclei_labels
```

- `zarr_path` – path to the OME-Zarr store  
- `--nuclei-channel` (default: `nuclei_DAPI`)  
- `--label-name` (default: `nuclei_labels`)  

> Main logic is found in `segmentation.py`. For each timepoint, it:
> 1. Reads a 3D volume from the DAPI channel.  
> 2. Applies a global Otsu threshold → 3D blob detection (LoG) → 3D watershed.  
> 3. Builds a `(T, 1, Z, Y, X)` label volume (dtype = `uint16`).  
> 4. Writes it under `/labels/<label_name>/0` in the same Zarr group, preserving chunking and compressor.

### Parallelized Segmentation

You can also compare single-worker vs. parallel segmentation times:

```bash
czb-zarr-challenge segment_p   data/20241107_infection.zarr   --nuclei-channel nuclei_DAPI   --label-name nuclei_labels   --profile
```

- The `--profile` flag runs segmentation twice (once on a single worker, once on eight workers) and prints elapsed times for comparison.

## Visualization

To visualize cell infection (with optional segmentation contours):

```bash
czb-zarr-challenge visualize   data/20241107_infection.zarr   output/
```

### Examples

```bash
czb-zarr-challenge visualize   data/20241107_infection.zarr   output/   --timepoints 0 5 10   --z-slice 8   --no-segmentation   --show-infection   --intensity-increase 2.0   --count-increase 20
```

- `zarr_path` – input OME-Zarr store  
- `output_dir` – directory to save PNGs and GIFs  
- `--timepoints` (〈int〉…) – specific timepoints to visualize (default = all)  
- `--z-slice` 〈int〉 (default = middle slice)  
- `--no-segmentation` (disable contour overlay)  
- `--show-infection` (recolor nuclei in magenta when virus volume crosses threshold)  
- `--intensity-increase` 〈float〉 (default = 2.0) – fold-change threshold for infection onset  
- `--count-increase` 〈int〉 (default = 20) – absolute voxel count increase threshold for infection onset  

> **Implementation details:**  
> - The `visualize` subcommand calls `visualize_infection(...)` in `visualize.py`.  
> - It can overlay segmentation contours and recolor infected nuclei once criteria are met.

## Dependencies & Environment

To reproduce all functionality:

1. **Create a fresh virtual environment**  
   ```bash
   python3 -m venv venv_repro
   source venv_repro/bin/activate
   pip install --upgrade pip
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
---
