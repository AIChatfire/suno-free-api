#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : asr
# @Time         : 2024/5/20 13:37
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

# from funasr import AutoModel
# # paraformer-zh is a multi-functional asr model
# # use vad, punc, spk or not as you need
# model = AutoModel(model="paraformer-zh",  vad_model="fsmn-vad",  punc_model="ct-punc",
#                   # spk_model="cam++",
#                   )
# res = model.generate(input=f"{model.model_path}/example/asr_example.wav",
#                      batch_size_s=300,
#                      hotword='魔搭')
# print(res)


print(pd.read_html("https://api.chatfire.cn/pricing"))
