import os
import requests
import re
import difflib

# ==========================================
# CƠ SỞ DỮ LIỆU ĐỐI CHIẾU (CHUẨN HÓA THEO VDD)
# Format: (calo, protein, carb, fat) trên 100g
# ==========================================
NUTRIHOME_REFERENCE = {
    # ===== PROTEIN / THỊT =====
    "ức gà": (165.0, 31.0, 0.0, 3.6),
    "đùi gà": (209.0, 26.0, 0.0, 10.9),
    "cánh gà": (188.0, 19.1, 0.0, 12.4),
    "thịt gà ta": (199.0, 20.3, 0.0, 13.1),
    "thịt gà công nghiệp": (134.0, 22.9, 0.0, 4.7),
    "thịt gà": (199.0, 20.3, 0.0, 13.1),
    "thịt vịt": (267.0, 17.8, 0.0, 21.8),
    "thịt ngan": (288.0, 17.1, 0.0, 24.4),
    "thịt bò nạc": (118.0, 21.5, 0.0, 3.5),
    "thịt bò loại i": (118.0, 21.0, 0.0, 3.8),
    "thịt bò loại ii": (167.0, 18.0, 0.0, 10.5),
    "thịt bò": (167.0, 21.0, 0.0, 9.2),
    "thịt bê": (85.0, 20.0, 0.0, 0.5),
    "thịt heo nạc": (139.0, 19.0, 0.0, 7.0),
    "thịt lợn nạc": (139.0, 19.0, 0.0, 7.0),
    "thịt heo ba chỉ": (260.0, 16.5, 0.0, 21.5),
    "thịt lợn ba chỉ": (260.0, 16.5, 0.0, 21.5),
    "nửa nạc nửa mỡ": (260.0, 16.5, 0.0, 21.5),
    "thịt heo": (139.0, 19.0, 0.0, 7.0),
    "thịt lợn": (139.0, 19.0, 0.0, 7.0),
    "thịt trâu": (97.0, 20.4, 0.0, 1.4),
    "thịt dê": (122.0, 20.7, 0.0, 4.3),
    "thịt cừu": (219.0, 16.4, 0.0, 17.0),
    "thịt thỏ": (158.0, 21.5, 0.0, 8.0),
    "thịt ngựa": (176.0, 21.5, 0.0, 10.0),
    "nầm bò": (97.0, 14.8, 0.0, 4.2),           # Dạ dày bò
    "dạ dày bò": (97.0, 14.8, 0.0, 4.2),
    "dạ dày lợn": (85.0, 14.6, 0.0, 2.9),
    "gan bò": (110.0, 17.4, 4.8, 3.1),
    "gan gà": (111.0, 18.2, 0.0, 3.4),
    "gan lợn": (116.0, 18.8, 0.0, 3.6),
    "tim bò": (89.0, 15.0, 0.0, 3.0),
    "tim gà": (114.0, 16.0, 0.0, 5.5),
    "tim lợn": (94.0, 15.1, 0.0, 3.2),
    "lưỡi bò": (164.0, 13.6, 0.0, 12.1),
    "lưỡi lợn": (178.0, 14.2, 0.0, 12.8),
    "bầu dục bò": (67.0, 12.5, 0.0, 1.8),
    "bầu dục lợn": (81.0, 13.0, 0.0, 3.1),
    "mề gà": (99.0, 21.3, 0.0, 1.3),
    "phổi bò": (103.0, 15.2, 0.0, 4.7),
    "phổi lợn": (92.0, 14.8, 0.0, 3.6),
    "óc bò": (124.0, 9.0, 4.8, 9.5),
    "óc lợn": (123.0, 9.0, 0.0, 9.5),
    "tiết bò": (75.0, 18.0, 0.0, 0.2),
    "tiết lợn": (25.0, 5.7, 0.0, 0.1),
    "giò lụa": (205.0, 16.9, 0.0, 15.0),
    "chả lợn": (517.0, 10.8, 0.0, 50.4),
    "chả quế": (339.0, 18.3, 0.0, 29.0),
    "xúc xích": (535.0, 27.2, 0.0, 47.4),
    "lạp xường": (585.0, 20.8, 0.0, 55.0),
    "thịt bò khô": (239.0, 51.0, 0.0, 1.6),
    "nem chua": (125.0, 20.7, 0.0, 3.3),
    "ruốc thịt": (369.0, 46.6, 0.0, 20.3),
    
    # ===== TRỨNG =====
    "trứng gà": (166.0, 14.8, 0.5, 11.6),
    "trứng vịt": (184.0, 13.0, 1.0, 14.2),
    "trứng cút": (154.0, 13.0, 1.0, 11.1),
    "trứng chim cút": (154.0, 13.0, 1.0, 11.1),
    "lòng đỏ trứng": (327.0, 13.6, 0.5, 29.8),
    "lòng trắng trứng": (46.0, 10.3, 0.5, 0.1),
    "trứng vịt lộn": (182.0, 13.6, 1.0, 12.4),
    
    # ===== HẢI SẢN =====
    "cá lóc": (97.0, 18.2, 0.0, 2.7),
    "cá quả": (97.0, 18.2, 0.0, 2.7),
    "cá chép": (96.0, 16.0, 0.0, 3.6),
    "cá hồi": (208.0, 20.0, 0.0, 13.0),
    "cá thu": (167.0, 18.2, 0.0, 10.5),
    "cá ngừ": (87.0, 21.0, 0.0, 0.3),
    "cá rô phi": (100.0, 19.7, 0.0, 2.3),
    "cá basa": (119.0, 15.2, 0.0, 5.9),
    "cá trắm": (91.0, 17.0, 0.0, 2.6),
    "cá mè": (144.0, 15.4, 0.0, 9.1),
    "cá nục": (111.0, 20.2, 0.0, 3.3),
    "cá trê": (173.0, 16.5, 0.0, 11.9),
    "cá mối": (116.0, 22.1, 0.0, 3.1),
    "cá đối": (108.0, 19.5, 0.0, 3.3),
    "cá trích": (166.0, 17.7, 0.0, 10.6),
    "tôm": (90.0, 18.4, 0.0, 1.8),
    "tép": (90.0, 18.4, 0.0, 1.8),
    "mực": (73.0, 16.3, 0.0, 0.9),
    "cua biển": (103.0, 17.5, 0.0, 3.6),
    "cua đồng": (87.0, 12.3, 0.0, 3.3),
    "ghẹ": (54.0, 11.9, 0.0, 0.7),
    "ốc": (84.0, 11.1, 0.0, 0.7),
    "hến": (45.0, 4.5, 0.0, 0.7),
    "sò": (51.0, 8.8, 0.0, 0.4),
    "nghêu": (42.0, 5.4, 0.0, 0.4),
    "hàu": (51.0, 8.8, 0.0, 0.4),
    "lươn": (130.0, 18.4, 0.0, 1.5),
    "ếch": (90.0, 20.0, 0.0, 1.1),
    "hải sâm": (90.0, 21.5, 0.0, 0.3),
    "rươi": (89.0, 12.4, 0.0, 4.4),
    
    # ===== SỮA =====
    "sữa bò tươi": (74.0, 3.9, 4.8, 4.4),
    "sữa tươi": (74.0, 3.9, 4.8, 4.4),
    "sữa dê tươi": (69.0, 3.5, 4.8, 4.1),
    "sữa chua": (61.0, 3.3, 3.6, 3.7),
    "sữa bột toàn phần": (494.0, 27.0, 38.0, 26.0),
    "sữa bột tách béo": (357.0, 35.0, 52.0, 1.0),
    "sữa đặc có đường": (336.0, 8.1, 56.0, 8.8),
    "sữa đặc": (336.0, 8.1, 56.0, 8.8),
    "phô mai": (380.0, 25.5, 2.0, 30.9),
    "pho mát": (380.0, 25.5, 2.0, 30.9),
    
    # ===== ĐẬU / SOY =====
    "đậu phụ": (95.0, 10.9, 2.4, 5.3),
    "đậu hũ": (95.0, 10.9, 2.4, 5.3),
    "sữa đậu nành": (54.0, 3.3, 6.0, 1.8),
    "đậu nành": (418.0, 34.0, 15.0, 18.4),
    "đậu tương": (418.0, 34.0, 15.0, 18.4),
    "tào phớ": (46.0, 3.8, 2.4, 1.2),
    "bột đậu tương": (428.0, 41.0, 20.0, 18.0),
    
    # ===== TINH BỘT =====
    "cơm trắng": (130.0, 2.7, 28.2, 0.3),
    "cơm": (130.0, 2.7, 28.2, 0.3),
    "cơm rang": (198.0, 6.0, 28.2, 9.7),
    "gạo lứt": (111.0, 2.6, 23.0, 0.9),
    "gạo tẻ": (344.0, 7.9, 76.2, 1.0),
    "gạo nếp": (348.0, 8.6, 76.2, 1.5),
    "gạo": (344.0, 7.9, 76.2, 1.0),
    "bún tươi": (110.0, 1.7, 25.7, 0.1),
    "bún": (110.0, 1.7, 25.7, 0.1),
    "bánh phở": (143.0, 3.2, 32.1, 0.2),
    "phở": (143.0, 3.2, 32.1, 0.2),
    "bánh mì": (249.0, 7.9, 52.6, 0.8),
    "bánh mỳ": (249.0, 7.9, 52.6, 0.8),
    "bánh bao": (221.0, 6.1, 45.0, 0.5),
    "khoai lang": (119.0, 0.8, 28.5, 0.2),
    "khoai tây": (93.0, 2.0, 21.0, 0.1),
    "ngô ngọt": (86.0, 3.2, 19.0, 1.2),
    "ngô hạt": (354.0, 8.6, 73.9, 4.7),
    "bắp": (354.0, 8.6, 73.9, 4.7),
    "yến mạch": (389.0, 16.9, 66.3, 6.9),
    "bột mì": (347.0, 11.0, 73.0, 1.1),
    "bột gạo": (360.0, 6.6, 76.2, 0.4),
    "bột năng": (343.0, 0.7, 82.0, 0.0),
    "miến": (338.0, 0.6, 82.0, 0.1),
    "mì ăn liền": (364.0, 6.7, 55.0, 5.9),
    "mỳ ăn liền": (364.0, 6.7, 55.0, 5.9),
    
    # ===== TRÁI CÂY =====
    "chuối": (97.0, 1.5, 22.2, 0.2),
    "chuối tiêu": (100.0, 1.5, 22.2, 0.2),
    "táo": (49.0, 0.5, 11.4, 0.2),
    "cam": (37.0, 0.9, 8.3, 0.1),
    "quít": (40.0, 0.8, 8.3, 0.0),
    "xoài": (60.0, 0.6, 13.9, 0.3),
    "dưa hấu": (16.0, 1.2, 2.3, 0.2),
    "đu đủ": (35.0, 1.0, 7.7, 0.1),
    "bơ vỏ xanh": (103.0, 1.9, 0.1, 9.4),
    "bơ vỏ tím": (76.0, 1.8, 0.1, 6.2),
    "ổi": (61.0, 0.6, 14.0, 0.8),
    "nhãn": (52.0, 0.9, 13.0, 0.0),
    "vải": (49.0, 0.7, 12.0, 0.3),
    "mít": (54.0, 0.6, 13.0, 0.2),
    "nho": (71.0, 0.4, 18.0, 0.1),
    "thanh long": (47.0, 1.3, 11.0, 0.0),
    "dứa": (32.0, 0.8, 8.0, 0.0),
    "thơm": (32.0, 0.8, 8.0, 0.0),
    "dâu tây": (59.0, 1.8, 13.0, 0.4),
    "kiwi": (68.0, 1.1, 15.0, 0.5),
    "lê": (48.0, 0.7, 11.0, 0.2),
    "đào": (37.0, 0.9, 9.0, 0.2),
    "mận": (23.0, 0.6, 5.0, 0.2),
    "mơ": (50.0, 0.9, 12.0, 0.3),
    "hồng": (48.0, 0.9, 12.0, 0.0),
    "sầu riêng": (138.0, 2.5, 28.0, 1.6),
    "măng cầu": (58.0, 1.8, 14.0, 0.2),
    "mãng cầu": (58.0, 1.8, 14.0, 0.2),
    
    # ===== RAU CỦ =====
    "rau muống": (23.0, 3.2, 2.5, 0.0),
    "rau ngót": (35.0, 5.3, 3.4, 0.0),
    "mồng tơi": (14.0, 2.0, 1.4, 0.0),
    "cải bó xôi": (23.0, 2.9, 3.6, 0.4),
    "cà chua": (15.0, 0.6, 3.0, 0.0),
    "cà rốt": (39.0, 1.5, 8.8, 0.2),
    "bí đỏ": (27.0, 0.9, 5.6, 0.1),
    "bí xanh": (16.0, 0.6, 3.0, 0.0),
    "bí đao": (16.0, 0.6, 3.0, 0.0),
    "cải bắp": (25.0, 1.8, 5.4, 0.1),
    "cải thảo": (14.0, 0.9, 2.8, 0.0),
    "cải ngọt": (17.0, 1.4, 3.0, 0.1),
    "cải xanh": (23.0, 1.7, 4.0, 0.1),
    "su hào": (44.0, 2.8, 9.0, 0.1),
    "củ cải trắng": (27.0, 1.5, 5.5, 0.1),
    "củ cải đỏ": (52.0, 1.3, 11.0, 0.0),
    "hành tây": (45.0, 1.8, 10.0, 0.1),
    "hành lá": (26.0, 1.3, 5.0, 0.0),
    "hành củ": (29.0, 1.3, 6.0, 0.3),
    "tỏi": (126.0, 6.0, 28.0, 0.3),
    "gừng": (41.0, 0.4, 9.0, 0.5),
    "nấm hương": (51.0, 5.5, 8.0, 0.5),
    "nấm rơm": (61.0, 3.6, 8.0, 3.2),
    "nấm mỡ": (37.0, 4.0, 5.0, 0.3),
    "măng tây": (24.0, 2.2, 4.0, 0.1),
    "mướp": (18.0, 0.9, 3.5, 0.1),
    "mướp đắng": (20.0, 0.9, 4.0, 0.0),
    "bầu": (18.0, 0.6, 3.5, 0.0),
    "dọc mùng": (13.0, 0.4, 2.5, 0.0),
    "giá đậu": (52.0, 5.5, 10.0, 0.1),
    "đậu cô ve": (77.0, 5.0, 15.0, 0.0),
    "đậu đũa": (67.0, 6.0, 13.0, 0.3),
    "đậu hà lan": (75.0, 6.5, 14.0, 0.3),
    "súp lơ": (34.0, 2.5, 6.0, 0.1),
    "cần tây": (54.0, 3.7, 10.0, 0.2),
    "ngó sen": (65.0, 1.0, 14.0, 0.1),
    "hạt sen": (164.0, 9.5, 34.0, 0.5),
    
    # ===== CHẤT BÉO / HẠT =====
    "dầu ăn": (900.0, 0.0, 0.0, 100.0),
    "dầu oliu": (900.0, 0.0, 0.0, 100.0),
    "dầu cám": (900.0, 0.0, 0.0, 100.0),
    "dầu cọ": (900.0, 0.0, 0.0, 100.0),
    "dầu dừa": (900.0, 0.0, 0.0, 100.0),
    "dầu mè": (900.0, 0.0, 0.0, 100.0),
    "dầu lạc": (900.0, 0.0, 0.0, 100.0),
    "dầu đậu tương": (900.0, 0.0, 0.0, 100.0),
    "dầu ngô": (900.0, 0.0, 0.0, 100.0),
    "dầu bông": (900.0, 0.0, 0.0, 100.0),
    "dầu hỗn hợp": (897.0, 0.0, 0.0, 99.7),
    "mỡ lợn": (896.0, 0.0, 0.0, 99.6),
    "bơ thực vật": (729.0, 0.5, 0.1, 80.7),
    "bơ": (717.0, 0.8, 0.1, 81.0),
    "đậu phộng": (573.0, 27.5, 15.5, 44.5),
    "lạc": (573.0, 27.5, 15.5, 44.5),
    "hạt điều": (553.0, 18.2, 30.2, 43.8),
    "óc chó": (654.0, 15.2, 13.7, 65.2),
    "hạnh nhân": (579.0, 21.1, 21.6, 49.9),
    "mè": (568.0, 20.1, 14.1, 46.4),
    "vừng": (568.0, 20.1, 14.1, 46.4),
    "hạt dẻ": (363.0, 6.8, 70.0, 1.8),
    "hạt bí": (528.0, 35.1, 5.6, 31.8),
    "hạt hướng dương": (652.0, 21.6, 11.0, 53.6),
    "macca": (767.0, 7.8, 14.0, 76.1),
    "hạt dẻ cười": (610.0, 21.1, 21.0, 45.8),
    
    # ===== GIA VỊ / KHÁC =====
    "nước mắm": (35.0, 5.1, 0.0, 0.0),
    "mắm tôm": (73.0, 14.8, 0.0, 1.5),
    "xì dầu": (55.0, 6.3, 8.0, 0.0),
    "nước tương": (55.0, 6.3, 8.0, 0.0),
    "dầu hào": (73.0, 2.9, 15.0, 0.3),
    "tương ớt": (41.0, 0.5, 9.0, 0.5),
    "giấm": (21.0, 0.0, 5.0, 0.0),
    "đường cát": (383.0, 1.1, 99.0, 0.0),
    "đường kính": (397.0, 0.0, 99.0, 0.0),
    "mật ong": (327.0, 0.4, 82.0, 0.0),
    "muối": (1.0, 0.0, 0.0, 0.0),
    "hạt tiêu": (365.0, 7.0, 64.0, 7.4),
    "mì chính": (282.0, 0.0, 60.0, 0.0),
    "bột ngọt": (282.0, 0.0, 60.0, 0.0),
    "bột canh": (62.2, 1.1, 12.0, 0.0),
    "bột nêm": (188.0, 12.7, 30.0, 1.8),
}


