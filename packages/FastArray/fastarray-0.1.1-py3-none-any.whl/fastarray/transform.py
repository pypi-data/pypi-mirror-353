# fastArray/transform.py
def split_into_patches(image: np.ndarray, patch_size=(256, 256), stride=None):
    """Split array [H, W, C] into patches."""
    stride = stride or patch_size
    h, w, c = image.shape
    ph, pw = patch_size
    sh, sw = stride
    patches = []

    for i in range(0, h - ph + 1, sh):
        for j in range(0, w - pw + 1, sw):
            patch = image[i:i+ph, j:j+pw, :]
            patches.append(patch)

    return np.stack(patches)
