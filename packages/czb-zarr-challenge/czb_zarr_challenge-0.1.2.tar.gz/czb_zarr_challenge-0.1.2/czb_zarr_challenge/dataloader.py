# Implement a PyTorch DataLoader that uses iohub and the OME-Zarr (Dataset 2) to 
# read data. 

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import iohub
import iohub.ngff
from iohub import open_ome_zarr
import tqdm
from pathlib import Path
from czb_zarr_challenge.get_metadata import get_metadata

# https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html
# basic skeleton of the OMEZarrDataset class (class header, __init__, __len__, __getitem__) generated with the help of ChatGPT. Function contents written by myself.

class OMEZarrDataset(Dataset):

    def __init__(self, zarr_path, axis="T"): # each timepoint is a training sample
        self.zarr_path = zarr_path
        self.axis = axis # could be T, C, or Z
        self.axis_index = {"T": 0, "C": 1, "Z": 2}[self.axis]

        self.dataset = open_ome_zarr(store_path=zarr_path, mode="r", layout="auto")

        # get the position, like in get_metadata.py
        if isinstance(self.dataset, iohub.ngff.Plate):
            self.position = next(iter(self.dataset.positions()))[1]
        else:
            self.position = self.dataset

        array_path = self.position.metadata.multiscales[0].datasets[0].path
        self.image_array = self.position[array_path] # 5D numpy array, [T, C, Z, Y, X]
        print("self.image_array shape is ", self.image_array.shape) # sanity check!

        self.metadata = get_metadata(zarr_path)
        self.num_samples = self.image_array.shape[self.axis_index]
        
    def __len__(self):
        return self.num_samples
    
    def __getitem__(self, idx):
        slc = [slice(None)] * 5
        slc[self.axis_index] = idx 
        # for example if we want timepoint 3 then we get [3, :, :, :, :]
        # or to get the 5th Z-slice then axis should be init to "Z" and we'll get [:, :, 5, :, :]
        data = self.image_array[tuple(slc)] # get 4D block
        # squeeze to rm dimension we sliced on. Ex. if sliced on timepoint then (1, C, Z, Y, X) -> (C, Z, Y, X)
        data = np.squeeze(data) 
        image = torch.tensor(data, dtype=torch.float32)
        return image

def get_dataloader(zarr_path, batch_size=4, shuffle=True, axis="T"):
    dataset = OMEZarrDataset(zarr_path, axis=axis)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

# --------------------------------------------

dl = get_dataloader("data/20241107_infection.zarr", batch_size=2, axis="T")

for batch in dl:
    print(batch.shape)
    break