# ==========================================
# HÀM CHUẨN HÓA / ĐỐI CHIẾU / RECONCILE
# ==========================================

def parse_num(val):
    if val is None or val == "": return 0.0
    if isinstance(val, (int, float)): return float(val)
    if isinstance(val, dict): val = val.get("value", 0.0)
    try:
        cleaned_str = str(val).replace(",", ".").strip()
        match = re.search(r"[-+]?\d*\.\d+|\d+", cleaned_str)
        if match: return float(match.group())
        return float(cleaned_str)
    except (ValueError, TypeError):
        return 0.0


def flatten_nutrition(food_item):
    flat_data = {}
    
    def extract_deep(data):
        if isinstance(data, dict):
            n_key = data.get("name", data.get("ten", data.get("nutrient", "")))
            v_key = data.get("value", data.get("giaTri", data.get("amount", "")))
            if n_key and v_key is not None and isinstance(n_key, str):
                flat_data[n_key.lower().strip()] = v_key
            for k, v in data.items():
                if isinstance(v, (dict, list)): extract_deep(v)
                else: flat_data[str(k).lower().strip()] = v
        elif isinstance(data, list):
            for item in data: extract_deep(item)
    
    extract_deep(food_item)
    
    def find_val(*possible_keys):
        for key in possible_keys:
            if key in flat_data: return flat_data[key]
        for key in possible_keys:
            for k, v in flat_data.items():
                if key in k: return v
        return 0.0
    
    cal  = parse_num(find_val('energy', 'nangluong', 'năng lượng', 'calo', 'kcal'))
    pro  = parse_num(find_val('protein', 'protid', 'protide', 'dam', 'đạm'))
    carb = parse_num(find_val('carbohydrate', 'glucid', 'glucide', 'carb', 'tinhbot', 'tinh bột'))
    fat  = parse_num(find_val('lipid', 'lipide', 'fat', 'beo', 'béo'))
    return round(cal, 1), round(pro, 1), round(carb, 1), round(fat, 1)


