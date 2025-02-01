from typing import List, Dict, Any
import re

def parse_fields(ocr_results: List[str]) -> Dict[str, Any]:
    """
    Parse OCR results from a Mozambican ID card into structured data.
    
    Args:
        ocr_results (List[str]): List of strings from OCR processing
    
    Returns:
        Dict[str, Any]: Structured data from the ID card
    """
    data = {
        "document_type": None,
        "id_number": None,
        "full_name": None,
        "date_of_birth": None,
        "height": None,
        "sex": None,
        "birth_place": None,
        "address": None,
    }
    
    # Helper function to find value after a key pattern
    def find_value_after_key(pattern: str) -> str:
        for i, text in enumerate(ocr_results):
            if re.search(pattern, text, re.IGNORECASE):
                # Try to get the next item if it exists
                if i + 1 < len(ocr_results):
                    return ocr_results[i + 1]
        return None

    # Extract document type
    if "BILHETE DE IDENTIDADE" in ocr_results:
        data["document_type"] = "BILHETE DE IDENTIDADE"

    # Extract ID number
    for text in ocr_results:
        if match := re.search(r'Nª:\s*(\d+[A-Z]?)', text):
            data["id_number"] = match.group(1)

    # Extract name
    data["full_name"] = find_value_after_key(r'Nome\s*/\s*Name:?')

    # Extract date of birth
    for text in ocr_results:
        if re.match(r'\d{2}/\d{2}/\d{4}', text):
            data["date_of_birth"] = text

    # Extract height
    for text in ocr_results:
        if match := re.search(r'Height:\s*(\d+,\d+)\s*m', text):
            data["height"] = match.group(1)

    # Extract sex
    for text in ocr_results:
        if match := re.search(r'Sex:\s*([MF])', text):
            data["sex"] = match.group(1)

    # Extract birth place
    data["birth_place"] = find_value_after_key(r'Birth:')

    # Extract address
    address_parts = []
    address_started = False
    for text in ocr_results:
        if re.search(r'Address:', text):
            address_started = True
            continue
        if address_started and not re.search(r'Signature|Assinatura', text):
            address_parts.append(text)
        if re.search(r'Signature|Assinatura', text):
            break
    data["address"] = " ".join(address_parts).strip() if address_parts else None


    # Clean up the data by removing None values and strip whitespace
    return {k: v.strip() if isinstance(v, str) else v 
            for k, v in data.items() 
            if v is not None}