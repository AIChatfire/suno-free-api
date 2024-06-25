#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chatfire
# @Time         : 2024/6/20 15:51
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

import jsonpath
from meutils.pipe import *
from meutils.serving.fastapi.dependencies.auth import get_bearer_token, HTTPAuthorizationCredentials
from meutils.schemas.suno_types import SunoAIRequest, API_GENERATE_V2, API_FEED, API_BILLING_INFO, MODELS
from meutils.llm.openai_utils import appu, create_chat_completion_chunk

from suno.controllers.utils import aapi_generate_v2, get_api_key, api_feed_to_redis, send_message
from suno.controllers.utils import api_feed_task_from_redis, api_feed_music_from_redis

from fastapi import APIRouter, Depends, BackgroundTasks

router = APIRouter()


@router.get("/models")
async def get_models():
    return MODELS


@router.get("/tasks/{task_id}")
async def get_music(task_id):
    return await api_feed_task_from_redis(task_id)


@router.get("/music/{music_ids}")
async def get_music(music_ids):
    return await api_feed_music_from_redis(music_ids)


@router.post('/generation')
async def generate_music(
        request: SunoAIRequest,
        backgroundtasks: BackgroundTasks,
        auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
):
    api_key = auth and auth.credentials or None

    logger.debug(request)
    data = request.model_dump()
    send_message(bjson(data))

    suno_token = await get_api_key()
    task_info = await aapi_generate_v2(suno_token, data)

    if task_info.get("status") == "complete":
        await appu('ppu-1', api_key=api_key)
        task_id = task_info.get('id', 'task_id')
        music_ids = jsonpath.jsonpath(task_info, "$.clips..id") | xjoin(',')
        # 新增字段
        task_info = {
            "task_id": task_id,
            "music_ids": music_ids,
            **task_info
        }

        backgroundtasks.add_task(api_feed_to_redis, api_key=suno_token, task_id=task_id, music_ids=music_ids)

    return task_info


if __name__ == '__main__':
    from meutils.serving.fastapi import App

    app = App()

    app.include_router(router, '/task/music/v1')

    app.run()
