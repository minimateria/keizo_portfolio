#hotpepper エリアリンクデータ取得完成版（logging実装）

import requests
import csv
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm
from google.colab import drive
drive.mount('/content/drive')
import datetime
today = datetime.date.today().strftime("%Y%m%d")

# ログの設定
logging.basicConfig(filename='/content/drive/MyDrive/hotpepper_area_list'+today+'.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def write_to_csv(data, file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

base_url = "https://beauty.hotpepper.jp/svcS{}"
base_nest_url = "https://beauty.hotpepper.jp/svcS{}/mac{}"
xpath_expression = "html > body > div:nth-of-type(3) > div:nth-of-type(3) > div:nth-of-type(1) > div:nth-of-type(1) > p:nth-of-type(1) > span:nth-of-type(1)"

start_suffix = "A"
end_suffix = "Z"

result_list = []

# プログレスバーの表示設定
total_pages = 26
with tqdm(total=total_pages) as pbar:
    for i in range(ord(start_suffix), ord(end_suffix) + 1):
        current_suffix = chr(i)
        current_url = base_url.format(current_suffix)
        logger.info(current_url)
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, "html.parser")
        element = soup.select_one(xpath_expression)
        if element:
            text = element.text.strip()
            result_list.append((current_suffix, text))
            logger.info(f"{current_suffix}: {text}")

            for j in range(ord(start_suffix[0]), ord(end_suffix[0]) + 1):
                current_mac = chr(j)
                current_nest_url = base_nest_url.format(current_suffix, current_suffix + current_mac)
                response = requests.get(current_nest_url)
                soup = BeautifulSoup(response.content, "html.parser")
                target_element = soup.select_one(xpath_expression)

                if target_element:
                    text = target_element.text.strip()
                    result_list.append((current_nest_url, text))
                    logger.info(f"{current_nest_url}: {text}")
                else:
                    logger.info(f"{current_nest_url}: Not found")

            if current_suffix == "A":
                for j in range(ord(start_suffix[0]), ord(end_suffix[0]) + 1):
                    current_mac = chr(j)
                    current_nest_url = base_nest_url.format(current_suffix, "J" + current_mac)
                    response = requests.get(current_nest_url)
                    soup = BeautifulSoup(response.content, "html.parser")
                    target_element = soup.select_one(xpath_expression)

                    if target_element:
                        text = target_element.text.strip()
                        result_list.append((current_nest_url, text))
                        logger.info(f"{current_nest_url}: {text}")
                    else:
                        logger.info(f"{current_nest_url}: Not found")

        else:
            logger.info(f"{current_suffix}: state Not found")
        pbar.update(1)

# CSVファイルにデータを書き込む
csv_file_path = "/content/drive/MyDrive/hotpepper_area_list"+today+".csv"
write_to_csv(result_list, csv_file_path)
