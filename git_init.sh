#!/usr/bin/env bash

#git init
git add *
git add .github/workflows/docker-image.yml

git commit -m "init"

#git rm  -r dist
#git remote add origin git@github.com:yuanjie-ai/MeUtils.git
#git branch -M master
git push -u origin main -f
# git remote remove origin

#git config --global user.name Betterme
#git config --global user.email 313303303@qq.com
