import base64
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Assuming these are in your cv2_group package structure
from cv2_group.data.data_processing import (
    create_patches,
    crop_image,
    pad_image,
    remove_padding,
    uncrop_mask,
    unpatch_image,
)

# Import all feature extraction functions
from cv2_group.features.feature_extraction import (
    analyze_primary_root,
    extract_root_instances,
    find_labels_in_rois,
    process_predicted_mask,
)
from cv2_group.models.model_definitions import load_trained_model
from cv2_group.utils.binary import ensure_binary_mask
from cv2_group.utils.configuration import MODEL_PATH, PATCH_SIZE
from cv2_group.utils.helpers import (
    _transform_rois_to_cropped_coords,
    numpy_to_base64_png,
)
from cv2_group.utils.predicting import predict_root
from cv2_group.utils.visualization import (
    display_mask_as_png_bytes,
    display_overlay,
    display_rois_on_image,
    display_tip_base_on_image,
)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(title="Root Segmentation and Analysis API")

# Configure CORS middleware
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model once globally
model = load_trained_model(MODEL_PATH)


# --- Pydantic Models for Request and Response ---
class RoiInput(BaseModel):
    x: int = Field(..., description="X-coordinate (left) of the ROI.")
    y: int = Field(..., description="Y-coordinate (top) of the ROI.")
    width: int = Field(..., description="Width of the ROI.")
    height: int = Field(..., description="Height of the ROI.")


class RootAnalysisResult(BaseModel):
    length: float = Field(
        ..., description="Euclidean length of the primary root path in pixels."
    )
    tip_coords: Optional[List[int]] = Field(
        None, description="Coordinates [row, col] of the root tip."
    )
    base_coords: Optional[List[int]] = Field(
        None, description="Coordinates [row, col] of the root base."
    )
    primary_path: Optional[List[List[int]]] = Field(
        None,
        description="List of [row, col] coordinates forming the primary " "root path.",
    )
    stats: Optional[Dict[str, Any]] = Field(
        None,
        description="Connected component statistics for the root (area, "
        "left, top, width, height, centroid_x, centroid_y).",
    )


class RootAnalysisItem(BaseModel):
    roi_definition: RoiInput = Field(
        ..., description="The original ROI definition for this " "analysis result."
    )
    analysis: RootAnalysisResult = Field(
        ...,
        description="The detailed analysis results for the root found " "in this ROI.",
    )


class RootPredictionResponse(BaseModel):
    message: str = "Prediction and analysis successful"
    original_image: str = Field(
        ..., description="Base64 encoded PNG of the original input image."
    )
    # Full-sized outputs
    full_size_mask_image: str = Field(  # RENAMED from mask_image
        ..., description="Base64 encoded PNG of the predicted binary mask (full size)."
    )
    full_size_overlay_image: str = Field(  # RENAMED from overlay_image
        ...,
        description="Base64 encoded PNG of the original image with root mask "
        "overlay (full size).",
    )
    full_size_rois_image: Optional[str] = Field(  # RENAMED from rois_image
        None,
        description="Base64 encoded PNG of the original image with ROIs (full size).",
    )
    full_size_tip_base_image: Optional[str] = Field(  # RENAMED from tip_base_image
        None,
        description="Base64 encoded PNG of the original image with root tips "
        "(green) and bases (red) drawn (full size).",
    )
    # Cropped outputs (new fields)
    cropped_rois_image: Optional[str] = Field(
        None, description="Base64 encoded PNG of the cropped image with ROIs drawn."
    )
    cropped_overlay_image: str = Field(
        ...,
        description="Base64 encoded PNG of the cropped image with root mask overlay.",
    )
    cropped_tip_base_image: Optional[str] = Field(
        None,
        description="Base64 encoded PNG of the cropped image with root tips "
        "(green) and bases (red) drawn.",
    )
    root_analysis_results: List[RootAnalysisItem] = Field(
        ..., description="List of analysis results for each specified ROI."
    )


