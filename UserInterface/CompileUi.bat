@ECHO OFF
SET InputFilePath=%CD%\%1.ui
SET OutputFilePath=%CD%\%1.py

pyuic5 -x %InputFilePath% -o %OutputFilePath%

pause