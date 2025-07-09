import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
import os

# --- Constants ---
COLOR_FLOOR = (150, 150, 150)
ASSETS_DIR = "assets"
OUTPUT_DIR = "assets"
TARGET_SIZE = (24, 24)

# --- Utility Functions ---
def print_array_details(A):
    print(f"{A.shape=}, {A.dtype=}, {np.amin(A)=}, {np.amax(A)=}")

def get_distance(img, bg):
    diff = img - bg
    return np.sqrt(np.sum(diff**2, axis=2))


def resize_and_save(image_path, output_path, new_size=(24, 24)):
    img = plt.imread(image_path)
    print(f"Array Before Resize: {image_path}")
    print_array_details(img)

    img_resized = cv.resize(img, new_size, interpolation=cv.INTER_AREA)

    # Convert to uint8
    if img_resized.dtype != np.uint8:
        img_resized = (img_resized * 255).astype(np.uint8)
        print(f"Your new image is ready for use:")
        print_array_details(img_resized)

    # Save using OpenCV
    cv.imwrite(output_path, cv.cvtColor(img_resized, cv.COLOR_RGB2BGR))

def get_corners(img):
    my, mx, _ = img.shape
    mx -= 1
    my -= 1
    return np.array([[0, 0, 1], [mx, 0, 1], [mx, my, 1], [0, my, 1], [0, 0, 1]]).T

def _create_mask(img, threshold=35):
    corners = get_corners(img)
    corner_pixels = []
    for x, y, _ in corners.T[:4]:
        corner_pixels.append(img[y, x])
    corner_pixels = np.array(corner_pixels)
    bg_color = np.mean(corner_pixels, axis=0)
    dist = get_distance(img, bg_color)
    return dist > threshold

def remove_background(img, tile_color=(150, 150, 150)):
    mask = _create_mask(img)
    mask_3c = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
    tile_color_arr = np.array(tile_color, dtype=np.uint8)
    return (img * mask_3c + tile_color_arr * (~mask_3c)).astype(np.uint8)

def process_all_assets():
    supported_exts = (".png", ".jpg", ".jpeg")
    skipped_files = []

    for filename in os.listdir(ASSETS_DIR):
        if not filename.lower().endswith(supported_exts):
            continue
        if "_24." in filename or "_ready." in filename:
            continue  # Skip already processed files

        input_path = os.path.join(ASSETS_DIR, filename)
        base_name = filename.rsplit(".", 1)[0]
        resized_filename = base_name + "_24.png"
        ready_filename = base_name + "_ready.png"
        resized_path = os.path.join(OUTPUT_DIR, resized_filename)
        ready_path = os.path.join(OUTPUT_DIR, ready_filename)

        try:
            img = plt.imread(input_path)

            # Resize
            img_resized = cv.resize(img, TARGET_SIZE, interpolation=cv.INTER_AREA)

            # Convert to uint8 if needed
            if img_resized.dtype != np.uint8:
                img_resized = (img_resized * 255).astype(np.uint8)

            # Save resized version
            cv.imwrite(resized_path, cv.cvtColor(img_resized, cv.COLOR_RGB2BGR))

            # Remove background
            if img_resized.shape[2] == 4:
                img_resized = img_resized[:, :, :3]  # drop alpha

            cleaned = remove_background(img_resized, tile_color=COLOR_FLOOR)

            # Save cleaned version
            cv.imwrite(ready_path, cv.cvtColor(cleaned, cv.COLOR_RGB2BGR))
            print(f"Processed: {filename} -> {resized_filename}, {ready_filename}")

        except Exception as e:
            print(f"Skipped {filename}: {e}")
            skipped_files.append(filename)

    if skipped_files:
        print("\nSkipped files:")
        for name in skipped_files:
            print(f"- {name}")

# Run when the script is executed
if __name__ == "__main__":
    process_all_assets()
