#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chatfire
# @Time         : 2024/6/20 15:51
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import json

import jsonpath
from meutils.pipe import *
from meutils.serving.fastapi.dependencies.auth import get_bearer_token, HTTPAuthorizationCredentials
from meutils.schemas.suno_types import SunoAIRequest, API_GENERATE_V2, API_FEED, API_BILLING_INFO, MODELS
from meutils.llm.openai_utils import appu
from meutils.notice.feishu import send_message

from fastapi import APIRouter, Depends, BackgroundTasks

from suno.controllers.utils import aapi_generate_v2, get_api_key, api_feed_to_redis, api_feed_from_redis

# create

# get

router = APIRouter()


@router.get("/models")
async def get_models():
    return MODELS


@router.get("/{song_ids}")
async def get_songs(song_ids):
    return api_feed_from_redis(song_ids)


@router.post('/creation')
async def create_song(
        request: SunoAIRequest,
        auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
        backgroundtasks: BackgroundTasks = BackgroundTasks,
):
    logger.debug(request)
    data = request.model_dump()
    send_message(bjson(data), title="歌曲创作任务")

    api_key = auth and auth.credentials or None

    suno_token = await get_api_key()
    task_info = await aapi_generate_v2(suno_token, data)

    if task_info.get("status") == "complete":
        await appu('ppu-1', api_key=api_key)
        ids = jsonpath.jsonpath(task_info, "$.clips..id") | xjoin(',')
        backgroundtasks.add_task(api_feed_to_redis, api_key=suno_token, ids=ids)

    return task_info


if __name__ == '__main__':
    from meutils.serving.fastapi import App

    app = App()

    app.include_router(router, '/suno')

    app.run()
