import base64
from pathlib import Path

import io
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont


class ImageUtil:
    @staticmethod
    def encode_image(image_path, encoding='utf-8'):
        # Function to encode the image
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode(encoding)

    @staticmethod
    def decode_image(base64_image):
        # Decode the base64-encoded image string
        decoded_image = base64.b64decode(base64_image)

        # Open the image using PIL (Python Imaging Library)
        img = Image.open(io.BytesIO(decoded_image))

        # Display the image
        img.show()

    @staticmethod
    def check_image_resolution(img_path):
        with open(img_path, 'rb') as image_file:
            image = Image.open(image_file)
            width, height = image.size
            print(f"Original image resolution: {width}x{height}")

            # Encode the image in base64
            image_file.seek(0)
            base64_encoded = base64.b64encode(image_file.read()).decode('utf-8')

            # Decode the base64 string back to an image
            image_data = base64.b64decode(base64_encoded)
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            print(f"Decoded image resolution: {width}x{height}")

    @staticmethod
    def set_img_with_grid(img_path, img_name, figsize=(14.4, 9), gird_space=50):
        # Display the image
        img = Image.open(Path(img_path, f"{img_name}.png"))
        # Create a figure and an axes
        # Load the image and display it with a grid without changing its resolution
        fig, ax = plt.subplots(figsize=figsize)  # Adjust figure size to match image resolution
        # fig, ax = plt.subplots(figsize=(28.8, 18))  # Adjust figure size to match image resolution
        # fig, ax = plt.subplots()  # Adjust figure size to match image resolution

        # Display the image
        ax.imshow(img)
        ax.axis('on')

        # Add a grid
        xticks = range(0, img.width, gird_space)
        yticks = range(0, img.height, gird_space)
        ax.set_xticks(xticks)
        ax.set_yticks(yticks)
        ax.grid(color='gray', linestyle='--', linewidth=0.5)
        # Label the axes
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        # Annotate each grid point with its coordinates
        for x in xticks:
            for y in yticks:
                ax.text(x, y, f'({x},{y})', color='blue', fontsize=5.5, ha='center', va='center')

        # Save the image with grid
        grid_image_path = Path(img_path, f"{img_name}_with_grid.png")
        plt.savefig(grid_image_path, bbox_inches='tight', pad_inches=0, dpi=100)
        plt.show()
        fig.savefig(Path(img_path, f"{img_name}_with_grid.png"))

    @staticmethod
    def calculate_coordinate_by_num(image_path, number, interval=100):
        # Load the image to get its dimensions
        image = Image.open(image_path)
        width, height = image.size

        # Calculate the number of columns
        columns = width // interval

        # Calculate row and column indices for the given number
        row_index = (number - 1) // columns
        column_index = (number - 1) % columns

        # Calculate the coordinates
        x_coordinate = column_index * interval
        y_coordinate = row_index * interval
        return (x_coordinate, y_coordinate)

    @staticmethod
    def set_img_with_nums(img_path, img_name, interval=100, font_size=30, font_color="red"):
        # Load the uploaded image
        image = Image.open(Path(img_path, f"{img_name}.png"))
        draw = ImageDraw.Draw(image)

        # Define font size and font for numbering
        try:
            font_path = "/Library/Fonts/Arial.ttf"
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
            print("Could not load specified font. Using default font.")

        # Get image dimensions
        width, height = image.size

        # Dictionary to store number and coordinate relationships
        num_coord_dict = {}

        # Draw the numbers and store coordinates
        number = 1
        for y in range(0, height, interval):
            for x in range(0, width, interval):
                draw.text((x, y), str(number), fill=font_color, font=font)
                num_coord_dict[number] = (x, y)
                number += 1

        # Save the modified image
        final_image_path_new = Path(img_path, f"{img_name}_with_nums.png")
        image.save(final_image_path_new)

        # Return the modified image and the dictionary
        return image, num_coord_dict
