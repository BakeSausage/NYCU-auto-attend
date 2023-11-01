cd %~dp0
if not exist config.ini (pip install -r requirements.txt)
python auto-attend.py
pause
