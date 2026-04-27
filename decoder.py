from PIL import Image
import numpy as np
from scipy.ndimage import rotate
import random
from stegano import lsb

# #open THE iamge resize to 300x300 -> convert to RGb image -> convert to greyscale ->
master_img = input("Enter master jpg image name(in current dir): ");
img_rgb = Image.open(master_img).convert("RGB")
img_rgb = img_rgb.resize((300, 300))
matrix_rgb = np.array(img_rgb)

R = matrix_rgb[:,:,0]
G = matrix_rgb[:,:,1]
B = matrix_rgb[:,:,2]

matrix_manual_gray = (0.299 * R + 0.587 * G + 0.114 * B).astype(np.uint8)
encoded_img = input("Enter encoded PNG image name(in current dir): ");
secret = lsb.reveal(encoded_img)
# secret = int(secret_str)

def decode_fixed(encoded):
    # Decode back from base36
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num = 0
    for char in encoded.lstrip("0"):  # strip leading zeros
        num = num * 36 + alphabet.index(char)
    return str(num)

decoded = int(decode_fixed(secret))
print(decoded)

size = len(str(decoded))

decoded_str = str(decoded)
random_number = int(decoded_str[0:5])
print(random_number)
# 1. Rotate by (3MSB of random_number which ranges from (0-999)) with wrap mode
transformed = rotate(matrix_manual_gray,random_number//100, reshape=True, mode='wrap')

# # 2. Flip horizontally if(4th MSB is 1)
if bool(int(str(random_number)[3])%2):
    transformed = np.fliplr(transformed)

# # 3. Flip verticallyz
else:
    transformed = np.flipud(transformed)

# # 4. Transpose if(last bit is 1)
if bool(int(str(random_number)[4])%2):
    transformed = transformed.T

img_final = Image.fromarray(transformed.astype(np.uint8))
img_final.save("Decode_transformed.jpg")

hex_matrix = np.vectorize(lambda x: hex(int(x)))(transformed)

#index = int(decoded_str[5:size-1])   # integer
index_str = decoded_str[5:size]            # convert to string
print("Index_str = ",index_str)
# Step 1: Split into 6-digit chunks
chunks = [index_str[i:i+6] for i in range(0, len(index_str), 6)]
print("chunks : ",chunks)
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

print("Chunks:", chunks)
print("Values:", results)
print("Decoded message:", message)
# ints = [int(chunk) for chunk in chunks]
# print("ints : ",ints)