def reconcile_macros(cal, pro, carb, fat):
    """
    Đảm bảo: calories ≈ 4*pro + 4*carb + 9*fat
    - Nếu khớp (sai số ≤ 15%) -> giữ nguyên
    - Nếu lệch -> ước lượng macro còn thiếu (đặc biệt khi carb = 0)
    - Cuối cùng LUÔN tính calo từ macro để đảm bảo khớp 100%
    """
    # Không có calo và không có macro -> trả 0
    if cal <= 0 and pro <= 0 and carb <= 0 and fat <= 0:
        return 0.0, 0.0, 0.0, 0.0
    
    # Không có macro nào nhưng có calo -> coi toàn bộ là carb
    if pro <= 0 and carb <= 0 and fat <= 0:
        if cal > 0:
            return round(cal, 1), 0.0, round(cal / 4.0, 1), 0.0
        return 0.0, 0.0, 0.0, 0.0
    
    cal_from_macro = 4 * pro + 4 * carb + 9 * fat
    
    # Nếu không có calo gốc -> dùng calo từ macro
    if cal <= 0:
        return round(cal_from_macro, 1), round(pro, 1), round(carb, 1), round(fat, 1)
    
    # Nếu calo khớp (sai số ≤ 15%) -> giữ nguyên calo gốc
    if abs(cal - cal_from_macro) <= 0.15 * cal:
        return round(cal, 1), round(pro, 1), round(carb, 1), round(fat, 1)
    
    # Calo lệch nhiều -> cố gắng thêm macro còn thiếu
    n_macro = sum(1 for m in (pro, carb, fat) if m > 0)
    
    if n_macro == 1:
        # Chỉ có 1 macro -> chia phần còn lại cho carb + fat theo tỉ lệ 50/50
        if pro > 0:
            remaining = cal - 4 * pro
            if remaining > 0:
                carb = remaining / 8.0          # 1/2 cho carb (4 kcal/g)
                fat  = remaining / 18.0         # 1/2 cho fat (9 kcal/g)
        elif fat > 0:
            remaining = cal - 9 * fat
            if remaining > 0:
                carb = remaining / 4.0
        elif carb > 0:
            remaining = cal - 4 * carb
            if remaining > 0:
                fat = remaining / 9.0
    elif n_macro == 2:
        # Thiếu đúng 1 macro -> ước lượng macro còn thiếu
        if carb <= 0:
            est = (cal - 4 * pro - 9 * fat) / 4.0
            if est > 0: carb = est
        elif pro <= 0:
            est = (cal - 4 * carb - 9 * fat) / 4.0
            if est > 0: pro = est
        elif fat <= 0:
            est = (cal - 4 * pro - 4 * carb) / 9.0
            if est > 0: fat = est
    # n_macro == 3: cả 3 macro đều có mà calo lệch -> ta tin macro hơn, tính lại calo
    
    cal_final = 4 * pro + 4 * carb + 9 * fat
    return round(cal_final, 1), round(pro, 1), round(carb, 1), round(fat, 1)


