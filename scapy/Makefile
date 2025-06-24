# 🚀 AEROSPACE SCADA & SECURITY SYSTEMS - Unified Makefile
# Comandos para gestión fácil del sistema SCADA y detector de protocolos inusuales

.PHONY: help install start start-dev start-simple stop clean test status scapy-help

# Variables
PYTHON := python3
VENV := scada_env
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python
CURRENT_DIR := $(shell basename $(CURDIR))

# Detectar si estamos en directorio scapy
ifeq ($(CURRENT_DIR),scapy)
    PROJECT_MODE := scapy
    PROJECT_NAME := Security Protocol Detector
else
    PROJECT_MODE := scada
    PROJECT_NAME := Aerospace SCADA System
endif

# Comando por defecto
help: ## 📚 Mostrar ayuda
	@echo "🚀 $(PROJECT_NAME)"
	@echo "=========================="
	@echo ""
ifeq ($(PROJECT_MODE),scapy)
	@echo "🛡️  DETECTOR DE PROTOCOLOS INUSUALES"
	@echo "   Herramientas de seguridad de red para detección de amenazas"
	@echo ""
	@echo "Comandos de Seguridad:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## 🛡️.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[31m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Comandos de Testing:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## 🧪.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[33m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🎯 Inicio rápido (Seguridad):"
	@echo "  make setup-security     # Configurar entorno de seguridad"
	@echo "  make detector-start     # Iniciar detector"
	@echo "  make test-sctp          # Validar detección SCTP"
	@echo ""
	@echo "⚠️  IMPORTANTE: Los comandos de testing generan tráfico de red"
	@echo "   Solo usar en entornos controlados"
else
	@echo "🚀 SISTEMA SCADA AEROESPACIAL"
	@echo "   Sistema de supervisión y control industrial"
	@echo ""
	@echo "Comandos SCADA:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## 🚀.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🎯 Inicio rápido (SCADA):"
	@echo "  make install            # Configurar entorno"
	@echo "  make start              # Lanzar sistema completo"
	@echo ""
	@echo "🛡️  Para herramientas de seguridad:"
	@echo "  cd scapy && make help   # Cambiar a modo seguridad"
endif
	@echo ""
	@echo "Comandos Generales:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## 🔧.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[32m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ============================================
# COMANDOS SCADA (Modo por defecto en raíz)
# ============================================

install: ## 🚀 Instalar entorno SCADA y dependencias
ifeq ($(PROJECT_MODE),scada)
	@echo "🛠️ Configurando entorno SCADA..."
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Entorno SCADA configurado correctamente"
	@echo "💡 Usa 'make start' para lanzar el sistema"
else
	@echo "⚠️  Estás en modo Security. Usa 'make setup-security' en su lugar"
endif

start: ## 🚀 Lanzar sistema SCADA completo (recomendado)
ifeq ($(PROJECT_MODE),scada)
	@echo "🚀 Lanzando Sistema SCADA completo..."
	$(PYTHON_VENV) launch_scada.py
else
	@echo "⚠️  Comando SCADA. Usa 'make detector-start' para seguridad"
endif

start-dev: ## 🚀 Lanzar SCADA en modo desarrollo
ifeq ($(PROJECT_MODE),scada)
	@echo "🔧 Lanzando en modo desarrollo..."
	$(PYTHON_VENV) dev_start.py
else
	@echo "⚠️  Comando SCADA. Usa 'make detector-dev' para seguridad"
endif

start-simple: ## 🚀 Lanzamiento SCADA simple (sin navegador automático)
ifeq ($(PROJECT_MODE),scada)
	@echo "⚡ Lanzamiento simple..."
	$(PYTHON_VENV) launch_scada.py --no-browser
else
	@echo "⚠️  Comando SCADA no disponible en modo Security"
endif

start-debug: ## 🚀 Lanzar SCADA con logs detallados
ifeq ($(PROJECT_MODE),scada)
	@echo "🐛 Lanzando con debug..."
	$(PYTHON_VENV) launch_scada.py --debug
else
	@echo "⚠️  Comando SCADA no disponible en modo Security"
endif

plc-only: ## 🚀 Solo PLC Virtual
ifeq ($(PROJECT_MODE),scada)
	@echo "🔧 Iniciando solo PLC Virtual..."
	$(PYTHON_VENV) core/simulation/virtual_plc.py
