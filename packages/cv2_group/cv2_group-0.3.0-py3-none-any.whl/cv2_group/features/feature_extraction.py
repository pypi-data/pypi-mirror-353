import logging
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.graph import route_through_array
from skimage.morphology import skeletonize
from skimage.segmentation import watershed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def separate_merged_roots(mask: np.ndarray, expected_plants: int = 5) -> np.ndarray:
    """
    Separate merged root regions in a binary mask using the watershed
    algorithm.
    """
    distance = ndi.distance_transform_edt(mask)
    min_distance = max(1, mask.shape[1] // (expected_plants * 2))
    top_portion = mask.shape[0] // 4
    distance_top = distance.copy()
    distance_top[top_portion:, :] = 0

    coords = peak_local_max(
        distance_top,
        min_distance=min_distance,
        num_peaks=expected_plants,
        exclude_border=False,
    )
    coords = coords[
        (coords[:, 0] >= 0)
        & (coords[:, 0] < mask.shape[0])
        & (coords[:, 1] >= 0)
        & (coords[:, 1] < mask.shape[1])
    ]

    markers = np.zeros_like(mask, dtype=int)
    for i, (r, c) in enumerate(coords, start=1):
        markers[r, c] = i

    labels = watershed(-distance, markers, mask=mask.astype(bool))

    return labels.astype(np.int32)


def process_predicted_mask(
    predicted_mask: np.ndarray,
    use_watershed: bool = True,
    expected_plants: int = 5,
) -> Tuple[np.ndarray, np.ndarray, int, np.ndarray, np.ndarray]:
    """
    Process a binary mask to generate labeled root instances.
    """
    binary_mask = np.array(predicted_mask, dtype=np.uint8)
    normalized_mask = (binary_mask // 255).astype(np.uint8)

    if use_watershed:
        label_ids = separate_merged_roots(normalized_mask, expected_plants)
        retval, _, stats, centroids = cv2.connectedComponentsWithStats(label_ids)
        totalLabels = retval
    else:
        retval, label_ids, stats, centroids = cv2.connectedComponentsWithStats(
            binary_mask
        )  # This input is always np.uint8 (0 or 255), which cv2 expects
        totalLabels = retval

    return binary_mask, label_ids, totalLabels, stats, centroids


def find_labels_in_rois(
    label_ids: np.ndarray,
    totalLabels: int,
    stats: np.ndarray,
    centroids: np.ndarray,
    rois: List[Tuple[int, int, int, int]],
) -> Tuple[Dict[str, Optional[int]], List[int]]:
    """
    Identify root labels within defined regions of interest (ROIs).
    """
    max_label_dict = {}
    max_label_list = []

    for counter, roi in enumerate(rois):
        key = f"label_{counter}"
        x, y, width, height = roi
        x_end, y_end = x + width, y + height

        indices_in_roi = []
        for i in range(1, totalLabels):
            if i >= stats.shape[0]:
                logger.warning(
                    f"Label ID {i} out of bounds for stats array (shape "
                    f"{stats.shape}). Skipping."
                )
                continue

            label_x = stats[i, cv2.CC_STAT_LEFT]
            label_y = stats[i, cv2.CC_STAT_TOP]
            label_width = stats[i, cv2.CC_STAT_WIDTH]
            label_height = stats[i, cv2.CC_STAT_HEIGHT]
            label_x_end = label_x + label_width
            label_y_end = label_y + label_height

            if not (
                x_end < label_x or label_x_end < x or y_end < label_y or label_y_end < y
            ):
                indices_in_roi.append(i)

        if indices_in_roi:
            max_height_label = max(
                indices_in_roi, key=lambda idx: stats[idx, cv2.CC_STAT_HEIGHT]
            )
            max_label_list.append(max_height_label)
            max_label_dict[key] = max_height_label
            logger.info(
                f"ROI {roi}: Label {max_height_label} has the highest "
                f"height: {stats[max_height_label, cv2.CC_STAT_HEIGHT]}"
            )
        else:
            max_label_dict[key] = None
            logger.info(f"ROI {roi}: No labels found.")

    return max_label_dict, max_label_list


def extract_root_instances(
    label_ids: np.ndarray, max_label_ids_for_rois: List[Optional[int]]
) -> List[Optional[np.ndarray]]:
    """
    Extract binary masks for individual root instances from a labeled image.
    """
    root_instances = []
    for label_id in max_label_ids_for_rois:
        if label_id is not None and label_id != 0:
            label_mask = np.where(label_ids == label_id, 1, 0).astype(np.uint8)
            root_instances.append(label_mask)
        else:
            root_instances.append(None)
    return root_instances


def analyze_primary_root(
    root_instances: List[Optional[np.ndarray]], original_roi_indices: List[int]
) -> List[Dict[str, Any]]:
    """
    Analyze the primary root of each binary mask instance.
    """
    results = []

    for i, root in enumerate(root_instances):
        result_entry: Dict[str, Any] = {
            "roi_index": original_roi_indices[i],
            "length": 0.0,
            "tip_coords": None,
            "base_coords": None,
            "primary_path": None,
        }

        if root is None:
            logger.info(
                f"Root instance {i} (original ROI index "
                f"{original_roi_indices[i]}) is None. Skipping analysis."
            )
            results.append(result_entry)
            continue

        logger.info(
            f"Analyzing root instance {i} (original ROI index "
            f"{original_roi_indices[i]})."
        )
        skeleton = skeletonize(root)

        # Step 1: Skeletonization
        logger.info("Generating skeleton from binary root mask...")
        skeleton = skeletonize(root)

        if np.any(skeleton):
            coords = np.where(skeleton > 0)
            if len(coords[0]) == 0:
                logger.error(
                    f"Root {i} (original ROI index {original_roi_indices[i]}):"
                    f" Skeleton has no coordinates. Skipping analysis."
                )
                results.append(result_entry)
                continue

            min_row_idx = np.argmin(coords[0])
            max_row_idx = np.argmax(coords[0])

            base = (coords[0][min_row_idx], coords[1][min_row_idx])
            tip = (coords[0][max_row_idx], coords[1][max_row_idx])

            if base == tip:
                logger.warning(
                    f"Root {i} (original ROI index {original_roi_indices[i]}):"
                    f" Base and Tip are identical or very close. Length "
                    f"will be 0."
                )
                result_entry.update(
                    {
                        "length": 0.0,
                        "tip_coords": list(tip),
                        "base_coords": list(base),
                        "primary_path": [list(base)] if base else [],
                    }
                )
                results.append(result_entry)
                continue

            costs = np.where(skeleton, 1, 1000000)

            try:
                path_coords, path_cost = route_through_array(
                    costs, start=base, end=tip, fully_connected=True
                )
                path_coords = np.array(path_coords)

                length = np.sum(
                    np.sqrt(np.sum(np.diff(path_coords, axis=0) ** 2, axis=1))
                )

                result_entry.update(
                    {
                        "length": float(length),
                        "tip_coords": list(tip),
                        "base_coords": list(base),
                        "primary_path": path_coords.tolist(),
                    }
                )
                results.append(result_entry)
            except Exception as e:
                logger.error(
                    f"Root {i} (original ROI index {original_roi_indices[i]}):"
                    f" Pathfinding failed with error: {e}"
                )
                results.append(result_entry)
        else:
            logger.error(
                f"Root {i} (original ROI index {original_roi_indices[i]}):"
                f" Skeleton contains no valid path."
            )
            results.append(result_entry)

    logger.info("Finished analyzing all root instances.")
    return results
