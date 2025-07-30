from typing import Any, Dict, List, Optional, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np


def display_mask_as_png_bytes(pred_mask: np.ndarray) -> bytes:
    """
    Encodes the predicted binary root mask into PNG bytes.

    Parameters
    ----------
    pred_mask : np.ndarray
        Predicted mask (2D array, typically values 0 or 255, dtype uint8).

    Returns
    -------
    bytes
        PNG image bytes.
    """
    if pred_mask.ndim == 3 and pred_mask.shape[-1] == 1:
        pred_mask = pred_mask[..., 0]
    elif pred_mask.ndim == 3 and pred_mask.shape[0] == 1:
        pred_mask = pred_mask[0]

    # Ensure the mask is uint8 and has values 0 or 255 for proper PNG encoding
    # If your binary_mask is already 0/1, convert it to 0/255
    if pred_mask.dtype != np.uint8 or pred_mask.max() == 1:
        pred_mask = (pred_mask * 255).astype(np.uint8)

    success, encoded_img = cv2.imencode(".png", pred_mask)
    if not success:
        raise ValueError("Failed to encode predicted mask image to PNG")
    return encoded_img.tobytes()


def display_overlay(
    cropped_image: np.ndarray,
    predicted_mask: np.ndarray,
    alpha: float = 0.5,
    show: bool = False,
    return_png_bytes: bool = True,
) -> bytes | None:
    """
    Generates and optionally returns an overlay of the predicted root mask
    on the original image.

    Parameters
    ----------
    cropped_image : np.ndarray
        Original grayscale image (2D or 3D).
    predicted_mask : np.ndarray
        Binary predicted root mask (2D, values 0 or 255, dtype uint8).
    alpha : float
        Transparency factor for the overlay.
    show : bool
        Whether to show the image using matplotlib (for local debugging,
        not for API).
    return_png_bytes : bool
        If True, return the overlay image as PNG bytes (for FastAPI use).

    Returns
    -------
    bytes or None
        PNG image bytes if return_png_bytes is True, else None.
    """

    if len(cropped_image.shape) == 2:
        original_rgb = cv2.cvtColor(cropped_image, cv2.COLOR_GRAY2BGR)
    else:
        original_rgb = cropped_image.copy()

    # Create red overlay mask
    red_mask = np.zeros_like(original_rgb)
    red_mask[..., 2] = predicted_mask  # Apply binary mask to red channel

    # Blend the images
    overlay = cv2.addWeighted(original_rgb, 1 - alpha, red_mask, alpha, 0)

    if show:
        plt.figure(figsize=(8, 8))
        plt.title("Overlay: Predicted Roots on Original Image")
        plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
        plt.axis("off")
        plt.show()

    if return_png_bytes:
        success, encoded_img = cv2.imencode(".png", overlay)
        if not success:
            raise ValueError("Failed to encode overlay image")
        return encoded_img.tobytes()

    return None


def display_rois_on_image(
    image: np.ndarray,
    rois: List[Tuple[int, int, int, int]],  # ROIs as (x, y, width, height)
    color: Tuple[int, int, int] = (0, 0, 255),  # Red color in BGR
    thickness: int = 5,
    return_png_bytes: bool = True,  # Default to returning bytes for FastAPI
) -> Optional[bytes]:
    """
    Draws rectangles for each ROI on a copy of the input image.

    Parameters
    ----------
    image : np.ndarray
        The original image (grayscale or BGR) on which to draw the ROIs.
    rois : List[Tuple[int, int, int, int]]
        List of ROIs, each as (x, y, width, height).
    color : Tuple[int, int, int], optional
        BGR color for the ROI rectangles, by default red.
    thickness : int, optional
        Thickness of the rectangle lines, by default 5.
    return_png_bytes : bool, optional
        If True, returns the image with ROIs as PNG bytes. Defaults to True.

    Returns
    -------
    Optional[bytes]
        PNG image bytes if `return_png_bytes` is True, otherwise None.
        (Returns the modified image array if `return_png_bytes` is False,
        for local use).
    """
    # Ensure image is 3 channels for drawing colored rectangles
    if len(image.shape) == 2:
        display_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        display_image = image.copy()  # Work on a copy to not alter the original

    for x, y, width, height in rois:
        # Define top-left and bottom-right corners
        top_left = (x, y)
        bottom_right = (x + width, y + height)
        cv2.rectangle(display_image, top_left, bottom_right, color, thickness)

    if return_png_bytes:
        is_success, buffer = cv2.imencode(".png", display_image)
        if is_success:
            return buffer.tobytes()
        else:
            raise RuntimeError("Could not encode ROI image to PNG bytes.")

    return None


def display_tip_base_on_image(
    image: np.ndarray,
    analysis_results: List[
        Dict[str, Any]
    ],  # List of analysis dicts from analyze_primary_root
    tip_color: Tuple[int, int, int] = (0, 255, 0),  # Green for tip (BGR)
    base_color: Tuple[int, int, int] = (0, 0, 255),  # Red for base (BGR)
    marker_radius: int = 15,
    marker_thickness: int = -1,  # -1 for filled circle
    return_png_bytes: bool = True,
) -> Optional[bytes]:
    """
    Draws markers for root tip and base coordinates on a copy of the input
    image.

    Parameters
    ----------
    image : np.ndarray
        The original image (grayscale or BGR) on which to draw the markers.
    analysis_results : List[Dict[str, Any]]
        List of dictionaries, each containing 'tip_coords' and 'base_coords'.
        These are the results from analyze_primary_root.
    tip_color : Tuple[int, int, int], optional
        BGR color for the tip markers, by default green.
    base_color : Tuple[int, int, int], optional
        BGR color for the base markers, by default red.
    marker_radius : int, optional
        Radius of the markers, by default 15.
    marker_thickness : int, optional
        Thickness of the marker lines, -1 for filled. By default -1.
    return_png_bytes : bool, optional
        If True, returns the image with markers as PNG bytes. Defaults to True.

    Returns
    -------
    Optional[bytes]
        PNG image bytes if `return_png_bytes` is True, otherwise None.
    """
    # Ensure image is 3 channels for drawing colored markers
    if len(image.shape) == 2:
        display_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        display_image = image.copy()  # Work on a copy to not alter the original

    for result in analysis_results:
        tip = result.get("tip_coords")
        base = result.get("base_coords")

        # Remember: OpenCV uses (x, y) for coordinates, while our coords are
        # (row, col) = (y, x)
        if tip:
            # tip_coords are [row, col] -> OpenCV needs (col, row)
            cv2.circle(
                display_image,
                (tip[1], tip[0]),
                marker_radius,
                tip_color,
                marker_thickness,
            )
        if base:
            # base_coords are [row, col] -> OpenCV needs (col, row)
            cv2.circle(
                display_image,
                (base[1], base[0]),
                marker_radius,
                base_color,
                marker_thickness,
            )

    if return_png_bytes:
        is_success, buffer = cv2.imencode(".png", display_image)
        if is_success:
            return buffer.tobytes()
        else:
            raise RuntimeError("Could not encode tip/base image to PNG bytes.")

    return None
