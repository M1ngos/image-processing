from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import easyocr
import io
from PIL import Image
import numpy as np
from typing import List


class IDDataResponse(BaseModel):
    front_data: List[str]
    back_data: List[str]


async def extract_id_data(
        front: UploadFile = File(...),
        back: UploadFile = File(...)
):
    try:
        # Initialize reader
        reader = easyocr.Reader(['pt', 'en'], gpu=False)

        # Process front image
        front_contents = await front.read()
        front_image = Image.open(io.BytesIO(front_contents))
        front_results = reader.readtext(np.array(front_image), detail=0)

        # Process back image
        back_contents = await back.read()
        back_image = Image.open(io.BytesIO(back_contents))
        back_results = reader.readtext(np.array(back_image), detail=0)

        return IDDataResponse(
            front_data=front_results,
            back_data=back_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))