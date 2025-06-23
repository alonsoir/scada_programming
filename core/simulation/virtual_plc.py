#!/usr/bin/env python3
"""
Virtual PLC Simulator
Simula un PLC con sensores de temperatura, presión y estado de bombas
Protocolo Modbus TCP Server
"""

import asyncio
import time
import random
import math
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VirtualPLC:
    def __init__(self, host='127.0.0.1', port=5020):
        self.host = host
        self.port = port
        self.running = False
        self.simulation_task = None

        # Tags del proceso (simulación aeroespacial)
        self.tags = {
            # Sensores de temperatura (°C)
            'engine_temp_1': {'address': 0, 'value': 25.0, 'min': 20, 'max': 150},
            'engine_temp_2': {'address': 1, 'value': 25.0, 'min': 20, 'max': 150},
            'cabin_temp': {'address': 2, 'value': 22.0, 'min': 18, 'max': 30},

            # Sensores de presión (bar)
            'hydraulic_pressure': {'address': 10, 'value': 200.0, 'min': 180, 'max': 220},
            'fuel_pressure': {'address': 11, 'value': 50.0, 'min': 45, 'max': 60},
            'oil_pressure': {'address': 12, 'value': 80.0, 'min': 70, 'max': 90},

            # Estados digitales
            'pump_1_status': {'address': 20, 'value': 1, 'type': 'bool'},
            'pump_2_status': {'address': 21, 'value': 0, 'type': 'bool'},
            'emergency_stop': {'address': 22, 'value': 0, 'type': 'bool'},
            'system_ready': {'address': 23, 'value': 1, 'type': 'bool'},

            # Contadores
            'flight_hours': {'address': 30, 'value': 1250, 'type': 'counter'},
            'cycles_count': {'address': 31, 'value': 850, 'type': 'counter'},
        }

        self.setup_modbus_server()

    def setup_modbus_server(self):
        """Configurar el servidor Modbus"""
        # Inicializar bloques de datos
        # Holding Registers (direcciones 0-99): valores analógicos
        # Coils (direcciones 0-99): valores digitales
        # Input Registers (direcciones 0-99): valores de solo lectura

        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0] * 100),  # Discrete Inputs
            co=ModbusSequentialDataBlock(0, [0] * 100),  # Coils
            hr=ModbusSequentialDataBlock(0, [0] * 100),  # Holding Registers
            ir=ModbusSequentialDataBlock(0, [0] * 100)  # Input Registers
        )

        context = ModbusServerContext(slaves=store, single=True)

        # Información del dispositivo
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'Virtual Aerospace PLC'
        identity.ProductCode = 'VAP-1000'
        identity.VendorUrl = 'http://localhost'
        identity.ProductName = 'Aerospace Control Unit Simulator'
        identity.ModelName = 'VAP-1000'
        identity.MajorMinorRevision = '1.0'

        self.context = context
        self.identity = identity

    async def simulate_sensors(self):
        """Simular valores de sensores en tiempo real"""
        logger.info("Iniciando simulación de sensores...")

        start_time = time.time()
        cycle_count = 0

        while self.running:
            current_time = time.time() - start_time
            cycle_count += 1

            # Debug: mostrar ciclo cada 10 iteraciones
            if cycle_count % 10 == 0:
                logger.info(f"Ciclo de simulación #{cycle_count}")

            # Obtener el store del contexto de manera segura
            try:
                # Acceder al slave context
                slave_context = self.context[0x00]  # Unit ID 0
                hr_store = slave_context.store['h']  # 'h' para holding registers
                co_store = slave_context.store['c']  # 'c' para coils
            except Exception as e:
                logger.error(f"Error accediendo al contexto: {e}")
                break

            # Simular temperaturas con variación senoidal + ruido
            for tag_name, tag_data in self.tags.items():
                if 'temp' in tag_name:
                    base_value = (tag_data['max'] + tag_data['min']) / 2
                    variation = (tag_data['max'] - tag_data['min']) * 0.3

                    # Variación senoidal lenta + ruido
                    sine_component = math.sin(current_time * 0.1) * variation * 0.5
                    noise = random.uniform(-2, 2)

                    new_value = base_value + sine_component + noise
                    new_value = max(tag_data['min'], min(tag_data['max'], new_value))

                    tag_data['value'] = round(new_value, 1)

                    # Actualizar en Modbus (multiplicar por 10 para precisión decimal)
                    modbus_value = int(new_value * 10)
                    try:
                        hr_store.setValues(tag_data['address'], [modbus_value])

                        # Debug: mostrar primer valor cada 10 ciclos
                        if cycle_count % 10 == 0 and tag_name == 'engine_temp_1':
                            logger.info(
                                f"Actualizando {tag_name}: {new_value}°C -> Modbus: {modbus_value} en dirección {tag_data['address']}")
                    except Exception as e:
                        logger.error(f"Error actualizando {tag_name}: {e}")

                # Simular presiones
                elif 'pressure' in tag_name:
                    base_value = (tag_data['max'] + tag_data['min']) / 2
                    variation = (tag_data['max'] - tag_data['min']) * 0.2

                    sine_component = math.sin(current_time * 0.05 + random.random()) * variation
                    noise = random.uniform(-1, 1)

                    new_value = base_value + sine_component + noise
                    new_value = max(tag_data['min'], min(tag_data['max'], new_value))

                    tag_data['value'] = round(new_value, 1)

                    # Actualizar en Modbus
                    modbus_value = int(new_value * 10)
                    try:
                        hr_store.setValues(tag_data['address'], [modbus_value])
                    except Exception as e:
                        logger.error(f"Error actualizando {tag_name}: {e}")

                # Simular estados digitales
                elif tag_data.get('type') == 'bool':
                    # Cambio ocasional de estados
                    if random.random() < 0.01:  # 1% probabilidad por ciclo
                        if tag_name == 'emergency_stop':
                            # Emergency stop rara vez se activa
                            if random.random() < 0.001:
                                tag_data['value'] = 1 - tag_data['value']
                        else:
                            tag_data['value'] = 1 - tag_data['value']

                    # Actualizar coils
                    try:
                        co_store.setValues(tag_data['address'], [tag_data['value']])
                    except Exception as e:
                        logger.error(f"Error actualizando coil {tag_name}: {e}")

                # Simular contadores
                elif tag_data.get('type') == 'counter':
                    if random.random() < 0.1:  # Incremento ocasional
                        tag_data['value'] += 1

                    # Actualizar en Modbus
                    try:
                        hr_store.setValues(tag_data['address'], [tag_data['value']])
                    except Exception as e:
                        logger.error(f"Error actualizando contador {tag_name}: {e}")

            await asyncio.sleep(1)  # Actualizar cada segundo

    async def start(self):
        """Iniciar el PLC virtual"""
        logger.info(f"Iniciando PLC virtual en {self.host}:{self.port}")
        self.running = True

        # Iniciar simulación de sensores
        self.simulation_task = asyncio.create_task(self.simulate_sensors())

        # Crear tarea del servidor Modbus TCP
        server_task = asyncio.create_task(
            StartAsyncTcpServer(
                context=self.context,
                identity=self.identity,
                address=(self.host, self.port)
            )
        )

        # Ejecutar ambas tareas concurrentemente
        try:
            await asyncio.gather(self.simulation_task, server_task)
        except asyncio.CancelledError:
            logger.info("Tareas canceladas")
        except Exception as e:
            logger.error(f"Error en las tareas: {e}")
        finally:
            self.stop()

    def stop(self):
        """Detener el PLC virtual"""
        logger.info("Deteniendo PLC virtual...")
        self.running = False
        if self.simulation_task and not self.simulation_task.done():
            self.simulation_task.cancel()

    def get_tag_value(self, tag_name):
        """Obtener valor actual de un tag"""
        return self.tags.get(tag_name, {}).get('value', None)

    def set_tag_value(self, tag_name, value):
        """Establecer valor de un tag"""
        if tag_name in self.tags:
            self.tags[tag_name]['value'] = value
            return True
        return False


# Función para ejecutar el PLC como script independiente
def run_plc():
    """Ejecutar el PLC virtual con manejo correcto de asyncio"""
    plc = VirtualPLC()

    async def run_async():
        try:
            await plc.start()
        except KeyboardInterrupt:
            logger.info("Interrupción recibida")
        except Exception as e:
            logger.error(f"Error en PLC: {e}")
        finally:
            plc.stop()

    try:
        # Crear nuevo loop de eventos
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        print("🚀 Iniciando PLC virtual...")
        print("📡 Presiona Ctrl+C para detener")

        loop.run_until_complete(run_async())

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo PLC virtual...")
        plc.stop()
    except Exception as e:
        logger.error(f"Error ejecutando PLC: {e}")
        plc.stop()
    finally:
        try:
            # Cancelar todas las tareas pendientes
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()

            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            loop.close()
        except Exception as e:
            logger.error(f"Error cerrando loop: {e}")


if __name__ == "__main__":
    run_plc()