import datetime
import logging
import os
import random
import re
import shutil
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
import cv2
import easyocr
from tqdm import tqdm
import torch
from group_slip.cfuns.image_scanner import scan_images


gpu_available = torch.cuda.is_available()

reader = easyocr.Reader(["th", "en"], gpu=gpu_available)


def ocr_images(image_path, y_start=0, y_end=0):
    image = cv2.imread(image_path)
    if image is None:
        logging.warning(f"ไม่สามารถอ่านภาพ: {image_path}")
        return None

    if y_start > 0 and y_end > 0 and y_end > y_start:
        image = image[y_start:y_end, :]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    results = reader.readtext(gray)
    exclude_keywords = ["จาก", "ไปยัง"]
    lines = []

    for _, text, _ in results:
        if not isinstance(text, str):
            continue
        text = text.strip()
        if not text:
            continue
        normalized_line = unicodedata.normalize("NFC", text)
        normalized_line = re.sub(r"\s+", "", normalized_line)

        if any(exclude_word in normalized_line for exclude_word in exclude_keywords):
            continue

        lines.append(normalized_line)

    return {"image": image_path, "text_lines": lines}


def thread_grouping_slip(cropped_images_path, y_start, y_end, limit, bank_name):
    if gpu_available:
        logging.info("GPU is available: " + torch.cuda.get_device_name(0))
    else:
        logging.info("GPU is not available, using CPU")

    file_list = scan_images(cropped_images_path)
    ocred_images = []

    max_workers = min(32, (os.cpu_count() or 4) * 4)
    logging.info(f"กำลังใช้งาน {max_workers} workers สำหรับการประมวลผล OCR")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        file_list = file_list[:limit] if limit is not None else file_list
        futures = {executor.submit(ocr_images, image_file, y_start, y_end): image_file for image_file in file_list}
        
        with tqdm(total=len(futures), desc="กำลังกำลังประมวลผล OCR") as pbar:
            for future in as_completed(futures):
                result = future.result()
                if result:
                    ocred_images.append(result)
                pbar.update(1)

    if not ocred_images:
        logging.warning("ไม่พบภาพที่ผ่าน OCR สำเร็จ")
        return

    last_result = random.choice(ocred_images)
    for idx, line in enumerate(last_result["text_lines"]):
        print(f"{idx + 1}: {line}")

    selected_column = input("เลือก Column สำหรับจัดกลุ่มภาพ: ")
    try:
        column_index = int(selected_column) - 1
    except ValueError:
        logging.error("กรุณาใส่หมายเลข column ที่ถูกต้อง")
        return

    grouped = {}
    for item in ocred_images:
        lines = item["text_lines"]
        if column_index < len(lines):
            key = lines[column_index]
        else:
            key = "unknown"

        grouped.setdefault(key, []).append(item["image"])

    for group_key, images in grouped.items():
        safe_key = group_key or "unknown"

        group_folder = os.path.join(
            os.getcwd(),
            f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{bank_name}_slip",
            f"group_{safe_key}",
        )
        os.makedirs(group_folder, exist_ok=True)

        for image_path in images:
            filename = os.path.basename(image_path)
            shutil.copy2(image_path, os.path.join(group_folder, filename))

    logging.info(f"จัดกลุ่ม Slip เป็น {len(grouped)} กลุ่ม")
