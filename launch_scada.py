#!/usr/bin/env python3
"""
🚀 AEROSPACE SCADA LAUNCHER
Script para lanzar todo el sistema SCADA de una vez

Ejecuta:
- PLC Virtual (puerto 5020)
- HMI Web (puerto 8050)
- Opcionalmente abre el navegador
"""

import subprocess
import time
import signal
import sys
import os
import webbrowser
import threading
from pathlib import Path
import argparse


class SCADALauncher:
    def __init__(self, auto_browser=True, debug=False):
        self.processes = []
        self.auto_browser = auto_browser
        self.debug = debug
        self.project_root = Path(__file__).parent

        # URLs del sistema
        self.plc_host = "127.0.0.1"
        self.plc_port = 5020
        self.hmi_host = "127.0.0.1"
        self.hmi_port = 8050
        self.hmi_url = f"http://{self.hmi_host}:{self.hmi_port}"

        # Configurar manejador de señales para limpieza
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def print_header(self):
        """Mostrar header del sistema"""
        print("\n" + "=" * 60)
        print("🚀 AEROSPACE SCADA SYSTEM LAUNCHER")
        print("=" * 60)
        print(f"📡 PLC Virtual: {self.plc_host}:{self.plc_port}")
        print(f"🌐 HMI Web: {self.hmi_url}")
        print(f"🔧 Debug Mode: {'ON' if self.debug else 'OFF'}")
        print(f"🌍 Auto Browser: {'ON' if self.auto_browser else 'OFF'}")
        print("=" * 60 + "\n")

    def check_environment(self):
        """Verificar que el entorno esté correctamente configurado"""
        print("🔍 Verificando entorno...")

        # Verificar Python
        print(f"   ✅ Python: {sys.version.split()[0]}")

        # Verificar archivos principales
        plc_file = self.project_root / "core" / "simulation" / "virtual_plc.py"
        hmi_file = self.project_root / "run_hmi.py"

        if not plc_file.exists():
            print(f"   ❌ Error: No se encuentra {plc_file}")
            return False

        if not hmi_file.exists():
            print(f"   ❌ Error: No se encuentra {hmi_file}")
            return False

        print(f"   ✅ PLC Virtual: {plc_file.name}")
        print(f"   ✅ HMI Web: {hmi_file.name}")

        # Verificar dependencias críticas
        try:
            import pymodbus
            import dash
            import plotly
            print(f"   ✅ pymodbus: {pymodbus.__version__}")
            print(f"   ✅ dash: {dash.__version__}")
            print(f"   ✅ plotly: {plotly.__version__}")
        except ImportError as e:
            print(f"   ❌ Error de dependencias: {e}")
            print("   💡 Ejecuta: pip install -r requirements.txt")
            return False

        print("   🎉 Entorno verificado correctamente\n")
        return True

    def start_plc(self):
        """Iniciar PLC Virtual"""
        print("🔧 Iniciando PLC Virtual...")

        plc_script = self.project_root / "core" / "simulation" / "virtual_plc.py"

        # Configurar output según modo debug
        stdout = None if self.debug else subprocess.DEVNULL
        stderr = None if self.debug else subprocess.DEVNULL

        try:
            process = subprocess.Popen(
                [sys.executable, str(plc_script)],
                stdout=stdout,
                stderr=stderr,
                cwd=self.project_root
            )

            self.processes.append(("PLC Virtual", process))
            print(f"   ✅ PLC iniciado (PID: {process.pid})")

            # Esperar un momento para que el PLC inicie
            time.sleep(3)

            # Verificar que sigue ejecutándose
            if process.poll() is None:
                print(f"   🚀 PLC Virtual ejecutándose en {self.plc_host}:{self.plc_port}")
                return True
            else:
                print(f"   ❌ Error: PLC Virtual terminó inesperadamente")
                return False

        except Exception as e:
            print(f"   ❌ Error iniciando PLC: {e}")
            return False

    def start_hmi(self):
        """Iniciar HMI Web"""
        print("🌐 Iniciando HMI Web...")

        hmi_script = self.project_root / "run_hmi.py"

        # Configurar output según modo debug
        stdout = None if self.debug else subprocess.DEVNULL
        stderr = None if self.debug else subprocess.DEVNULL

        try:
            process = subprocess.Popen(
                [sys.executable, str(hmi_script)],
                stdout=stdout,
                stderr=stderr,
                cwd=self.project_root
            )

            self.processes.append(("HMI Web", process))
            print(f"   ✅ HMI iniciado (PID: {process.pid})")

            # Esperar un momento para que el servidor web inicie
            time.sleep(4)

            # Verificar que sigue ejecutándose
            if process.poll() is None:
                print(f"   🌐 HMI Web ejecutándose en {self.hmi_url}")
                return True
            else:
                print(f"   ❌ Error: HMI Web terminó inesperadamente")
                return False

        except Exception as e:
            print(f"   ❌ Error iniciando HMI: {e}")
            return False

    def open_browser(self):
        """Abrir navegador automáticamente"""
        if not self.auto_browser:
            return

        print("🌍 Abriendo navegador...")

        def delayed_open():
            time.sleep(2)  # Esperar a que el servidor esté completamente listo
            try:
                webbrowser.open(self.hmi_url)
                print(f"   ✅ Navegador abierto en {self.hmi_url}")
            except Exception as e:
                print(f"   ⚠️  No se pudo abrir el navegador automáticamente: {e}")
                print(f"   💡 Abre manualmente: {self.hmi_url}")

        # Ejecutar en hilo separado para no bloquear
        threading.Thread(target=delayed_open, daemon=True).start()

    def show_status(self):
        """Mostrar estado del sistema"""
        print("\n" + "=" * 60)
        print("📊 ESTADO DEL SISTEMA SCADA")
        print("=" * 60)
        print(f"🔧 PLC Virtual: {self.plc_host}:{self.plc_port} - Simulando sensores")
        print(f"🌐 HMI Web: {self.hmi_url} - Interfaz disponible")
        print(f"📊 Monitor: python test_connection.py - Monitor de consola")
        print("=" * 60)
        print("🎯 INSTRUCCIONES:")
        print("   • Accede al HMI desde tu navegador")
        print("   • Los datos se actualizan cada 2 segundos")
        print("   • Presiona Ctrl+C para detener todo el sistema")
        print("=" * 60 + "\n")

    def monitor_processes(self):
        """Monitorear procesos y detectar fallos"""
        print("🔄 Monitoreando sistema...")

        try:
            while True:
                time.sleep(5)

                # Verificar que todos los procesos sigan ejecutándose
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"\n⚠️  {name} terminó inesperadamente (código: {process.returncode})")
                        self.cleanup()
                        return False

        except KeyboardInterrupt:
            print("\n🛑 Recibida señal de terminación...")
            return True

    def cleanup(self):
        """Limpiar todos los procesos"""
        print("\n🧹 Deteniendo sistema SCADA...")

        for name, process in self.processes:
            if process.poll() is None:  # Si sigue ejecutándose
                print(f"   🛑 Deteniendo {name} (PID: {process.pid})")
                try:
                    process.terminate()

                    # Esperar terminación grácil
                    try:
                        process.wait(timeout=5)
                        print(f"   ✅ {name} detenido correctamente")
                    except subprocess.TimeoutExpired:
                        print(f"   ⚡ Forzando terminación de {name}")
                        process.kill()
                        process.wait()

                except Exception as e:
                    print(f"   ⚠️  Error deteniendo {name}: {e}")

        print("\n✅ Sistema SCADA detenido completamente")
        print("👋 ¡Hasta la próxima!\n")

    def signal_handler(self, signum, frame):
        """Manejador de señales para terminación limpia"""
        self.cleanup()
        sys.exit(0)

    def launch(self):
        """Lanzar todo el sistema SCADA"""
        try:
            self.print_header()

            # Verificar entorno
            if not self.check_environment():
                return False

            # Iniciar componentes
            if not self.start_plc():
                print("❌ Error iniciando PLC Virtual")
                return False

            if not self.start_hmi():
                print("❌ Error iniciando HMI Web")
                self.cleanup()
                return False

            # Abrir navegador si está habilitado
            self.open_browser()

            # Mostrar estado
            self.show_status()

            # Monitorear sistema
            self.monitor_processes()

            return True

        except Exception as e:
            print(f"❌ Error general: {e}")
            return False
        finally:
            self.cleanup()


def main():
    """Función principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="🚀 Lanzador del Sistema SCADA Aeroespacial",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python launch_scada.py                 # Lanzamiento normal
  python launch_scada.py --no-browser   # Sin abrir navegador
  python launch_scada.py --debug        # Con logs detallados
  python launch_scada.py -d -n          # Debug sin navegador
        """
    )

    parser.add_argument(
        "--no-browser", "-n",
        action="store_true",
        help="No abrir navegador automáticamente"
    )

    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Modo debug (mostrar logs de componentes)"
    )

    args = parser.parse_args()

    # Crear y ejecutar launcher
    launcher = SCADALauncher(
        auto_browser=not args.no_browser,
        debug=args.debug
    )

    success = launcher.launch()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()