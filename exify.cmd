@echo off

IF EXIST build (call rmdir /S /Q build)

IF EXIST dist (call rmdir /S /Q dist)

IF EXIST *.spec (call del /S /Q /F *.spec)

call pyinstaller --noconfirm --clean -n crypt console_app.py

@echo on