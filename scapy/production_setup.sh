#!/bin/bash
# Script de configuración para producción del detector SCTP

set -e

echo "🛡️  Configurando Detector de Protocolos Inusuales para Producción"
echo "=================================================================="

# Verificar permisos de root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script debe ejecutarse como root (sudo)"
   echo "   sudo $0"
   exit 1
fi

echo "✅ Permisos de root confirmados"

# Verificar dependencias
echo "🔍 Verificando dependencias..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado"
    exit 1
fi

if ! python3 -c "import scapy" 2>/dev/null; then
    echo "❌ Scapy no instalado"
    echo "   Instalar con: pip3 install scapy"
    exit 1
fi

echo "✅ Dependencias verificadas"

# Detectar sistema operativo
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    INTERFACE_DEFAULT="en0"
    SERVICE_DIR="/Library/LaunchDaemons"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    INTERFACE_DEFAULT="eth0"
    SERVICE_DIR="/etc/systemd/system"
else
    echo "⚠️  Sistema operativo no completamente soportado: $OSTYPE"
    OS="Unknown"
    INTERFACE_DEFAULT="eth0"
fi

echo "📊 Sistema detectado: $OS"

# Configurar directorios
INSTALL_DIR="/opt/unusual-protocol-detector"
LOG_DIR="/var/log/unusual-protocols"
CONFIG_DIR="/etc/unusual-protocols"

echo "📁 Creando directorios del sistema..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$CONFIG_DIR"

# Detectar directorio de los archivos
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR"

# Si estamos en el directorio padre, buscar en scapy/
if [[ ! -f "$SOURCE_DIR/unusual_protocol_detector.py" ]]; then
    if [[ -f "$SOURCE_DIR/scapy/unusual_protocol_detector.py" ]]; then
        SOURCE_DIR="$SOURCE_DIR/scapy"
        echo "📁 Archivos encontrados en: $SOURCE_DIR"
    else
        echo "❌ Error: No se encuentran los archivos del detector"
        echo "   Buscando unusual_protocol_detector.py en:"
        echo "   - $SOURCE_DIR/unusual_protocol_detector.py"
        echo "   - $SOURCE_DIR/scapy/unusual_protocol_detector.py"
        exit 1
    fi
fi

# Copiar archivos (desde la ubicación detectada)
echo "📋 Copiando archivos del detector..."
if [[ -f "$SOURCE_DIR/unusual_protocol_detector.py" ]]; then
    cp "$SOURCE_DIR/unusual_protocol_detector.py" "$INSTALL_DIR/"
    echo "  ✅ unusual_protocol_detector.py copiado"
else
    echo "  ❌ unusual_protocol_detector.py no encontrado"
    exit 1
fi

if [[ -f "$SOURCE_DIR/log_analyzer.py" ]]; then
    cp "$SOURCE_DIR/log_analyzer.py" "$INSTALL_DIR/"
    echo "  ✅ log_analyzer.py copiado"
else
    echo "  ⚠️  log_analyzer.py no encontrado - creando básico"
    # Crear un analizador básico si no existe
    cat > "$INSTALL_DIR/log_analyzer.py" << 'EOF'
#!/usr/bin/env python3
print("Analizador de logs básico - versión simplificada")
EOF
fi

# NO copiar herramientas de testing/generación
echo "🔒 NOTA DE SEGURIDAD: Los generadores de tráfico SCTP NO se instalan en producción"
echo "   Solo para desarrollo/testing en: $SOURCE_DIR/sctp_test_generator.py"
echo "   Solo para desarrollo/testing en: $SOURCE_DIR/test_simple_sctp.py"

# Verificar que se copiaron correctamente
if [[ ! -f "$INSTALL_DIR/unusual_protocol_detector.py" ]]; then
    echo "❌ Error: No se pudo copiar el detector principal"
    exit 1
fi

# Configurar permisos
echo "🔐 Configurando permisos..."
if [[ "$OS" == "macOS" ]]; then
    chown -R root:wheel "$INSTALL_DIR"
    chown -R root:wheel "$LOG_DIR"
    chown -R root:wheel "$CONFIG_DIR"
else
    chown -R root:root "$INSTALL_DIR"
    chown -R root:root "$LOG_DIR"
    chown -R root:root "$CONFIG_DIR"
fi

