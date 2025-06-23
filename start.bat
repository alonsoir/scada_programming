@echo off
REM 🚀 AEROSPACE SCADA - Windows Start Script

echo 🚀 Iniciando Sistema SCADA Aeroespacial...
echo ============================================

REM Verificar entorno virtual
if not defined VIRTUAL_ENV (
    echo ⚠️  Activando entorno virtual...
    if exist "scada_env\Scripts\activate.bat" (
        call scada_env\Scripts\activate.bat
        echo ✅ Entorno virtual activado
    ) else (
        echo ❌ Error: No se encuentra scada_env\
        echo 💡 Ejecuta: python -m venv scada_env
        pause
        exit /b 1
    )
)

REM Verificar dependencias
echo 🔍 Verificando dependencias...
python -c "import pymodbus, dash, plotly" 2>nul
if errorlevel 1 (
    echo ❌ Error: Dependencias faltantes
    echo 💡 Ejecuta: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Dependencias verificadas

REM Crear directorio para logs
if not exist "logs" mkdir logs

REM Iniciar PLC Virtual
echo 🔧 Iniciando PLC Virtual...
start /B "PLC Virtual" python core\simulation\virtual_plc.py > logs\plc.log 2>&1

REM Esperar a que inicie
timeout /t 3 /nobreak > nul

REM Iniciar HMI Web
echo 🌐 Iniciando HMI Web...
start /B "HMI Web" python run_hmi.py > logs\hmi.log 2>&1

REM Esperar a que inicie
timeout /t 4 /nobreak > nul

REM Abrir navegador
echo 🌍 Abriendo navegador...
timeout /t 2 /nobreak > nul
start http://127.0.0.1:8050

REM Mostrar estado
echo.
echo ============================================
echo 📊 SISTEMA SCADA EJECUTÁNDOSE
echo ============================================
echo 🔧 PLC Virtual: 127.0.0.1:5020
echo 🌐 HMI Web: http://127.0.0.1:8050
echo 📋 Logs: logs\plc.log, logs\hmi.log
echo ============================================
echo 🎯 Presiona cualquier tecla para detener
echo.

REM Esperar input del usuario
pause > nul

REM Detener procesos
echo 🛑 Deteniendo sistema SCADA...
taskkill /F /FI "WindowTitle eq PLC Virtual*" 2>nul
taskkill /F /FI "WindowTitle eq HMI Web*" 2>nul
echo ✅ Sistema detenido
echo 👋 ¡Hasta la próxima!
pause