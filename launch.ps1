# Usage:
# cd C:\Users\$env:USERNAME
# & "\\wsl$\Ubuntu\home\noe\dev\rly\launch.ps1"

$projectRoot = "\\wsl$\Ubuntu\home\noe\dev\rly"
$pythonExe = "C:\Users\noevh\Documents\MEGA\VsCode\rly-env\.venv\Scripts\python.exe"

& $pythonExe -c @"
import sys
sys.path.insert(0, r'$projectRoot\src')
from rly.main import start_server
import threading, webview
t = threading.Thread(target=start_server, daemon=True)
t.start()
webview.create_window('rly', 'http://127.0.0.1:8000', width=1000, height=700)
webview.start()
"@