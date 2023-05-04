# 公式
import tempfile

# サードパーティ
import mastodon
import tweepy

# 自作
import ogp_image
import secret

def get_TwitterAPI_handler(config):
    # Twitter API 認証
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)
    return tweepy.API(auth, wait_on_rate_limit=True)

def get_MastodonAPI_handler(config):
    # Mastodon API 認証
    return mastodon.Mastodon(
        api_base_url  = config.server,
        client_id     = config.client_key,
        client_secret = config.client_secret,
        access_token  = config.access_token
    )

def tweet(tweet_text, image_url, debug=True):
    # ログ用
    print("【ツイート】")
    print(tweet_text)
    
    # 一時ファイルに画像ダウンロード
    with tempfile.NamedTemporaryFile() as fp:
        image_path = ogp_image.download_OGP_image(image_url, fp)
        if not debug:    
            api = get_TwitterAPI_handler(secret.TwitterAPI)
            if image_path is not None:
                media_ids = [api.media_upload(image_path, file=fp).media_id]
                api.update_status(status=tweet_text, media_ids=media_ids)
            else:
                api.update_status(status=tweet_text)

def toot(toot_text, image_url, debug=True):
    # ログ用
    print("【トゥート】")
    print(toot_text)

    if not debug:    
        api = get_MastodonAPI_handler(secret.MastodonAPI)
        api.toot(toot_text)
