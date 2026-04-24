import asyncio
import logging
import os
import re
import sqlite3
import threading
from collections import Counter
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Literal

import requests

TRANSLATION = Literal["youdao"]

logging.basicConfig(level=logging.DEBUG)


def get_all_invalid_unique_characters(file_name: str = "invalid_words.txt") -> list:
    """get all invalid words

    Args:
        file_name (str, optional): _description_. Defaults to "invalid_words.txt".

    Returns:
        list: _description_
    """
    # check

    # append,无意义字符
    # def exists_word(word: str) -> bool:
    #     """Whether it is a word or not"""
    #     connect = sqlite3.connect("stardict.db")
    #     cursor = connect.cursor()
    #     sql: str = f"select word,sw from stardict where sw='{word}'"
    #     cursor.execute(sql)
    #     data = cursor.fetchall()
    #     cursor.close()
    #     connect.cursor()
    #     if len(data) == 0:
    #         return False
    #     else:
    #         return True

    #
    file_name = os.path.join(os.getcwd(), "utils", file_name)
    logging.debug(f"{file_name}")
    # read
    with open(file_name) as f:
        all_characters = f.readlines()
        all_clean_characters = []
        for characters in all_characters:
            all_clean_characters.extend(re.findall("[a-zA-Z]+", characters))
        all_clean_characters = list(set(all_clean_characters))
        logging.debug(f"invalid characters: {len(all_clean_characters)}")
        return all_clean_characters


def get_all_readed_unique_characters(file_name: str = "readed_words.txt") -> list:
    """get all readed words

    Args:
        file_name (str, optional): _description_. Defaults to "readed_words.txt".

    Returns:
        list: _description_
    """
    # TODO 待完成
    return []


def get_specify_chapter_valid_words(
    file_name: str, want_chapter_title: str, next_chapter_title: str
) -> list:
    """_summary_ 读取指定章节

    Args:
        want_chapter_title (str): _description_
        next_chapter_title (str): _description_

    Returns:
        list: _description_
    """
    with open(file_name) as f:
        all_characters: list = [line.strip("\n") for line in f.readlines()]

        logging.debug(f"{all_characters}")
        logging.debug(f"{len(all_characters)}")

        want_index = []
        next_index = []
        for index in range(len(all_characters)):
            if want_chapter_title in all_characters[index]:
                # all_characters.
                logging.debug(f"{index}:{all_characters[index]}")
                want_index.append(index)
            if next_chapter_title in all_characters[index]:
                logging.debug(f"{index}: {all_characters[index]}")
                next_index.append(index)

        if len(want_index) == 2 and len(next_index) == 2:
            # 常规处理 [title_index,body_index]
            # 当index都是2个时，want chapter是最后一个 到 next chapter的最后一个。
            content = all_characters[want_index[-1] : next_index[-1]]
        elif len(want_index) > 2 or len(next_index) > 2:
            # 非常规的，同
            logging.warning(f"want_index:{want_index},next_index:{next_index}")
            content = all_characters[want_index[1] : next_index[1]]
            logging.warning("handle index range, want_index:1,next_index:1")
        else:
            raise ValueError("索引少于2,chapter title error")
        logging.debug(content)
        content1 = split_clean_sentences(content)
        return content1


def split_clean_sentences(all_characters: list) -> list:
    # TODO 重构命名
    """分割清理

    Args:
        sentences (list): _description_

    Returns:
        list: _description_
    """
    # clean all characters
    all_clean_characters: list = []
    for characters in all_characters:
        clean_characters: list = re.findall("[a-zA-Z]+", characters)
        all_clean_characters.extend(clean_characters)
    logging.debug(f"all clean words: {len(all_clean_characters)}")

    # clean invalid characters
    # 获取所有无效不重复的无效字符
    invalid_characters = get_all_invalid_unique_characters()
    # 排除所有已知
    readed_characters = get_all_readed_unique_characters()
    # 所有待排除
    all_exclude_characters = invalid_characters + readed_characters
    for invalid_character in all_exclude_characters:
        # 无效字符存在的次数
        count_num: int = all_clean_characters.count(invalid_character)
        if count_num > 0:
            # TODO 当无效字符存在时，remove n次
            for _ in range(count_num):
                all_clean_characters.remove(invalid_character)

    # logging.debug(f"all clean and valid words: {all_clean_characters}")
    logging.debug(f"all clean and valid words: {len(all_clean_characters)}")
    return all_clean_characters


