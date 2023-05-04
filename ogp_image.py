import os
import requests
import traceback
import tempfile

from bs4 import BeautifulSoup

"""
ウェブサイトに設定されているサムネイル画像 OGP Image を取得する
"""

def download_OGP_image(page_url: str, temp_path: str):
    """
    指定された URL の OGP Image を指定フォルダにダウンロードする

    Perameters
    ----------
    page_url
        対象URL
    file_path
        一時ファイルのパス
    """
    try:
        image_url = fetch_OGP_image_url(page_url)

        # HTTP GET
        res = requests.get(image_url)

        # 正常応答なし
        if res.status_code != 200:
            print("正常応答なし")
            return None
        
        # MIMEより拡張子取得
        mimetype = res.headers["content-type"]
        if "image/png" not in mimetype and "image/jpeg" not in mimetype:
            print("MIMEが正常でない")
            return None
        
        # ダウンロード
        data = res.content
        with open(temp_path, "w+b") as fp:
            fp.write(data)
    
        return fp.name
    
    except Exception as e:
        print(traceback.format_exc())
        return None

def fetch_OGP_image_url(page_url: str):
    """
    指定 URL の OGP Image の URL を取得する
    
    Parameter
    ---------
    page_url : str
        対象 URL
    
    Return
    ------
    image_url : str
        画像 URL
    """
    # OGP og:image を取得するページの指定
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, features="html.parser")
    response.close()

    # HTMLを解析しURL取得
    image_url = soup.select('[property="og:image"]')[0].get("content")
    return image_url

if __name__ == "__main__":
    with tempfile.NamedTemporaryFile("w+b") as fp:
        page_url = "https://www.nicovideo.jp/watch/sm41686885"
        save_path = download_OGP_image(page_url, fp)
        print(save_path)
