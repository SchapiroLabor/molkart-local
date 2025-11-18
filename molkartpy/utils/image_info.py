import tifffile
import dask.array as da
from ome_types import from_tiff

def extract_img_props(img_path,pixel_size=None):

    #Extract data_type, pyramidal specs, height, width
    with tifffile.TiffFile(img_path) as tif:
        series = tif.series[0]
        pyr_levels=len(series.levels)
        is_pyramid=pyr_levels > 1
        data_type=series.dtype.name

        full_res_shape = series.shape  # tuple
        ndim = len(full_res_shape)

        try:
            axes = series.axes
        except Exception:
            axes = None

        if axes:
            axes = axes.upper()
        else:
            # Fallback: guess axes
            # - 2D -> YX
            # - 3D -> CYX (assume channel-first)
            axes = "YX" if ndim == 2 else "CYX"

        # Normalize: drop Z if present
        if "Z" in axes:
            z_index = axes.index("Z")
            full_res_shape = tuple(
                dim for i, dim in enumerate(full_res_shape) if i != z_index
            )
            axes = ''.join(ax for ax in axes if ax != "Z")

        # Now handle remaining patterns (2D or 3D)
        if axes == "YX" or axes == "XY":
            channels = 1
            h, w = full_res_shape[-2], full_res_shape[-1]

        elif axes == "CYX":
            channels = full_res_shape[0]
            h, w = full_res_shape[-2], full_res_shape[-1]

        elif axes == "CXY":
            channels = full_res_shape[0]
            h, w = full_res_shape[-2], full_res_shape[-1]

        elif axes == "YXC":
            channels = full_res_shape[-1]
            h, w = full_res_shape[0], full_res_shape[1]

        else:
            print(f"Warning: Unrecognized axes '{axes}'. Falling back to YX.")
            channels = 1
            h, w = full_res_shape[-2], full_res_shape[-1]

        if is_pyramid:
            subres_dims = [
                level.pages[0].shape for level in series.levels[1:]
            ]
        else:
            subres_dims = None

        # dask_array = da.from_array(series.pages[0].asarray(), chunks="auto")
        # dask_chunksize = dask_array.chunksize
        
    #Try to extract pixel size from ome-xml
    if pixel_size is None:
        print('Pixel size not specified in the arguments (-mpp)')
        try:
            metadata = from_tiff(img_path)
            pixel_size = metadata.images[0].pixels.physical_size_x
            pixel_size_unit = metadata.images[0].pixels.physical_size_x_unit
            print(f'Detected pixel size: {pixel_size} {pixel_size_unit}')
        except Exception as err:
            print(err)
            print('Pixel size or pixel size unit detection using ome-types failed')
            pixel_size = 1
            pixel_size_unit="pixel"
    else:
        pixel_size=pixel_size
        pixel_size_unit="µm"

    
    img_props = {
        "pixel_size": pixel_size,
        "pixel_size_unit": pixel_size_unit,
        "data_type": data_type,
        "pyramid": is_pyramid,
        "levels": pyr_levels,
        "sub_levels_dims": subres_dims,
        "size_x": w,
        "size_y": h,
        "channels": channels,
        "axes": axes,
        # "chunksize": dask_chunksize,
    }
    
    return img_props

def read_image_dask(img_path):
    """Read image using dask array from tifffile"""
    img_dask = da.from_array(tifffile.imread(img_path), chunks="auto")
    if img_dask.ndim == 2:
        img_dask = img_dask.reshape((1, img_dask.shape[0], img_dask.shape[1]))
    return img_dask