def get_all_valid_words(file_name: str) -> list:
    # TODO 重构处理
    """get all words from file,and valid
    读取book;读取字幕文件

    Args:
        file_name (str): file name

    Returns:
        list: _description_
    """
    # check
    logging.debug(file_name)

    # read
    with open(file_name) as f:
        all_characters: list = f.readlines()
        logging.debug(f"{len(all_characters)}")

        # clean all characters
        all_clean_characters: list = []
        for characters in all_characters:
            clean_characters: list = re.findall("[a-zA-Z]+", characters)
            all_clean_characters.extend(clean_characters)
        logging.debug(f"all clean words: {len(all_clean_characters)}")

        # clean invalid characters
        # 获取所有无效不重复的无效字符
        invalid_characters = get_all_invalid_unique_characters()
        # 排除所有已知
        readed_characters = get_all_readed_unique_characters()
        # 所有待排除
        all_exclude_characters = invalid_characters + readed_characters
        for invalid_character in all_exclude_characters:
            # 无效字符存在的次数
            count_num: int = all_clean_characters.count(invalid_character)
            if count_num > 0:
                # TODO 当无效字符存在时，remove n次
                for _ in range(count_num):
                    all_clean_characters.remove(invalid_character)

        # logging.debug(f"all clean and valid words: {all_clean_characters}")
        logging.debug(f"all clean and valid words: {len(all_clean_characters)}")
        return all_clean_characters


def write_words(words: list, file_name: str, level: int = 0) -> None:
    """_summary_

    Args:
        words (list): _description_
        file_name: 写入的文件名
        level (int, optional): 写入范围，0表示全部写入，n表示写入词频前n个. Defaults to 0.
    """
    file_name = os.path.join(os.getcwd(), "res", file_name)
    # 分析
    words_info: Counter = Counter(words)
    logging.debug(f"{words_info.total()}")

    # 写入
    if level == 0:
        all_words_info: list[tuple["str", int]] = words_info.most_common()
    else:
        all_words_info: list[tuple["str", int]] = words_info.most_common(level)
    all_words = [word_info[0] for word_info in all_words_info]
    with open(file_name, "w", encoding="utf8") as f:
        f.write("\n".join(all_words))


def get_all_urls(file_name: str = "urls.txt") -> list:
    """_summary_

    Args:
        file_name (str): _description_

    Returns:
        list: _description_
    """
    # check

    file_path = os.path.join(os.getcwd(), "files", "urls.txt")
    with open(file_path) as f:
        all_urls = [url.strip("\n") for url in f.readlines()]
    return all_urls


def get_all_valid_words_page(urls: list) -> list[str]:
    """return words length greater than 1 and really is word"""
    all_res = {}

    def get_page_words(url: str) -> tuple(str, list):
        """get valid characters

        Args:
            url (str): _description_
            list (_type_): _description_

        Returns:
            _type_: _description_
        """
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"get page fail {response.status_code} : {url}")
            return []
        words_repetition_list = re.findall("[a-zA-Z]+", response.text)
        return url, words_repetition_list

    def handle_response(response: Future):
        # url, words: list = response.result()
        # all_res[url] = words
        pass
        # words_list = list(set(words_repetition_list))
        # words_more_list = [res for res in words_list if len(res) > 1]

    # create threading pool
    pool = ThreadPoolExecutor(max_workers=3)
    for url in urls:
        task: Future = pool.submit(get_page_words, url)
        task.add_done_callback(handle_response)

    return all_res


def calculate_valid_words(valid: list, invalid: list[list, list]) -> list:
    """calculate valid data,remove all invalid res

    Args:
        valid (list): _description_
        invalid (list[list,list]): _description_

    Returns:
        list: _description_
    """
    pass


def check_directory(directory: str) -> None:
    """检查单个目录
    # TODO 检查任意目录
    Args:
        directory (str): _description_
    """
    if not os.path.exists(directory):
        os.mkdir(directory)


