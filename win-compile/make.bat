chdir ..
IF NOT EXIST .\..\ect GOTO ERROR
pyinstaller --noconsole --path=.\..\ect --hidden-import sklearn.neighbors.typedefs ect.py
"C:\Users\Dev\AppData\Local\Programs\Python\Python36\Lib\site-packages\PyQt5\Qt\bin"
copy "C:\Users\Dev\AppData\Local\Programs\Python\Python36\Lib\site-packages\PyQt5\Qt\bin\*" ".\dist\ect\"
xcopy ".\ui" ".\dist\ect\ui\*" /s /e
copy ".\res.qrc" ".\dist\ect\*"
copy ".\res_rc.py" ".\dist\ect\*"
copy ".\win-compile\matplotlibrc" ".\dist\ect\mpl-data\" /Y
xcopy ".\data" ".\dist\ect\data\*" /s /e
rename ".\dist\ect\ect.exe" "INDACT.exe"
rename ".\dist\ect" "INDACT"
exit
:ERROR
echo "you forgot to copy ect module with clustering libs"