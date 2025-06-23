#!/usr/bin/env python3
"""
Prueba básica de pymodbus para verificar instalación
"""

import asyncio
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.client import ModbusTcpClient
import threading
import time


def test_with_sync_client():
    """Prueba usando cliente síncrono (más simple)"""
    print("🧪 Ejecutando prueba con cliente síncrono...")

    # Crear datastore básico con más espacio
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 100),  # Discrete inputs
        co=ModbusSequentialDataBlock(0, [0] * 100),  # Coils
        hr=ModbusSequentialDataBlock(0, [42, 123, 456] + [0] * 97),  # Holding registers
        ir=ModbusSequentialDataBlock(0, [0] * 100)  # Input registers
    )

    context = ModbusServerContext(slaves=store, single=True)

    print("✅ Servidor creado, iniciando en puerto 5020...")

    # Función para ejecutar el servidor en thread separado
    def run_server():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            StartAsyncTcpServer(context=context, address=("127.0.0.1", 5020))
        )

    # Iniciar servidor en thread separado
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Esperar a que el servidor inicie
    time.sleep(3)

    print("🔌 Probando conexión cliente...")

    # Probar cliente síncrono
    try:
        client = ModbusTcpClient(host="127.0.0.1", port=5020)

        if client.connect():
            print("✅ Cliente conectado!")

            # Leer registros uno por uno primero
            print("📊 Leyendo registros individuales:")
            for i in range(3):
                result = client.read_holding_registers(i, 1, unit=1)
                if not result.isError():
                    print(f"   Registro {i}: {result.registers[0]}")
                else:
                    print(f"   Error en registro {i}: {result}")

            # Ahora intentar leer múltiples
            print("📊 Leyendo múltiples registros:")
            result = client.read_holding_registers(0, 3, unit=1)

            if not result.isError():
                print(f"📊 Valores leídos: {result.registers}")
                print("🎉 ¡Prueba exitosa!")
                return True
            else:
                print(f"❌ Error leyendo múltiples: {result}")
                return False

        else:
            print("❌ Error: Cliente no pudo conectar")
            return False

    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

    finally:
        try:
            client.close()
        except:
            pass


def simple_client_test():
    """Prueba muy básica solo del cliente"""
    print("🔧 Prueba básica de importación...")

    try:
        from pymodbus.client import ModbusTcpClient
        from pymodbus.server import StartAsyncTcpServer
        from pymodbus.datastore import ModbusSequentialDataBlock

        print("✅ Imports exitosos!")
        print(f"📦 pymodbus version disponible")

        # Crear cliente de prueba
        client = ModbusTcpClient(host="127.0.0.1", port=5020)
        print("✅ Cliente creado exitosamente!")

        return True

    except ImportError as e:
        print(f"❌ Error de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False


if __name__ == "__main__":
    print("🧪 PRUEBA BÁSICA DE PYMODBUS")
    print("=" * 40)

    # Primero probar imports
    if simple_client_test():
        print("\n" + "=" * 40)
        print("🚀 Probando servidor + cliente...")

        if test_with_sync_client():
            print("\n✅ ¡Todas las pruebas exitosas!")
            print("💡 pymodbus está funcionando correctamente")
        else:
            print("\n⚠️  Error en la comunicación servidor-cliente")
            print("💡 Verifica que el puerto 5020 esté libre")
    else:
        print("\n❌ Error en la instalación de pymodbus")
        print("💡 Intenta: pip uninstall pymodbus && pip install pymodbus==3.5.4")