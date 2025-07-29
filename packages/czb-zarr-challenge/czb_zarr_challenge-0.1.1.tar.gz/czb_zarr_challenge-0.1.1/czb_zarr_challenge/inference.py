# Profile the time it takes to read the data and to run inference with a pre-trained model 
# (e.g., those provided with torchivision). 

import time
import torch
import torch.nn.functional as F
from torchvision import models
from torch.utils.data import DataLoader
from tqdm import tqdm
from dataloader import OMEZarrDataset


def profile_inference(zarr_path, batch_size=4, num_batches=10):

    # here we'll use a pretrained resnet18 model from torchvision: docs at https://docs.pytorch.org/vision/main/models/generated/torchvision.models.resnet18.html
    device = torch.device("cpu")
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model = model.to(device)
    model.eval()

    dataset = OMEZarrDataset(zarr_path, axis="T")
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    total_data_load_time = 0.0
    total_inference_time = 0.0

    data_iter = iter(dataloader)

    for i in tqdm(range(num_batches), desc="Batches", unit="batch"):
        t0 = time.time() # time waiting for next batch
        try:
            batch5d = next(data_iter)  # shape = [B, 3, Z, H, W]
        except StopIteration: # last batch
            break
        total_data_load_time += time.time() - t0

        B, C, Z, H, W = batch5d.shape
        z_center = Z // 2
        batch2d = batch5d[:, :, z_center, :, :].float() # we need to get from 5d -> 2d, make shape (B, 3, H, W)

        batch2d = batch2d.to(device) # resnet needs 224x224 images (from resnet docs)
        batch2d = F.interpolate(batch2d, size=(224, 224), mode="bilinear", align_corners=False)

        # normalize using ImageNet stats (also from resnet docs)
        mean = torch.tensor([0.485, 0.456, 0.406], device=device).view(1, 3, 1, 1)
        std  = torch.tensor([0.229, 0.224, 0.225], device=device).view(1, 3, 1, 1)
        batch2d = (batch2d - mean) / std

        t1 = time.time() # inference time!
        with torch.no_grad():
            outputs = model(batch2d)
        total_inference_time += time.time() - t1

    # -------
    avg_data_load = total_data_load_time / num_batches
    avg_inference = total_inference_time / num_batches

    print(f"\nAverage batch loading time: {avg_data_load:.4f} s")
    print(f"Average inference time: {avg_inference:.4f} s")
    # -------
