#!/usr/bin/env python3
"""
🔧 AEROSPACE SCADA - Development Launcher
Script para desarrollo que muestra todos los logs en tiempo real

Características:
- Logs visibles en terminales separadas
- Monitoreo detallado de todos los componentes
- Fácil debugging y desarrollo
"""

import subprocess
import time
import signal
import sys
import os
import webbrowser
import threading
from pathlib import Path
import platform


class SCADADevLauncher:
    def __init__(self):
        self.processes = []
        self.project_root = Path(__file__).parent
        self.system = platform.system().lower()

        # Configurar manejador de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def print_dev_header(self):
        """Header para modo desarrollo"""
        print("\n" + "=" * 70)
        print("🔧 AEROSPACE SCADA - DEVELOPMENT MODE")
        print("=" * 70)
        print("🎯 Características del modo desarrollo:")
        print("   • Logs visibles en tiempo real")
        print("   • Terminales separadas para cada componente")
        print("   • Fácil debugging y monitoreo")
        print("   • Recarga automática en desarrollo")
        print("=" * 70 + "\n")

    def open_terminal_command(self, title, command):
        """Obtener comando para abrir nueva terminal según SO"""
        if self.system == "darwin":  # macOS
            script = f'''
            tell application "Terminal"
                do script "{command}"
                set custom title of front window to "{title}"
            end tell
            '''
            return ["osascript", "-e", script]

        elif self.system == "linux":
            # Probar diferentes terminales de Linux
            if os.path.exists("/usr/bin/gnome-terminal"):
                return ["gnome-terminal", "--title", title, "--", "bash", "-c", f"{command}; read"]
            elif os.path.exists("/usr/bin/xterm"):
                return ["xterm", "-title", title, "-e", f"bash -c '{command}; read'"]
            elif os.path.exists("/usr/bin/konsole"):
                return ["konsole", "--title", title, "-e", f"bash -c '{command}; read'"]

        elif self.system == "windows":
            return ["cmd", "/c", "start", f'"{title}"', "cmd", "/k", command]

        return None

    def start_component_in_terminal(self, name, script_path, title):
        """Iniciar componente en terminal separada"""
        print(f"🚀 Iniciando {name} en terminal separada...")

        # Comando para ejecutar el script
        python_cmd = f"cd {self.project_root} && python {script_path}"

        # Obtener comando de terminal específico del SO
        terminal_cmd = self.open_terminal_command(title, python_cmd)

        if terminal_cmd:
            try:
                if self.system == "windows":
                    process = subprocess.Popen(terminal_cmd, shell=True)
                else:
                    process = subprocess.Popen(terminal_cmd)

                self.processes.append((name, process))
                print(f"   ✅ {name} iniciado en terminal: '{title}'")
                return True

            except Exception as e:
                print(f"   ❌ Error abriendo terminal para {name}: {e}")
                return False
        else:
            print(f"   ⚠️  No se pudo determinar comando de terminal para {self.system}")
            # Fallback: ejecutar en background
            return self.start_component_background(name, script_path)

    def start_component_background(self, name, script_path):
        """Fallback: iniciar componente en background con logs"""
        print(f"🚀 Iniciando {name} en background...")

        try:
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Crear hilo para mostrar logs
            def show_logs():
                for line in process.stdout:
                    print(f"[{name}] {line.rstrip()}")

            log_thread = threading.Thread(target=show_logs, daemon=True)
            log_thread.start()

            self.processes.append((name, process))
            print(f"   ✅ {name} iniciado (PID: {process.pid})")
            return True

        except Exception as e:
            print(f"   ❌ Error iniciando {name}: {e}")
            return False

    def start_monitor_terminal(self):
        """Iniciar monitor de consola en terminal separada"""
        print("📊 Iniciando Monitor de Consola...")

        monitor_cmd = f"cd {self.project_root} && python test_connection.py"
        terminal_cmd = self.open_terminal_command("SCADA Monitor", monitor_cmd)

        if terminal_cmd:
            try:
                if self.system == "windows":
                    subprocess.Popen(terminal_cmd, shell=True)
                else:
                    subprocess.Popen(terminal_cmd)
                print("   ✅ Monitor iniciado en terminal separada")
            except Exception as e:
                print(f"   ⚠️  Error abriendo monitor: {e}")
        else:
            print("   💡 Para usar monitor: python test_connection.py")

    def show_dev_instructions(self):
        """Mostrar instrucciones para desarrollo"""
        print("\n" + "=" * 70)
        print("🔧 INSTRUCCIONES DE DESARROLLO")
        print("=" * 70)
        print("🏢 TERMINALES ABIERTAS:")
        print("   • PLC Virtual - Simulador de sistemas aeroespaciales")
        print("   • HMI Web - Servidor de interfaz web")
        print("   • Monitor - Herramientas de debugging (opcional)")
        print()
        print("🌐 ACCESOS:")
        print("   • HMI Web: http://127.0.0.1:8050")
        print("   • PLC Modbus: 127.0.0.1:5020")
        print()
        print("🔧 DESARROLLO:")
        print("   • Modifica código y reinicia componentes individualmente")
        print("   • Logs visibles en cada terminal")
        print("   • Usa Ctrl+C en cada terminal para detener componentes")
        print()
        print("📁 ARCHIVOS PRINCIPALES:")
        print("   • core/simulation/virtual_plc.py - PLC Virtual")
        print("   • run_hmi.py - Interfaz Web")
        print("   • core/protocols/modbus_client.py - Cliente Modbus")
        print("=" * 70 + "\n")

    def open_browser_delayed(self):
        """Abrir navegador después de un delay"""

        def delayed_open():
            time.sleep(6)  # Esperar más tiempo en modo desarrollo
            try:
                webbrowser.open("http://127.0.0.1:8050")
                print("🌍 Navegador abierto automáticamente")
            except Exception as e:
                print(f"⚠️  Error abriendo navegador: {e}")

        threading.Thread(target=delayed_open, daemon=True).start()

    def wait_for_exit(self):
        """Esperar a que el usuario termine el desarrollo"""
        print("🔄 MODO DESARROLLO ACTIVO")
        print("   • Componentes ejecutándose en terminales separadas")
        print("   • Presiona Enter para abrir Monitor de Consola")
        print("   • Presiona Ctrl+C para finalizar sesión de desarrollo")
        print()

        try:
            # Esperar input del usuario
            input("Presiona Enter para abrir Monitor (o Ctrl+C para salir): ")
            self.start_monitor_terminal()

            # Continuar esperando
            print("\n🔄 Sesión de desarrollo en curso...")
            print("   • Presiona Ctrl+C para finalizar")

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Finalizando sesión de desarrollo...")

    def cleanup(self):
        """Limpiar procesos (menos agresivo en modo desarrollo)"""
        print("🧹 Limpiando sesión de desarrollo...")

        # En modo desarrollo, los procesos están en terminales separadas
        # Solo limpiar los que iniciamos directamente
        for name, process in self.processes:
            if process.poll() is None:
                try:
                    process.terminate()
                    print(f"   ✅ {name} marcado para terminación")
                except:
                    pass

        print("✅ Sesión de desarrollo finalizada")
        print("💡 Cierra manualmente las terminales que siguen abiertas")
        print("👋 ¡Feliz desarrollo!")

    def signal_handler(self, signum, frame):
        """Manejador de señales"""
        self.cleanup()
        sys.exit(0)

    def launch_dev(self):
        """Lanzar en modo desarrollo"""
        try:
            self.print_dev_header()

            # Verificar entorno básico
            if not Path("core/simulation/virtual_plc.py").exists():
                print("❌ Error: No se encuentra virtual_plc.py")
                return False

            if not Path("run_hmi.py").exists():
                print("❌ Error: No se encuentra run_hmi.py")
                return False

            # Iniciar componentes en terminales separadas
            success = True

            # PLC Virtual
            if not self.start_component_in_terminal(
                    "PLC Virtual",
                    "core/simulation/virtual_plc.py",
                    "SCADA PLC Virtual"
            ):
                success = False

            time.sleep(2)

            # HMI Web
            if not self.start_component_in_terminal(
                    "HMI Web",
                    "run_hmi.py",
                    "SCADA HMI Web"
            ):
                success = False

            if not success:
                print("❌ Error iniciando algunos componentes")
                return False

            # Abrir navegador
            self.open_browser_delayed()

            # Mostrar instrucciones
            self.show_dev_instructions()

            # Esperar a que termine el desarrollo
            self.wait_for_exit()

            return True

        except Exception as e:
            print(f"❌ Error en modo desarrollo: {e}")
            return False
        finally:
            self.cleanup()


def main():
    """Función principal"""
    launcher = SCADADevLauncher()
    success = launcher.launch_dev()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()