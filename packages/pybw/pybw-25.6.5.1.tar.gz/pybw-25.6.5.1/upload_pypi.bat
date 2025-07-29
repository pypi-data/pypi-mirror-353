@echo off

echo.
echo ***********************
echo * Confirm to continue *
echo ***********************
echo.
pause
echo.

echo [1] remove old files ...
rmdir /s /q build dist pybw.egg-info > nul
rmdir /s /q pybw > nul
xcopy /e /h /i ..\pybw pybw > nul
echo.

echo [2] run setup.py ...
python setup.py sdist bdist_wheel > nul
echo.

echo [3] upload to pypi
echo.
twine upload dist/* 
echo.

pause
