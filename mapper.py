# #imports
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

# print("Manual grayscale matrix shape:", matrix_manual_gray.shape)
# print("Matrix:\n", matrix_manual_gray)

#img_manual_gray = Image.fromarray(matrix_manual_gray)


# # Generate a random integer of fixed length to choose transformations on matrix_manual_gray matrix
length = 5
random_number = random.randint(10**(length-1), 10**length-1)
print("Random number generated : ",random_number)
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

# # Transformed matrix_manual_gray to transformed matrix -> now converting transformed matrix as image(just to see)
img_final = Image.fromarray(transformed.astype(np.uint8))
img_final.save("final_transformed.jpg")
# print("Matrix:\n", transformed)

# # Convert transformed int matrix to hex
hex_matrix = np.vectorize(lambda x: hex(int(x)))(transformed)

# #input the message to map
message = input("Enter the messaage ")
print(message);

# #finding hex of message
hex_array = [hex(ord(c)) for c in message];

print("hex of message : ",hex_array)

# results = {}
# for key in hex_array:
#     positions = np.argwhere(hex_matrix == key)
#     if positions.size > 0:
#         # Take the first occurrence only
#         results[key] = positions[0].tolist()
#     else:
#         results[key] = None   

# print(results)
index_numbers = []
for key in hex_array:
    positions = np.argwhere(hex_matrix == key)
    if positions.shape[0] >= 16:   # check if at least 16 occurrences exist
        row, col = positions[15]   # 16th occurrence (0-based index → 6)
        index_numbers.append(f"{row:03d}{col:03d}")
    else:
        index_numbers.append("000")

#print(index_numbers)
# Concatenate into one string
final_index = "".join(index_numbers)

print("hex matched idexes : ",index_numbers)
print("hex matched idexes as int",final_index)

before_enc = str(random_number) + str(final_index)
print("before Encoded:",before_enc )
def encode_fixed(final_index, width=12):
    # Convert to integer
    num = int(final_index)

    # Encode to base36 (digits + letters)
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    encoded = ""
    while num > 0:
        num, rem = divmod(num, 36)
        encoded = alphabet[rem] + encoded

    # Pad to fixed width
    encoded = encoded.zfill(width)
    return encoded

def decode_fixed(encoded):
    # Decode back from base36
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num = 0
    for char in encoded.lstrip("0"):  # strip leading zeros
        num = num * 36 + alphabet.index(char)
    return str(num)

encoded = encode_fixed(before_enc, width=12)
decoded = decode_fixed(encoded)

print("Encoded:", encoded)   # Always 12 chars
print("Decoded:", decoded)   # Original number

message = str(encoded)

# Hide the integer inside an image
encoded_img = input("Enter PNG image name to be encoded(in current dir): ");
secret_image = lsb.hide(encoded_img, message)
secret_image.save("EncLSB.png")

print("Integer hidden successfully in output.png")

# revealed = lsb.reveal("EncLSB.png")
# print("Revealed integer: ", revealed)