"""Utility functions and dataset class for generating shape images."""
import random
import math
import numpy as np
import cv2

class ShapesDataset:
    """
    The dataset can be used for training and validation of object detection models.
    The class names can be specified as a list of shape names or 'all' for default shapes.
    The dataset generates images, masks, and bounding boxes for each shape.
    The class names are:
    - 'BG' (background)
    - 'square'
    - 'circle'
    - 'triangle'
    - 'hexagon'
    - 'pentagon'
    - 'star'
    """
    def __init__(self, class_names=None):
        """Initializes the dataset with class names."""
        if class_names is None:
            raise ValueError("class_names must be provided. Use 'all' for default shapes or a list of shape names")
        if isinstance(class_names, str):
            if class_names.lower() == 'all':
                self.class_names = [
                    'BG', 'square', 'circle', 'triangle', 'hexagon', 'pentagon', 'star'
                ]
            else:
                # If a single string is provided, treat it as a single class name
                self.class_names = ['BG', class_names.lower()]
        if isinstance(class_names, list):
            self.class_names = ['BG'] + [cls.lower() for cls in class_names]

    def draw_shape(self, image, shape, dims, color):
        """Draws a shape from the given specs."""
        x, y, s = dims
        bbox = None
        if shape == 'square':
            cv2.rectangle(image, (x-s, y-s), (x+s, y+s), color, -1)
            bbox = [x-s, y-s, x+s, y+s]
        elif shape == "circle":
            cv2.circle(image, (x, y), s, color, -1)
            bbox = [x-s, y-s, x+s, y+s]
        elif shape == "triangle":
            points = np.array([
                [x, y-s],
                [int(x - s / math.sin(math.radians(60))), y + s],
                [int(x + s / math.sin(math.radians(60))), y + s]
            ], dtype=np.int32)
            cv2.fillPoly(image, [points], color)
            bbox = [
                int(x - s / math.sin(math.radians(60))),
                y-s,
                int(x + s / math.sin(math.radians(60))),
                y+s
            ]
        elif shape == "hexagon":
            angles = np.linspace(0, 2 * np.pi, 7)[:-1]
            points = np.array([[int(x + s * np.cos(a)), int(y + s * np.sin(a))] for a in angles])
            cv2.fillPoly(image, [points], color)
            bbox = [x-s, y-s, x+s, y+s]
        elif shape == "pentagon":
            angles = np.linspace(0, 2 * np.pi, 6)[:-1]
            points = np.array([[int(x + s * np.cos(a)), int(y + s * np.sin(a))] for a in angles])
            cv2.fillPoly(image, [points], color)
            bbox = [x-s, y-s, x+s, y+s]
        elif shape == "star":
            outer_points = []
            inner_points = []
            for i in range(5):
                angle = (2 * np.pi * i) / 5 - np.pi / 2
                outer_points.append([
                    int(x + s * np.cos(angle)),
                    int(y + s * np.sin(angle))
                ])
                angle += np.pi / 5
                inner_points.append([
                    int(x + 0.4 * s * np.cos(angle)),
                    int(y + 0.4 * s * np.sin(angle))
                ])
            points = []
            for i in range(5):
                points.append(outer_points[i])
                points.append(inner_points[i])
            cv2.fillPoly(image, [np.array(points)], color)
            bbox = [x-s, y-s, x+s, y+s]
        return image, bbox

    def random_shape(self, height, width, shape=None):
        """Generates specifications of a random or specified shape."""
        if shape is None:
            shape = random.choice(self.class_names[1:])  # Exclude BG
        color = tuple(random.randint(0, 255) for _ in range(3))
        buffer = 20
        y = random.randint(buffer, height - buffer - 1)
        x = random.randint(buffer, width - buffer - 1)
        s = random.randint(buffer, height//4)
        return shape, color, (x, y, s)

    def random_image(self, height, width, num_shapes=None):
        """Creates random specifications of an image with multiple shapes."""
        bg_color = np.array([random.randint(0, 255) for _ in range(3)])
        shapes = []
        if num_shapes is None:
            num_shapes = random.randint(1, 4)
        available_shapes = self.class_names[1:]
        random.shuffle(available_shapes)
        for i in range(num_shapes):
            shape = available_shapes[i % len(available_shapes)]
            shape_spec = self.random_shape(height, width, shape)
            shapes.append(shape_spec)
        return bg_color, shapes

    def create_image_and_mask(self, height, width, num_shapes=None, forced_shape=None):
        """Generate image, mask, and bounding boxes."""
        bg_color, shapes = self.random_image(height, width, num_shapes)
        if forced_shape is not None:
            shapes = [(forced_shape, color, dims) for _, color, dims in shapes]
        image = np.ones([height, width, 3], dtype=np.uint8)
        image = image * bg_color.astype(np.uint8)
        mask = np.zeros([height, width, len(shapes)], dtype=np.uint8)
        bboxes = []
        shape_classes = []
        for i, (shape, color, dims) in enumerate(shapes):
            image, bbox = self.draw_shape(image, shape, dims, color)
            mask_slice = np.zeros([height, width, 1], dtype=np.uint8)
            mask[:, :, i:i+1], _ = self.draw_shape(mask_slice, shape, dims, 1)
            bboxes.append(bbox)
            shape_classes.append(self.class_names.index(shape))
        return image, mask, bboxes, shape_classes
