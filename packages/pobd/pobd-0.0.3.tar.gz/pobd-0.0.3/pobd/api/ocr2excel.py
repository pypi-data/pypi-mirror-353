import pandas as pd
import copy

from pathlib import Path
from pobd.core.Baidu import BaiduOCR
from pofile import get_files, mkdir
from poprogress import simple_progress
from loguru import logger


# 验证输入参数
def verify_path(img_path, output_path=r'./', output_excel_path='social_security_card.xlsx', doc_name=None):
    vat_img_files = get_files(img_path)
    if vat_img_files == None:
        raise BaseException(f'{img_path}这个文件目录下，没有存放任何{doc_name}，请确认后重新运行')
    mkdir(Path(output_path).absolute())  # 如果不存在，则创建输出目录
    if output_excel_path.endswith('.xlsx') or output_excel_path.endswith('xls'):  # 如果指定的输出excel结尾不正确，则报错退出
        abs_output_excel = Path(output_path).absolute() / output_excel_path
    else:  # 指定了，但不是xlsx或者xls结束
        raise BaseException(
            f'输出结果名：output_excel参数，必须以xls或者xlsx结尾，您的输入:{output_excel_path}有误，请修改后重新运行')
    return vat_img_files, abs_output_excel


# 保存到excel
def to_excel(result_df, abs_output_excel):
    if len(result_df) > 0:
        df = pd.DataFrame(result_df)
        df.to_excel(str(abs_output_excel), index=False, engine='openpyxl')
        logger.info(f'识别结果已保存到：{abs_output_excel}')
        return True
    else:
        logger.error(f'该文件夹下，没有任何符合条件的文件')
        return False

# 通用处理
def process_document(img_path=None, output_path=None, output_excel_path=None, app_id=None, api_key=None, secret_key=None, ocr_func=None, extract_func=None, doc_name='文件'):

    vat_img_files, abs_output_excel = verify_path(img_path, output_path, output_excel_path, doc_name)
    baidu_ocr = BaiduOCR(app_id, api_key, secret_key)

    result_df = []
    for img in simple_progress(vat_img_files):
        ocr_result = ocr_func(baidu_ocr, img)          # 控制调用百度的接口

        words = ocr_result.get('words_result', {})
        if len(words) == 0:
            words = ocr_result.get('result', {})

        data = extract_func(words)
        result_df.append(data)

    return to_excel(result_df, abs_output_excel)

# 社保卡识别
def social_security_card(img_path, output_path=r'./', output_excel_path='social_security_card.xlsx', api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.social_security_card(img),      # 控制调用百度的接口
        extract_func=extract_social_security_card,
        doc_name='社保卡'
    )


def extract_social_security_card(words):
    return {
        '姓名': words.get('name', {}).get('word', ''),
        '社保号码': words.get('social_security_number', {}).get('word', ''),
        '卡号': words.get('card_number', {}).get('word', ''),
        '银行账号': words.get('bank_card_number', {}).get('word', ''),
        '签发日期': words.get('issue_date', {}).get('word', '')
    }

# 离婚证识别
def divorce_certificate(img_path, output_path=r'./', output_excel_path='divorce_certificate.xlsx', api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.divorce_certificate(img),
        extract_func=extract_divorce_certificate,
        doc_name='离婚证'
    )

def extract_divorce_certificate(words):
    return {
        '男_姓名': words.get('姓名_男', [{}])[0].get('word', ''),
        '男_身份证号': words.get('身份证件号_男', [{}])[0].get('word', ''),
        '男_出生日期': words.get('出生日期_男', [{}])[0].get('word', ''),
        '男_国籍': words.get('国籍_男', [{}])[0].get('word', ''),
        '男_性别': words.get('性别_男', [{}])[0].get('word', ''),
        '女_姓名': words.get('姓名_女', [{}])[0].get('word', ''),
        '女_身份证号': words.get('身份证件号_女', [{}])[0].get('word', ''),
        '女_出生日期': words.get('出生日期_女', [{}])[0].get('word', ''),
        '女_国籍': words.get('国籍_女', [{}])[0].get('word', ''),
        '女_性别': words.get('性别_女', [{}])[0].get('word', ''),
        '登记日期': words.get('登记日期', [{}])[0].get('word', ''),
        '离婚证字号': words.get('离婚证字号', [{}])[0].get('word', ''),
        '持证人': words.get('持证人', [{}])[0].get('word', ''),
        '备注': words.get('备注', [{}])[0].get('word', '')
    }

# 结婚证识别
def marriage_certificate(img_path, output_path=r'./', output_excel_path='marriage_certificate.xlsx', api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.marriage_certificate(img),
        extract_func=extract_marriage_certificate,
        doc_name='结婚证'
    )

