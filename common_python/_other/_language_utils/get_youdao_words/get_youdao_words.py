import requests


def fetch_wordbook_data(limit=15, offset=0):
    url = f"https://youdao.com/wordbook/webapi/words?limit={limit}&offset={offset}"

    # Cookie
    cookies = {
        "cookie_name": "OUTFOX_SEARCH_USER_ID_NCOO=1502430254.4788342; OUTFOX_SEARCH_USER_ID=-937408331@223.166.94.41; P_INFO=18285574257|1698989374|1|dict_logon|00&99|null&null&null#shh&null#10#0|&0||18285574257; DICT_PERS=v2|urs-phone-web||DICT||web||-1||1698989374895||223.166.95.27||urs-phoneyd.c415b38d1b804ad09@163.com||lY6LkMOMJF0wFRLTB64OERJunMOA0HOWRlfhMzGhMz5RlW0LUM6L6z0wukMpy6MeLRl5PLPu0fgZ0QBkLTLn4z5R; DICT_UT=urs-phoneyd.c415b38d1b804ad09@163.com; DICT_SESS=v2|qj3a2Zpw0WkE64wFRHOMROY0HeLRMJFRYlOLk5k4qBRJFPMOEnHgLRgFh4qZhHp40p4kMqZOMQz064RM6L6Lqy0QuhfYfnLgL0; DICT_LOGIN=3||1700040501072; DICT_DOCTRANS_SESSION_ID=YmFmZjg3ZTQtMmZmOS00NjBlLTg4M2ItOTk5YTgzZGQwOGNm"
    }

    response = requests.get(url, cookies=cookies)

    if response.status_code == 200:
        data = response.json()
        if data.get("msg") == "SUCCESS":
            return data
        print(f"获取失败: {data}")
    else:
        print(f"请求失败，状态码: {response.status_code}")
        return None


def fetch_all_wordbook_data(limit=15):
    offset = 0
    all_data = []

    while True:
        data = fetch_wordbook_data(limit, offset)

        if not data or not data.get("data"):
            print("获取完毕,退出")
            break

        current_page_data = data["data"]
        total = current_page_data["total"]
        itemList = current_page_data["itemList"]
        words = [item["word"] for item in itemList]
        print(f"共:{total}个; 获取第 {offset} offset数据成功。")
        all_data.extend(words)

        if len(itemList) < limit:
            print("最后一页退出")
            break

        offset += limit

    return all_data


all_wordbook_data = fetch_all_wordbook_data()
if all_wordbook_data:
    print(f"共获取到 {len(all_wordbook_data)} 条数据。")
    with open("res.txt", "w") as f:
        f.write("\n".join(all_wordbook_data))
else:
    print("未获取到数据。")
