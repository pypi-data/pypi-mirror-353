import os 
import argparse 
from datetime import datetime
import requests
import pyaic
from pyaic.utils.pdf2words import pdf_read_text, pdf_text2words
from pyaic.translate.haici import fetch_en2cn
from pyaic import logger

class PaperHandle:
    def __init__(self, path, mdpath, midpath, logger=None):
        self.path = path 
        self.mdpath = mdpath 
        self.midpath = midpath 
        self.logger = logger 

    
    def download1(self):
        ccmd = f"curl -k -L -o {self.midpath} {self.path}"
        if self.logger: logger.debug(f"ccmd: {ccmd}")
        os.system(ccmd)
    
    def download(self):
        url = self.path
        midpath = self.midpath

        proxies = {
            "http": "http://localhost:7890",
            "https": "http://localhost:7890",
        }

        response = requests.get(url, proxies=proxies, stream=True)

        if response.status_code == 200:
            with open(midpath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            if self.logger: logger.debug(f"下载完成，文件保存为 {midpath}")
        else:
            if self.logger: logger.debug(f"下载失败，状态码: {response.status_code}")

    def get_words(self):
        file = self.midpath
        text = pdf_read_text(file)
        words = pdf_text2words(text)
        if self.logger: logger.debug(f"len(words): {len(words)}, words: {words.i[:10]}")
        return words 
    
    def write_md(self):

        with open(self.mdpath, "w") as f:
            f.write(f"""
---
title: {self.path}                 
author: cbguo
date: {datetime.now()}
tags: [paper ]
categories: [paper]
image: https://lh3.googleusercontent.com/ogw/AF2bZyjKd3HHh1cY1QIcRVS0DmKTzjYbz4lLuaTntYUXiuS2SA=s64-c-mo
---


""")
            f.write(f'''
## paper
[{self.path}]({self.path})


''')
            
            word_lis = list()

            words = self.get_words()
            for i, (k, v) in enumerate(words.items()):
                if i > 20: break
                i_str = f"{i}"
                k_str = f"{k}"
                v_str = f"{v}"
                #if self.logger: logger.debug(i_str, k_str, v_str)
                #if self.logger: logger.debug(f"i: {i_str:<5}, k: {k_str:<15}, v: {v_str:<5}")
                en_str = "; ".join(fetch_en2cn(k))
                en_str = en_str.replace("\n", "")
                ss = (f"i: {i_str:<5}, k: {k_str:<15}, v: {v_str:<5}, \ten: {en_str:<20}")
                if i%10 == 0 and self.logger: logger.debug(f"{ss}")
                word_lis.append(ss)

            word_str = "\n".join(word_lis)
            f.write(f'''
## wordss
```text
{word_str}
```
                    
''')
        pass 





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将paper路径转成md阅读文档")
    parser.add_argument(
        "path", type=str, 
        help="paper路径"
    )
    parser.add_argument(
        "mdpath", type=str, default="a.md",
        help="md文件路径名称"
    )
    parser.add_argument(
        "--midpath", type=str, default="_.pdf",
        help="下载后的pdf路径"
    )
    args = parser.parse_args()
    if logger: logger.debug(f"args: {args}")

    # curl -k -L -o a.pdf "https://arxiv.org/pdf/1706.03762v7"

    
    handle = PaperHandle(args.path, args.mdpath, args.midpath, logger=logger)

    if logger: logger.debug(f"download...")
    handle.download()

    if logger: logger.debug(f"write_md...")
    handle.write_md()


