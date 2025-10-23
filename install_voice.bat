@echo off
echo ================================================
echo Thames Water Voice Chatbot - Installation
echo ================================================
echo.

echo Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing Python packages...
pip install streamlit>=1.28.0
pip install audio-recorder-streamlit
pip install SpeechRecognition
pip install gTTS
pip install pydub

echo.
echo NOTE: PyAudio installation on Windows may require manual steps:
echo 1. Download the appropriate .whl file from:
echo    https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
echo 2. Install with: pip install downloaded_file.whl
echo.

echo.
echo ================================================
echo Installation complete!
echo ================================================
echo.
echo To run the voice chatbot:
echo   streamlit run voice_chatbot.py
echo.
echo To run the text-only chatbot:
echo   streamlit run water_company_chatbot.py
echo.
echo ================================================
pause
