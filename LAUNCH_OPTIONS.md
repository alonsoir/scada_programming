# 🚀 OPCIONES DE LANZAMIENTO - AEROSPACE SCADA

Este documento describe todas las formas disponibles de lanzar el sistema SCADA.

## 📋 Resumen de Opciones

| Método | Archivo | Descripción | Mejor Para |
|--------|---------|-------------|------------|
| **🚀 Launcher Principal** | `launch_scada.py` | Script Python completo | Uso general |
| **⚡ Script Bash** | `start.sh` | Script rápido Unix/macOS | Usuarios Linux/Mac |
| **🪟 Script Windows** | `start.bat` | Script para Windows | Usuarios Windows |
| **🔧 Modo Desarrollo** | `dev_start.py` | Terminales separadas | Desarrollo/Debug |
| **🛠️ Makefile** | `make start` | Comandos make | Desarrolladores |
| **🎯 Manual** | Scripts individuales | Control granular | Testing/Debug |

---

## 1. 🚀 Launcher Principal (Recomendado)

### Uso Básico
```bash
python launch_scada.py
```

### Opciones Avanzadas
```bash
# Sin abrir navegador automáticamente
python launch_scada.py --no-browser

# Con logs detallados (debugging)
python launch_scada.py --debug

# Ambas opciones
python launch_scada.py --debug --no-browser
```

### Características
- ✅ Verificación automática del entorno
- ✅ Manejo de errores robusto
- ✅ Terminación limpia con Ctrl+C
- ✅ Abre navegador automáticamente
- ✅ Monitoreo continuo de procesos
- ✅ Multiplataforma (Windows/macOS/Linux)

---

## 2. ⚡ Script Bash (Unix/macOS)

### Uso
```bash
# Hacer ejecutable (solo la primera vez)
chmod +x start.sh

# Ejecutar
./start.sh
```

### Características
- ✅ Verificación de entorno virtual
- ✅ Activación automática de scada_env
- ✅ Logs guardados en `/tmp/`
- ✅ Abre navegador automáticamente (macOS/Linux)
- ✅ Limpieza automática al salir

### Logs
```bash
# Ver logs en tiempo real
tail -f /tmp/scada_plc.log
tail -f /tmp/scada_hmi.log
```

---

## 3. 🪟 Script Windows

### Uso
```batch
start.bat
```

### Características
- ✅ Activación automática de entorno virtual
- ✅ Verificación de dependencias
- ✅ Logs guardados en `logs/`
- ✅ Abre navegador automáticamente
- ✅ Terminación con cualquier tecla

### Logs
```batch
# Ver logs
type logs\plc.log
type logs\hmi.log
```

---

## 4. 🔧 Modo Desarrollo

### Uso
```bash
python dev_start.py
```

### Características
- ✅ **Terminales separadas** para cada componente
- ✅ **Logs visibles** en tiempo real
- ✅ **Fácil debugging** individual
- ✅ **Monitor opcional** con Enter
- ✅ **Desarrollo iterativo** cómodo

### Flujo de Desarrollo
1. Ejecuta `python dev_start.py`
2. Se abren terminales separadas:
   - Terminal 1: PLC Virtual
   - Terminal 2: HMI Web
3. Modifica código en tu editor
4. Reinicia solo el componente necesario (Ctrl+C en su terminal)
5. Usa Monitor de Consola para testing

---

## 5. 🛠️ Comandos Make

### Instalación Inicial
```bash
make install    # Configurar entorno completo
```

### Lanzamiento
```bash
make start      # Lanzamiento normal
make start-dev  # Modo desarrollo
make start-simple  # Sin navegador
make start-debug   # Con logs detallados
```

### Componentes Individuales
```bash
make plc-only   # Solo PLC Virtual
make hmi-only   # Solo HMI Web
make monitor    # Solo Monitor
```

### Gestión
```bash
make status     # Estado del sistema
make stop       # Detener todos los procesos
make clean      # Limpiar archivos temporales
make test       # Ejecutar tests
```

### Información
```bash
make help       # Ver todos los comandos
make info       # Información del sistema
```

---

## 6. 🎯 Lanzamiento Manual

### PLC Virtual
```bash
python core/simulation/virtual_plc.py
```

### HMI Web
```bash
python run_hmi.py
```

### Monitor de Consola
```bash
python test_connection.py
```

### Tests
```bash
python tests/minimal_test.py
python tests/simple_test.py
python tests/simple_plc.py
```

---

## 🔧 Configuración de Puertos

### Por Defecto
- **PLC Modbus**: `127.0.0.1:5020`
- **HMI Web**: `http://127.0.0.1:8050`

### Cambiar Puertos
Para cambiar puertos, edita las variables en los archivos:

**PLC Virtual** (`core/simulation/virtual_plc.py`):
```python
VirtualPLC(host='127.0.0.1', port=5020)
```

**HMI Web** (`run_hmi.py`):
```python
hmi.run(host='127.0.0.1', port=8050)
```

---

## 🚨 Solución de Problemas

### Error: Puerto en Uso
```bash
# Verificar qué proceso usa el puerto
lsof -i :5020  # PLC
lsof -i :8050  # HMI

# Detener procesos
make stop
# o manualmente:
pkill -f "virtual_plc.py"
pkill -f "run_hmi.py"
```

### Error: Dependencias Faltantes
```bash
# Reinstalar dependencias
pip install -r requirements.txt

# O con make
make upgrade
```

### Error: Entorno Virtual
```bash
# Recrear entorno
rm -rf scada_env
make install
```

### Error: Sin Conexión PLC-HMI
1. Verificar que el PLC Virtual esté ejecutándose
2. Verificar logs de conexión
3. Usar `python test_connection.py` para diagnóstico

---

## 📊 Monitoreo y Logs

### Ubicaciones de Logs

| Método | Ubicación Logs |
|--------|----------------|
| `launch_scada.py` | Solo en pantalla (--debug) |
| `start.sh` | `/tmp/scada_plc.log`, `/tmp/scada_hmi.log` |
| `start.bat` | `logs/plc.log`, `logs/hmi.log` |
| `dev_start.py` | Terminales separadas |
| Manual | Solo en pantalla |

### Comandos Útiles
```bash
# Ver estado en tiempo real
make status

# Monitor de consola interactivo
make monitor

# Logs en tiempo real (Unix)
tail -f /tmp/scada_*.log
```

---

## 🎯 Recomendaciones por Uso

### 👨‍💻 **Para Desarrollo**
```bash
python dev_start.py
```
**Razón**: Terminales separadas facilitan debugging

### 🏭 **Para Demostración**
```bash
python launch_scada.py
```
**Razón**: Lanzamiento limpio y automático

### 🧪 **Para Testing**
```bash
make test
make start-debug
```
**Razón**: Logs detallados para diagnóstico

### ⚡ **Para Uso Rápido**
```bash
make start
```
**Razón**: Comando corto y manejo automático

### 🪟 **En Windows**
```batch
start.bat
```
**Razón**: Optimizado para entorno Windows

---

## 📚 Documentación Adicional

- **README.md**: Documentación completa del proyecto
- **requirements.txt**: Lista de dependencias
- **tests/**: Scripts de verificación y testing
- **core/**: Documentación de módulos internos

---

**💡 Consejo**: Comienza con `python launch_scada.py` para uso general, y cambia a `python dev_start.py` cuando necesites desarrollar o debuggear.