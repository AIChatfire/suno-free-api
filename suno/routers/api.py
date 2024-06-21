#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : suno_api
# @Time         : 2024/5/29 15:43
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 原生api


from meutils.pipe import *
from meutils.serving.fastapi.dependencies.auth import get_bearer_token, HTTPAuthorizationCredentials
from meutils.schemas.suno_types import SunoAIRequest, API_GENERATE_V2, API_FEED, API_BILLING_INFO

from fastapi import APIRouter, Depends

from suno.controllers.utils import api_feed, api_billing_info
from suno.controllers.utils import aapi_generate_v2

router = APIRouter()


@router.get(API_BILLING_INFO)  # check token
async def suno_api_billing_info(
        auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
):
    api_key = auth and auth.credentials or None

    return api_billing_info(api_key)


@router.post(API_GENERATE_V2)
async def suno_api_generate_v2(
        request: SunoAIRequest,
        auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
):
    logger.debug(request)

    api_key = auth and auth.credentials or None

    data = request.model_dump()

    task = await aapi_generate_v2(api_key, data)

    return task


@router.get(API_FEED)
async def suno_api_feed(
        ids: str,
        auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
):
    api_key = auth and auth.credentials or None

    return api_feed(api_key, ids)


if __name__ == '__main__':
    from meutils.serving.fastapi import App

    app = App()

    app.include_router(router, '/suno')

    app.run()
