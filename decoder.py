# # imports
from PIL import Image
import numpy as np
from scipy.ndimage import rotate
import random
from stegano import lsb
# #


# # inputs
master_img = input("Enter master jpg image name(in current dir): ");
encoded_img = input("Enter encoded PNG image name(in current dir): ");
# #


# # open THE iamge resize to 300x300 -> convert to RGb image -> convert to greyscale ->
img_rgb = Image.open(master_img).convert("RGB")
img_rgb = img_rgb.resize((300, 300))
matrix_rgb = np.array(img_rgb)

R = matrix_rgb[:,:,0]
G = matrix_rgb[:,:,1]
B = matrix_rgb[:,:,2]

matrix_manual_gray = (0.299 * R + 0.587 * G + 0.114 * B).astype(np.uint8)
# #


# # decoding the encoded image
secret = lsb.reveal(encoded_img)
# #

# # transforming master image based on decoded secret
def decode_fixed(encoded):
    # Decode back from base36
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num = 0
    for char in encoded.lstrip("0"):  # strip leading zeros
        num = num * 36 + alphabet.index(char)
    return str(num)

decoded = int(decode_fixed(secret))
size = len(str(decoded))
decoded_str = str(decoded)

random_number = int(decoded_str[0:5])

digits = np.array([int(d) for d in str(random_number)])
transformed = np.tile(digits, (90000 // digits.size + 1))[:90000]
transformed = transformed.reshape(300, 300)
# matrix tranformation
transformed = np.dot(matrix_manual_gray,transformed)
transformed = transformed%255

# # extracting message from master image based on index given in decoded secret
hex_matrix = np.vectorize(lambda x: hex(int(x)))(transformed)

index_str = decoded_str[5:size]

# Step 1: Split into 6-digit chunks
chunks = [index_str[i:i+6] for i in range(0, len(index_str), 6)]
# Step 2: Convert each chunk to integer
results = []
for chunk in chunks:
    # Pad to 6 digits if shorter
    chunk = chunk.zfill(6)

    # First 3 digits = row, last 3 digits = col
    row = int(chunk[:3])
    col = int(chunk[3:])

    # Fetch value from matrix
    value = hex_matrix[row, col]
    results.append(value)

# Convert hex values to ASCII characters
ascii_chars = [chr(int(val, 16)) for val in results]
message = "".join(ascii_chars)

print("Decoded message:", message)
