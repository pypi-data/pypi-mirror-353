"""
Package
"""

# Here we import everything for easy access
# Should allow for "from cv2_group import crop_image"
# OR import cv2_group (to use: cv2_group.crop_image())
# Make sure this list stays up to date with new functions
from cv2_group.data.data_ingestion import (
    load_image,
    rename_pairs,
    upload_data,
    upload_to_azure_datastore,
)
from cv2_group.data.data_processing import (
    create_patches,
    create_patches_alternative,
    crop_image,
    crop_image_with_bbox,
    pad_image,
    pad_image_alternative,
    remove_padding,
    uncrop_mask,
    unpatch_image,
)
from cv2_group.data.data_validation import check_size_match, is_binary_mask
from cv2_group.features.feature_extraction import (
    analyze_primary_root,
    extract_root_instances,
    find_labels_in_rois,
    process_predicted_mask,
    separate_merged_roots,
)
from cv2_group.models.model_definitions import load_trained_model
from cv2_group.models.model_evaluation import (
    iou_score,
    pixel_accuracy,
    plot_f1,
    plot_loss,
    print_best_val_metrics,
)
from cv2_group.models.model_saving import save_model
from cv2_group.utils.binary import ensure_binary_mask
from cv2_group.utils.helpers import (
    f1,
    numpy_to_base64_png,
    precision,
    recall,
    transform_rois_to_cropped_coords,
)

# from cv2_group.utils.configuration import MODEL_PATH, PATCH_SIZE
# Can also add streamlit functions
from cv2_group.utils.predicting import predict_root
from cv2_group.utils.visualization import (
    display_mask_as_png_bytes,
    display_overlay,
    display_rois_on_image,
    display_tip_base_on_image,
)

# Had to comment the one below out, it throws errors with azure
# from cv2_group.data.data_splitting import authenticate_clients, list_image_files


# Add model_training here later.


# Still misses data_splitting functions (Azure error)
# Make sure to keep updated
__all__ = [
    "load_image",
    "create_patches",
    "crop_image",
    "pad_image",
    "remove_padding",
    "unpatch_image",
    "is_binary_mask",
    "check_size_match",
    "crop_image_with_bbox",
    "create_patches_alternative",
    "pad_image_alternative",
    "uncrop_mask",
    "upload_data",
    "rename_pairs",
    "upload_to_azure_datastore",
    "authenticate_clients",
    "list_image_files",
    "analyze_primary_root",
    "extract_root_instances",
    "find_labels_in_rois",
    "process_predicted_mask",
    "separate_merged_roots",
    "print_best_val_metrics",
    "plot_loss",
    "plot_f1",
    "pixel_accuracy",
    "iou_score",
    "print_best_val_metrics",
    "plot_loss",
    "plot_f1",
    "pixel_accuracy",
    "iou_score",
    "ensure_binary_mask",
    "predict_root",
    "display_mask_as_png_bytes",
    "display_overlay",
    "display_rois_on_image",
    "display_tip_base_on_image",
    "recall",
    "precision",
    "f1",
    "numpy_to_base64_png",
    "transform_rois_to_cropped_coords",
    "load_trained_model",
    "save_model",
]
