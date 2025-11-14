#!/bin/sh
python -c "import os; import subprocess; subprocess.run(['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', os.getenv('PORT', '8000')])"