def cross_reference_nutrihome(name, api_cal, api_pro, api_carb, api_fat):
    """
    Luôn đối chiếu reference. Nếu match, dùng reference để BỔ SUNG
    các giá trị API trả về 0.
    """
    name_lower = str(name).lower().strip()
    matched_key = None
    
    # 1. Substring match với key dài nhất
    sorted_keys = sorted(NUTRIHOME_REFERENCE.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key in name_lower:
            matched_key = key
            break
    
    # 2. Fuzzy match nếu chưa có
    if not matched_key:
        close = difflib.get_close_matches(name_lower, NUTRIHOME_REFERENCE.keys(), n=1, cutoff=0.75)
        if close:
            matched_key = close[0]
    
    if not matched_key:
        return api_cal, api_pro, api_carb, api_fat
    
    ref_cal, ref_pro, ref_carb, ref_fat = NUTRIHOME_REFERENCE[matched_key]
    
    # Bổ sung từng field nếu API trả về 0
    final_cal  = api_cal  if api_cal  > 0 else ref_cal
    final_pro  = api_pro  if api_pro  > 0 else ref_pro
    final_carb = api_carb if api_carb > 0 else ref_carb
    final_fat  = api_fat  if api_fat  > 0 else ref_fat
    
    # Nếu API trả carb > 30 cho món rau/củ (rõ ràng sai) -> dùng reference
    veg_kw = ['rau', 'cải', 'bắp cải', 'su hào', 'củ cải', 'bí ', 'bầu', 'mướp',
              'cà chua', 'cà rốt', 'nấm', 'măng', 'giá đỗ', 'giá đậu']
    if any(kw in name_lower for kw in veg_kw):
        if final_carb > 30 and ref_carb < 30:
            final_carb = ref_carb
            final_cal  = ref_cal
            final_pro  = ref_pro
            final_fat  = ref_fat
    
    return final_cal, final_pro, final_carb, final_fat


# ==========================================
# PHÂN LOẠI, ĐƠN VỊ, DỊ ỨNG
# ==========================================

LIQUID_KEYWORDS = [
    'nước', 'sữa tươi', 'sữa bò', 'sữa dê', 'dầu', 'mắm', 'rượu', 'bia',
    'trà', 'cà phê', 'cafe', 'giấm', 'xì dầu', 'nước tương', 'dầu hào',
    'nước sốt', 'nước ép', 'nước cốt', 'nước dùng', 'nước canh', 'nước hầm'
]
SOLID_DAIRY = ['sữa bột', 'sữa đặc', 'sữa chua', 'phô mai', 'pho mát', 'váng sữa']


def detect_unit(name, category):
    name_lower = str(name).lower()
    
    # Ưu tiên các ngoại lệ rắn
    for kw in SOLID_DAIRY:
        if kw in name_lower:
            return '100g'
    
    for kw in LIQUID_KEYWORDS:
        if re.search(rf'\b{re.escape(kw)}\b', name_lower):
            return '100ml'
    
    return '100g'


def analyze_and_normalize(name):
    clean_name = re.sub(r'[^\w\s]', ' ', str(name).lower())
    
    def has_word(word_list):
        for w in word_list:
            if re.search(rf'\b{re.escape(w)}\b', clean_name):
                return True
        return False
    
    category = 'other'
    price = 5000
    allergens = set()
    
    # ---- 1. SỮA (dairy) ----
    if has_word(['sữa', 'phô mai', 'pho mát', 'yogurt', 'váng sữa']):
        if not has_word(['đậu nành', 'dừa', 'gạo', 'yến mạch', 'hạt']):
            category = 'dairy'
            allergens.add('dairy')
            price = 35000 if 'bột' in clean_name else 6000
    
    # ---- 2. ĐỒ UỐNG ----
    elif has_word(['nước', 'bia', 'rượu', 'trà', 'cà phê', 'cafe', 'giải khát']):
        category = 'drink'
        price = 15000 if has_word(['bia', 'rượu']) else 10000
    
    # ---- 3. PROTEIN (thịt) ----
    elif has_word(['bò', 'bê']) and not has_word(['khô', 'bánh', 'kẹo']):
        category = 'protein'; price = 28000
    elif has_word(['lợn', 'heo', 'giò', 'chả', 'nầm']) and not has_word(['bánh', 'rau', 'kẹo']):
        category = 'protein'; price = 15000
    elif has_word(['gà', 'vịt', 'chim', 'ngan', 'ngỗng']) and not has_word(['bánh', 'kẹo', 'trứng']):
        category = 'protein'; price = 8000
    elif has_word(['trâu', 'dê', 'cừu', 'thỏ']) and not has_word(['bánh', 'kẹo']):
        category = 'protein'; price = 25000
    
    # ---- Trứng ----
    if has_word(['trứng']) and not has_word(['hoa', 'bánh', 'kẹo']):
        category = 'protein'; price = 3500
        allergens.add('egg')
    
    # ---- Hải sản ----
    if has_word(['cá', 'tôm', 'tép', 'cua', 'mực', 'ốc', 'hàu', 'hến',
                 'nghêu', 'sò', 'ghẹ', 'lươn', 'ếch', 'hải sản']):
        if not has_word(['bánh', 'kẹo', 'mắm']):
            category = 'protein'; price = 25000
            allergens.add('seafood')
    
    # ---- Đậu nành ----
    if has_word(['đậu phụ', 'đậu hũ', 'đậu nành', 'đậu tương',
                 'tương bần', 'tương hột', 'tào phớ']):
        if not has_word(['tương ớt', 'tương cà']):
            category = 'protein'; price = 4000
            allergens.add('soy')
    
    # ---- 4. TINH BỘT ----
    elif has_word(['gạo', 'cơm', 'cháo', 'xôi', 'nếp', 'cốm']):
        category = 'carb'; price = 3000
    elif has_word(['khoai', 'sắn', 'ngô', 'bắp', 'củ']):
        category = 'carb'; price = 2500
    elif has_word(['bún', 'phở', 'miến', 'mì', 'hủ tiếu']):
        category = 'carb'; price = 4000
        if has_word(['mì']): allergens.add('gluten')
    
    # ---- Bánh mì / gluten ----
    if has_word(['bánh mì', 'bánh mỳ', 'bột mì', 'lúa mì', 'bánh bao',
                 'bánh quy', 'bánh ngọt', 'bánh bông lan', 'yến mạch']):
        category = 'carb'; price = 15000
        allergens.add('gluten')
    elif has_word(['bánh']) and category == 'other':
        category = 'carb'; price = 10000
    
    # ---- 5. CHẤT BÉO ----
    if has_word(['dầu', 'mỡ']):
        category = 'fat'
        price = 15000
    
    if has_word(['bơ']) and not has_word(['sữa', 'quả']):
        category = 'fat'; price = 20000
    
    if has_word(['lạc', 'đậu phộng']):
        category = 'fat'; price = 8000
        allergens.add('peanut')
    
    if has_word(['hạnh nhân', 'óc chó', 'hạt điều', 'mắc ca',
                 'hạt dẻ', 'hạt bí', 'hạt hướng dương']):
        category = 'fat'; price = 35000
        allergens.add('nuts')
    
    if has_word(['mè', 'vừng']):
        category = 'fat'; price = 12000
        allergens.add('sesame')
    
    # ---- 6. RAU CỦ ----
    if category == 'other' and has_word(['rau', 'cải', 'nấm', 'cà chua', 'cà rốt',
                                          'bí', 'bầu', 'mướp', 'su hào', 'măng',
                                          'giá', 'củ', 'hành', 'tỏi', 'gừng']):
        category = 'vegetable'; price = 2500
    
    # ---- 7. TRÁI CÂY ----
    if category == 'other' and has_word(['chuối', 'táo', 'cam', 'xoài', 'bưởi',
                                          'dưa', 'ổi', 'nhãn', 'vải', 'mít',
                                          'đu đủ', 'quả', 'trái', 'nho', 'lê',
                                          'đào', 'mận', 'mơ', 'hồng']):
        category = 'fruit'; price = 5000
    
    # ---- 8. GIA VỊ ----
    if category == 'other' and has_word(['muối', 'đường', 'tiêu', 'mắm',
                                          'giấm', 'bột ngọt', 'hạt nêm',
                                          'tương ớt', 'tương cà', 'nước tương']):
        category = 'spice'; price = 4000
        if has_word(['mắm']):
            allergens.add('seafood')
    
    # ---- PRICE OVERRIDE ----
    PRICE_OVERRIDES = {
        'bánh cá': 25000, 'đường cát': 2500, 'đường phèn': 3500,
        'tương ớt': 15000, 'tương cà': 15000, 'nước tương': 12000,
        'nước mắm': 30000, 'dầu oliu': 45000, 'sữa chua': 7000,
        'cá hồi': 45000, 'bào ngư': 150000, 'yến sào': 500000,
    }
    for k, v in PRICE_OVERRIDES.items():
        if k in clean_name:
            price = v
    
    unit = detect_unit(name, category)
    allergen_str = '{' + ','.join(sorted(allergens)) + '}' if allergens else '{}'
    return category, price, unit, allergen_str


# ==========================================
# SINH FILE SQL
# ==========================================

def generate_final_sql():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_filename = os.path.join(os.path.dirname(script_dir), "seed.sql")
    
    print("Đang tải dữ liệu và đối chiếu đa nguồn...")
    api_url = ("https://viendinhduong.vn/api/fe/foodNatunal/getPageFoodData"
               "?page=1&pageSize=853&energy=0&categories=")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"❌ Lỗi API: HTTP {response.status_code}")
            return
        
        res_json = response.json()
        if isinstance(res_json, list) and res_json:
            food_list = res_json[0].get("data", [])
        elif isinstance(res_json, dict):
            data_field = res_json.get("data", {})
            food_list = data_field.get("data", []) if isinstance(data_field, dict) else data_field
        else:
            food_list = []
        
        if not food_list and isinstance(res_json, dict) and 'data' in res_json:
            food_list = res_json['data']
        
        valid_foods = []
        for f in food_list:
            if not isinstance(f, dict): continue
            name = f.get('name_vi') or f.get('TenThucPham') or f.get('name') or f.get('foodName')
            if name:
                f['_extracted_name'] = name
                valid_foods.append(f)
        
        print(f"-> Thu nhận {len(valid_foods)} món. Đang xử lý...")
        
        grouped = {k: [] for k in
                   ['protein', 'carb', 'fat', 'dairy', 'vegetable',
                    'fruit', 'drink', 'spice', 'other']}
        
        stats = {'fixed_cal': 0, 'fixed_carb': 0, 'total': 0}
        
        for food in valid_foods:
            raw_name = str(food['_extracted_name']).strip()
            name = raw_name.replace("'", "''")
            
            category, price, unit, allergen = analyze_and_normalize(raw_name)
            
            api_cal, api_pro, api_carb, api_fat = flatten_nutrition(food)
            
            # 1) Bổ sung từ reference
            cal, pro, carb, fat = cross_reference_nutrihome(
                raw_name, api_cal, api_pro, api_carb, api_fat
            )
            
            # 2) Reconcile để calo = 4P + 4C + 9F
            old_cal, old_carb = cal, carb
            cal, pro, carb, fat = reconcile_macros(cal, pro, carb, fat)
            
            stats['total'] += 1
            if abs(cal - old_cal) > 1.0: stats['fixed_cal'] += 1
            if abs(carb - old_carb) > 1.0: stats['fixed_carb'] += 1
            
            line = (f"('{name}', '{category}', {price}, '{unit}', "
                    f"{cal:.1f}, {pro:.1f}, {carb:.1f}, {fat:.1f}, '{allergen}')")
            grouped[category].append(line)
        
        # Ghi file
        with open(sql_filename, mode='w', encoding='utf-8') as f:
            f.write("INSERT INTO foods "
                    "(name, category, price_per_unit, unit, calories, "
                    "protein, carbs, fat, allergen_tags) VALUES\n")
            total = sum(len(v) for v in grouped.values())
            cur = 0
            for cat, items in grouped.items():
                if not items: continue
                f.write(f"\n-- {cat.capitalize()}\n")
                for line in items:
                    cur += 1
                    f.write(line + (";\n" if cur == total else ",\n"))
        
        print(f"✅ HOÀN TẤT! Đã ghi '{os.path.basename(sql_filename)}'")
        print(f"   Tổng số món: {stats['total']}")
        print(f"   Số dòng được chỉnh calo: {stats['fixed_cal']}")
        print(f"   Số dòng được bổ sung carb: {stats['fixed_carb']}")
    
    except Exception as e:
        print(f"❌ Lỗi khi thực thi: {e}")


if __name__ == "__main__":
    generate_final_sql()