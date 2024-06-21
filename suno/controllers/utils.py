#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : suno
# @Time         : 2024/3/27 20:37
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : todo: 轮询、redis统一任务、转存oss【优化重构】

import jsonpath
from meutils.pipe import *
from meutils.db.redis_db import redis_client
from meutils.schemas.suno_types import BASE_URL, API_SESSION, API_GENERATE_V2, API_FEED, API_BILLING_INFO, MODELS
from meutils.config_utils.lark_utils import aget_spreadsheet_values
from meutils.notice.feishu import send_message


def get_refresh_token(api_key):  # 定时更新一次就行
    """
    last_active_session_id, last_active_token
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Cookie": f"__client={api_key}"
    }
    # url = f"https://clerk.suno.com/v1/client?_clerk_js_version={_CLERK_JS_VERSION}"
    url = f"https://clerk.suno.com/v1/client"

    response = httpx.get(url, headers=headers)
    logger.debug(response.text)
    if response.status_code == 200:
        obj = response.json()
        # last_active_token = jsonpath.jsonpath(obj, "$..jwt")[0]
        last_active_session_id = jsonpath.jsonpath(obj, "$..last_active_session_id")[0]

        return last_active_session_id

    return response.text


@alru_cache(ttl=3600 * 24)
async def aget_refresh_token(api_key):  # 定时更新一次就行
    url = f"https://clerk.suno.com/v1/client"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Cookie": f"__client={api_key}"
    }

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        response = await client.get(url)
        if response.is_success:
            obj = response.json()
            logger.debug(obj)
            last_active_session_id = jsonpath.jsonpath(obj, "$..last_active_session_id")[0]
            return last_active_session_id


def get_access_token(api_key):
    last_active_session_id = get_refresh_token(api_key)  # last_active_token 没啥用

    # url = f"https://clerk.suno.com/v1/client/sessions/{last_active_session_id}/tokens?_clerk_js_version={_CLERK_JS_VERSION}"
    url = f"https://clerk.suno.com/v1/client/sessions/{last_active_session_id}/tokens"

    headers = {
        # "Authorization": f"Bearer {last_active_token}",
        "Cookie": f"__client={api_key}"
    }

    response = httpx.post(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('jwt')
    return response.text


@alru_cache(ttl=30 - 3)
async def aget_access_token(api_key):
    last_active_session_id = await aget_refresh_token(api_key)  # last_active_token 没啥用
    url = f"https://clerk.suno.com/v1/client/sessions/{last_active_session_id}/tokens"

    headers = {
        "Cookie": f"__client={api_key}"
    }

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        response = await client.post(url)
        return response.is_success and response.json().get('jwt')


def api_generate_v2(api_key, payload):
    access_token = get_access_token(api_key)
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    httpx_client = httpx.Client(base_url=BASE_URL, headers=headers)

    response = httpx_client.post(API_GENERATE_V2, json=payload)
    if response.status_code == 200:
        return response.json()  # jsonpath.jsonpath(dd, "$.clips..id")
    return response.text


async def aapi_generate_v2(api_key, payload):
    access_token = await aget_access_token(api_key)
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30) as client:
        response = await client.post(API_GENERATE_V2, json=payload)

        logger.debug(response.text)

        return response.is_success and response.json()


def api_feed(api_key, ids):
    access_token = get_access_token(api_key)
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    httpx_client = httpx.Client(base_url=BASE_URL, headers=headers)

    response = httpx_client.get(API_FEED, params={"ids": ids})
    if response.status_code == 200:
        return response.json()  # jsonpath.jsonpath(dd, "$.clips..id")
    return response.text


@alru_cache(ttl=15)
async def aapi_feed(api_key, ids: str):
    access_token = await aget_access_token(api_key)
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30) as client:
        if isinstance(ids, list):
            ids = ','.join(ids)
        response = await client.get(API_FEED, params={"ids": ids})
        return response.is_success and response.json()  # 获取任务


def api_billing_info(api_key):
    access_token = get_access_token(api_key)
    logger.debug(access_token)

    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    httpx_client = httpx.Client(base_url=BASE_URL, headers=headers)

    response = httpx_client.get(API_BILLING_INFO)
    if response.status_code == 200:
        return response.json()  # total_credits_left
    return response.text


@alru_cache(ttl=5)
async def aapi_billing_info(api_key):
    access_token = await aget_access_token(api_key)
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30) as client:
        response = await client.get(API_BILLING_INFO)
        return response.is_success and response.json()


def api_session(api_key):
    access_token = get_access_token(api_key)

    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    httpx_client = httpx.Client(base_url=BASE_URL, headers=headers)

    response = httpx_client.get(API_SESSION)
    if response.status_code == 200:
        return response.json()['models'] or MODELS
    return response.text


# 歌曲统一管理
async def api_feed_to_redis(api_key, ids: str):
    while 1:
        await asyncio.sleep(10)
        logger.debug(f"异步获取歌曲\n{ids}")

        songs = await aapi_feed(api_key, ids)  # 15s 请求一次

        if all(song.get('status') == 'streaming' for song in songs):  # 歌词生成就返回，没必要 complete
            for song in songs:
                redis_client.set(f"suno:{song.get('id')}", json.dumps(song), ex=3600 * 24 * 100)

            logger.debug(f"异步获取歌曲: 成功")
            return


def api_feed_from_redis(ids):
    songs = []
    for id in ids.split(','):
        song = redis_client.get(f"suno:{id}")
        song = song and json.loads(song)
        songs.append(song)

    return songs


#
# async def api_feed_to_redis(api_key, ids):
#     song_ids = ids.strip().split(',')
#
#     songs = []
#     for song_id in song_ids:
#         song = redis_client.get(f"suno:{song_id}")
#         if song:
#             songs.append(json.loads(song))
#         else:
#             while 1:
#                 _songs = await aapi_feed(api_key, song_id)  # 15s 请求一次
#
#                 logger.debug(f"拉取歌曲{song_id}")
#
#                 if _songs[-1].get("status") == 'complete':
#                     redis_client.set(f"suno:{song_id}", json.dumps(_songs[-1]), ex=3600 * 24 * 100)
#                     songs += _songs
#                     break
#
#     logger.debug(songs)
#     return songs


# 轮询api-keys
async def get_api_key():
    feishu_url = 'https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=Jxlglo'
    df = await aget_spreadsheet_values(feishu_url=os.getenv('SUNO_FEISHU_URL', feishu_url), to_dataframe=True)
    api_keys = list(filter(None, df[0].tolist()))
    for _ in range(5):
        api_key = np.random.choice(api_keys)
        try:
            billing_info = await aapi_billing_info(api_key)
            if billing_info['total_credits_left'] > 10:
                return api_key
        except Exception as e:
            logger.debug(e)
            send_message(f"{e}\n\n{api_key}", title="suno cookies失效或者余额不足")


def song_info(df):
    """
    #   'audio_url': 'https://cdn1.suno.ai/63c85335-d8ec-4e17-882a-e51c2f358b2d.mp3',
    #   'video_url': 'https://cdn1.suno.ai/25c7e34b-6986-4f7c-a5f2-537dd80e370c.mp4',
    # https://cdn1.suno.ai/image_bea09d9e-be4a-4c27-a0bf-67c4a92d6e16.png
    :param df:
    :return:
    """
    df['🎵音乐链接'] = df['id'].map(
        lambda x: f"**请两分钟后试听**[🎧音频](https://cdn1.suno.ai/{x}.mp3)[▶️视频](https://cdn1.suno.ai/{x}.mp4)"
    )
    df['专辑图'] = df['id'].map(lambda x: f"![🖼](https://cdn1.suno.ai/image_{x}.png)")

    df_ = df[["id", "created_at", "model_name", "🎵音乐链接", "专辑图"]]

    return f"""
