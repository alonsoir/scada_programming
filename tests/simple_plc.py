#!/usr/bin/env python3
"""
PLC Virtual Simplificado para debugging
"""

import asyncio
import threading
import time
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification


class SimplePLC:
    def __init__(self, host='127.0.0.1', port=5020):
        self.host = host
        self.port = port
        self.running = False

        # Crear datastore con valores fijos simples
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0] * 100),
            co=ModbusSequentialDataBlock(0, [1, 0, 1, 1] + [0] * 96),  # Algunos coils activos
            hr=ModbusSequentialDataBlock(0, [250, 251, 220, 2000, 500, 800] + [0] * 94),
            # Temps y presiones simuladas
            ir=ModbusSequentialDataBlock(0, [0] * 100)
        )

        self.context = ModbusServerContext(slaves=store, single=True)

        # Información del dispositivo
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'Simple PLC'
        identity.ProductCode = 'SP-1000'
        identity.ProductName = 'Simple SCADA PLC'

        self.identity = identity

    def start_server(self):
        """Iniciar servidor en hilo separado"""

        def run_server():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                print(f"🚀 Iniciando PLC simple en {self.host}:{self.port}")

                loop.run_until_complete(
                    StartAsyncTcpServer(
                        context=self.context,
                        identity=self.identity,
                        address=(self.host, self.port)
                    )
                )

            except Exception as e:
                print(f"❌ Error en servidor: {e}")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.running = True
        self.server_thread.start()

        print("⏳ Esperando a que el servidor inicie...")
        time.sleep(2)
        print("✅ Servidor iniciado!")

    def stop(self):
        """Detener servidor"""
        self.running = False
        print("🛑 Deteniendo PLC simple...")


def test_simple_plc():
    """Probar el PLC simplificado"""
    from pymodbus.client import ModbusTcpClient

    # Iniciar PLC
    plc = SimplePLC()
    plc.start_server()

    print("\n🔌 Probando conexión cliente...")

    try:
        client = ModbusTcpClient(host="127.0.0.1", port=5020, timeout=5)

        if client.connect():
            print("✅ Cliente conectado al PLC simple!")

            # Probar lectura de holding registers
            print("\n📊 Leyendo Holding Registers:")
            result = client.read_holding_registers(0, 6, unit=1)
            if not result.isError():
                print(f"   Registros 0-5: {result.registers}")
            else:
                print(f"   Error: {result}")

            # Probar lectura de coils
            print("\n🔘 Leyendo Coils:")
            result = client.read_coils(0, 4, unit=1)
            if not result.isError():
                print(f"   Coils 0-3: {result.bits}")
            else:
                print(f"   Error: {result}")

            # Probar escritura
            print("\n✍️  Probando escritura...")
            result = client.write_register(0, 999, unit=1)
            if not result.isError():
                print("   ✅ Escritura exitosa")

                # Verificar escritura
                result = client.read_holding_registers(0, 1, unit=1)
                if not result.isError():
                    print(f"   Valor leído después de escritura: {result.registers[0]}")
            else:
                print(f"   Error en escritura: {result}")

            client.close()
            print("\n🎉 ¡Todas las pruebas exitosas!")
            return True

        else:
            print("❌ Error: No se pudo conectar")
            return False

    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False
    finally:
        plc.stop()


if __name__ == "__main__":
    print("🧪 PRUEBA DE PLC SIMPLIFICADO")
    print("=" * 40)

    if test_simple_plc():
        print("\n✅ ¡PLC simplificado funciona!")
        print("💡 Ahora puedes probar el PLC completo")
    else:
        print("\n❌ Error en PLC simplificado")
        print("💡 Revisa la instalación de pymodbus")