else
	@echo "⚠️  Comando SCADA no disponible en modo Security"
endif

hmi-only: ## 🚀 Solo HMI Web
ifeq ($(PROJECT_MODE),scada)
	@echo "🌐 Iniciando solo HMI Web..."
	$(PYTHON_VENV) run_hmi.py
else
	@echo "⚠️  Comando SCADA no disponible en modo Security"
endif

monitor: ## 🚀 Monitor de consola SCADA
ifeq ($(PROJECT_MODE),scada)
	@echo "📊 Iniciando monitor..."
	$(PYTHON_VENV) test_connection.py
else
	@echo "⚠️  Comando SCADA no disponible en modo Security"
endif

# ============================================
# COMANDOS SECURITY (Modo scapy)
# ============================================

setup-security: ## 🛡️ Configurar entorno de seguridad
ifeq ($(PROJECT_MODE),scapy)
	@echo "🛡️ Configurando entorno de seguridad..."
	@echo "🔍 Verificando permisos root..."
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "⚠️  Algunos comandos requieren sudo para captura de paquetes"; \
	fi
	$(PYTHON) -c "import scapy; print('✅ Scapy disponible')" 2>/dev/null || pip install scapy
	@echo "✅ Entorno de seguridad configurado"
	@echo "💡 Usa 'make detector-start' para iniciar detector"
else
	@echo "⚠️  Cambia al directorio scapy primero: cd scapy && make setup-security"
endif

detector-start: ## 🛡️ Iniciar detector de protocolos inusuales
ifeq ($(PROJECT_MODE),scapy)
	@echo "🛡️ Iniciando detector de protocolos inusuales..."
	@echo "⚠️  Requiere permisos de root para captura de paquetes"
	sudo $(PYTHON) unusual_protocol_detector.py
else
	@echo "⚠️  Cambia al directorio scapy primero: cd scapy && make detector-start"
endif

detector-dev: ## 🛡️ Detector en modo desarrollo (verbose)
ifeq ($(PROJECT_MODE),scapy)
	@echo "🔧 Detector en modo desarrollo..."
	sudo $(PYTHON) unusual_protocol_detector.py --verbose
else
	@echo "⚠️  Cambia al directorio scapy primero: cd scapy && make detector-dev"
endif

detector-test: ## 🛡️ Verificar instalación del detector
ifeq ($(PROJECT_MODE),scapy)
	@echo "🧪 Verificando detector..."
	sudo /opt/unusual-protocol-detector/start_detector.sh --test 2>/dev/null || \
	$(PYTHON) -c "from scapy.layers.inet import IP; from scapy.layers.sctp import SCTP; print('✅ Detector listo')"
else
	@echo "⚠️  Cambia al directorio scapy primero: cd scapy && make detector-test"
endif

test-sctp: ## 🧪 Generar tráfico SCTP de prueba
ifeq ($(PROJECT_MODE),scapy)
	@echo "🧪 Generando tráfico SCTP de prueba..."
	@echo "⚠️  IMPORTANTE: Solo usar en entornos controlados"
	@echo "⚠️  Este comando genera tráfico de red sintético"
	@read -p "¿Continuar? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	sudo $(PYTHON) sctp_test_generator.py
else
	@echo "⚠️  Cambia al directorio scapy primero: cd scapy && make test-sctp"
endif

test-simple: ## 🧪 Test simple de detección SCTP
ifeq ($(PROJECT_MODE),scapy)
	@echo "🧪 Test simple de detección..."
	sudo $(PYTHON) test_simple_sctp.py
else
	@echo "⚠️  Cambia al directorio scapy primero: cd scapy && make test-simple"
endif

analyze-logs: ## 🛡️ Analizar logs de seguridad
ifeq ($(PROJECT_MODE),scapy)
	@echo "📊 Analizando logs de seguridad..."
	sudo /opt/unusual-protocol-detector/analyze_logs.sh 2>/dev/null || \
	$(PYTHON) log_analyzer.py --log /var/log/unusual-protocols/unusual_protocols.log 2>/dev/null || \
	echo "⚠️  No se encontraron logs. Ejecuta el detector primero"
else
	@echo "⚠️  Cambia al directorio scapy primero: cd scapy && make analyze-logs"
endif

