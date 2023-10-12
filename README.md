webui-user.batのCOMMANDLINE_ARGSに--apiを追加
```
@echo off

set PYTHON=
set GIT=
set VENV_DIR=
@REM set COMMANDLINE_ARGS=
set COMMANDLINE_ARGS=--api --listen

call webui.bat
```