
import os

"""
Shared constants for backend services.

This module consolidates railway lists, mappings, and other constants
that are used across multiple services.
"""

# ==============================================================================
# Operators
# ==============================================================================
OPERATOR_JR_EAST = "odpt.Operator:JR-East"
OPERATOR_TOKYO_METRO = "odpt.Operator:TokyoMetro"
OPERATOR_TOEI = "odpt.Operator:Toei"

ALL_OPERATORS = [
    OPERATOR_JR_EAST,
    OPERATOR_TOKYO_METRO,
    OPERATOR_TOEI,
]

# ==============================================================================
# File Paths
# ==============================================================================
TRAVEL_TIMES_FILE = os.path.join(os.path.dirname(__file__), "travel_times.json")

# ==============================================================================
# JR East Railways
# ==============================================================================

JR_EAST_RAILWAYS = [
    "odpt.Railway:JR-East.ChuoRapid",
    "odpt.Railway:JR-East.Yamanote",
    "odpt.Railway:JR-East.ChuoSobuLocal",
    "odpt.Railway:JR-East.SobuRapid",
    "odpt.Railway:JR-East.JobanRapid",
    "odpt.Railway:JR-East.JobanLocal",
    "odpt.Railway:JR-East.KeihinTohokuNegishi",
    "odpt.Railway:JR-East.SaikyoKawagoe",
    "odpt.Railway:JR-East.ShonanShinjuku",
    "odpt.Railway:JR-East.Tokaido",
    "odpt.Railway:JR-East.Yokosuka",
    "odpt.Railway:JR-East.Takasaki",
    "odpt.Railway:JR-East.Utsunomiya",
    "odpt.Railway:JR-East.Musashino",
    "odpt.Railway:JR-East.Keiyo",
    "odpt.Railway:JR-East.Nambu",
    "odpt.Railway:JR-East.Yokohama",
    "odpt.Railway:JR-East.Sotobo",
    "odpt.Railway:JR-East.Uchibo",
]

# Tokyo Metro Railways
TOKYO_METRO_RAILWAYS = [
    "odpt.Railway:TokyoMetro.Ginza",
    "odpt.Railway:TokyoMetro.Marunouchi",
    "odpt.Railway:TokyoMetro.Hibiya",
    "odpt.Railway:TokyoMetro.Tozai",
    "odpt.Railway:TokyoMetro.Chiyoda",
    "odpt.Railway:TokyoMetro.Yurakucho",
    "odpt.Railway:TokyoMetro.Hanzomon",
    "odpt.Railway:TokyoMetro.Namboku",
    "odpt.Railway:TokyoMetro.Fukutoshin",
]

# Toei Subway Railways
TOEI_RAILWAYS = [
    "odpt.Railway:Toei.Asakusa",
    "odpt.Railway:Toei.Mita",
    "odpt.Railway:Toei.Shinjuku",
    "odpt.Railway:Toei.Oedo",
]

# All railways combined
ALL_RAILWAYS = JR_EAST_RAILWAYS + TOKYO_METRO_RAILWAYS + TOEI_RAILWAYS


# ==============================================================================
# Railway Name Mappings
# ==============================================================================

# Japanese to English railway name mapping
RAILWAY_JA_TO_EN = {
    "中央線快速": "ChuoRapid",
    "山手線": "Yamanote",
    "中央・総武各駅停車": "ChuoSobuLocal",
    "総武快速線": "SobuRapid",
    "京浜東北・根岸線": "KeihinTohokuNegishi",
    "常磐線快速": "JobanRapid",
    "常磐線各駅停車": "JobanLocal",
    "埼京・川越線": "SaikyoKawagoe",
    "湘南新宿ライン": "ShonanShinjuku",
    "東海道線": "Tokaido",
    "横須賀線": "Yokosuka",
    "高崎線": "Takasaki",
    "宇都宮線": "Utsunomiya",
    "武蔵野線": "Musashino",
    "京葉線": "Keiyo",
    "南武線": "Nambu",
    "横浜線": "Yokohama",
    "銀座線": "Ginza",
    "丸ノ内線": "Marunouchi",
    "日比谷線": "Hibiya",
    "東西線": "Tozai",
    "千代田線": "Chiyoda",
    "有楽町線": "Yurakucho",
    "半蔵門線": "Hanzomon",
    "南北線": "Namboku",
    "副都心線": "Fukutoshin",
    "浅草線": "Asakusa",
    "三田線": "Mita",
    "新宿線": "Shinjuku",
    "大江戸線": "Oedo",
    "外房線": "Sotobo",
    "内房線": "Uchibo",
    "総武本線": "Sobu",
    "成田線": "Narita",
    "成田線我孫子支線": "NaritaAbikoBranch",
    "中央本線": "Chuo",
    "中央本線(辰野支線)": "ChuoTatsunoBranch",
    "只見線": "Tadami",
    "山田線": "Yamada",
    "奥羽本線": "Ou",
    "花輪線": "Hanawa",
    "津軽線": "Tsugaru",
    "五能線": "Gono",
    "米坂線": "Yonesaka",
    "仙山線": "Senzan",
    "奥羽本線(山形線)": "OuYamagata",
    "陸羽東線": "RikuEast",
    "羽越本線": "Uetsu",
    "陸羽西線": "RikuWest",
    "篠ノ井線": "Shinonoi",
    "東横線": "Toyoko",
}

