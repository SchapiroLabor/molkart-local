import argparse
import pathlib
from molkartpy.core.get_cropsummary import get_cropSummary
from molkartpy.utils import image_info
from molkartpy.utils.plotting import create_crop_overview
import os

def get_args():
    parser = argparse.ArgumentParser(
        description="Generate crop summary for given image."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the input image file - TIFF or OME-TIFF, CYX, or YX format."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=".",
        help="Directory to save the crop summary file (default: current directory)."
    )
    parser.add_argument(
        "--output_stem",
        type=str,
        default="image",
        help="Stem name for the output crop summary file (default: image)."
    )
    parser.add_argument(
        "--crop_amount",
        type=int,
        default=4,
        help="Number of crops to extract (default: 4)."
    )
    parser.add_argument(
        "--crop_size",
        type=int,
        nargs=2,
        default=(500, 500),
        help="Size of each crop as width height (default: 500 500)."
    )
    parser.add_argument(
        "--nuclei_index",
        type=int,
        default=0,
        help="Index of the nuclei channel in the image (default: 0)."
    )
    parser.add_argument(
        "--nonzero_fraction",
        type=float,
        default=0.4,
        help="Minimum fraction of non-zero pixels required in the nuclei channel within a crop (default: 0.4)."
    )
    return parser.parse_args()

def main():
    args = get_args()
    args.input = os.path.abspath(args.input)

    # Read image
    img = image_info.read_image_dask(args.input)

    # Generate crop summary
    c_summary = get_cropSummary(
        img,
        crop_amount=args.crop_amount,
        crop_size=tuple(args.crop_size),
        nuclei_index=args.nuclei_index,
        nonzero_fraction=args.nonzero_fraction
    )

    summary = open(pathlib.Path(os.path.join(args.output, args.output_stem) + "_CropSummary.txt"), "w")
    summary.write(str(c_summary))
    summary.close()

    # Print results
    for crop_id, indices in c_summary.items():
        print(f"{crop_id}: {indices}")
    
    # Create crop overview plot
    create_crop_overview(
        img,
        c_summary,
        output=args.output,
        output_stem=args.output_stem,
        max_size=600
    )
