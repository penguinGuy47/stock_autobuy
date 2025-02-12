@echo off
cd C:\Users\%USERNAME%\Desktop\Code\Python\autobuy || (echo "Failed to navigate to the project directory" & pause & exit)
call .\env\Scripts\activate || (echo "Failed to activate virtual environment" & pause & exit)
cd frontend || (echo "Failed to navigate to the frontend directory" & pause & exit)
npm start || (echo "Failed to start npm" & pause & exit)
pause
