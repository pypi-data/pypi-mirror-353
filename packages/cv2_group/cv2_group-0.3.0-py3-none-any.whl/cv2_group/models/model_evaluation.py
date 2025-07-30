import logging

import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def print_best_val_metrics(history):
    """Print best validation loss and F1-score from training history.

    Args:
        history (tensorflow.python.keras.callbacks.History):
            Keras History object returned by model.fit().
    """
    best_val_loss = min(history.history["val_loss"])
    best_val_f1 = max(history.history["val_f1"])
    logger.info(f"Best validation loss: {best_val_loss}")
    logger.info(f"Best validation f1: {best_val_f1}")


def plot_loss(history):
    """Plot training and validation loss curves.

    Args:
        history (tensorflow.python.keras.callbacks.History):
            Keras History object returned by model.fit().
    """
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]
    epochs = np.arange(1, len(loss) + 1)

    plt.plot(epochs, loss, label="train_loss")
    plt.plot(epochs, val_loss, label="val_loss")
    plt.legend()
    plt.xlabel("Epoch")
    plt.ylabel("Loss (binary_crossentropy)")
    _ = plt.xticks(np.arange(1, len(loss) + 1, 3))


def plot_f1(history):
    """Plot training and validation F1-score curves.

    Args:
        history (tensorflow.python.keras.callbacks.History):
            Keras History object returned by model.fit().
    """
    train_f1 = history.history["f1"]
    val_f1 = history.history["val_f1"]
    epochs = np.arange(1, len(train_f1) + 1)

    plt.plot(epochs, train_f1, label="train_f1")
    plt.plot(epochs, val_f1, label="val_f1")
    plt.legend()
    plt.xlabel("Epoch")
    plt.ylabel("F1")
    _ = plt.xticks(np.arange(1, len(train_f1) + 1, 3))


def pixel_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate pixel-wise accuracy between ground truth and prediction masks.

    Args:
        y_true (np.ndarray): Ground truth binary mask. Shape: (H, W)
        y_pred (np.ndarray): Predicted binary mask. Shape: (H, W)

    Returns:
        float: Pixel accuracy (correct pixels / total pixels)
    """
    correct = np.sum(y_true == y_pred)
    total = y_true.size
    accuracy = correct / total
    logger.info(f"Pixel Accuracy: {accuracy:.4f}")
    return accuracy


def iou_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate Intersection over Union (IoU) score between ground truth
    and predicted binary masks.

    Args:
        y_true (np.ndarray): Ground truth binary mask. Shape: (H, W)
        y_pred (np.ndarray): Predicted binary mask. Shape: (H, W)

    Returns:
        float: IoU score
    """
    intersection = np.logical_and(y_true, y_pred).sum()
    union = np.logical_or(y_true, y_pred).sum()
    if union == 0:
        iou = 1.0  # Perfect score if both masks are empty
    else:
        iou = intersection / union
    logger.info(f"IoU Score: {iou:.4f}")
    return iou
