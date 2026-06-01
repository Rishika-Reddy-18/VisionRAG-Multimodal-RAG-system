import easyocr
import cv2
import re
import numpy as np

reader = easyocr.Reader(['en'])


def preprocess_image(image_path):

    img = cv2.imread(image_path)

    if img is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    img = cv2.resize(
        img,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    sharpened = cv2.filter2D(
        gray,
        -1,
        kernel
    )

    return sharpened


def extract_text_from_image(image_path):

    try:

        processed = preprocess_image(
            image_path
        )

        results = reader.readtext(
            processed,
            detail=0,
            paragraph=True
        )

        text = " ".join(results)

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    except Exception as e:

        print(
            f"OCR Error: {e}"
        )

        try:

            img = cv2.imread(
                image_path
            )

            if img is None:
                return ""

            results = reader.readtext(
                img,
                detail=0,
                paragraph=True
            )

            text = " ".join(results)

            text = re.sub(
                r"\s+",
                " ",
                text
            )

            return text.strip()

        except Exception as e:

            print(
                f"Fallback OCR Error: {e}"
            )

            return ""