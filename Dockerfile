# 使用官方python基础镜像
FROM python:3.10-slim
#FROM api-reverse

# 创建工作目录
WORKDIR /app

# 复制当前目录下的所有文件到工作目录
COPY . .

# 安装python依赖
RUN pip install --no-cache-dir -r requirements.txt -U -i https://mirror.baidu.com/pypi/simple
RUN pip install --no-cache-dir chatllm --no-deps -U # -i https://mirror.baidu.com/pypi/simple

# 暴露端口
EXPOSE 8000

# 容器启动时运行命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

#  => => naming to docker.io/library/api-reverse                                                                                                                                                                                     0.0s
# docker run -p 8000:8000 -e GITHUB_COPILOT_TOKEN=123 chatllm/api-reverse
# docker push chatllm/api-reverse
# docker run -d -p 39999:8000 chatllm/api-reverse

# docker tag apitool chatllm/api-tokens:chatfire # 重命名

#docker run --name apitool -d -p 39966:80 chatllm/api-tokens

