import os


def get_words_from_file(file_path):
    with open(file_path, encoding="utf-8") as file:
        return set(file.readlines())


def main():
    # 1. 从 res.txt 中获取所有单词
    res_file_path = "res.txt"
    res_words = set()
    with open(res_file_path, encoding="utf-8") as res_file:
        res_words = set(res_file.readlines())

    # 2. 遍历以 "youdao" 开头且以 ".txt" 结尾的文件，获取这些文件中的所有单词
    youdao_files = [
        file
        for file in os.listdir()
        if file.startswith("youdao") and file.endswith(".txt")
    ]
    youdao_words = set()
    for youdao_file in youdao_files:
        youdao_file_path = os.path.join(os.getcwd(), youdao_file)
        youdao_words.update(get_words_from_file(youdao_file_path))

    # 3. 找到在 res.txt 中存在但在其他文件中不存在的单词
    unique_words = res_words - youdao_words

    # 输出结果
    print("在 res.txt 中存在但在其他文件中不存在的单词:")
    for word in unique_words:
        print(word)


if __name__ == "__main__":
    main()
