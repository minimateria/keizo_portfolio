import re
import requests
import pandas as pd
from tqdm import tqdm  # tqdmを追加

def extract_postal_code_and_remove_hyphen(text):
    postal_code_pattern = r"\d{3}-\d{4}"  # 郵便番号の正規表現パターン (例: 123-4567)
    match = re.search(postal_code_pattern, text)
    if match:
        postal_code_with_hyphen = match.group()
        post_number = postal_code_with_hyphen.replace("-", "")
        return post_number
    else:
        return None

# 取り込むファイルフォルダ内のxlsxファイルを読み込む
df = pd.read_excel(r"取り込むファイル\salon_data.xlsx", dtype=str, na_filter=False)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# 郵便番号をチェックし、空だった場合は住所を入力して取得
for index, row in tqdm(df.iterrows(), total=len(df)):  # tqdmをループに追加
    postal_code = str(row["郵便番号"])
    if postal_code == "":
        address = address = str(row["住所"])
        url = f'https://www.google.com/search?q=postalcode {address}'
        response = requests.get(url, headers=headers)
        page_content = response.text
        post_number = extract_postal_code_and_remove_hyphen(page_content)

        if post_number:
            df.at[index, "郵便番号"] = post_number
            #print(post_number)
        else:
            print("郵便番号が見つかりませんでした")

# ファイルに変更を保存
df.to_excel(r"取り込むファイル\result.xlsx", index=False)