🎵 **「{df['title'][0]}」**

`风格: {df['tags'][0]}`

```toml
{df['prompt'][0]}
```


{df_.to_markdown(index=False).replace('|:-', '|-').replace('-:|', '-|')}
    """


if __name__ == '__main__':
    # api_key = os.getenv("SUNO_API_KEY")
    #
    # print(get_refresh_token(api_key))
    # print(arun(aget_refresh_token(api_key)))

    # print(refresh_token(api_key))
    # print(get_access_token(api_key))
    # payload = {
    #     "gpt_description_prompt": "a romantic ballad song about not being able to wait to see you again",
    #     "mv": "chirp-v3-5",
    #     "prompt": "",
    #     "make_instrumental": True
    # }
    # payload = {
    #     "prompt": "[Verse]\nSun is high and the skies are blue\nFeels so good just being with you\n\n[Verse 2]\nWe got time and a world to see\nLiving life and we're feeling free\n\n[Chorus]\nOh oh sunny day delight\nEverything just feels so right\nOh oh shining so bright\nDance with me till the night\n\n[Verse 3]\nRunning wild under golden skies\nSmile so big can't believe my eyes\n\n[Bridge]\nHand in hand we can touch the stars\nDoesn't matter how far we are\n\n[Chorus]\nOh oh sunny day delight\nEverything just feels so right\nOh oh shining so bright\nDance with me till the night",
    #     "tags": "r&b",
    #     "mv": "chirp-v3-5",
    #     "title": "Sunny Day Delight",
    #     "continue_clip_id": None,
    #     "continue_at": None,
    #     "infill_start_s": None,
    #     "infill_end_s": None
    # }

    # payload = {
    #     # 优先级最高
    #     "prompt": "[Verse]\nSun is high and the skies are blue\nFeels so good just being with you\n\n[Verse 2]\nWe got time and a world to see\nLiving life and we're feeling free\n\n[Chorus]\nOh oh sunny day delight\nEverything just feels so right\nOh oh shining so bright\nDance with me till the night\n\n[Verse 3]\nRunning wild under golden skies\nSmile so big can't believe my eyes\n\n[Bridge]\nHand in hand we can touch the stars\nDoesn't matter how far we are\n\n[Chorus]\nOh oh sunny day delight\nEverything just feels so right\nOh oh shining so bright\nDance with me till the night",
    #     # "prompt": "",
    #
    #     # "gpt_description_prompt": "创作一首中文歌曲",
    #
    #     "mv": "chirp-v3-5",
    #
    #     "make_instrumental": True,
    #     "tags": "r&b",
    #     "title": "Chatfire",
    #     "continue_clip_id": None,
    #     "continue_at": None,
    #     "infill_start_s": None,
    #     "infill_end_s": None
    # }
    #
    # logger.debug(api_generate_v2(api_key, payload))

    # ids = "ee6d4369-3c75-4526-b6f1-b5f2f271cf30"
    # print(api_feed(api_key, ids))

    # for i in range(100):  # 测试过期时间
    #     print(api_billing_info(api_key))
    #     time.sleep(60)

    print(arun(get_api_key()))