def extract_marriage_certificate(words):
    return {
            "姓名_男": words.get("姓名_男", [{}])[0].get("word", ""),
            "身份证件号_男": words.get("身份证件号_男", [{}])[0].get("word", ""),
            "出生日期_男": words.get("出生日期_男", [{}])[0].get("word", ""),
            "国籍_男": words.get("国籍_男", [{}])[0].get("word", ""),
            "性别_男": words.get("性别_男", [{}])[0].get("word", ""),
            "姓名_女": words.get("姓名_女", [{}])[0].get("word", ""),
            "身份证件号_女": words.get("身份证件号_女", [{}])[0].get("word", ""),
            "出生日期_女": words.get("出生日期_女", [{}])[0].get("word", ""),
            "国籍_女": words.get("国籍_女", [{}])[0].get("word", ""),
            "性别_女": words.get("性别_女", [{}])[0].get("word", ""),
            "结婚证字号": words.get("结婚证字号", [{}])[0].get("word", ""),
            "持证人": words.get("持证人", [{}])[0].get("word", ""),
            "登记日期": words.get("登记日期", [{}])[0].get("word", ""),
            "备注": words.get("备注", [{}])[0].get("word", "")
        }

# 身份证识别
def id_card(img_path, output_path=r'./', output_excel_path='id_card.xlsx', app_id=None, api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        app_id=app_id,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.id_card(img),
        extract_func=extract_id_card,
        doc_name='身份证'
    )

def extract_id_card(words):
    return {
            "姓名": words.get("姓名", {}).get("words", ""),
            "性别": words.get("性别", {}).get("words", ""),
            "民族": words.get("民族", {}).get("words", ""),
            "出生": words.get("出生", {}).get("words", ""),
            "住址": words.get("住址", {}).get("words", ""),
            "公民身份号码": words.get("公民身份号码", {}).get("words", "")
        }


# 身份证混贴识别
def id_card_mix(img_path, output_path=r'./', output_excel_path='id_card_mix.xlsx', api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.id_card_mix(img),
        extract_func=extract_id_card_mix,
        doc_name='身份证混贴'
    )

def extract_id_card_mix(words):
    data = {
        "姓名": "",
        "性别": "",
        "民族": "",
        "出生": "",
        "住址": "",
        "公民身份号码": "",
        "签发机关": "",
        "签发日期": "",
        "失效日期": ""
    }

    for card in words:
        card_type = card.get("card_info", {}).get("card_type")
        card_result = card.get("card_result", {})

        if card_type == "idcard_front":
            data["姓名"] = card_result.get("姓名", {}).get("words", "")
            data["性别"] = card_result.get("性别", {}).get("words", "")
            data["民族"] = card_result.get("民族", {}).get("words", "")
            data["出生"] = card_result.get("出生", {}).get("words", "")
            data["住址"] = card_result.get("住址", {}).get("words", "")
            data["公民身份号码"] = card_result.get("公民身份号码", {}).get("words", "")

        elif card_type == "idcard_back":
            data["签发机关"] = card_result.get("签发机关", {}).get("words", "")
            data["签发日期"] = card_result.get("签发日期", {}).get("words", "")
            data["失效日期"] = card_result.get("失效日期", {}).get("words", "")

    return data


# 银行卡识别
def bank_card(img_path, output_path=r'./', output_excel_path='bank_card.xlsx', app_id=None, api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        app_id=app_id,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.bank_card(img),
        extract_func=extract_bank_card,
        doc_name='银行卡'
    )

def extract_bank_card(words):
    # 0：不能识别; 1：借记卡; 2：贷记卡（原信用卡大部分为贷记卡）; 3：准贷记卡; 4：预付费卡
    card_type = {0: "不能识别", 1: "借记卡", 2: "贷记卡", 3: "准贷记卡", 4: "预付费卡"}
    return {
        "有效期": words['valid_date'],
        "银行卡号": words['bank_card_number'],
        "银行名称": words['bank_name'],
        "银行卡类型": card_type[words['bank_card_type']],
        "持卡人姓名": words['holder_name'],
    }

# 驾驶证识别
def driving_license(img_path, output_path=r'./', output_excel_path='driving_license.xlsx', app_id=None, api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        app_id=app_id,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.driving_license(img),
        extract_func=extract_driving_license,
        doc_name='驾驶证'
    )

def extract_driving_license(words):
    return {
            "姓名": words.get("姓名", {}).get("words", ""),
            "至": words.get("至", {}).get("words", ""),
            "出生日期": words.get("出生日期", {}).get("words", ""),
            "证号": words.get("证号", {}).get("words", ""),
            "住址": words.get("住址", {}).get("words", ""),
            "发证单位": words.get("发证单位", {}).get("words", ""),
            "初次领证日期": words.get("初次领证日期", {}).get("words", ""),
            "国籍": words.get("国籍", {}).get("words", ""),
            "准驾车型": words.get("准驾车型", {}).get("words", ""),
            "性别": words.get("性别", {}).get("words", ""),
            "有效期限": words.get("有效期限", {}).get("words", ""),
        }

