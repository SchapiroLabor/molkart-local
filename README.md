# molkart-local
Repository for local modules used in nf-core/molkart - https://nf-co.re/molkart/dev.

The purpose of this repository is to have one place to manage local modules for molkart mostly in the context of Docker images, as their functionalities are either overlapping or basic so it is possible to include more tools in one image.

## Included scripts:

* molkart_clahe.py - Contrast-limited adjusted histogram equalization (CLAHE) on single-channel `tif` images.
* molkart_crophdf5.py - converts input to `hdf5` and creates crops and a CropOverview.
* molkart_croptiff.py - creates `tiff` crops based on a provided CropOverview (To be adapted)
* molkart_maskfilter.py - takes a segmentation mask and filters cells based on area from the mask.
* molkart_spot2cell.py - matches a spot table to a segmentation mask to produce a cell-by-transcript matrix.
* molkart_stack.py - takes multiple input images and concatenates them to a stack - pyramidal output. (channel names not preserved)
* molkartqc.py - gathers provided quality control metrices and gathers them into one `csv` file.