# molkart-local / MolkartGarage
Repository for local modules used in nf-core/molkart - https://nf-co.re/molkart/dev.

The purpose of this repository is to have one place to manage local modules for molkart mostly in the context of Docker images, as their functionalities are either overlapping or basic so it is possible to include more tools in one image.

## Included scripts:

### Contrast-limited adaptive histogram equalization (CLAHE)
* molkart_clahe.py - Contrast-limited adjusted histogram equalization (CLAHE) on single-channel `tif` images.\

| Argument        | Required | Default Value | Description                                 |
|-----------------|----------|---------------|---------------------------------------------|
| --input     | Yes      | N/A           | File path to input image.                   |
| --output    | Yes      | N/A           | Path to output image.                       |
| --cliplimit     | Yes      | 0.01          | Clip Limit for CLAHE.                       |
| --kernel        | No       | 25            | Kernel size for CLAHE.                      |
| --nbins         | No       | 256           | Number of bins for CLAHE.                   |
| --pixel-size| No       | N/A           | Image pixel size.                           |
| --tile-size     | No       | 1072          | Tile size for pyramid generation (must be divisible by 16). |
| --version       | No       | 0.1.1         | Print version and exit   |


### Spot2cell - Transcript assignment to cell labels
* molkart_spot2cell.py - matches a spot table to a segmentation mask to produce a cell-by-transcript matrix.

| Argument         | Required | Default Value | Description                     |
|------------------|----------|---------------|---------------------------------|
| --spot_table| No       | N/A           | Spot table to project.         |
| --cell_mask | No       | N/A           | Sample ID.                      |
| --output        | No       | N/A           | Output path.                    |
| --version       | No       | 0.1.1         | Print version and exit |

### Maskfilter - Filter segmentation masks by area
* molkart_maskfilter.py - takes a segmentation mask and filters cells based on area from the mask.

| Argument       | Required | Default Value | Description                                       |
|----------------|----------|---------------|---------------------------------------------------|
| --input    | Yes      | N/A           | File path to input image.                         |
| --output   | Yes      | N/A           | Path to output image.                             |
| --output_qc    | No       | N/A           | Path to output qc csv file.                       |
| --min_area     | No       | None          | Lower area (in px) threshold for cell removal.    |
| --max_area     | No       | None          | Upper area (in px) threshold for cell removal.    |
| --version      | No       | 0.1.1         | Print version and exit         |

### Other scripts
* molkart_crophdf5.py - converts input to `hdf5` and creates crops and a CropOverview.
* molkart_croptiff.py - creates `tiff` crops based on a provided CropOverview (To be adapted)
* molkart_stack.py - takes multiple input images and concatenates them to a stack - pyramidal output. (channel names not preserved)
* molkartqc.py - gathers provided quality control metrices and gathers them into one `csv` file.
