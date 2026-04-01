@echo off
echo [ATTENTION] Memulai Setup Environment COGNIFY...

:: 1. Setup Cloud Backend
echo [1/3] Membangun venv untuk Cloud Backend...
cd cloud_backend
python -m venv venv-cloud
call venv-cloud\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements-cloud.txt
python -m spacy download id_core_web_sm
call venv-cloud\Scripts\deactivate.bat
cd ..

:: 2. Setup Edge Runtime
echo [2/3] Membangun venv untuk Edge Runtime (LattePanda)...
cd edge_runtime
python -m venv venv-edge
call venv-edge\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements-edge.txt
call venv-edge\Scripts\deactivate.bat
cd ..

:: 3. Setup AI Engine & MLOps
echo [3/3] Membangun venv untuk AI Engine & Training...
cd ai_engine
python -m venv venv-train
call venv-train\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements-train.txt
call venv-train\Scripts\deactivate.bat
cd ..

echo Selesai! Semua environment COGNIFY berhasil diinstal dan diisolasi.
pause