chmod 755 "$INSTALL_DIR"/*.py
chmod 755 "$LOG_DIR"
chmod 644 "$CONFIG_DIR"/*.conf 2>/dev/null || true

# Crear archivo de configuración
echo "⚙️  Creando configuración..."
cat > "$CONFIG_DIR/detector.conf" << EOF
# Configuración del Detector de Protocolos Inusuales
INTERFACE=$INTERFACE_DEFAULT
LOG_LEVEL=INFO
ENABLE_STATS=true
STATS_INTERVAL=300
ENABLE_EMAIL_ALERTS=false
EMAIL_RECIPIENTS=""
MAX_LOG_SIZE=100MB
LOG_ROTATION_DAYS=30
EOF

# Crear script de inicio
echo "🚀 Creando script de inicio..."
cat > "$INSTALL_DIR/start_detector.sh" << 'EOF'
#!/bin/bash
# Script de inicio del detector

# Cargar configuración si existe
if [[ -f /etc/unusual-protocols/detector.conf ]]; then
    source /etc/unusual-protocols/detector.conf
else
    # Valores por defecto
    INTERFACE="en0"
    LOG_LEVEL="INFO"
fi

cd /opt/unusual-protocol-detector

# Verificar que el detector existe
if [[ ! -f "unusual_protocol_detector.py" ]]; then
    echo "❌ Error: unusual_protocol_detector.py no encontrado"
    exit 1
fi

# Modo de prueba
if [[ "$1" == "--test" ]]; then
    echo "🧪 Modo de prueba - verificando componentes..."
    python3 -c "
from scapy.layers.inet import IP
from scapy.layers.sctp import SCTP
print('✅ Scapy SCTP disponible')
print('✅ Sistema listo para detección')
    "
    exit 0
fi

# Configurar logging
export PYTHONUNBUFFERED=1
mkdir -p /var/log/unusual-protocols

echo "🔍 Iniciando detector de protocolos inusuales..."
echo "   Interfaz: $INTERFACE"
echo "   Log Level: $LOG_LEVEL"
echo "   Logs en: /var/log/unusual-protocols/"

# Iniciar detector
python3 unusual_protocol_detector.py 2>&1 | tee -a /var/log/unusual-protocols/detector.log
EOF

chmod +x "$INSTALL_DIR/start_detector.sh"

# Crear servicio según el OS
if [[ "$OS" == "macOS" ]]; then
    echo "🍎 Configurando servicio para macOS (launchd)..."

    SERVICE_FILE="$SERVICE_DIR/com.security.unusual-protocol-detector.plist"

    cat > "$SERVICE_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.security.unusual-protocol-detector</string>
    <key>ProgramArguments</key>
    <array>
        <string>$INSTALL_DIR/start_detector.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/unusual-protocols/service.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/unusual-protocols/service.error.log</string>
    <key>UserName</key>
    <string>root</string>
</dict>
</plist>
EOF

    # Configurar permisos del servicio
    chmod 644 "$SERVICE_FILE"
    chown root:wheel "$SERVICE_FILE"

    echo ""
    echo "📋 COMANDOS PARA macOS:"
    echo "   Cargar servicio:    sudo launchctl load $SERVICE_FILE"
    echo "   Descargar servicio: sudo launchctl unload $SERVICE_FILE"
    echo "   Ver estado:         sudo launchctl list | grep unusual-protocol"
    echo "   Ver logs:           tail -f /var/log/unusual-protocols/service.log"

elif [[ "$OS" == "Linux" ]]; then
    echo "🐧 Configurando servicio para Linux (systemd)..."
    cat > "$SERVICE_DIR/unusual-protocol-detector.service" << EOF
[Unit]
Description=Unusual Protocol Detector
After=network.target

[Service]
Type=simple
User=root
ExecStart=$INSTALL_DIR/start_detector.sh
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    echo "📋 Para iniciar el servicio:"
    echo "   sudo systemctl enable unusual-protocol-detector"
    echo "   sudo systemctl start unusual-protocol-detector"
    echo "📋 Para ver logs:"
    echo "   sudo journalctl -u unusual-protocol-detector -f"
fi

# Crear script de análisis de logs
echo "📊 Configurando análisis automático de logs..."
cat > "$INSTALL_DIR/analyze_logs.sh" << 'EOF'
#!/bin/bash
# Script de análisis automático de logs

LOG_FILE="/var/log/unusual-protocols/unusual_protocols.log"
REPORT_DIR="/var/log/unusual-protocols/reports"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$REPORT_DIR"

echo "📊 Generando reporte de seguridad..."

# Verificar si existe el archivo de log
if [[ ! -f "$LOG_FILE" ]]; then
    echo "⚠️  Archivo de log no encontrado: $LOG_FILE"
    echo "   El detector debe ejecutarse primero para generar logs"
    echo "   Ejecutar: sudo python3 /opt/unusual-protocol-detector/unusual_protocol_detector.py"
    exit 1
fi

# Generar reporte básico (sin dependencia de jq)
python3 /opt/unusual-protocol-detector/log_analyzer.py \
    --log "$LOG_FILE" > "$REPORT_DIR/security_report_$DATE.txt"

echo "✅ Reporte guardado en: $REPORT_DIR/security_report_$DATE.txt"

# Verificar alertas críticas sin jq
if [[ -f "$LOG_FILE" ]]; then
    CRITICAL_COUNT=$(grep -c "HIGH ALERT" "$LOG_FILE" 2>/dev/null || echo "0")
    TOTAL_ALERTS=$(grep -c "ALERT" "$LOG_FILE" 2>/dev/null || echo "0")

    echo ""
    echo "📊 RESUMEN RÁPIDO:"
    echo "   Total de alertas: $TOTAL_ALERTS"
    echo "   Alertas críticas: $CRITICAL_COUNT"

    if [[ "$CRITICAL_COUNT" -gt 0 ]]; then
        echo ""
        echo "🚨 ÚLTIMAS ALERTAS CRÍTICAS:"
        grep "HIGH ALERT" "$LOG_FILE" | tail -3
    fi
else
    echo "⚠️  No se encontraron logs para analizar"
fi
EOF

chmod +x "$INSTALL_DIR/analyze_logs.sh"

# Configurar cron para análisis automático
echo "⏰ Configurando análisis automático cada hora..."
if [[ "$OS" == "macOS" ]]; then
    # En macOS, usar crontab pero verificar permisos
    echo "⚠️  En macOS, puede requerirse autorización de 'Acceso total al disco' para cron"
    echo "   Ve a: Preferencias del Sistema > Seguridad y Privacidad > Privacidad > Acceso total al disco"
    echo "   Añade: /usr/sbin/cron"
fi

# Añadir entrada de cron (compatible con macOS y Linux)
(crontab -l 2>/dev/null | grep -v "analyze_logs.sh"; echo "0 * * * * $INSTALL_DIR/analyze_logs.sh") | crontab -

# Crear rotación de logs
if [[ "$OS" == "Linux" ]]; then
    cat > "/etc/logrotate.d/unusual-protocols" << EOF
/var/log/unusual-protocols/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        systemctl reload unusual-protocol-detector || true
    endscript
}
EOF
fi

echo ""
echo "✅ INSTALACIÓN COMPLETADA"
echo "========================="
echo ""
echo "📁 Archivos instalados en: $INSTALL_DIR"
echo "📊 Logs en: $LOG_DIR"
echo "⚙️  Configuración en: $CONFIG_DIR/detector.conf"
echo ""

# Verificar instalación
echo "🔍 VERIFICACIÓN DE INSTALACIÓN:"
if [[ -f "$INSTALL_DIR/unusual_protocol_detector.py" ]]; then
    echo "  ✅ Detector principal instalado"
else
    echo "  ❌ Detector principal NO instalado"
fi

if [[ -f "$INSTALL_DIR/log_analyzer.py" ]]; then
    echo "  ✅ Analizador de logs instalado"
else
    echo "  ❌ Analizador de logs NO instalado"
fi

if [[ -f "$CONFIG_DIR/detector.conf" ]]; then
    echo "  ✅ Configuración creada"
else
    echo "  ❌ Configuración NO creada"
fi

echo ""
echo "🧪 VALIDACIÓN DEL SISTEMA:"
echo "   Verificar instalación: sudo $INSTALL_DIR/start_detector.sh --test"
echo "   Ejecutar detector:      sudo $INSTALL_DIR/start_detector.sh"
echo ""
echo "🚀 COMANDOS ÚTILES PARA macOS:"
echo "   # Monitorear en tiempo real:"
echo "   sudo python3 $INSTALL_DIR/unusual_protocol_detector.py"
echo ""
echo "   # Ver interfaces disponibles:"
echo "   ifconfig | grep -E '^[a-z]'"
echo ""
echo "   # Monitorear logs:"
echo "   tail -f $LOG_DIR/unusual_protocols.log"
echo ""
echo "   # Generar reportes de seguridad:"
echo "   sudo $INSTALL_DIR/analyze_logs.sh"
echo ""
echo "🔒 NOTA DE SEGURIDAD:"
echo "   - Los generadores de tráfico SCTP permanecen en desarrollo"
echo "   - Ubicación: ~/g/scada_programming/scapy/"
echo "   - Solo usar para testing controlado y validación"
echo "   - NO ejecutar en producción sin supervisión"
echo ""
echo "🚀 PRÓXIMOS PASOS:"
echo "1. Editar configuración si es necesario:"
echo "   sudo nano $CONFIG_DIR/detector.conf"
echo ""
echo "2. Iniciar el detector:"
if [[ "$OS" == "macOS" ]]; then
    echo "   # Como servicio (recomendado):"
    echo "   sudo launchctl load $SERVICE_DIR/com.security.unusual-protocol-detector.plist"
    echo "   # O manualmente:"
    echo "   sudo $INSTALL_DIR/start_detector.sh"
elif [[ "$OS" == "Linux" ]]; then
    echo "   sudo systemctl enable unusual-protocol-detector"
    echo "   sudo systemctl start unusual-protocol-detector"
fi
echo ""
echo "3. Verificar funcionamiento:"
echo "   tail -f $LOG_DIR/unusual_protocols.log"
echo ""
echo "4. Configurar alertas (opcional):"
echo "   # Editar $INSTALL_DIR/analyze_logs.sh"
echo "   # Añadir notificaciones por email/Slack"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Este es un sistema de DETECCIÓN, no prevención"
echo "   - Revisa logs regularmente para amenazas"
echo "   - Los tests de validación están en ~/g/scada_programming/scapy/"
echo "   - Solo usa tests en entornos controlados"