# English to Japanese railway name mapping
RAILWAY_EN_TO_JA = {v: k for k, v in RAILWAY_JA_TO_EN.items()}


# ==============================================================================
# GTFS-RT Route Code Mappings
# ==============================================================================

# Map between GTFS-RT trip_id suffix and railway names
ROUTE_CODE_TO_RAILWAY = {
    "T": "ChuoRapid",           # 中央線快速
    "H": "JobanRapid",          # 常磐線快速
    "G": "Yamanote",            # 山手線
    "B": "ChuoSobuLocal",       # 中央・総武各駅停車
    "F": "SobuRapid",           # 総武快速線
    "K": "KeihinTohokuNegishi", # 京浜東北・根岸線
    "E": "Tokaido",             # 東海道線
    "Y": "Keiyo",               # 京葉線
}

RAILWAY_TO_ROUTE_CODE = {v: k for k, v in ROUTE_CODE_TO_RAILWAY.items()}

# Display names for route codes
ROUTE_CODE_TO_DISPLAY_NAME = {
    "T": "中央線快速",
    "H": "常磐線",
    "G": "山手線",
    "B": "中央・総武各駅停車",
    "F": "総武快速線",
    "K": "京浜東北線",
    "E": "東海道線",
    "Y": "京葉線",
}


# ==============================================================================
# API Configuration
# ==============================================================================

ODPT_BASE_URL = "https://api-challenge.odpt.org/api/v4"
GTFS_RT_URL = "https://api-challenge.odpt.org/api/v4/gtfs/realtime/jreast_odpt_train_trip_update"


# ==============================================================================
# GTFS Codes & Mappings
# ==============================================================================

# Metro Line Codes (GTFS prefix to Line Name suffix)
GTFS_METRO_CODES = {
    "G": "Ginza", "M": "Marunouchi", "m": "Marunouchi", "H": "Hibiya",
    "T": "Tozai", "C": "Chiyoda", "Y": "Yurakucho", "Z": "Hanzomon",
    "N": "Namboku", "F": "Fukutoshin"
}

# Toei Line Codes
GTFS_TOEI_CODES = {
    "A": "Asakusa", "I": "Mita", "S": "Shinjuku", "E": "Oedo"
}

# Detailed Railway Info (Name mappings for local use)
METRO_TOEI_RAILWAY_INFO = {
    # Metro
    "odpt.Railway:TokyoMetro.Ginza": {"name_ja": "銀座線", "name_en": "Ginza Line"},
    "odpt.Railway:TokyoMetro.Marunouchi": {"name_ja": "丸ノ内線", "name_en": "Marunouchi Line"},
    "odpt.Railway:TokyoMetro.Hibiya": {"name_ja": "日比谷線", "name_en": "Hibiya Line"},
    "odpt.Railway:TokyoMetro.Tozai": {"name_ja": "東西線", "name_en": "Tozai Line"},
    "odpt.Railway:TokyoMetro.Chiyoda": {"name_ja": "千代田線", "name_en": "Chiyoda Line"},
    "odpt.Railway:TokyoMetro.Yurakucho": {"name_ja": "有楽町線", "name_en": "Yurakucho Line"},
    "odpt.Railway:TokyoMetro.Hanzomon": {"name_ja": "半蔵門線", "name_en": "Hanzomon Line"},
    "odpt.Railway:TokyoMetro.Namboku": {"name_ja": "南北線", "name_en": "Namboku Line"},
    "odpt.Railway:TokyoMetro.Fukutoshin": {"name_ja": "副都心線", "name_en": "Fukutoshin Line"},
    # Toei
    "odpt.Railway:Toei.Asakusa": {"name_ja": "浅草線", "name_en": "Asakusa Line"},
    "odpt.Railway:Toei.Mita": {"name_ja": "三田線", "name_en": "Mita Line"},
    "odpt.Railway:Toei.Shinjuku": {"name_ja": "新宿線", "name_en": "Shinjuku Line"},
    "odpt.Railway:Toei.Oedo": {"name_ja": "大江戸線", "name_en": "Oedo Line"},
}
