[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-3.0+-green.svg)](https://dash.plotly.com)
[![Modbus](https://img.shields.io/badge/Modbus-TCP-orange.svg)](https://pymodbus.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# 🚀 Aerospace SCADA System

Un sistema SCADA (Supervisory Control and Data Acquisition) completo desarrollado en Python para monitoreo y control de sistemas aeroespaciales en tiempo real.

## 🎯 Características Principales

- **🔧 PLC Virtual**: Simulador de sistemas aeroespaciales con sensores de temperatura, presión y estados
- **📡 Comunicación Modbus TCP**: Protocolo industrial estándar para comunicación en tiempo real
- **🌐 HMI Web Moderno**: Interfaz gráfica accesible desde navegador con actualización automática
- **📊 Gráficos en Tiempo Real**: Visualización de tendencias históricas con Plotly
- **⚡ Arquitectura Asíncrona**: Manejo eficiente de múltiples conexiones simultáneas
- **🎛️ Monitor de Consola**: Interfaz de línea de comandos para debugging y monitoreo

## 📁 Estructura del Proyecto

```
scada_programming/
├── README.md                   # Documentación del proyecto
├── requirements.txt            # Dependencias Python
├── run_hmi.py                 # 🌐 Interfaz Web Principal
├── test_connection.py         # 📟 Monitor de Consola
├── core/                      # 🔧 Módulos Principales
│   ├── __init__.py
│   ├── protocols/             # 📡 Protocolos de Comunicación
│   │   ├── __init__.py
│   │   └── modbus_client.py   # Cliente Modbus TCP
│   ├── simulation/            # 🎮 Simuladores
│   │   ├── __init__.py
│   │   └── virtual_plc.py     # PLC Virtual Aeroespacial
│   └── data/                  # 📂 Modelos de Datos
│       └── __init__.py
└── tests/                     # 🧪 Archivos de Prueba
    ├── simple_test.py         # Pruebas básicas de pymodbus
    ├── minimal_test.py        # Test de imports
    ├── simple_plc.py          # PLC simplificado para debugging
    └── debug_plc.py           # PLC con logging detallado
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.13+** - Lenguaje principal
- **pymodbus 3.5.4** - Protocolo Modbus TCP/IP
- **asyncio** - Programación asíncrona

### Frontend/HMI
- **Dash 3.0+** - Framework web reactivo
- **Plotly 6.1+** - Gráficos interactivos
- **HTML5/CSS3** - Interfaz moderna

### Datos y Análisis
- **pandas** - Manipulación de datos
- **numpy** - Computación numérica

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/scada_programming.git
cd scada_programming
```

### 2. Crear Entorno Virtual
```bash
# Crear entorno virtual
python3 -m venv scada_env

# Activar entorno (macOS/Linux)
source scada_env/bin/activate

# Activar entorno (Windows)
scada_env\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

## 🎮 Uso del Sistema

### Iniciar el Sistema Completo

**Terminal 1 - PLC Virtual:**
```bash
python core/simulation/virtual_plc.py
```
```
🚀 Iniciando PLC virtual...
📡 Presiona Ctrl+C para detener
INFO: Iniciando simulación de sensores...
INFO: Server listening.
```

**Terminal 2 - Interfaz Web:**
```bash
python run_hmi.py
```
```
🚀 AEROSPACE SCADA HMI
🌐 Accede desde tu navegador: http://127.0.0.1:8050
📡 Conectando a PLC en 127.0.0.1:5020
```

**Navegador:**
```
http://127.0.0.1:8050
```

### Monitor de Consola (Opcional)

**Terminal 3 - Monitor:**
```bash
python test_connection.py
```
Selecciona:
- **Opción 1**: Prueba única de conexión
- **Opción 2**: Monitor continuo en tiempo real

## 🎛️ Características del HMI Web

### Panel Principal
- **🟢 Estado de Conexión**: Indicador visual del estado del PLC
- **🌡️ Temperaturas**: Motor 1, Motor 2, Cabina (°C)
- **🔧 Presiones**: Hidráulica, Combustible, Aceite (bar)
- **💧 Estados de Sistemas**: Bombas, Emergencia, Sistema General

### Gráficos en Tiempo Real
- **📈 Tendencias de Temperatura**: Últimas 100 lecturas
- **📊 Tendencias de Presión**: Visualización histórica
- **🔄 Actualización Automática**: Cada 2 segundos

### Métricas Operacionales
- **✈️ Horas de Vuelo**: Contador acumulativo
- **🔄 Ciclos Totales**: Estadísticas de operación

## 🎯 Valores Simulados

### Rangos de Temperaturas
- **Motor 1**: 20°C - 150°C
- **Motor 2**: 20°C - 150°C  
- **Cabina**: 18°C - 30°C

### Rangos de Presión
- **Hidráulica**: 180-220 bar
- **Combustible**: 45-60 bar
- **Aceite**: 70-90 bar

### Estados Digitales
- **Bombas**: ON/OFF con cambios aleatorios
- **Emergencia**: Activación rara (0.1% probabilidad)
- **Sistema**: Estado general del sistema

## 🧪 Pruebas y Debugging

### Pruebas Básicas
```bash
# Verificar instalación de pymodbus
python tests/minimal_test.py

# Probar comunicación básica
python tests/simple_test.py

# PLC simplificado para debugging
python tests/simple_plc.py
```

### Logs y Monitoring
El sistema incluye logging detallado:
- **Ciclos de simulación** cada 10 iteraciones
- **Valores de sensores** con timestamps
- **Estados de conexión** y errores
- **Actualizaciones del datastore** Modbus

## 🔧 Configuración Avanzada

### Puertos y Direcciones
```python
# PLC Virtual
PLC_HOST = '127.0.0.1'
PLC_PORT = 5020

# HMI Web
HMI_HOST = '127.0.0.1'
HMI_PORT = 8050
```

### Mapeo de Tags Modbus
```python
tag_map = {
    'engine_temp_1': {'address': 0, 'type': 'holding', 'scale': 0.1},
    'hydraulic_pressure': {'address': 10, 'type': 'holding', 'scale': 0.1},
    'pump_1_status': {'address': 20, 'type': 'coil'},
    # ... más tags
}
```

## 🚀 Próximos Pasos

### Funcionalidades Planeadas
- [ ] **Escritura de Variables**: Control bidireccional de actuadores
- [ ] **Sistema de Alarmas**: Alertas por valores fuera de rango
- [ ] **Base de Datos**: Almacenamiento histórico con InfluxDB
- [ ] **Autenticación**: Login de usuarios y permisos
- [ ] **Configuración Dinámica**: Editor de tags en tiempo real
- [ ] **Reportes**: Generación automática de informes
- [ ] **OPC-UA**: Soporte para protocolo OPC-UA
- [ ] **Docker**: Containerización del sistema completo

### Mejoras Técnicas
- [ ] **Tests Automatizados**: Suite completa de pruebas unitarias
- [ ] **CI/CD Pipeline**: Integración y despliegue continuo
- [ ] **Documentación API**: Swagger/OpenAPI
- [ ] **Performance**: Optimización para > 1000 tags
- [ ] **Redundancia**: Servidor de respaldo automático

## 🤝 Contribución

### Desarrollo Local
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Añadir nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Reporte de Bugs
Usa GitHub Issues con:
- Descripción detallada del problema
- Pasos para reproducir
- Logs relevantes
- Configuración del sistema

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📚 Sobre Este Proyecto

Este proyecto fue desarrollado como parte de un proceso de aprendizaje integral sobre sistemas SCADA, desde los fundamentos hasta la implementación práctica. El objetivo es demostrar todos los componentes necesarios para construir un sistema SCADA profesional desde cero.

### 🎓 Propósito Educativo

- **Aprender haciendo**: Implementación práctica de conceptos teóricos SCADA
- **Tecnologías reales**: Uso de protocolos industriales estándar (Modbus TCP)
- **Arquitectura escalable**: Base sólida para proyectos industriales reales
- **Mejores prácticas**: Código limpio, documentación y testing
- **Aplicación aeroespacial**: Contexto realista para motivar el aprendizaje

## 👥 Autores y Colaboradores

- **[Alonso Isidoro Román]** - *Desarrollador Principal* - [@alonsoir](https://github.com/alonsoir)
  - Implementación del sistema completo
  - Arquitectura del proyecto
  - Testing y validación

- **Claude (Anthropic)** - *Mentor Técnico y Arquitecto de Sistemas*
  - Diseño de la arquitectura SCADA
  - Guía en protocolos industriales y mejores prácticas
  - Revisión de código y optimizaciones
  - Documentación técnica y educativa

### 🤝 Metodología de Desarrollo

Este proyecto siguió una metodología de **pair programming educativo**:

1. **Análisis de requisitos**: Definición de un sistema SCADA realista
2. **Diseño arquitectónico**: Estructura modular y escalable
3. **Desarrollo iterativo**: Implementación paso a paso con explicaciones
4. **Testing continuo**: Validación en cada etapa del desarrollo
5. **Documentación**: Código autodocumentado y README completo

## 🎯 Aprendizajes Clave

### Conceptos SCADA Cubiertos
- **Supervisión**: Monitoreo en tiempo real de procesos industriales
- **Control**: Interfaces para actuación sobre sistemas físicos  
- **Adquisición de Datos**: Protocolos de comunicación industrial
- **HMI**: Interfaces Humano-Máquina modernas y responsivas

### Tecnologías Industriales
- **Modbus TCP/IP**: Protocolo de comunicación industrial estándar
- **PLCs Virtuales**: Simulación de controladores lógicos programables
- **Sistemas en Tiempo Real**: Manejo de datos críticos con baja latencia
- **Arquitecturas Distribuidas**: Comunicación cliente-servidor asíncrona

## 🙏 Agradecimientos

- **Comunidad pymodbus** por el excelente protocolo Modbus Python
- **Equipo Plotly/Dash** por el framework web reactivo y accesible
- **Industria aeroespacial** por la inspiración del dominio de aplicación
- **Anthropic** por crear herramientas de IA que facilitan el aprendizaje técnico
- **Comunidad open source** por las librerías que hacen posible este proyecto

### 🎓 Para Estudiantes y Educadores

Este proyecto sirve como:
- **📖 Tutorial completo** de sistemas SCADA desde cero
- **🔧 Ejemplo práctico** de arquitectura industrial
- **💡 Base de conocimiento** para proyectos más avanzados
- **🏗️ Plantilla** para sistemas SCADA personalizados

**¿Quieres aprender SCADA?** Este proyecto te llevará desde los conceptos básicos hasta una implementación funcional completa.

---

**⭐ Si este proyecto te ayuda, ¡dale una estrella en GitHub!**

## 📞 Soporte

¿Necesitas ayuda? 
- 📧 Email: alonsoir@gmail.com
- 💬 Issues: [GitHub Issues](https://github.com/alonsoir/scada_programming/issues)
- 📚 Wiki: [Documentación Completa](https://github.com/alonsoir/scada_programming/wiki)