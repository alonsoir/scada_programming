#!/usr/bin/env python3
"""
PLC Virtual con debugging para entender la estructura del contexto
"""

import asyncio
import time
import threading
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DebugPLC:
    def __init__(self, host='127.0.0.1', port=5020):
        self.host = host
        self.port = port
        self.running = False

        # Crear datastore con valores iniciales
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0] * 100),
            co=ModbusSequentialDataBlock(0, [1, 0, 1, 1] + [0] * 96),
            hr=ModbusSequentialDataBlock(0, [250, 300, 220, 2000, 500, 800] + [0] * 94),
            ir=ModbusSequentialDataBlock(0, [0] * 100)
        )

        self.context = ModbusServerContext(slaves=store, single=True)

        # Información del dispositivo
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'Debug PLC'
        identity.ProductCode = 'DBG-1000'

        self.identity = identity

    async def debug_context(self):
        """Debuggear la estructura del contexto"""
        logger.info("🔍 Debuggeando estructura del contexto...")

        await asyncio.sleep(2)  # Esperar a que el servidor inicie

        try:
            # Inspeccionar el contexto
            logger.info(f"Tipo de contexto: {type(self.context)}")
            logger.info(f"Claves del contexto: {dir(self.context)}")

            # Intentar acceder al slave 0
            slave_0 = self.context[0x00]
            logger.info(f"Slave 0 tipo: {type(slave_0)}")
            logger.info(f"Slave 0 atributos: {dir(slave_0)}")

            # Intentar acceder al store
            store = slave_0.store
            logger.info(f"Store tipo: {type(store)}")
            logger.info(f"Store claves: {list(store.keys()) if hasattr(store, 'keys') else 'No keys method'}")

            # Probar diferentes claves para holding registers
            for key in ['hr', 'h', 'holding', '4']:
                try:
                    hr_store = store[key]
                    logger.info(f"✅ Holding registers encontrados en clave '{key}': {type(hr_store)}")

                    # Probar leer valores
                    values = hr_store.getValues(0, 6)
                    logger.info(f"✅ Valores iniciales (0-5): {values}")

                    # Probar escribir valores
                    hr_store.setValues(0, [999])
                    new_values = hr_store.getValues(0, 1)
                    logger.info(f"✅ Después de escribir 999: {new_values}")

                    break

                except KeyError:
                    logger.info(f"❌ Clave '{key}' no encontrada")
                except Exception as e:
                    logger.error(f"❌ Error con clave '{key}': {e}")

            # Probar coils
            for key in ['co', 'c', 'coils', '1']:
                try:
                    co_store = store[key]
                    logger.info(f"✅ Coils encontrados en clave '{key}': {type(co_store)}")

                    values = co_store.getValues(0, 4)
                    logger.info(f"✅ Valores coils (0-3): {values}")
                    break

                except KeyError:
                    logger.info(f"❌ Clave coil '{key}' no encontrada")
                except Exception as e:
                    logger.error(f"❌ Error con clave coil '{key}': {e}")

        except Exception as e:
            logger.error(f"❌ Error general debuggeando contexto: {e}")

        logger.info("🔍 Debug completado")

    async def start_debug(self):
        """Iniciar el PLC con debug"""
        logger.info(f"Iniciando Debug PLC en {self.host}:{self.port}")
        self.running = True

        # Crear tareas
        debug_task = asyncio.create_task(self.debug_context())
        server_task = asyncio.create_task(
            StartAsyncTcpServer(
                context=self.context,
                identity=self.identity,
                address=(self.host, self.port)
            )
        )

        try:
            await asyncio.gather(debug_task, server_task, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error en debug PLC: {e}")


def run_debug_plc():
    """Ejecutar el PLC de debug"""
    plc = DebugPLC()

    async def run_async():
        try:
            await plc.start_debug()
        except KeyboardInterrupt:
            logger.info("Debug PLC detenido")
        except Exception as e:
            logger.error(f"Error: {e}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        print("🔍 Iniciando Debug PLC...")
        print("📡 Presiona Ctrl+C para detener")

        loop.run_until_complete(run_async())

    except KeyboardInterrupt:
        print("\n🛑 Debug PLC detenido")
    except Exception as e:
        logger.error(f"Error ejecutando debug: {e}")
    finally:
        try:
            loop.close()
        except:
            pass


if __name__ == "__main__":
    run_debug_plc()