def predict_from_array(
    image: np.ndarray, original_image_shape: Tuple[int, int]
) -> Tuple[
    np.ndarray, np.ndarray, Tuple[int, int, int, int], Tuple[int, int], np.ndarray
]:
    """
    Encapsulates the prediction logic for a single image, now returning
    the cropped image used for prediction, the binary mask uncropped
    back to the original image's dimensions, the cropping parameters,
    and the binary mask *before* uncropping (for cropped visualizations).

    Parameters
    ----------
    image : np.ndarray
        The input image as a NumPy array (can be grayscale or BGR).
    original_image_shape : Tuple[int, int]
        The (height, width) of the image *before* any cropping by crop_image.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, Tuple[int, int, int, int], Tuple[int, int],
        np.ndarray]
        - The cropped image (square_image) that was actually fed into the model.
        - The predicted binary mask, uncropped and resized to the original_image_shape.
        - The original bounding box (x, y, width, height) of the largest component
          in the *original* input image.
        - The offsets (x_offset, y_offset) used to place the component within
          the square_image.
        - The binary mask *before* uncropping
        (i.e., matching the cropped_image_for_prediction size).
    """
    # Ensure image is grayscale for prediction if it's not already
    if len(image.shape) == 3:
        image_for_cropping = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_for_cropping = image.copy()  # Work on a copy

    # Call the updated crop_image function
    cropped_image_for_prediction, original_bbox, square_offsets = crop_image(
        image_for_cropping
    )

    padded_image, (top, bottom, left, right) = pad_image(
        cropped_image_for_prediction, PATCH_SIZE
    )
    patches, i, j, rgb_image = create_patches(padded_image, PATCH_SIZE)

    # Ensure 'model' is accessible in this scope (e.g., passed as an argument or global)
    global model
    preds = predict_root(patches, model)

    predicted_mask_padded = unpatch_image(preds, i, j, rgb_image, PATCH_SIZE)
    predicted_mask_cropped = remove_padding(
        predicted_mask_padded, top, bottom, left, right
    )

    # Ensure this returns a proper 0/255 uint8 mask
    binary_mask_cropped_square = ensure_binary_mask(predicted_mask_cropped)

    # Uncrop the mask back to the original image dimensions
    uncropped_binary_mask = uncrop_mask(
        binary_mask_cropped_square, original_image_shape, original_bbox, square_offsets
    )

    # Return the cropped_image_for_prediction (the square image),
    # the uncropped_binary_mask (matching original image size),
    # and the cropping parameters for further use, plus the binary_mask_cropped_square.
    return (
        cropped_image_for_prediction,
        uncropped_binary_mask,
        original_bbox,
        square_offsets,
        binary_mask_cropped_square,
    )


