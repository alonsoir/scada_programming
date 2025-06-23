#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión PLC virtual <-> Cliente Modbus
Ejecutar después de iniciar virtual_plc.py
"""

import asyncio
import time
from core.protocols.modbus_client import ModbusClient


async def continuous_monitoring():
    """Monitor continuo de tags del PLC"""
    client = ModbusClient()

    print("🚀 Iniciando monitor de PLC virtual...")
    print("📡 Intentando conectar...")

    if not await client.connect():
        print("❌ Error: No se pudo conectar al PLC virtual")
        print("💡 Asegúrate de ejecutar: python core/simulation/virtual_plc.py")
        return

    print("✅ Conectado exitosamente!")
    print("📊 Monitoreando tags en tiempo real... (Ctrl+C para salir)\n")

    try:
        cycle_count = 0
        while True:
            cycle_count += 1
            start_time = time.time()

            # Leer todos los tags
            data = await client.scan_cycle()

            if data:
                # Limpiar pantalla
                print("\033[2J\033[H", end="")

                print(f"🔄 Ciclo #{cycle_count} - {time.strftime('%H:%M:%S')}")
                print("=" * 60)

                # Agrupar por categorías
                print("🌡️  TEMPERATURAS:")
                for tag, value in data.items():
                    if 'temp' in tag:
                        status = "🔥" if value > 100 else "❄️" if value < 25 else "✅"
                        print(f"   {status} {tag.replace('_', ' ').title()}: {value:.1f}°C")

                print("\n🔧 PRESIONES:")
                for tag, value in data.items():
                    if 'pressure' in tag:
                        # Determinar estado según rangos típicos
                        if 'hydraulic' in tag:
                            status = "⚠️" if value < 190 or value > 210 else "✅"
                        elif 'fuel' in tag:
                            status = "⚠️" if value < 48 or value > 58 else "✅"
                        else:
                            status = "✅"
                        print(f"   {status} {tag.replace('_', ' ').title()}: {value:.1f} bar")

                print("\n💧 SISTEMAS:")
                for tag, value in data.items():
                    if 'status' in tag or 'stop' in tag or 'ready' in tag:
                        if 'emergency' in tag:
                            status = "🚨" if value else "✅"
                            state = "ACTIVADO" if value else "Normal"
                        else:
                            status = "✅" if value else "⭕"
                            state = "ON" if value else "OFF"
                        print(f"   {status} {tag.replace('_', ' ').title()}: {state}")

                print("\n📈 CONTADORES:")
                for tag, value in data.items():
                    if 'hours' in tag or 'cycles' in tag:
                        print(f"   📊 {tag.replace('_', ' ').title()}: {value}")

                # Mostrar tiempo de ciclo
                cycle_time = (time.time() - start_time) * 1000
                print(f"\n⏱️  Tiempo de ciclo: {cycle_time:.1f}ms")
                print("=" * 60)
                print("Presiona Ctrl+C para salir")

            else:
                print("⚠️  No se pudieron leer datos del PLC")

            await asyncio.sleep(2)  # Actualizar cada 2 segundos

    except KeyboardInterrupt:
        print("\n\n👋 Monitor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en el monitor: {e}")
    finally:
        await client.disconnect()
        print("🔌 Desconectado del PLC")


async def single_test():
    """Prueba única de conexión y lectura"""
    client = ModbusClient()

    print("🧪 Ejecutando prueba única de conexión...")

    if await client.connect():
        print("✅ Conexión exitosa!")

        # Leer algunos tags específicos
        print("\n📋 Leyendo tags de prueba:")

        test_tags = ['engine_temp_1', 'hydraulic_pressure', 'pump_1_status', 'system_ready']

        for tag in test_tags:
            value = await client.read_tag(tag)
            if value is not None:
                if isinstance(value, bool):
                    print(f"   ✓ {tag}: {'ON' if value else 'OFF'}")
                elif isinstance(value, float):
                    print(f"   ✓ {tag}: {value:.1f}")
                else:
                    print(f"   ✓ {tag}: {value}")
            else:
                print(f"   ❌ {tag}: Error de lectura")

        await client.disconnect()
        print("\n🎉 Prueba completada exitosamente!")

    else:
        print("❌ Error de conexión")
        print("💡 Asegúrate de que virtual_plc.py esté ejecutándose")


def run_with_new_loop(coro):
    """Ejecutar corrutina con nuevo loop de eventos"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except Exception as e:
        print(f"Error ejecutando: {e}")
        return None
    finally:
        try:
            loop.close()
        except:
            pass


def main():
    """Menú principal"""
    print("🔧 SISTEMA DE PRUEBA SCADA")
    print("=" * 40)
    print("1. Prueba única de conexión")
    print("2. Monitor continuo en tiempo real")
    print("3. Salir")
    print("=" * 40)

    while True:
        try:
            choice = input("\nSelecciona una opción (1-3): ").strip()

            if choice == '1':
                run_with_new_loop(single_test())
                break
            elif choice == '2':
                run_with_new_loop(continuous_monitoring())
                break
            elif choice == '3':
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Usa 1, 2 o 3.")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break


if __name__ == "__main__":
    main()