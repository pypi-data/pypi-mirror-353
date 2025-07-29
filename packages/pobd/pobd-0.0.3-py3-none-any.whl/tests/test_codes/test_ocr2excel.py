from pathlib import Path
from pobd.api.ocr2excel import *
from loguru import logger
import unittest
import os

base_dir = Path(__file__).resolve().parent

class Ocr2Excel(unittest.TestCase):
    """
    test for ocr2excel.py
    """

    def setUp(self):
        self.app_id = os.getenv("app_id", None)
        self.api_key = os.getenv("api_key", None)
        self.secret_key = os.getenv("secret_key", None)

    # 单个识别社保卡
    def test_social_security_card(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Social' / 'img.png'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Social'

        r = social_security_card(
            img_path=str(input_file),
            output_path=str(output_file),
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)


    # 识别离婚证
    def test_divorce_certificate(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Divorce' / 'divorce.png'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Divorce' / 'divorce_certificate.xlsx'

        r = divorce_certificate(
            img_path=str(input_file),
            output_excel_path=str(output_file),
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)

    # 识别结婚证
    def test_marriage_certificate(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Marriage' / 'marriage.png'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Marriage' / 'marriage_certificate.xlsx'

        r = divorce_certificate(
            img_path=str(input_file),
            output_excel_path=str(output_file),
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)

    # (批量)识别身份证
    def test_id_card(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Id_card'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Id_card' / 'id_card.xlsx'

        r = id_card(
            img_path=str(input_file),
            output_excel_path=str(output_file),
            app_id=self.app_id,
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)

    # 识别身份证混贴
    def test_id_card_mix(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Id_card_mix' / 'id_card_mix.png'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Id_card_mix' / 'id_card_mix.xlsx'

        r = id_card_mix(
            img_path=str(input_file),
            output_excel_path=str(output_file),
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)

    # 识别银行卡
    def test_bank_card(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'BankCard' / 'bankcard.jpg'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'BankCard' / 'bankcard.xlsx'

        r = bank_card(
            img_path=str(input_file),
            output_excel_path=str(output_file),
            app_id=self.app_id,
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)

    # 识别驾驶证
    def test_driving_license(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'DrivingLicense' / 'drive.png'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'DrivingLicense' / 'drive.xlsx'

        r = driving_license(
            img_path=str(input_file),
            output_excel_path=str(output_file),
            app_id=self.app_id,
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)

    # 识别行驶证
    def test_vehicle_license(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'VehicleLicense' / 'vehicle.jpg'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'VehicleLicense' / 'vehicle.xlsx'

        r = vehicle_license(
            img_path=str(input_file),
            output_excel_path=str(output_file),
            app_id=self.app_id,
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)

    # 文字识别(标准版)
    def test_words_identify(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Words' / '1.png'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Words' / 'words.xlsx'

        r = words_identify(
            img_path=str(input_file),
            output_excel_path=str(output_file),
            app_id=self.app_id,
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)

    # 文字识别(高精度版)
    def test_words_identify_precision(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Words' / '1.png'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'Words' / 'words.xlsx'

        r = words_identify_precision(
            img_path=str(input_file),
            output_excel_path=str(output_file),
            app_id=self.app_id,
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)

    # 增值税发票识别
    def test_vat_invoice(self):
        input_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'VatInvoice' / 'img.png'
        output_file = base_dir.parents[1] / 'tests' / 'test_files' / 'ocr' / 'VatInvoice' / 'vat.xlsx'

        r = vat_invoice(
            img_path=str(input_file),
            output_excel_path=str(output_file),
            app_id=self.app_id,
            api_key=self.api_key,
            secret_key=self.secret_key,
        )
        logger.info(r)
        self.assertTrue(r)