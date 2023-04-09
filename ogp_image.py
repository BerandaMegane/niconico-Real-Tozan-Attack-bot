import os
import requests
import traceback

from bs4 import BeautifulSoup

def download_OGP_image(page_url: str, save_dir: str):
    """
    指定された URL の OGP Image を指定フォルダにダウンロードする

    Perameters
    ----------
    page_url
        対象URL
    save_dir
        画像の保存先ディレクトリ
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
        if "image/png" in mimetype:
            file_ext = ".png"
        elif "image/jpeg" in mimetype:
            file_ext = ".jpg"
        else:
            print("MIMEが正常でない")
            return None
        
        # ダウンロードファイル名
        save_path = os.path.join(save_dir, "temp_image" + file_ext)
        
        # ダウンロード
        with open(save_path, mode='wb') as local_file:
            data = res.content
            local_file.write(data)

            return save_path
        
        return None
    
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
    save_dir = "."
    page_url = "https://www.nicovideo.jp/watch/sm41686885"
    save_path = download_OGP_image(page_url, save_dir)
    print(save_path)
