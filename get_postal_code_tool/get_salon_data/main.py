#店舗詳細データ取得excelフォーマット完成版

import requests
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
import json
import pandas as pd

def get_target_text(url):
    # ページのコンテンツを取得
    response = requests.get(url)
    content = response.content

    # BeautifulSoupオブジェクトを作成
    soup = BeautifulSoup(content, 'html.parser')

    # script要素をすべて取得
    script_tags = soup.find_all('script')

    # JSONデータを含むscript要素を探索
    for script_tag in script_tags:
        script_text = script_tag.string
        if script_text and '"@type": "BeautySalon"' in script_text:
            # JSONデータをパースして目的のテキストを取得
            data = json.loads(script_text)
            return data

    return None

# CSVファイルからURLを読み込む
urls = []
with open('salon_list.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        urls.append(row['リンク'])

# データを取得してDataFrameに格納
data_list = []
for url in tqdm(urls, desc="処理中", ascii=True):
    target_data = get_target_text(url)
    if target_data:
        # JSONデータを成型してリストに追加
        flattened_data = {}
        for key, value in target_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flattened_data[f"{key}:{sub_key}"] = sub_value
            else:
                flattened_data[key] = value

        # URLからcodeを抽出
        code = url.split("https://beauty.hotpepper.jp/", 1)[-1].split("/", 1)[0]
        flattened_data['code'] = code

        data_list.append(flattened_data)

# DataFrameを作成
df = pd.DataFrame(data_list)

# Excelファイルとしてエクスポート
df.to_excel('salon_data.xlsx', index=False)
