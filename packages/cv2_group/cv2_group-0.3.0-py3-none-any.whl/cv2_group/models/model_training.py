import logging
import os
from typing import Tuple

import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import (
    ImageDataGenerator,
    img_to_array,
    load_img,
)

from cv2_group.models.model_definitions import load_trained_model
from cv2_group.utils.configuration import MODEL_PATH
from cv2_group.utils.helpers import f1

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s"
)


def load_and_prepare_model_for_retraining(learning_rate: float = 1e-5) -> Model:
    """
    Loads a previously trained U-Net model and compiles it for further training.

    Args:
        learning_rate (float): The learning rate to use for the optimizer.

    Returns:
        Model: A compiled U-Net model ready for retraining.
    """
    logging.info("Loading pre-trained model...")
    model = load_trained_model(MODEL_PATH)

    logging.info("Compiling model with Adam optimizer and binary_crossentropy loss.")
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss="binary_crossentropy",
        metrics=["accuracy", f1],
    )
    return model


<<<<<<< HEAD
def load_image_mask_arrays(image_dir, mask_dir, patch_size):
    """
    Load and preprocess image and mask arrays from directories.

    Parameters
    ----------
    image_dir : str
        Path to the directory containing input images.
    mask_dir : str
        Path to the directory containing mask images.
    patch_size : int
        Target size for image resizing (height and width).

    Returns
    -------
    images : np.ndarray
        Normalized image array of shape (N, patch_size, patch_size, 3).
    masks : np.ndarray
        Binarized mask array of shape (N, patch_size, patch_size, 1).
    """
=======
def load_image_mask_arrays(
    image_dir: str, mask_dir: str, patch_size: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Loads and processes images and corresponding masks.

    Args:
        image_dir (str): Directory containing input images.
        mask_dir (str): Directory containing corresponding masks.
        patch_size (int): Size to which images and masks will be resized.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Tuple of normalized image and mask arrays.
    """
    logging.info(f"Loading images from: {image_dir}")
    logging.info(f"Loading masks from: {mask_dir}")

>>>>>>> 55baa7a (Adding sweep job training and evaluating models)
    image_filenames = sorted(os.listdir(image_dir))
    mask_filenames = sorted(os.listdir(mask_dir))

    image_paths = [os.path.join(image_dir, fname) for fname in image_filenames]
    mask_paths = [os.path.join(mask_dir, fname) for fname in mask_filenames]

    images = [
        img_to_array(load_img(p, target_size=(patch_size, patch_size))) / 255.0
        for p in image_paths
    ]

    masks = [
        np.round(
            img_to_array(
                load_img(
                    p, target_size=(patch_size, patch_size), color_mode="grayscale"
                )
            )
            / 255.0
        )
        for p in mask_paths
    ]

    logging.info(
        f"Loaded {len(images)} images and {len(masks)} masks. "
        f"Mask stats — Min: {np.min(masks)}, Max: {np.max(masks)}, "
        f"Unique: {np.unique(masks)}"
    )

    return np.array(images), np.array(masks)


def create_data_generators(
    patch_size: int,
    train_image_path: str,
    train_mask_path: str,
    val_image_path: str,
    val_mask_path: str,
    batch_size: int = 32,
):
    """
    Creates data generators for training and validation.

    Args:
        patch_size (int): Target size for image patches.
        train_image_path (str): Directory with training images.
        train_mask_path (str): Directory with training masks.
        val_image_path (str): Directory with validation images.
        val_mask_path (str): Directory with validation masks.
        batch_size (int): Batch size for the generators.

    Returns:
        tuple: Training and validation data generators.
    """
    logging.info("Creating training and validation generators...")
    train_images, train_masks = load_image_mask_arrays(
        train_image_path, train_mask_path, patch_size
    )
    val_images, val_masks = load_image_mask_arrays(
        val_image_path, val_mask_path, patch_size
    )

    train_image_datagen = ImageDataGenerator()
    train_mask_datagen = ImageDataGenerator()
    val_image_datagen = ImageDataGenerator()
    val_mask_datagen = ImageDataGenerator()

    train_image_gen = train_image_datagen.flow(
        train_images, batch_size=batch_size, seed=42, shuffle=True
    )
    train_mask_gen = train_mask_datagen.flow(
        train_masks, batch_size=batch_size, seed=42, shuffle=True
    )

    test_image_gen = val_image_datagen.flow(
        val_images, batch_size=batch_size, seed=42, shuffle=False
    )
    test_mask_gen = val_mask_datagen.flow(
        val_masks, batch_size=batch_size, seed=42, shuffle=False
    )

    logging.info("Data generators created successfully.")

    train_generator = zip(train_image_gen, train_mask_gen)
    test_generator = zip(test_image_gen, test_mask_gen)

    return train_generator, test_generator, train_image_gen, test_image_gen


def train_unet_model(
    model: Model,
    train_generator,
    test_generator,
    train_image_generator,
    test_image_generator,
    epochs: int = 1,
):
    """
    Trains the provided U-Net model.

    Args:
        model (Model): The U-Net model to train.
        train_generator: Training data generator.
        test_generator: Validation data generator.
        train_image_generator: Raw training image generator for length.
        test_image_generator: Raw validation image generator for length.
        epochs (int): Number of training epochs.

    Returns:
        History: Keras training history object.
    """
    logging.info(f"Starting training for {epochs} epoch(s)...")
    history = model.fit(
        train_generator,
        steps_per_epoch=len(train_image_generator),
        epochs=epochs,
        validation_data=test_generator,
        validation_steps=len(test_image_generator),
    )
    logging.info("Training complete.")
    return history
