#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : app.py
# @Time         : 2023/12/15 15:13
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import os

from meutils.pipe import *
from meutils.notice.feishu import *

send_message(os.getenv("API_KEY"))

from meutils.serving.fastapi import App
from chatllm.api.routers import chat_completions

app = App()

app.include_router(chat_completions.router, '/v1')

if __name__ == '__main__':
    app.run(port=39999)


# python3 -m meutils.clis.server gunicorn-run smooth_app:app --pythonpath python3 --port 39006
