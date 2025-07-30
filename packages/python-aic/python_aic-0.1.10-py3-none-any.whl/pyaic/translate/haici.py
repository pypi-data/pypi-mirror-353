import requests
from bs4 import BeautifulSoup



__all__ = [
    "fetch_en2cn"
]


def fetch_en2cn(word):
    url = f"https://dict.cn/{word}"
    translation_list = list()
    try:
        # 发送HTTP请求并获取网页内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        # 使用Beautiful Soup解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 在网页中找到翻译内容
        translations = soup.find("div", class_="basic clearfix").find_all("li")
        
        # 提取翻译结果并打印
        translation_list = [translation.get_text() for translation in translations]
        # translation_text = '\n'.join(translation_list)
        # print(f"翻译结果：\n----{translation_text.strip()}---")
        return translation_list
        
    except requests.RequestException as e:
        print(f"请求错误: word: {word}, e:{e}")
    except Exception as e:
        print(f"Error: word: {word}, , e: {e}")

    return translation_list


# # 测试爬取翻译
# word_to_translate = input("请输入要翻译的单词或短语：")
# fetch_translation(word_to_translate)
