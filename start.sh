#!/bin/bash
# 🚀 AEROSPACE SCADA - Quick Start Script
# Para macOS/Linux

echo "🚀 Iniciando Sistema SCADA Aeroespacial..."
echo "============================================"

# Verificar entorno virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Activando entorno virtual..."
    if [ -d "scada_env" ]; then
        source scada_env/bin/activate
        echo "✅ Entorno virtual activado"
    else
        echo "❌ Error: No se encuentra scada_env/"
        echo "💡 Ejecuta: python3 -m venv scada_env && source scada_env/bin/activate"
        exit 1
    fi
fi

# Verificar dependencias
echo "🔍 Verificando dependencias..."
python -c "import pymodbus, dash, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Dependencias faltantes"
    echo "💡 Ejecuta: pip install -r requirements.txt"
    exit 1
fi
echo "✅ Dependencias verificadas"

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo sistema SCADA..."

    if [ ! -z "$PLC_PID" ] && kill -0 $PLC_PID 2>/dev/null; then
        echo "   Deteniendo PLC Virtual (PID: $PLC_PID)"
        kill $PLC_PID 2>/dev/null
    fi

    if [ ! -z "$HMI_PID" ] && kill -0 $HMI_PID 2>/dev/null; then
        echo "   Deteniendo HMI Web (PID: $HMI_PID)"
        kill $HMI_PID 2>/dev/null
    fi

    # Esperar un momento para terminación limpia
    sleep 2

    # Forzar si es necesario
    if [ ! -z "$PLC_PID" ] && kill -0 $PLC_PID 2>/dev/null; then
        kill -9 $PLC_PID 2>/dev/null
    fi

    if [ ! -z "$HMI_PID" ] && kill -0 $HMI_PID 2>/dev/null; then
        kill -9 $HMI_PID 2>/dev/null
    fi

    echo "✅ Sistema detenido"
    echo "👋 ¡Hasta la próxima!"
    exit 0
}

# Configurar trap para limpieza
trap cleanup SIGINT SIGTERM

# Iniciar PLC Virtual
echo "🔧 Iniciando PLC Virtual..."
python core/simulation/virtual_plc.py > /tmp/scada_plc.log 2>&1 &
PLC_PID=$!

# Esperar a que inicie
sleep 3

# Verificar que el PLC esté ejecutándose
if ! kill -0 $PLC_PID 2>/dev/null; then
    echo "❌ Error: PLC Virtual no pudo iniciarse"
    echo "📋 Log: /tmp/scada_plc.log"
    exit 1
fi

echo "✅ PLC Virtual iniciado (PID: $PLC_PID)"

# Iniciar HMI Web
echo "🌐 Iniciando HMI Web..."
python run_hmi.py > /tmp/scada_hmi.log 2>&1 &
HMI_PID=$!

# Esperar a que inicie
sleep 4

# Verificar que el HMI esté ejecutándose
if ! kill -0 $HMI_PID 2>/dev/null; then
    echo "❌ Error: HMI Web no pudo iniciarse"
    echo "📋 Log: /tmp/scada_hmi.log"
    cleanup
    exit 1
fi

echo "✅ HMI Web iniciado (PID: $HMI_PID)"

# Abrir navegador (macOS)
if command -v open >/dev/null 2>&1; then
    echo "🌍 Abriendo navegador..."
    sleep 2
    open http://127.0.0.1:8050
elif command -v xdg-open >/dev/null 2>&1; then
    echo "🌍 Abriendo navegador..."
    sleep 2
    xdg-open http://127.0.0.1:8050
fi

# Mostrar estado
echo ""
echo "============================================"
echo "📊 SISTEMA SCADA EJECUTÁNDOSE"
echo "============================================"
echo "🔧 PLC Virtual: 127.0.0.1:5020"
echo "🌐 HMI Web: http://127.0.0.1:8050"
echo "📋 Logs: /tmp/scada_plc.log, /tmp/scada_hmi.log"
echo "============================================"
echo "🎯 Presiona Ctrl+C para detener"
echo ""

# Mantener script ejecutándose y monitorear procesos
while true; do
    sleep 5

    # Verificar que ambos procesos sigan ejecutándose
    if ! kill -0 $PLC_PID 2>/dev/null; then
        echo "❌ PLC Virtual terminó inesperadamente"
        cleanup
        exit 1
    fi

    if ! kill -0 $HMI_PID 2>/dev/null; then
        echo "❌ HMI Web terminó inesperadamente"
        cleanup
        exit 1
    fi
done