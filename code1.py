import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pytesseract
import cv2
import numpy as np

app = FastAPI()

def parse_lab_report_text(text):
    lines = text.splitlines()
    results = []

    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 3:
            try:
                test_name = " ".join(parts[:-2])
                value = float(parts[-2])
                ref_range = parts[-1]

                if '-' in ref_range:
                    ref_low, ref_high = map(float, ref_range.split('-'))
                    out_of_range = not (ref_low <= value <= ref_high)
                else:
                    ref_low = ref_high = None
                    out_of_range = False

                results.append({
                    "lab_test_name": test_name,
                    "lab_test_value": value,
                    "bio_reference_range": ref_range,
                    "lab_test_out_of_range": out_of_range
                })
            except:
                continue
    return results

@app.post("/get-lab-tests")
async def get_lab_tests(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Uploaded file is not a valid image")
        

        text = pytesseract.image_to_string(img)
        extracted_data = parse_lab_report_text(text)

        return {
            "is_success": True,
            "data": extracted_data
        }

    except Exception as e:
        return JSONResponse(content={"is_success": False, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("code1:app", host="127.0.0.1", port=8000, reload=True)

