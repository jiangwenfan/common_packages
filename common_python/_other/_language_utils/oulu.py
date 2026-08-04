import datetime
import difflib
import json
import math
import os
import random
import sys
from turtle import write

import pymysql
import requests
from colorama import Fore, init


def create_eudic_book() -> str:
    # current_datetime = datetime.datetime.now()
    # book_name = f"{current_datetime.month}-{current_datetime.day}-{current_datetime.hour}-{current_datetime.minute}"
    book_name = get_book_name()

    # 创建欧陆生词本
    url = "https://api.frdic.com/api/open/v1/studylist/category"
    headers = {"Content-Type": "application/json", "Authorization": config["token"]}
    create_data = {"language": "en", "name": book_name}
    response = requests.post(url=url, headers=headers, json=create_data)
    print(response.text)
    if response.status_code == 201:
        response_data = json.loads(response.text)
        try:
            id: str = response_data["data"]["id"]
        except KeyError:
            print("创建失败")
            sys.exit()
    else:
        print("创建失败")
        sys.exit()
    return id


def write_word_eudic_book(words: list):
    # 写入单词到欧陆生词本
    url = "https://api.frdic.com/api/open/v1/studylist/words"
    write_data = {"id": create_eudic_book(), "language": "en", "words": words}
    headers = {"Content-Type": "application/json", "Authorization": config["token"]}
    response = requests.post(url=url, headers=headers, json=write_data)
    print(response.text)
    if response.status_code == 201:
        if "导入成功" in json.loads(response.text)["message"]:
            print("导入成功")
        else:
            print("导入失败")
    else:
        print("导入失败")
        sys.exit()


def get_all_eudic_book():
    # 获取所以生词本 [{id,name},{}]
    url = "https://api.frdic.com/api/open/v1/studylist/category?language=en"
    headers = {"Content-Type": "application/json", "Authorization": config["token"]}
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        response_data = json.loads(response.text)
        book_list = response_data["data"]
        print(book_list)
        return book_list
    else:
        print("生词本获取失败")
        sys.exit()


def get_all_words_of_bookname_and_write_local(book_id, book_name):
    # 获取所有生词本保存到本地。 获取数据不完整。
    if book_id != 0:
        url = f"https://api.frdic.com/api/open/v1/studylist/words/{book_id}?language=en&category_id=0&page=2&page_size=50"
        headers = {"Content-Type": "application/json", "Authorization": config["token"]}
        response = requests.get(url=url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            words_info = response_data["data"]
            words_list = [word_info["word"] for word_info in words_info]
            with open(f"menu/{book_name}.txt", "w") as f:
                f.write("\n".join(words_list))
            print("生词本写入成功")
        else:
            print("获取单词失败")
            sys.exit()
    else:
        print("没有获取到book id")
        sys.exit()
