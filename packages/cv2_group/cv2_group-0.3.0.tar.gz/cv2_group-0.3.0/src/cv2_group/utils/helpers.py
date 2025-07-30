import base64
import logging
from typing import List, Tuple

import cv2
import numpy as np
from fastapi import HTTPException, status
from keras import backend as K

logger = logging.getLogger(__name__)


def recall(y_true, y_pred):
    """
    Compute the recall score for binary classification.

    Recall is the ratio of true positives to the total number of actual positives:
    Recall = TP / (TP + FN)

    Parameters
    ----------
    y_true : tensor
        Ground truth binary labels (0 or 1).
    y_pred : tensor
        Predicted binary labels (0 or 1).

    Returns
    -------
    tensor
        Recall score as a scalar tensor.
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    return true_positives / (possible_positives + K.epsilon())


def precision(y_true, y_pred):
    """
    Compute the precision score for binary classification.

    Precision is the ratio of true positives to the total number of predicted positives:
    Precision = TP / (TP + FP)

    Parameters
    ----------
    y_true : tensor
        Ground truth binary labels (0 or 1).
    y_pred : tensor
        Predicted binary labels (0 or 1).

    Returns
    -------
    tensor
        Precision score as a scalar tensor.
    """
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    return true_positives / (predicted_positives + K.epsilon())


def f1(y_true, y_pred):
    """
    Compute the F1 score for binary classification/segmentation.

    The F1 score is the harmonic mean of precision and recall:
        F1 = 2 * (precision * recall) / (precision + recall)

    This version includes a safeguard against division by zero to avoid returning NaN.

    Returns:
        tensor: F1 score (scalar tensor).
    """
    prec = precision(y_true, y_pred)
    rec = recall(y_true, y_pred)
    denom = prec + rec + K.epsilon()

    return K.switch(K.equal(denom, 0), 0.0, 2 * (prec * rec) / denom)


def numpy_to_base64_png(image_array: np.ndarray) -> str:
    """Encodes a NumPy array (image) into a base64 string as PNG."""
    is_success, buffer = cv2.imencode(".png", image_array)
    if not is_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not encode image to PNG.",
        )
    return base64.b64encode(buffer).decode("utf-8")


def transform_rois_to_cropped_coords(
    rois_original: List[Tuple[int, int, int, int]],
    original_bbox: Tuple[int, int, int, int],
    square_offsets: Tuple[int, int],
) -> List[Tuple[int, int, int, int]]:
    """
    Transforms ROI coordinates from the original image's coordinate system
    to the coordinate system of the cropped and centered square image.

    Parameters
    ----------
    rois_original : List[Tuple[int, int, int, int]]
        A list of ROIs, where each ROI is (x, y, width, height) relative to
        the *original* input image.
    original_bbox : Tuple[int, int, int, int]
        The bounding box (x, y, width, height) of the largest component in the
        *original* input image, as returned by crop_image.
    square_offsets : Tuple[int, int]
        The offsets (x_offset, y_offset) used to place the original_bbox's
        content within the square_image, as returned by crop_image.

    Returns
    -------
    List[Tuple[int, int, int, int]]
        A list of transformed ROIs, where each ROI is (x, y, width, height)
        relative to the *cropped and centered square image*.
    """
    logger.info("Transforming ROIs to cropped image coordinates.")

    transformed_rois = []
    original_bbox_x, original_bbox_y, _, _ = original_bbox
    square_offset_x, square_offset_y = square_offsets

    for roi_x, roi_y, roi_width, roi_height in rois_original:
        # Calculate ROI's position relative to the original bounding box's top-left
        # This is the coordinate within the "content" that was moved to the square_image
        relative_x = roi_x - original_bbox_x
        relative_y = roi_y - original_bbox_y

        # Add the square_offsets to get the position in the square_image
        transformed_x = relative_x + square_offset_x
        transformed_y = relative_y + square_offset_y

        # The width and height of the ROI remain the same
        transformed_width = roi_width
        transformed_height = roi_height

        transformed_rois.append(
            (transformed_x, transformed_y, transformed_width, transformed_height)
        )

    logger.info(f"Transformed {len(rois_original)} ROIs.")
    return transformed_rois
