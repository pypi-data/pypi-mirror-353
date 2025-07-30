import os

# Constants
PATCH_SIZE = 128

# Get the absolute path to the directory containing this configuration.py file
# This will be: .../cv2_group_package/src/cv2_group/utils
_current_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate from _current_dir to the 'cv2_group_package' root
# From: .../cv2_group_package/src/cv2_group/utils
# Go up 1 level (os.pardir): .../cv2_group_package/src/cv2_group/
# Go up 2 levels (os.pardir, os.pardir): .../cv2_group_package/src/
# Go up 3 levels (os.pardir, os.pardir, os.pardir): .../cv2_group_package/

_package_root = os.path.abspath(
    os.path.join(
        _current_dir,
        os.pardir,  # up from 'utils' to 'cv2_group'
        os.pardir,  # up from 'cv2_group' to 'src'
        os.pardir,  # up from 'src' to 'cv2_group_package'
    )
)

# Now construct the full absolute path to the model
# It's at: <package_root>/models/your_model_file.h5
MODEL_PATH = os.path.join(
    _package_root,
    "models",  # The 'models' directory at the package root
    "martin_235439_unet_model_4_no_wandb_128px.h5",
)

# Optional: Print the resolved path during development to verify
print(f"DEBUG: Resolved MODEL_PATH: {MODEL_PATH}")