# --- FastAPI Endpoints ---
@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict/", response_model=RootPredictionResponse)
async def predict(
    file: UploadFile = File(
        ..., description="Image file to predict root segmentation."
    ),
    expected_plants: int = Query(
        5, description="Estimated number of individual root systems."
    ),
    rois_json: Optional[str] = Form(
        None,
        description="Optional JSON string of ROIs. Each ROI is "
        "{'x': int, 'y': int, 'width': int, 'height': int}",
    ),
):
    try:
        # 1. Process Input Image
        original_image_bgr = await _process_input_image(file)
        logger.info("Image received and decoded.")

        # Get the original image shape (height, width) before any cropping
        original_image_shape = original_image_bgr.shape[:2]  # (height, width)

        # 2. Perform Core Prediction
        (
            cropped_image_for_prediction,
            uncropped_binary_mask,
            original_bbox,
            square_offsets,
            binary_mask_cropped_square,
        ) = predict_from_array(original_image_bgr, original_image_shape)

        if uncropped_binary_mask is None or uncropped_binary_mask.size == 0:
            raise HTTPException(
                status_code=500,
                detail="Segmentation model returned an empty or invalid mask.",
            )

        # 3. Process ROIs
        (
            rois_for_analysis,
            rois_input_for_response,
            original_roi_indices,
        ) = _process_rois_json(rois_json)

        # NEW: Transform ROIs for the cropped image view
        transformed_rois_for_cropped_view = _transform_rois_to_cropped_coords(
            rois_for_analysis, original_bbox, square_offsets
        )

        # 4. Perform Root Analysis
        final_analysis_data = _perform_root_analysis(
            uncropped_binary_mask,
            expected_plants,
            rois_for_analysis,
            rois_input_for_response,
            original_roi_indices,
        )

        # Prepare analysis results for display on cropped images
        analysis_results_for_display_cropped = []
        # Prepare analysis results for display on full-size images
        analysis_results_for_display_full_size = []

        if rois_for_analysis and final_analysis_data:
            for i, item in enumerate(final_analysis_data):
                original_idx = next(
                    (
                        idx
                        for idx, roi_input in enumerate(rois_input_for_response)
                        if roi_input == item.roi_definition
                    ),
                    None,
                )
                if original_idx is not None:
                    raw_result = item.analysis.model_dump()

                    # Full-size results (copy original raw_result and add roi_index)
                    full_size_raw_result = raw_result.copy()
                    full_size_raw_result["roi_index"] = original_idx
                    analysis_results_for_display_full_size.append(full_size_raw_result)

                    # Cropped results (transform coordinates)
                    if raw_result.get("tip_coords"):
                        original_tip_x = raw_result["tip_coords"][1]
                        original_tip_y = raw_result["tip_coords"][0]
                        transformed_tip_x = (
                            original_tip_x - original_bbox[0]
                        ) + square_offsets[0]
                        transformed_tip_y = (
                            original_tip_y - original_bbox[1]
                        ) + square_offsets[1]
                        raw_result["tip_coords"] = [
                            transformed_tip_y,
                            transformed_tip_x,
                        ]

                    if raw_result.get("base_coords"):
                        original_base_x = raw_result["base_coords"][1]
                        original_base_y = raw_result["base_coords"][0]
                        transformed_base_x = (
                            original_base_x - original_bbox[0]
                        ) + square_offsets[0]
                        transformed_base_y = (
                            original_base_y - original_bbox[1]
                        ) + square_offsets[1]
                        raw_result["base_coords"] = [
                            transformed_base_y,
                            transformed_base_x,
                        ]

                    if raw_result.get("primary_path"):
                        transformed_path = []
                        for row, col in raw_result["primary_path"]:
                            transformed_col = (col - original_bbox[0]) + square_offsets[
                                0
                            ]
                            transformed_row = (row - original_bbox[1]) + square_offsets[
                                1
                            ]
                            transformed_path.append([transformed_row, transformed_col])
                        raw_result["primary_path"] = transformed_path

                    raw_result[
                        "roi_index"
                    ] = original_idx  # Re-add for display function if needed
                    analysis_results_for_display_cropped.append(raw_result)

        # 5. Generate Full-Size Visualizations
        (
            full_size_overlay_image_base64,
            full_size_mask_image_base64,
            full_size_rois_image_base64,
            full_size_tip_base_image_base64,
        ) = _generate_full_size_visualizations(
            original_image_bgr,
            uncropped_binary_mask,
            rois_for_analysis,  # ROIs are for original image
            analysis_results_for_display_full_size,
            # Analysis results for original image
        )

        # 6. Generate Cropped Visualizations
        (
            cropped_rois_image_base64,
            cropped_overlay_image_base64,
            cropped_tip_base_image_base64,
        ) = _generate_cropped_visualizations(
            cropped_image_for_prediction,
            binary_mask_cropped_square,
            transformed_rois_for_cropped_view,  # Transformed ROIs for cropped image
            analysis_results_for_display_cropped,
            # Transformed analysis results for cropped image
        )

        # 7. Convert original_image_bgr to base64 PNG for response
        is_success, buffer = cv2.imencode(".png", original_image_bgr)
        original_image_base64 = base64.b64encode(buffer).decode("utf-8")

        return RootPredictionResponse(
            message="Prediction and analysis successful",
            original_image=original_image_base64,
            full_size_overlay_image=full_size_overlay_image_base64,
            full_size_mask_image=full_size_mask_image_base64,
            full_size_rois_image=full_size_rois_image_base64,
            full_size_tip_base_image=full_size_tip_base_image_base64,
            cropped_rois_image=cropped_rois_image_base64,
            cropped_overlay_image=cropped_overlay_image_base64,
            cropped_tip_base_image=cropped_tip_base_image_base64,
            root_analysis_results=final_analysis_data,
        )

    except HTTPException as he:
        raise he
    except ValueError as ve:
        logger.error(f"Client error: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Prediction and analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )


# --- Save Function (for Step 1.5.4) ---
class SaveImageRequest(BaseModel):
    image_data: str = Field(..., description="Base64 encoded PNG image data.")
    username: str = Field(..., description="Username for file naming.")
    image_type: str = Field(
        ..., description="Type of image (e.g., 'original', 'mask', 'overlay')."
    )


@app.post("/save-image")
async def save_image_endpoint(request: SaveImageRequest):
    """
    Endpoint to save a base64 encoded image to the server.
    """
    try:
        # Decode base64 image data
        image_bytes = base64.b64decode(request.image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)

        if image is None:
            raise HTTPException(status_code=400, detail="Could not decode image data.")

        date_str = datetime.today().strftime("%Y-%m-%d")
        # Sanitize username to be filesystem-safe
        safe_username = "".join(
            c for c in request.username if c.isalnum() or c in ("_", "-")
        ).strip()
        if not safe_username:
            safe_username = "unknown_user"

        # Define save directory (you might want to make this configurable)
        save_dir = "saved_images"
        os.makedirs(save_dir, exist_ok=True)  # Ensure directory exists

        file_name = f"{date_str}_{safe_username}_{request.image_type}.png"
        file_path = os.path.join(save_dir, file_name)

        cv2.imwrite(file_path, image)
        logger.info(f"Saved image to: {file_path}")

        return {
            "message": f"Image '{file_name}' saved successfully.",
            "path": file_path,
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to save image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")


async def _process_input_image(file: UploadFile) -> np.ndarray:
    """
    Decodes the uploaded image file and ensures it's in BGR format.
    Raises HTTPException if the image cannot be decoded.
    """
    contents = await file.read()
    file_bytes = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)

    if image is None:
        raise HTTPException(
            status_code=400, detail="Could not decode image. Invalid image file."
        )

    # Ensure image is 3-channel (BGR) for consistent processing and visualization
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:  # RGBA
        return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    else:  # Already BGR
        return image.copy()  # Make a copy to avoid modifying original in place


def _process_rois_json(
    rois_json: Optional[str],
) -> Tuple[List[Tuple[int, int, int, int]], List[RoiInput], List[int]]:
    """
    Parses the ROIs JSON string, validates each ROI, and returns lists
    suitable for analysis and response.
    Raises HTTPException for invalid JSON or ROI structure.
    """
    rois_for_analysis: List[Tuple[int, int, int, int]] = []
    rois_input_for_response: List[RoiInput] = []
    original_roi_indices: List[int] = []

    if rois_json:
        try:
            rois_data = json.loads(rois_json)
            for idx, r_dict in enumerate(rois_data):
                # Validate ROI structure using Pydantic
                roi_model = RoiInput(**r_dict)
                rois_for_analysis.append(
                    (roi_model.x, roi_model.y, roi_model.width, roi_model.height)
                )
                rois_input_for_response.append(roi_model)
                original_roi_indices.append(idx)  # Store the original index
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode ROIs JSON: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ROIs JSON format: {e}",
            )
        except Exception as e:  # Catch Pydantic validation errors or other issues
            logger.error(f"Error parsing ROI data: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ROI structure or data: {e}. "
                "Expected objects with 'x', 'y', 'width', 'height'.",
            )
    else:
        logger.info("No ROIs provided. Analysis results will be empty.")

    return rois_for_analysis, rois_input_for_response, original_roi_indices


