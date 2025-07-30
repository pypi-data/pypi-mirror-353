import argparse
import logging
from group_slip.cfuns.ocr_and_group import thread_grouping_slip
import warnings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
warnings.filterwarnings("ignore", message=".*pin_memory.*")


def main():
    parser = argparse.ArgumentParser(description="จัดกลุ่ม Slip ตามชื่อ")
    parser.add_argument("-i", "--image_path", type=str, required=True, help="ที่ตั้งไฟล์ภาพที่ต้องการจัดกลุ่ม")
    parser.add_argument("-b", "--is_crop_by_bank", type=str, required=True, choices=["scb", "kbank", "next"], help="ธนาคารเจ้าของ Slip (เลือกได้: scb, kbank, next)")
    parser.add_argument("-l", "--limit", type=int, help="จำนวนภาพสูงสุดที่ต้องการประมวลผล")
    args = parser.parse_args()

    image_path = args.image_path
    is_crop_by = args.is_crop_by_bank
    limit = args.limit

    SLIP_TYPE = {
        "scb": (700, 1100),
        "kbank": (200, 745),
        "next": (400, 1100),
    }

    y_position = SLIP_TYPE.get(is_crop_by.lower())

    if not y_position:
        logging.error("ไม่พบประเภท Slip ที่ระบุ กรุณาใช้ 'scb', 'kbank', หรือ 'next'")
    else:
        thread_grouping_slip(image_path, y_position[0], y_position[1], limit, is_crop_by.lower())


if __name__ == "__main__":
    main()
