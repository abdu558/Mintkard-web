# # from PIL import Image
# # import numpy as np

# # def resize_image(image_path, max_width):
# #     # Open the image file
# #     img = Image.open(image_path)
    
# #     # Calculate the new height to maintain aspect ratio
# #     width, height = img.size
# #     new_height = int(max_width * height / width)
    
# #     # Resize the image using advanced matrix operations
# #     img_resized = img.resize((max_width, new_height), resample=Image.LANCZOS)
    
# #     # Convert the image to a NumPy array and return it
# #     return np.array(img_resized)

# import numpy as np
# from PIL import Image

# # Open the image and convert it to grayscale
# img = Image.open('image.png').convert('L')

# # Convert the image to a NumPy array
# img_array = np.array(img)

# # Get the original image dimensions
# original_width, original_height = img.size

# # Set the new width to 300 pixels and calculate the new height
# new_width = 300
# new_height = int((original_height / original_width) * new_width)

# # Create a matrix that scales the image to the new dimensions
# scale_matrix = np.array([[new_width/original_width, 0],
#                          [0, new_height/original_height]])

# # Apply the scale matrix to the image array
# resized_img_array = np.matmul(scale_matrix, img_array)

# # Convert the resized image array back to a PIL Image object
# resized_img = Image.fromarray(np.uint8(resized_img_array))

# # Save the resized image
# resized_img.save('AAAAA.png')

# # # Example usage:
# # image_path = 'image.png'
# # max_width = 300
# # resized_image = resize_image(image_path, max_width)
# # resized_image = Image.fromarray(resized_image)
# # resized_image.save('resized_image.png')
