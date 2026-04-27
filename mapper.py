# # imports
from PIL import Image
import numpy as np
from scipy.ndimage import rotate
import random
from stegano import lsb
# #


# # inputs
master_img = input("Enter master jpg image name(in current dir): ");
encoded_img = input("Enter PNG image name to be encoded(in current dir): ");
message = input("Enter the messaage ")
print("message :- ",message);
# #



# # open THE iamge resize to 300x300 -> convert to RGB image -> convert to greyscale ->
img_rgb = Image.open(master_img).convert("RGB")
img_rgb = img_rgb.resize((300, 300))
matrix_rgb = np.array(img_rgb)

R = matrix_rgb[:,:,0]
G = matrix_rgb[:,:,1]
B = matrix_rgb[:,:,2]

matrix_manual_gray = (0.299 * R + 0.587 * G + 0.114 * B).astype(np.uint8)
# #


# # Generate a random integer of fixed length use it for transformations on matrix_manual_gray matrix
length = 5
random_number = random.randint(10**(length-1), 10**length-1)
digits = np.array([int(d) for d in str(random_number)])

# spanning 1x5 martix to 300x300
transformed = np.tile(digits, (90000 // digits.size + 1))[:90000]
transformed = transformed.reshape(300, 300)

# matrix tranformation  
transformed = np.dot(matrix_manual_gray,transformed)

# limiting to max value 255
transformed = transformed%255
# #


# # Convert transformed int matrix to hex
hex_matrix = np.vectorize(lambda x: hex(int(x)))(transformed)
# #

# # finding hex of message
hex_array = [hex(ord(c)) for c in message];
# #

# # finding matching image hex and meesage hex and returning matched indexes and concatenating them to single string
index_numbers = []
for key in hex_array:
    positions = np.argwhere(hex_matrix == key)
    if positions.shape[0] >= 16:   # check if at least 16 occurrences exist
        row, col = positions[15]   # 16th occurrence (0-based index → 6)
        index_numbers.append(f"{row:03d}{col:03d}")
    else:
        index_numbers.append("000")


final_index = "".join(index_numbers)
# #


# # encoding above string of numbers into encoded image(user input) 
# # and save the new encoded image using LSB steganography
before_enc = str(random_number) + str(final_index)
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

encoded = encode_fixed(before_enc, width=12)

message = str(encoded)

# Hide the integer inside an image
secret_image = lsb.hide(encoded_img, message)
secret_image.save("EncLSB.png")

print("Message hidden successfully in EncLSB.png")
# # end