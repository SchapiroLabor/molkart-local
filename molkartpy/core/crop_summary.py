import random
import math
import numpy as np
from skimage.filters import threshold_otsu

def otsu_from_random_sample(arr, max_pixels=1000000):
    """
    Compute Otsu threshold from a random subset of up to `max_pixels` pixels.
    Works on Dask arrays without loading the full image.
    """
    H, W = arr.shape

    total = H * W

    if total <= max_pixels:
        # Just load the whole thing if it's small enough
        sample = arr.compute()
        return threshold_otsu(sample)

    # Sampling probability
    p = max_pixels / total

    p_axis = math.sqrt(p)
    row_mask = np.random.rand(H) < p_axis
    col_mask = np.random.rand(W) < p_axis

    sample = arr[row_mask][:, col_mask].compute()

    # If sample is empty (extremely unlikely), fallback to coarse grid
    if sample.size == 0:
        stride = int(math.sqrt(total / max_pixels))
        sample = arr[::stride, ::stride].compute()

    return threshold_otsu(sample)

def get_cropSummary(image, crop_amount=4, crop_size=(50, 50), nuclei_index=0, nonzero_fraction=0.3):
    """Get cropping summary for a given image based on non-zero pixel fraction.

    Args:
        image (dask.array): Input image as a Dask array.
        nuclei_index (int): Index of the nuclei channel.
        nonzero_fraction (float): Fraction how much of the crop can be empty.
    """
    nuclei_channel = image[nuclei_index, :, :]
    height, width = nuclei_channel.shape

    previous_crops = []
    indices = {}
    count = 1

    attempts = 0
    max_attempts = crop_amount * 50

    thresh = otsu_from_random_sample(nuclei_channel)
    while count < crop_amount+1 and attempts < max_attempts:
        attempts += 1

        # compute crop bounding box
        ext_h = crop_size[1] // 2
        ext_w = crop_size[0] // 2

        h = random.randint(ext_h, height - ext_h)
        w = random.randint(ext_w, width - ext_w)

        h_up, h_down = h - ext_h, h + ext_h
        w_lt, w_rt = w - ext_w, w + ext_w

        # check overlap
        if any(not (h_down <= ph_up or h_up >= ph_down or w_rt <= pw_lt or w_lt >= pw_rt)
               for ph_up, ph_down, pw_lt, pw_rt in previous_crops):
            continue
        crop = nuclei_channel[h_up:h_down, w_lt:w_rt]
        frac = (crop > thresh).mean().compute()
        if frac >= nonzero_fraction:
            crop_id = f"crop_{count:02d}"
            previous_crops.append((h_up, h_down, w_lt, w_rt))
            indices.update({crop_id: [(h_up, h_down), (w_lt, w_rt)]})
            count += 1

    return indices