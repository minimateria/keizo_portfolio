import pandas as pd
from tqdm import tqdm
import re
import unicodedata

master_list = pd.read_csv("x-ken-all.csv",usecols=[2,6,7,8],names=('郵便番号', '住所1', '住所2', '住所3'),encoding="cp932",dtype=str,na_filter=False)
master_list["住所"] = master_list['住所1']+master_list['住所2']+master_list['住所3']
master_list.drop(['住所1', '住所2', '住所3'], axis=1, inplace=True)

# 文字数の大きい順に並び変える
master_list = master_list.sort_values(by='住所', key=lambda x: x.str.len(), ascending=False)
salon_list = pd.read_excel(r"取り込むファイル\DMリスト_最新_20230804_123031_20230804_130245.xlsx",dtype=str,na_filter=False)

#################################### 完成版　2023/08/06 ################################################
# 数字を漢数字に変換する関数
def number_to_kanji(number_str):
    # 漢数字として使う文字のリストを定義
    kanji_digits = ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    kanji_tens = ["", "十", "百", "千", "万", "億"]  # 十の位以上に対応するように修正

    # 漢数字に変換しない住所リストを定義
    not_convert_list = [
        "北海道旭川市",
        "北海道江別市",
        "夕張郡長沼町",
        "雨竜郡妹背牛町",
        "雨竜郡秩父別町",
        "上川郡鷹栖町",
        "上川郡東神楽町",
        "上川郡東川町",
        "喜多方市",
        "空知郡南幌町",
        "和賀郡西和賀町",
        "中央アエル",
        "住友生命仙台中央ビル"
    ]

    # 住所が漢数字に変換しないリストに含まれている場合は変換を行わない
    for addr in not_convert_list:
        if addr in number_str:
            return number_str

    # 数字を漢数字に変換する関数
    def replace_digit(match):
        number = match.group(0)
        if len(number) == 1:
            # 一桁の場合はそのまま漢数字に変換
            return kanji_digits[int(number)]
        else:
            # 二桁以上の場合は各桁を漢数字に変換
            kanji_result = ""
            digit_count = 0
            num = int(number)
            while num > 0:
                digit = num % 10
                if digit != 0:
                    # 二桁目が"1"の場合は"十"を挿入した後に"一"を削除
                    if digit == 1 and digit_count == 1 and len(kanji_result) > 0 and kanji_result[-1] == "十":
                        kanji_result = kanji_tens[digit_count]
                    else:
                        kanji_result = kanji_digits[digit] + kanji_tens[digit_count] + kanji_result
                num //= 10
                digit_count += 1

            # 数字が2桁以上の場合は先頭の"一"を削除
            kanji_result = kanji_result.replace("一", "", 1)
            return kanji_result

    # 数字の右に"F"があれば"階"に置換
    number_str = number_str.replace("F", "階")
    number_str = number_str.replace("Ｆ", "階")

    # 正規表現を使って、数字を漢数字に置き換える（数字の右に"F"がある場合は変換しない）
    return re.sub(r'\d+(?!階)', replace_digit, number_str)

# 住所の数字を漢数字に変換
salon_list["住所"] = salon_list["住所"].apply(number_to_kanji)
#変換確認用
#print(salon_list)

# tqdmを使ってプログレスバーを追加
for index, row in tqdm(salon_list.iterrows(), total=len(salon_list)):
    if row['郵便番号'] == '':
        #address = row['住所']
        #全角・半角や大文字・小文字を区別しない
        address = unicodedata.normalize('NFKC', row['住所']).casefold()
        matched_row = master_list[master_list['住所'].apply(lambda x: x in address)]
        if not matched_row.empty:
            salon_list.at[index, '郵便番号'] = matched_row.iloc[0]['郵便番号']

# 結果をExcelファイルにエクスポート
output_file = 'result.xlsx'
salon_list.to_excel(output_file, index=False)