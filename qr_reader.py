import cv2
from pyzbar.pyzbar import decode



def read_qr(image_path):
    """
    Reads a QR code from the given image file and returns the decoded data.

    :param image_path: Path to the image file containing the QR code.
    :return: Decoded data as a string, or None if no QR code is found.
    """
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Decode QR codes in the image
    decoded_objects = decode(img)
    if decoded_objects:
        # Return the data from the first QR code found
        qr_data = decoded_objects[0].data.decode('utf-8')
        return qr_data
    else:
        print("No QR code found in the image.")
        return None
