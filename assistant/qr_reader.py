"""Utilities for reading QR codes from images."""

import logging

import cv2
from pyzbar.pyzbar import decode


logger = logging.getLogger(__name__)


def read_qr(image_path: str) -> str | None:
    """
    Reads a QR code from the given image file and returns the decoded data.
    The image is preprocessed to enhance readability. If ``pyzbar`` fails to
    decode the QR code, the function falls back to OpenCV's ``QRCodeDetector``.

    :param image_path: Path to the image file containing the QR code.
    :return: Decoded data as a string, or None if no QR code is found.
    """
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

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

    logger.warning("No QR code found in the image %s", image_path)
    return None
