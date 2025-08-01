"""Utilities for reading QR codes from images."""

import logging

import numpy as np

import cv2
from pyzbar.pyzbar import decode


logger = logging.getLogger(__name__)


def read_qr(raw_byte_array: bytearray) -> str | None:
    """
    Reads a QR code from the given image file and returns the decoded data.
    The image is preprocessed to enhance readability. If ``pyzbar`` fails to
    decode the QR code, the function falls back to OpenCV's ``QRCodeDetector``.

    :return: Decoded data as a string, or None if no QR code is found.
    """
    # Convert byte array to numpy array and decode into OpenCV image
    np_arr = np.frombuffer(raw_byte_array, dtype=np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) 
    if img is None:
        raise FileNotFoundError(f"Bytearray not found.")

    # # Preprocess image to improve readability
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # processed = cv2.adaptiveThreshold(
    #     gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    # )

    # Try decoding with pyzbar first
    decoded_objects = decode(img)
    if decoded_objects:
        qr_data = decoded_objects[0].data.decode("utf-8")
        return qr_data

    # Fallback to OpenCV's QRCodeDetector
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    if data:
        return data

    logger.warning("No QR code found in the bytearray")
    return None