def check_file(file: str) -> None:
    """检查任意文件

    Args:
        file (str): _description_
    """
    pass


def get_len_2():
    # 区分 长度为2 和 大于2的
    # words_2_set = set()
    # words_more_set = set()
    # for word in words_readlly_set:
    #     if len(word) == 2:
    #         words_2_set.add(word)
    #     else:
    #         words_more_set.add(word)
    pass


def write_length():
    # 写入danci长度为2的
    with open("words_2.txt", "a", encoding="utf8") as f:
        f.write("\n".join(words_2_set))

    # 给单词长度超过2的排序 安装长度排序排序
    words_more_list = list(words_more_set)
    for index in range(len(words_more_list)):
        for index in range(len(words_more_list)):
            if index + 1 < len(words_more_list) and len(words_more_list[index]) < len(
                words_more_list[index + 1]
            ):
                words_more_list[index], words_more_list[index + 1] = (
                    words_more_list[index + 1],
                    words_more_list[index],
                )

    return words_more_list


def judge_word(word: str) -> bool:
    """
    判断单词是不是首字母大写。

    Dog True
    dog False
    DoG False

    re.findall("[A-Z][a-z]+","Dog")
    ['Dog']
    re.findall("[A-Z][a-z]+","dog")
    []
    re.findall("[A-Z][a-z]+","DoG")
    ['Do']
    re.findall("[A-Z][a-z]+","DoG-Dog")
    ['Do', 'Dog']
    """
    res: list = re.findall("[A-Z][a-z]+", word)
    if len(res) == 1 and len(res[0]) == len(word):
        return True
    return False


def delete_local_words(words_list: list[str]) -> list[str]:
    """去除本地单词 locl_*.txt"""
    # 获取local_**.txt的文件
    local_file_list = [
        file
        for file in os.listdir()
        if file.split(".")[-1] == "txt" and file.split("_")[0] == "local"
    ]
    if len(local_file_list) == 0:
        return words_list
    all_local_words: list = []
    for file in local_file_list:
        with open(file, encoding="utf8") as f:
            words = f.readlines()
        all_local_words.extend(words)
    all_local_words = [word.rstrip("\n") for word in words]

    # 处理为中间形态进行比较。 凡是首字母大写的都转为小写
    compare_all_local_words = []
    for word in all_local_words:
        if judge_word(word):
            word = word.lower()
        compare_all_local_words.append(word)

    compare_online_words = []
    for word in words_list:
        if judge_word(word):
            word = word.lower()
        compare_online_words.append(word)

    print("local: ", compare_all_local_words)
    print("get: ", compare_online_words)
    res: set = set(compare_online_words) - set(compare_all_local_words)
    return list(res)


def translate_word(translation_company: TRANSLATION):
    match translation_company:
        case "youdao":
            pass
        case _:
            raise ValueError("not support!")


def generate_menu_message() -> tuple[list, str]:
    """generate wanglu file menu

    Returns:
        str: _description_
    """
    path: str = os.path.join(os.getcwd(), "data")
    characters: list = [
        character for character in os.listdir(path) if character.startswith("wanglu_")
    ]
    logging.info(f"all: {characters}")

    res = []
    for character in characters:
        abs_character = os.path.join(os.getcwd(), "data", character)
        if os.path.isfile(abs_character):
            res.append(character)
        if os.path.isdir(abs_character):
            child_character = [
                child for child in os.listdir(abs_character) if child.endswith(".txt")
            ]
            res.extend(child_character)
        else:
            logging.warning(f"not support file: {abs_character}")
    logging.info(f"{res}")
    res.sort()
    return res, "\n".join(res)


# demo
# words = get_all_valid_words("./test_res/test.txt")
# word_info: Counter = Counter(words) # 指定前n个词汇 写入
# print(word_info.most_common(500))
# print("共:",word_info.total())

# demo2
# words = get_specify_chapter_valid_words("./test_res/test.txt","How It Began: The One Push-up Challenge","For Good Habits Only")
# print(words)

# demo3
# write_words(words,"haha.txt")

res = generate_menu_message()
print(res)
