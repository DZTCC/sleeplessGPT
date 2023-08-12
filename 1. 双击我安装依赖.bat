@echo off
cd /d %~dp0
pip install -r requirements.txt
python print('安装完成')