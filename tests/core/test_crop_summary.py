import pytest
import numpy as np
import dask.array as da
from molkartpy.core.crop_summary import otsu_from_random_sample, get_cropSummary
from skimage.filters import threshold_otsu


# ----------------------------
#  otsu_from_random_sample
# ----------------------------

def test_otsu_small_array_matches_skimage():
    arr = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    darr = da.from_array(arr, chunks=(50, 50))

    t_func = otsu_from_random_sample(darr, max_pixels=20000)
    t_true = threshold_otsu(arr)

    # threshold must be close (not bit-exact due to float conversions)
    assert abs(t_func - t_true) < 1.0


def test_otsu_large_array_sampling():
    arr = np.random.randint(0, 255, (2000, 2000), dtype=np.uint8)
    darr = da.from_array(arr, chunks=(500, 500))

    # Ensure function runs fast and returns a number
    t = otsu_from_random_sample(darr, max_pixels=50000)

    assert isinstance(t, (int, float, np.integer, np.floating))


def test_otsu_empty_sample_fallback():
    """
    Force empty sampling by overriding np.random.rand to return 1 everywhere.
    Then verify fallback sampling is used.
    """
    arr = np.random.randint(0, 255, (500, 500), dtype=np.uint8)
    darr = da.from_array(arr, chunks=(200, 200))

    original_rand = np.random.rand

    try:
        # Always return 1 → row_mask & col_mask = False everywhere → empty crop
        np.random.rand = lambda *args: np.ones(args, dtype=float)

        t = otsu_from_random_sample(darr, max_pixels=1000)
        print(t)
        assert isinstance(t, (int, float, np.integer, np.floating))
    finally:
        np.random.rand = original_rand


# ----------------------------
#  get_cropSummary
# ----------------------------

def test_get_cropSummary_basic():
    # Create a "nuclei" channel with a high-intensity square in the center
    img = np.zeros((1, 300, 300), dtype=np.uint8)
    img[0, 100:200, 100:200] = 255

    darr = da.from_array(img, chunks=(1, 100, 100))

    results = get_cropSummary(
        darr,
        crop_amount=3,
        crop_size=(40, 40),
        nuclei_index=0,
        nonzero_fraction=0.2,
    )

    assert len(results) <= 3
    assert all(k.startswith("crop_") for k in results.keys())

def test_get_cropSummary_crop_size_larger_than_image():
    img = np.zeros((1, 50, 50), dtype=np.uint8)
    img[0, 10:40, 10:40] = 255

    darr = da.from_array(img, chunks=(1, 25, 25))

    with pytest.raises(ValueError, match="Crop size is larger than image dimensions."):
        get_cropSummary(
            darr,
            crop_amount=2,
            crop_size=(100, 100),  # larger than image
            nuclei_index=0,
            nonzero_fraction=0.2,
        )

def test_get_cropSummary_nonzero_fraction_filtering():
    # very sparse image (mostly zeros → few crops allowed)
    img = np.zeros((1, 200, 200), dtype=np.uint8)
    img[0, 10:20, 10:20] = 255  # tiny region

    darr = da.from_array(img, chunks=(1, 100, 100))

    results = get_cropSummary(
        darr,
        crop_amount=5,
        crop_size=(40, 40),
        nuclei_index=0,
        nonzero_fraction=0.5,  # require 50% nonzero → impossible
    )

    assert len(results) == 0


def test_get_cropSummary_no_overlap():
    img = np.zeros((1, 400, 400), dtype=np.uint8)
    img[0, 50:350, 50:350] = 255  # large area so many crops succeed

    darr = da.from_array(img, chunks=(1, 200, 200))

    results = get_cropSummary(
        darr,
        crop_amount=4,
        crop_size=(60, 60),
        nuclei_index=0,
        nonzero_fraction=0.1,
    )

    boxes = list(results.values())

    def overlap(a, b):
        (h1_up, h1_down), (w1_lt, w1_rt) = a
        (h2_up, h2_down), (w2_lt, w2_rt) = b
        return not (h1_down <= h2_up or h1_up >= h2_down or
                    w1_rt <= w2_lt or w1_lt >= w2_rt)

    # ensure pairwise non-overlap
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            assert not overlap(boxes[i], boxes[j])


def test_get_cropSummary_reproducible_with_seed(monkeypatch):
    """Use monkeypatch to force deterministic random ints."""
    seeds = iter([100] * 10000)

    def fake_randint(a, b):
        return next(seeds)

    monkeypatch.setattr("random.randint", fake_randint)

    img = np.zeros((1, 300, 300), dtype=np.uint8)
    img[0, 120:180, 120:180] = 255

    darr = da.from_array(img, chunks=(1, 150, 150))

    A = get_cropSummary(darr, crop_amount=2, crop_size=(40, 40))
    seeds = iter([100] * 10000)
    B = get_cropSummary(darr, crop_amount=2, crop_size=(40, 40))

    assert A == B