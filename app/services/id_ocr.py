from datetime import datetime
import logging
import os
import aiofiles
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import easyocr
import io
from PIL import Image
import numpy as np
from typing import Dict, Any
from app.utils.field_extraction import parse_fields


logger = logging.getLogger(__name__)

UPLOAD_DIR = "id_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IDDataResponse(BaseModel):
    front_data: Dict[str, Any]
    # back_data: Dict[str, Any]

async def extract_id_data(
    front: UploadFile = File(...),
    back: UploadFile = File(...)
):
    try:
        
        # if not front.content_type.startswith('image/'):
        #     raise HTTPException(status_code=400, detail="File must be an image")
    
        # # Generate unique filename
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # filename = f"{timestamp}_{front.filename}"
        # filepath = os.path.join(UPLOAD_DIR, filename)
        
        
        #  # Save the file
        # async with aiofiles.open(filepath, 'wb') as out_file:
        #     content = await front.read()
        #     await out_file.write(content)
            
            
        # reader = easyocr.Reader(['pt', 'en'], gpu=False)
        reader = easyocr.Reader(['pt', 'en'])
        
        # Process front image.
        front_contents = await front.read()
        front_image = Image.open(io.BytesIO(front_contents)).convert('L')
        front_results = reader.readtext(np.array(front_image), detail=0)
        organized_front = parse_fields(front_results)
        
        # Process back image.
        # back_contents = await back.read()
        # back_image = Image.open(io.BytesIO(back_contents))
        # back_results = reader.readtext(np.array(back_image), detail=0)
        # organized_back = parse_data(back_results)

        # print(organized_front)
        logger.info("data :"+str(organized_front))

        return IDDataResponse(
            front_data=organized_front,
            # back_data=organized_back
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