# 行驶证识别
def vehicle_license(img_path, output_path=r'./', output_excel_path='vehicle_license.xlsx', app_id=None, api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        app_id=app_id,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.vehicle_license(img),
        extract_func=extract_vehicle_license,
        doc_name='行驶证'
    )

def extract_vehicle_license(words):
    return {
            "车辆识别代号": words.get("车辆识别代号", {}).get("words", ""),
            "住址": words.get("住址", {}).get("words", ""),
            "发证单位": words.get("发证单位", {}).get("words", ""),
            "发证日期": words.get("发证日期", {}).get("words", ""),
            "品牌型号": words.get("品牌型号", {}).get("words", ""),
            "车辆类型": words.get("车辆类型", {}).get("words", ""),
            "所有人": words.get("所有人", {}).get("words", ""),
            "使用性质": words.get("使用性质", {}).get("words", ""),
            "发动机号码": words.get("发动机号码", {}).get("words", ""),
            "号牌号码": words.get("号牌号码", {}).get("words", ""),
            "注册日期": words.get("注册日期", {}).get("words", ""),
        }

# 文字识别
def words_identify(img_path, output_path=r'./', output_excel_path='words.xlsx', app_id=None, api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        app_id=app_id,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.words_identify(img),
        extract_func=extract_words_identify,
        doc_name='文字识别（标准版）'
    )

def extract_words_identify(words):
    data = {}
    for i in range(len(words)):
        data[i] = words[i]['words']

    return data

# 文字识别（高精度版）
def words_identify_precision(img_path, output_path=r'./', output_excel_path='words.xlsx', app_id=None, api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        app_id=app_id,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.words_identify_precision(img),
        extract_func=extract_words_identify_precision,
        doc_name='文字识别（高精度版）'
    )

def extract_words_identify_precision(words):
    data = {}
    for i in range(len(words)):
        data[i] = words[i]['words']

    return data

# 增值税发票识别
def vat_invoice(img_path, output_path=r'./', output_excel_path='words.xlsx', app_id=None, api_key=None, secret_key=None):
    return process_document(
        img_path=img_path,
        output_path=output_path,
        output_excel_path=output_excel_path,
        app_id=app_id,
        api_key=api_key,
        secret_key=secret_key,
        ocr_func=lambda ocr, img: ocr.vat_invoice(img),
        extract_func=extract_vat_invoice,
        doc_name='增值税发票识别'
    )

def extract_vat_invoice(words_result):
    return {
        "发票代码": words_result.get("InvoiceCode", ""),
        "发票号码": words_result.get("InvoiceNum", ""),
        "开票日期": words_result.get("InvoiceDate", ""),
        "销售方名称": words_result.get("SellerName", ""),
        "销售方纳税人识别号": words_result.get("SellerRegisterNum", ""),
        "销售方地址": words_result.get("SellerAddress", ""),
        "销售方开户行及账号": words_result.get("SellerBank", ""),
        "购买方名称": words_result.get("PurchaserName", ""),
        "购买方纳税人识别号": words_result.get("PurchaserRegisterNum", ""),
        "商品名称": words_result.get("CommodityName", [{}])[0].get("word", "") if words_result.get("CommodityName") else "",
        "商品数量": words_result.get("CommodityNum", [{}])[0].get("word", "") if words_result.get("CommodityNum") else "",
        "商品单价": words_result.get("CommodityPrice", [{}])[0].get("word", "") if words_result.get("CommodityPrice") else "",
        "商品金额": words_result.get("CommodityAmount", [{}])[0].get("word", "") if words_result.get("CommodityAmount") else "",
        "商品税率": words_result.get("CommodityTaxRate", [{}])[0].get("word", "") if words_result.get("CommodityTaxRate") else "",
        "商品税额": words_result.get("CommodityTax", [{}])[0].get("word", "") if words_result.get("CommodityTax") else "",
        "总金额": words_result.get("TotalAmount", ""),
        "总税额": words_result.get("TotalTax", ""),
        "价税合计": words_result.get("AmountInFiguers", ""),
        "价税合计大写": words_result.get("AmountInWords", ""),
        "开票人": words_result.get("NoteDrawer", ""),
        "收款人": words_result.get("Payee", ""),
        "复核人": words_result.get("Checker", ""),
        "密码区": words_result.get("Password", ""),
        "机器编号": words_result.get("MachineCode", ""),
        "发票类型": words_result.get("InvoiceType", ""),
        "发票原始类型": words_result.get("InvoiceTypeOrg", ""),
        "备注": words_result.get("Remarks", ""),
        "服务类型": words_result.get("ServiceType", ""),
        "是否代开": words_result.get("Agent", ""),
        "发票标签": words_result.get("InvoiceTag", ""),
        "校验码": words_result.get("CheckCode", ""),
        "发票代码确认": words_result.get("InvoiceCodeConfirm", ""),
        "发票号码确认": words_result.get("InvoiceNumConfirm", ""),
    }