setup-production: ## 🛡️ Instalar detector en producción
ifeq ($(PROJECT_MODE),scapy)
	@echo "🛡️ Instalando detector en producción..."
	@echo "⚠️  Requiere permisos de administrador"
	sudo bash production_setup.sh
else
	@echo "⚠️  Cambia al directorio scapy primero: cd scapy && make setup-production"
endif

security-status: ## 🛡️ Estado del sistema de seguridad
ifeq ($(PROJECT_MODE),scapy)
	@echo "🛡️ Estado del Sistema de Seguridad:"
	@echo "=================================="
	@echo "🔍 Detector de Protocolos:"
	@pgrep -f "unusual_protocol_detector.py" >/dev/null && echo "   ✅ Ejecutándose" || echo "   ❌ Detenido"
	@echo "📊 Logs:"
	@if [ -f "/var/log/unusual-protocols/unusual_protocols.log" ]; then \
		echo "   ✅ Logs disponibles"; \
		echo "   📄 Último evento: $$(tail -1 /var/log/unusual-protocols/unusual_protocols.log 2>/dev/null | cut -d' ' -f1-2)"; \
	else \
		echo "   ❌ Sin logs"; \
	fi
	@echo "🔧 Interfaz de red:"
	@echo "   Monitoreando: en0 (por defecto)"
else
	@echo "⚠️  Cambia al directorio scapy primero: cd scapy && make security-status"
endif

# ============================================
# COMANDOS GENERALES (Ambos modos)
# ============================================

test: ## 🔧 Ejecutar tests apropiados
ifeq ($(PROJECT_MODE),scada)
	@echo "🧪 Ejecutando tests SCADA..."
	$(PYTHON_VENV) tests/minimal_test.py
	$(PYTHON_VENV) tests/simple_test.py
	@echo "✅ Tests SCADA completados"
else
	@echo "🧪 Ejecutando tests de seguridad..."
	@make detector-test
	@echo "✅ Tests de seguridad completados"
endif

stop: ## 🔧 Detener todos los procesos
ifeq ($(PROJECT_MODE),scada)
	@echo "🛑 Deteniendo procesos SCADA..."
	@pkill -f "virtual_plc.py" 2>/dev/null || true
	@pkill -f "run_hmi.py" 2>/dev/null || true
	@pkill -f "launch_scada.py" 2>/dev/null || true
	@echo "✅ Procesos SCADA detenidos"
else
	@echo "🛑 Deteniendo procesos de seguridad..."
	@sudo pkill -f "unusual_protocol_detector.py" 2>/dev/null || true
	@sudo launchctl unload /Library/LaunchDaemons/com.security.unusual-protocol-detector.plist 2>/dev/null || true
	@echo "✅ Procesos de seguridad detenidos"
endif

status: ## 🔧 Estado del sistema
ifeq ($(PROJECT_MODE),scada)
	@echo "📊 Estado del Sistema SCADA:"
	@echo "=========================="
	@echo "🔧 PLC Virtual:"
	@pgrep -f "virtual_plc.py" >/dev/null && echo "   ✅ Ejecutándose" || echo "   ❌ Detenido"
	@echo "🌐 HMI Web:"
	@pgrep -f "run_hmi.py" >/dev/null && echo "   ✅ Ejecutándose" || echo "   ❌ Detenido"
	@echo ""
	@echo "🌐 URLs:"
	@echo "   HMI Web: http://127.0.0.1:8050"
	@echo "   PLC Modbus: 127.0.0.1:5020"
else
	@make security-status
endif

