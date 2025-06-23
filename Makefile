# 🚀 AEROSPACE SCADA SYSTEM - Makefile
# Comandos para gestión fácil del sistema SCADA

.PHONY: help install start start-dev start-simple stop clean test status

# Variables
PYTHON := python3
VENV := scada_env
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python

# Comando por defecto
help: ## 📚 Mostrar ayuda
	@echo "🚀 AEROSPACE SCADA SYSTEM"
	@echo "=========================="
	@echo ""
	@echo "Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🎯 Inicio rápido:"
	@echo "  make install    # Configurar entorno"
	@echo "  make start      # Lanzar sistema completo"
	@echo ""

install: ## 🛠️ Instalar entorno y dependencias
	@echo "🛠️ Configurando entorno SCADA..."
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Entorno configurado correctamente"
	@echo "💡 Usa 'make start' para lanzar el sistema"

start: ## 🚀 Lanzar sistema completo (recomendado)
	@echo "🚀 Lanzando Sistema SCADA completo..."
	$(PYTHON_VENV) launch_scada.py

start-dev: ## 🔧 Lanzar en modo desarrollo (terminales separadas)
	@echo "🔧 Lanzando en modo desarrollo..."
	$(PYTHON_VENV) dev_start.py

start-simple: ## ⚡ Lanzamiento simple (sin navegador automático)
	@echo "⚡ Lanzamiento simple..."
	$(PYTHON_VENV) launch_scada.py --no-browser

start-debug: ## 🐛 Lanzar con logs detallados
	@echo "🐛 Lanzando con debug..."
	$(PYTHON_VENV) launch_scada.py --debug

plc-only: ## 🔧 Solo PLC Virtual
	@echo "🔧 Iniciando solo PLC Virtual..."
	$(PYTHON_VENV) core/simulation/virtual_plc.py

hmi-only: ## 🌐 Solo HMI Web
	@echo "🌐 Iniciando solo HMI Web..."
	$(PYTHON_VENV) run_hmi.py

monitor: ## 📊 Monitor de consola
	@echo "📊 Iniciando monitor..."
	$(PYTHON_VENV) test_connection.py

test: ## 🧪 Ejecutar tests
	@echo "🧪 Ejecutando tests..."
	$(PYTHON_VENV) tests/minimal_test.py
	$(PYTHON_VENV) tests/simple_test.py
	@echo "✅ Tests completados"

stop: ## 🛑 Detener todos los procesos SCADA
	@echo "🛑 Deteniendo procesos SCADA..."
	@pkill -f "virtual_plc.py" 2>/dev/null || true
	@pkill -f "run_hmi.py" 2>/dev/null || true
	@pkill -f "launch_scada.py" 2>/dev/null || true
	@echo "✅ Procesos detenidos"

status: ## 📊 Estado del sistema
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

clean: ## 🧹 Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -f /tmp/scada_*.log 2>/dev/null || true
	rm -rf logs/*.log 2>/dev/null || true
	@echo "✅ Limpieza completada"

clean-all: clean ## 🗑️ Limpiar todo incluyendo entorno virtual
	@echo "🗑️ Eliminando entorno virtual..."
	rm -rf $(VENV)
	@echo "✅ Limpieza completa terminada"

upgrade: ## ⬆️ Actualizar dependencias
	@echo "⬆️ Actualizando dependencias..."
	$(PIP) install --upgrade -r requirements.txt
	@echo "✅ Dependencias actualizadas"

info: ## ℹ️ Información del sistema
	@echo "ℹ️ Información del Sistema SCADA:"
	@echo "================================"
	@echo "🐍 Python: $(shell $(PYTHON) --version)"
	@echo "📁 Directorio: $(shell pwd)"
	@echo "🏗️ Entorno virtual: $(VENV)"
	@echo "📦 Dependencias:"
	@$(PYTHON_VENV) -c "import pymodbus; print(f'   pymodbus: {pymodbus.__version__}')" 2>/dev/null || echo "   pymodbus: No instalado"
	@$(PYTHON_VENV) -c "import dash; print(f'   dash: {dash.__version__}')" 2>/dev/null || echo "   dash: No instalado"
	@$(PYTHON_VENV) -c "import plotly; print(f'   plotly: {plotly.__version__}')" 2>/dev/null || echo "   plotly: No instalado"

# Configuraciones especiales
.ONESHELL:
.SHELLFLAGS := -e -c

# Verificar que el entorno virtual existe para comandos que lo necesitan
$(PYTHON_VENV):
	@echo "❌ Error: Entorno virtual no encontrado"
	@echo "💡 Ejecuta: make install"
	@exit 1