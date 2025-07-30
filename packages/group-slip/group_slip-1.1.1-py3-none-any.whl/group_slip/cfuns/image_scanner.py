import logging
import os


def scan_images(image_path):
    target_file_list = []
    try:
        for file in os.listdir(image_path):
            full_path = os.path.join(image_path, file)
            if os.path.isfile(full_path) and file.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".gif")
            ):
                target_file_list.append(full_path)

        logging.info(f"พบรูปภาพจำนวน {len(target_file_list)} รูปในโฟลเดอร์: {image_path}")
    except Exception as e:
        logging.error(f"เกิดข้อผิดพลาดในการสแกนภาพ: {e}")

    return target_file_list