clean: ## 🔧 Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
ifeq ($(PROJECT_MODE),scada)
	rm -f /tmp/scada_*.log 2>/dev/null || true
	rm -rf logs/*.log 2>/dev/null || true
else
	@echo "🧹 Limpiando logs de seguridad (requiere sudo)..."
	@sudo rm -f /var/log/unusual-protocols/*.log 2>/dev/null || true
endif
	@echo "✅ Limpieza completada"

clean-all: clean ## 🔧 Limpiar todo incluyendo entorno virtual
ifeq ($(PROJECT_MODE),scada)
	@echo "🗑️ Eliminando entorno virtual..."
	rm -rf $(VENV)
endif
	@echo "✅ Limpieza completa terminada"

upgrade: ## 🔧 Actualizar dependencias
ifeq ($(PROJECT_MODE),scada)
	@echo "⬆️ Actualizando dependencias SCADA..."
	$(PIP) install --upgrade -r requirements.txt
	@echo "✅ Dependencias SCADA actualizadas"
else
	@echo "⬆️ Actualizando dependencias de seguridad..."
	pip install --upgrade scapy
	@echo "✅ Dependencias de seguridad actualizadas"
endif

info: ## 🔧 Información del sistema
	@echo "ℹ️ Información del Sistema:"
	@echo "=========================="
	@echo "🐍 Python: $(shell $(PYTHON) --version)"
	@echo "📁 Directorio: $(shell pwd)"
	@echo "🏗️ Modo de proyecto: $(PROJECT_MODE)"
ifeq ($(PROJECT_MODE),scada)
	@echo "🏗️ Entorno virtual: $(VENV)"
	@echo "📦 Dependencias SCADA:"
	@$(PYTHON_VENV) -c "import pymodbus; print(f'   pymodbus: {pymodbus.__version__}')" 2>/dev/null || echo "   pymodbus: No instalado"
	@$(PYTHON_VENV) -c "import dash; print(f'   dash: {dash.__version__}')" 2>/dev/null || echo "   dash: No instalado"
	@$(PYTHON_VENV) -c "import plotly; print(f'   plotly: {plotly.__version__}')" 2>/dev/null || echo "   plotly: No instalado"
else
	@echo "📦 Dependencias de Seguridad:"
	@$(PYTHON) -c "import scapy; print(f'   scapy: {scapy.__version__}')" 2>/dev/null || echo "   scapy: No instalado"
	@echo "🔧 Sistema de detección:"
	@ls /opt/unusual-protocol-detector/ 2>/dev/null | head -3 | sed 's/^/   /' || echo "   Sin instalación de producción"
endif
	@echo ""
	@echo "🎯 Comandos principales:"
ifeq ($(PROJECT_MODE),scada)
	@echo "   make start              # Sistema SCADA completo"
	@echo "   cd scapy && make help   # Herramientas de seguridad"
else
	@echo "   make detector-start     # Detector de seguridad"
	@echo "   cd .. && make help      # Sistema SCADA"
endif

# ============================================
# COMANDOS DE DESARROLLO Y HELPERS
# ============================================

switch-to-scada: ## 🔧 Cambiar a modo SCADA
ifeq ($(PROJECT_MODE),scapy)
	@echo "🔄 Cambiando a modo SCADA..."
	@echo "cd .. && make help"
	@cd .. && make help
else
	@echo "✅ Ya estás en modo SCADA"
endif

switch-to-security: ## 🔧 Cambiar a modo Seguridad
ifeq ($(PROJECT_MODE),scada)
	@echo "🔄 Cambiando a modo Seguridad..."
	@if [ -d "scapy" ]; then \
		echo "cd scapy && make help"; \
		cd scapy && make help; \
	else \
		echo "❌ Directorio scapy no encontrado"; \
	fi
else
	@echo "✅ Ya estás en modo Seguridad"
endif

project-info: ## 🔧 Información completa del proyecto
	@echo "📋 INFORMACIÓN COMPLETA DEL PROYECTO"
	@echo "===================================="
	@echo ""
	@echo "🚀 Aerospace SCADA System (Directorio raíz):"
	@echo "   - Sistema de supervisión y control industrial"
	@echo "   - Interfaz HMI web con Dash/Plotly"
	@echo "   - Comunicación Modbus TCP con PLC virtual"
	@echo "   - Simulación de sistemas aeroespaciales"
	@echo ""
	@echo "🛡️ Unusual Protocol Detector (Directorio scapy):"
	@echo "   - Detector de protocolos inusuales en tiempo real"
	@echo "   - Detección de amenazas SCTP, GRE, ESP, OSPF"
	@echo "   - Clasificación inteligente de tráfico"
	@echo "   - Despliegue distribuido con ZeroMQ (roadmap)"
	@echo ""
	@echo "🎯 Para empezar:"
	@echo "   SCADA:     make install && make start"
	@echo "   Security:  cd scapy && make setup-security && make detector-start"

# Configuraciones especiales
.ONESHELL:
.SHELLFLAGS := -e -c

# Verificar que el entorno virtual existe para comandos SCADA que lo necesitan
$(PYTHON_VENV):
	@echo "❌ Error: Entorno virtual no encontrado"
	@echo "💡 Ejecuta: make install"
	@exit 1