def _generate_full_size_visualizations(
    original_image_bgr: np.ndarray,
    uncropped_binary_mask: np.ndarray,
    rois_for_analysis: List[Tuple[int, int, int, int]],
    analysis_results_for_display_full_size: List[
        Dict[str, Any]
    ],  # NEW: for full-size tip/base
) -> Tuple[str, str, str, str]:  # NEW: Added return for full_size_tip_base_image
    """
    Generates base64 encoded PNG images for full-sized overlay, mask, ROIs,
    and tip/base.

    Parameters
    ----------
    original_image_bgr : np.ndarray
        The full-sized, 3-channel (BGR) original image.
    uncropped_binary_mask : np.ndarray
        The binary mask, uncropped and matching the original_image_bgr dimensions.
    rois_for_analysis : List[Tuple[int, int, int, int]]
        List of ROIs (x, y, width, height) relative to the original image.
    analysis_results_for_display_full_size : List[Dict[str, Any]]
        Analysis results where tip/base/path coordinates are relative to
        the original image's coordinate system.

    Returns
    -------
    Tuple[str, str, str, str]
        Base64 encoded strings for:
        - full_size_overlay_image
        - full_size_mask_image
        - full_size_rois_image
        - full_size_tip_base_image
    """
    # ROIs image (full size)
    if rois_for_analysis:
        rois_image_bytes = display_rois_on_image(
            original_image_bgr, rois_for_analysis, return_png_bytes=True
        )
        full_size_rois_image_base64 = numpy_to_base64_png(
            cv2.imdecode(
                np.frombuffer(rois_image_bytes, np.uint8), cv2.IMREAD_UNCHANGED
            )
        )
    else:
        # If no ROIs, send a blank image for ROIs overlay
        rois_image_bytes_placeholder = np.zeros_like(original_image_bgr, dtype=np.uint8)
        if len(rois_image_bytes_placeholder.shape) == 2:
            rois_image_bytes_placeholder = cv2.cvtColor(
                rois_image_bytes_placeholder, cv2.COLOR_GRAY2BGR
            )
        is_success, buffer = cv2.imencode(".png", rois_image_bytes_placeholder)
        full_size_rois_image_base64 = base64.b64encode(buffer).decode("utf-8")

    # Overlay image (mask on original, full size)
    overlay_bytes = display_overlay(
        cropped_image=original_image_bgr,  # Use the full-sized original image
        predicted_mask=uncropped_binary_mask,  # Use the full-sized uncropped mask
        alpha=0.5,
        show=False,
        return_png_bytes=True,
    )
    full_size_overlay_image_base64 = numpy_to_base64_png(
        cv2.imdecode(np.frombuffer(overlay_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
    )

    # Mask image (full size)
    mask_bytes = display_mask_as_png_bytes(
        uncropped_binary_mask
    )  # Use the full-sized uncropped mask
    full_size_mask_image_base64 = numpy_to_base64_png(
        cv2.imdecode(np.frombuffer(mask_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
    )

    # Full-size Tip & Base image
    if analysis_results_for_display_full_size:
        tip_base_image_bytes = display_tip_base_on_image(
            original_image_bgr,
            analysis_results_for_display_full_size,
            return_png_bytes=True,
        )
        full_size_tip_base_image_base64 = numpy_to_base64_png(
            cv2.imdecode(
                np.frombuffer(tip_base_image_bytes, np.uint8), cv2.IMREAD_UNCHANGED
            )
        )
    else:
        tip_base_image_bytes_placeholder = np.zeros_like(
            original_image_bgr, dtype=np.uint8
        )
        if len(tip_base_image_bytes_placeholder.shape) == 2:
            tip_base_image_bytes_placeholder = cv2.cvtColor(
                tip_base_image_bytes_placeholder, cv2.COLOR_GRAY2BGR
            )
        is_success, buffer = cv2.imencode(".png", tip_base_image_bytes_placeholder)
        full_size_tip_base_image_base64 = base64.b64encode(buffer).decode("utf-8")

    return (
        full_size_overlay_image_base64,
        full_size_mask_image_base64,
        full_size_rois_image_base64,
        full_size_tip_base_image_base64,  # NEW return value
    )


def _generate_cropped_visualizations(
    cropped_image_for_prediction: np.ndarray,
    binary_mask_cropped_square: np.ndarray,
    transformed_rois_for_cropped_view: List[Tuple[int, int, int, int]],
    analysis_results_for_display_cropped: List[
        Dict[str, Any]
    ],  # Analysis results transformed to cropped coords
) -> Tuple[str, str, str]:  # NEW: Added return for cropped_tip_base_image
    """
    Generates base64 encoded PNG images for cropped overlay, mask, ROIs, and tip/base.

    Parameters
    ----------
    cropped_image_for_prediction : np.ndarray
        The cropped (square) image that was used for prediction.
    binary_mask_cropped_square : np.ndarray
        The binary mask corresponding to the cropped_image_for_prediction.
    transformed_rois_for_cropped_view : List[Tuple[int, int, int, int]]
        List of ROIs (x, y, width, height) relative to the cropped image.
    analysis_results_for_display_cropped : List[Dict[str, Any]]
        Analysis results where tip/base/path coordinates are transformed to
        the cropped image's coordinate system.

    Returns
    -------
    Tuple[str, str, str]
        Base64 encoded strings for:
        - cropped_rois_image
        - cropped_overlay_image
        - cropped_tip_base_image
    """
    # Ensure cropped_image_for_prediction is 3-channel for visualization functions
    if len(cropped_image_for_prediction.shape) == 2:
        cropped_image_bgr = cv2.cvtColor(
            cropped_image_for_prediction, cv2.COLOR_GRAY2BGR
        )
    else:
        cropped_image_bgr = cropped_image_for_prediction.copy()

    # Cropped ROIs image
    if transformed_rois_for_cropped_view:
        rois_image_bytes = display_rois_on_image(
            cropped_image_bgr, transformed_rois_for_cropped_view, return_png_bytes=True
        )
        cropped_rois_image_base64 = numpy_to_base64_png(
            cv2.imdecode(
                np.frombuffer(rois_image_bytes, np.uint8), cv2.IMREAD_UNCHANGED
            )
        )
    else:
        cropped_rois_image_bytes_placeholder = np.zeros_like(
            cropped_image_bgr, dtype=np.uint8
        )
        is_success, buffer = cv2.imencode(".png", cropped_rois_image_bytes_placeholder)
        cropped_rois_image_base64 = base64.b64encode(buffer).decode("utf-8")

    # Cropped Overlay image
    overlay_bytes = display_overlay(
        cropped_image=cropped_image_bgr,
        predicted_mask=binary_mask_cropped_square,
        alpha=0.5,
        show=False,
        return_png_bytes=True,
    )
    cropped_overlay_image_base64 = numpy_to_base64_png(
        cv2.imdecode(np.frombuffer(overlay_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
    )

    # Cropped Tip & Base image
    if analysis_results_for_display_cropped:
        tip_base_image_bytes = display_tip_base_on_image(
            cropped_image_bgr,
            analysis_results_for_display_cropped,
            return_png_bytes=True,
        )
        cropped_tip_base_image_base64 = numpy_to_base64_png(
            cv2.imdecode(
                np.frombuffer(tip_base_image_bytes, np.uint8), cv2.IMREAD_UNCHANGED
            )
        )
    else:
        tip_base_image_bytes_placeholder = np.zeros_like(
            cropped_image_bgr, dtype=np.uint8
        )
        is_success, buffer = cv2.imencode(".png", tip_base_image_bytes_placeholder)
        cropped_tip_base_image_base64 = base64.b64encode(buffer).decode("utf-8")

    return (
        cropped_rois_image_base64,
        cropped_overlay_image_base64,
        cropped_tip_base_image_base64,
    )


def _perform_root_analysis(
    binary_mask: np.ndarray,
    expected_plants: int,
    rois_for_analysis: List[Tuple[int, int, int, int]],
    rois_input_for_response: List[RoiInput],
    original_roi_indices: List[int],
) -> List[RootAnalysisItem]:
    """
    Performs root instance extraction and primary root analysis.
    Returns a list of RootAnalysisItem objects.
    """
    _, label_ids, totalLabels, stats, centroids = process_predicted_mask(
        binary_mask,
        use_watershed=False,
        expected_plants=expected_plants,
    )

    max_label_dict = {}
    if rois_for_analysis:
        max_label_dict, _ = find_labels_in_rois(
            label_ids, totalLabels, stats, centroids, rois_for_analysis
        )

    labels_to_extract_ordered = [
        max_label_dict.get(f"label_{i}") for i in range(len(rois_for_analysis))
    ]
    root_instances_ordered = extract_root_instances(
        label_ids, labels_to_extract_ordered
    )

    analysis_results_raw = analyze_primary_root(
        root_instances_ordered, original_roi_indices
    )

    final_analysis_data: List[RootAnalysisItem] = []
    for i, roi_input_model in enumerate(rois_input_for_response):
        result_for_roi = next(
            (res for res in analysis_results_raw if res.get("roi_index") == i), None
        )

        default_analysis_data = {
            "length": 0.0,
            "tip_coords": None,
            "base_coords": None,
            "primary_path": None,
            "stats": None,
        }

        current_analysis_data = default_analysis_data
        if result_for_roi:
            analysis_copy = result_for_roi.copy()
            del analysis_copy["roi_index"]
            current_analysis_data = analysis_copy

            label_id_in_roi = max_label_dict.get(f"label_{i}")
            if (
                label_id_in_roi is not None
                and label_id_in_roi != 0
                and label_id_in_roi < stats.shape[0]
            ):
                roi_stats = {
                    "area": int(stats[label_id_in_roi, cv2.CC_STAT_AREA]),
                    "left": int(stats[label_id_in_roi, cv2.CC_STAT_LEFT]),
                    "top": int(stats[label_id_in_roi, cv2.CC_STAT_TOP]),
                    "width": int(stats[label_id_in_roi, cv2.CC_STAT_WIDTH]),
                    "height": int(stats[label_id_in_roi, cv2.CC_STAT_HEIGHT]),
                    "centroid_x": float(centroids[label_id_in_roi, 0]),
                    "centroid_y": float(centroids[label_id_in_roi, 1]),
                }
                current_analysis_data["stats"] = roi_stats
            else:
                current_analysis_data["stats"] = None

        final_analysis_data.append(
            RootAnalysisItem(
                roi_definition=roi_input_model,
                analysis=RootAnalysisResult(**current_analysis_data),
            )
        )
    return final_analysis_data
