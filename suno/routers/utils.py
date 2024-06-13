#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : suno
# @Time         : 2024/3/27 20:37
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

import jsonpath
from meutils.pipe import *
from meutils.schemas.suno_types import _CLERK_JS_VERSION, BASE_URL, API_GENERATE_V2, API_FEED, API_BILLING_INFO


def get_refresh_token(api_key):  # 定时更新一次就行
    """
    last_active_session_id, last_active_token
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Cookie": f"__client={api_key}"
    }
    url = f"https://clerk.suno.com/v1/client?_clerk_js_version={_CLERK_JS_VERSION}"

    response = httpx.get(url, headers=headers)
    if response.status_code == 200:
        obj = response.json()
        last_active_token = jsonpath.jsonpath(obj, "$..jwt")[0]
        last_active_session_id = jsonpath.jsonpath(obj, "$..last_active_session_id")[0]

        return last_active_token, last_active_session_id

    return response.text


def get_access_token(api_key):
    last_active_token, last_active_session_id = get_refresh_token(api_key)  # last_active_token 没啥用

    url = f"https://clerk.suno.com/v1/client/sessions/{last_active_session_id}/tokens?_clerk_js_version={_CLERK_JS_VERSION}"

    headers = {
        # "Authorization": f"Bearer {last_active_token}",
        "Cookie": f"__client={api_key}"
    }

    response = httpx.post(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('jwt')
    return response.text


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


if __name__ == '__main__':
    api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8yaDhXTEF5a0F2Q0hDaDc0QWNmT084UFZKY0giLCJyb3RhdGluZ190b2tlbiI6ImpkanRicW5obHFrMDE3MXVtaXpleTE3MjI3dm8wcXR0Y3Z3dnk2bDEifQ.YOwf2UMfq5WnqLxlLtjqjlfpYp-kMy6XYAVXJzWP5xwFvZh4bZ2ANMOT6YcFIe_GDb5wWWYEoZ_e_9dlV_X3CeMYezgvHf4mWWibJhDntjy4X1SdfEKf73VzsQ9_tXHMBXUEnMr6YTrCrPrJ3z6uZEZWgkIrNMAViW5xo5gX0l1H26Ro7Qoyjox8QFn4INQUL1F1GjtZjObycRpChsyCYWCPstdDzBDOJmwl4r_aSFpxnLBmGHDxIsCOB9q_WMyMMvwW9W5HbS0pg6yLUxpNTsgx1ozqTb698WSg0fjuA15bNNH7zL5le9dvyHwCcgbnaYjbj0ri6_sZp17IN-1tDg"

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

    payload = {
        # 优先级最高
        "prompt": "[Verse]\nSun is high and the skies are blue\nFeels so good just being with you\n\n[Verse 2]\nWe got time and a world to see\nLiving life and we're feeling free\n\n[Chorus]\nOh oh sunny day delight\nEverything just feels so right\nOh oh shining so bright\nDance with me till the night\n\n[Verse 3]\nRunning wild under golden skies\nSmile so big can't believe my eyes\n\n[Bridge]\nHand in hand we can touch the stars\nDoesn't matter how far we are\n\n[Chorus]\nOh oh sunny day delight\nEverything just feels so right\nOh oh shining so bright\nDance with me till the night",
        # "prompt": "",

        # "gpt_description_prompt": "创作一首中文歌曲",

        "mv": "chirp-v3-5",

        "make_instrumental": True,
        "tags": "r&b",
        "title": "Chatfire",
        "continue_clip_id": None,
        "continue_at": None,
        "infill_start_s": None,
        "infill_end_s": None
    }

    # print(api_generate_v2(api_key, payload))
    # ids = "ee6d4369-3c75-4526-b6f1-b5f2f271cf30"
    # print(api_feed(api_key, ids))

    for i in range(100):  # 测试过期时间
        print(api_billing_info(api_key))
        time.sleep(60)
