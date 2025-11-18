import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pathlib

def create_crop_overview(image, crop_dict, output, output_stem, max_size=600):
    """
    Create a crop overview PNG with at most max_size x max_size resolution.
    
    Parameters
    ----------
    image : np.ndarray
        Input image, shape (C, H, W) or (H, W)
    crop_dict : dict
        Crop dictionary with coordinates, e.g.,
        {'crop_01': [(h0,h1),(w0,w1)], ...}
    output : str or Path
        Output directory
    output_stem : str
        Base name for output PNG
    max_size : int
        Maximum size for width and height of output image
    """
    # Compute max projection once
    image_max = image.max(axis=0) 

    h, w = image_max.shape

    # Compute scale factor to keep max dimension <= max_size
    scale = min(1.0, max_size / max(h, w))

    if scale < 1.0:
        from skimage.transform import resize
        new_h, new_w = int(h*scale), int(w*scale)
        image_max = resize(image_max, (new_h, new_w), anti_aliasing=True)

    fig, ax = plt.subplots(figsize=(6,6))  # fixed figure size for display
    ax.imshow(image_max, cmap="gray")

    for idx, crop in enumerate(crop_dict.values(), start=1):
        h0, h1 = crop[0]
        w0, w1 = crop[1]

        # scale crop coordinates
        h0, h1 = int(h0*scale), int(h1*scale)
        w0, w1 = int(w0*scale), int(w1*scale)

        rect = patches.Rectangle((w0, h0), w1-w0, h1-h0, linewidth=1, edgecolor='red', facecolor='none')
        ax.add_patch(rect)
        ax.text(w0, h0, str(idx), color='white', fontsize=8)

    out_path = pathlib.Path(output) / f"{output_stem}_CropSummary.png"
    plt.axis('off')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)