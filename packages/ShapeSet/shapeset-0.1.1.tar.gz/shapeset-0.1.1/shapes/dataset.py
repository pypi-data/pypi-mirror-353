"""Dataset generation utilities for shape images."""

import os
import random
from typing import Union

import numpy as np
import cv2
from tqdm import tqdm

from shapes.utils import ShapesDataset


def generate(class_names: Union[list, str],
             num_train: int,
             num_val: int,
             image_size: int,
             output_dir: str,
             seed: int = 42):
    """
    Generate and save the shapes dataset.
    Args:
        class_names (list or str): List of shape names or 'all' for default shapes.
        num_train (int): Number of training images to generate.
        num_val (int): Number of validation images to generate.
        image_size (int): Size of the generated images (width and height).
        output_dir (os.PathLike): Directory where the dataset will be saved.
    """

    # Set random seed for reproducibility
    random.seed(seed)
    np.random.seed(seed=seed)

    if image_size < 80:
        raise ValueError("Image size must be at least 80 pixels.")

    dataset = ShapesDataset(class_names=class_names)

    # Calculate images per shape type
    num_shape_types = len(dataset.class_names) - 1  # Exclude BG
    if num_train < num_shape_types or num_val < num_shape_types:
        raise ValueError("Number of training and validation images must be at "
                         "least equal to the number of shape types.")
    train_imgs_per_shape = num_train // num_shape_types
    val_imgs_per_shape = num_val // num_shape_types

    # Create directories
    train_img_dir = os.path.join(output_dir, 'train', 'images')
    train_mask_dir = os.path.join(output_dir, 'train', 'masks')
    train_anno_dir = os.path.join(output_dir, 'train', 'annotations')
    val_img_dir = os.path.join(output_dir, 'val', 'images')
    val_mask_dir = os.path.join(output_dir, 'val', 'masks')
    val_anno_dir = os.path.join(output_dir, 'val', 'annotations')

    # Create all directories
    for d in [train_img_dir, train_mask_dir, train_anno_dir,
              val_img_dir, val_mask_dir, val_anno_dir]:
        os.makedirs(d, exist_ok=True)

    # Generate training data
    print("Generating training data...")
    for shape_type in dataset.class_names[1:]:  # Exclude BG
        print(f"Generating {train_imgs_per_shape} training images for {shape_type}")
        for i in tqdm(range(train_imgs_per_shape)):
            # Force specific shape type for equal distribution
            image, mask, bboxes, shape_classes = dataset.create_image_and_mask(
                image_size, image_size, num_shapes=1, forced_shape=shape_type)
            # Calculate unique index for each shape type
            shape_idx = dataset.class_names.index(shape_type) - 1
            idx = shape_idx * train_imgs_per_shape + i

            # Save image
            image_path = os.path.join(train_img_dir, f'train_shape_{idx:04d}.png')
            cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

            # Save individual masks
            for j in range(mask.shape[-1]):
                mask_path = os.path.join(train_mask_dir, f'train_shape_{idx:04d}_mask_{j}.png')
                cv2.imwrite(mask_path, mask[:, :, j] * 255)

            # Save annotations
            anno_path = os.path.join(train_anno_dir, f'train_shape_{idx:04d}.txt')
            with open(anno_path, 'w', encoding='utf-8') as f:
                for bbox, cls in zip(bboxes, shape_classes):
                    f.write(f"{cls} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n")

    # Generate validation data
    print("\nGenerating validation data...")
    for shape_type in dataset.class_names[1:]:  # Exclude BG
        print(f"Generating {val_imgs_per_shape} validation images for {shape_type}")
        for i in tqdm(range(val_imgs_per_shape)):
            # Force specific shape type for equal distribution
            image, mask, bboxes, shape_classes = dataset.create_image_and_mask(
                image_size, image_size, num_shapes=1, forced_shape=shape_type)
            # Calculate unique index for each shape type
            shape_idx = dataset.class_names.index(shape_type) - 1
            idx = shape_idx * val_imgs_per_shape + i

            # Save image
            image_path = os.path.join(val_img_dir, f'val_shape_{idx:04d}.png')
            cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

            # Save individual masks
            for j in range(mask.shape[-1]):
                mask_path = os.path.join(val_mask_dir, f'val_shape_{idx:04d}_mask_{j}.png')
                cv2.imwrite(mask_path, mask[:, :, j] * 255)

            # Save annotations
            anno_path = os.path.join(val_anno_dir, f'val_shape_{idx:04d}.txt')
            with open(anno_path, 'w', encoding='utf-8') as f:
                for bbox, cls in zip(bboxes, shape_classes):
                    f.write(f"{cls} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n")

    print("✅ Dataset generation complete!")
    print(f"📁 Dataset saved in: {os.path.abspath(output_dir)}\n")