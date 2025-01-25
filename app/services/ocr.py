import base64
import re

import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from passporteye import read_mrz
import io, cv2


class IDDataResponse(BaseModel):
    front_data: dict
    back_data: dict
    front_image_base64: str
    back_image_base64: str


def preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert('L')  # Grayscale
    image = image.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    return image


def extract_text(image: Image.Image) -> str:
    custom_config = r'--oem 3 --psm 6 -l por'
    text = pytesseract.image_to_string(image, config=custom_config)
    return text.strip()


def parse_front_text(text: str) -> dict:
    data = {}
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Extract ID Number (N followed by 12 digits and a letter)
    id_pattern = r'N\d{12}[A-Z]'
    for line in lines:
        if re.match(id_pattern, line):
            data["id_number"] = line
            break

    # Name appears after the ID line
    if "id_number" in data:
        id_index = lines.index(data["id_number"])
        if id_index + 1 < len(lines):
            data["name"] = lines[id_index + 1]

    # Extract Date of Birth
    dob_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    for line in lines:
        if "Data de Nascimento" in line or "Date of Birth" in line:
            match = re.search(dob_pattern, line)
            if not match and lines.index(line) + 1 < len(lines):
                match = re.search(dob_pattern, lines[lines.index(line) + 1])
            if match:
                data["date_of_birth"] = match.group()

    # Extract Height (e.g., 1,69 m)
    for line in lines:
        if "Altura/Height" in line:
            height = re.search(r'\d,\d{2}\s?m', line)
            if height:
                data["height"] = height.group().replace(' ', '')

    # Extract Sex (F/M)
    for line in lines:
        if "Sexo/Sex" in line:
            sex = re.search(r'[FM]', line)
            if sex:
                data["sex"] = sex.group()

    # Extract Place of Birth and Address
    for i, line in enumerate(lines):
        if "Naturalidade/Place of Birth" in line and i + 1 < len(lines):
            data["place_of_birth"] = lines[i + 1]
        if "Local de Residencia/Address" in line and i + 1 < len(lines):
            data["address"] = lines[i + 1]

    return data


def parse_back_text(text: str) -> dict:
    data = {}
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Key-value pairs using regex to handle inline values
    patterns = {
        "issuance_date": r"(?<=Data de Emissao / Issuance Date:).*|\d{2}/\d{2}/\d{4}",
        "expiry_date": r"(?<=Válido Até / Expiry Date:).*|\d{2}/\d{2}/\d{4}",
        "marital_status": r"(?<=Estado Civil / Marital Status:).*",
        "father_name": r"(?<=Nome do Pai / Father Name:).*",
        "mother_name": r"(?<=Nome da Mãe / Mother Name:).*"
    }

    for field, pattern in patterns.items():
        for line in lines:
            match = re.search(pattern, line)
            if match:
                value = match.group().strip()
                if value:
                    data[field] = value.split()[0]  # Take first part to avoid extra text
                    break

    return data


# @app.post("/extract-id-data/", response_model=IDDataResponse)
async def extract_id_data(
        front: UploadFile = File(...),
        back: UploadFile = File(...)
):
    try:
        # Process front image
        front_image = Image.open(io.BytesIO(await front.read()))
        front_image_preprocessed = preprocess_image(front_image)
        front_text = extract_text(front_image_preprocessed)
        front_data = parse_front_text(front_text)

        # Process back image
        back_image = Image.open(io.BytesIO(await back.read()))
        back_image_preprocessed = preprocess_image(back_image)
        back_text = extract_text(back_image_preprocessed)
        back_data = parse_back_text(back_text)

        # Prioritize front ID over back
        if "id_number" in front_data and "id_number" in back_data:
            back_data.pop("id_number")

        # Encode images to base64
        buffered = io.BytesIO()
        front_image.save(buffered, format="JPEG")
        front_base64 = base64.b64encode(buffered.getvalue()).decode()

        buffered = io.BytesIO()
        back_image.save(buffered, format="JPEG")
        back_base64 = base64.b64encode(buffered.getvalue()).decode()

        return IDDataResponse(
            front_data=front_data,
            back_data=back_data,
            front_image_base64=front_base64,
            back_image_base64=back_base64
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))