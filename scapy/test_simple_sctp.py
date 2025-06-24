#!/usr/bin/env python3
"""
Test SCTP simplificado - Solo lo básico para verificar detección
"""

from scapy.layers.inet import IP
from scapy.layers.sctp import SCTP
from scapy.all import send
import time


def test_basic_sctp():
    """Test básico de SCTP - solo IP + SCTP sin chunks específicos"""
    print("🧪 Test SCTP Básico")
    print("=" * 30)

    # Verificar importaciones
    try:
        print("✅ IP disponible")
        print("✅ SCTP disponible")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    # Crear paquete SCTP básico
    target_ip = "127.0.0.1"  # localhost
    source_ip = "192.168.1.123"  # tu IP

    print(f"📡 Enviando SCTP desde {source_ip} hacia {target_ip}")

    # Test 1: Puerto de telecomunicaciones (legítimo)
    print("🔧 Test 1: Puerto Diameter (3868) - Legítimo")
    packet1 = IP(src=source_ip, dst=target_ip) / SCTP(sport=12345, dport=3868)

    try:
        send(packet1, verbose=False)
        print("  ✅ Paquete enviado correctamente")
        time.sleep(1)
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test 2: Puerto sospechoso
    print("⚠️  Test 2: Puerto 1337 - Sospechoso")
    packet2 = IP(src=source_ip, dst=target_ip) / SCTP(sport=54321, dport=1337)

    try:
        send(packet2, verbose=False)
        print("  ✅ Paquete enviado correctamente")
        time.sleep(1)
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Test 3: IP externa
    print("🌐 Test 3: Desde IP externa (8.8.8.8)")
    packet3 = IP(src="8.8.8.8", dst=target_ip) / SCTP(sport=3868, dport=9999)

    try:
        send(packet3, verbose=False)
        print("  ✅ Paquete enviado correctamente")
        time.sleep(1)
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print("\n🎯 Tests completados!")
    print("Revisa la terminal del detector para ver las alertas")
    return True


def check_scapy_sctp():
    """Verificar qué componentes SCTP están disponibles"""
    print("🔍 Verificando componentes SCTP disponibles...")

    try:
        from scapy.layers.sctp import SCTP
        print("✅ SCTP básico: Disponible")
    except ImportError:
        print("❌ SCTP básico: No disponible")
        return False

    try:
        from scapy.layers.sctp import SCTPChunkInit
        print("✅ SCTPChunkInit: Disponible")
    except ImportError:
        print("⚠️  SCTPChunkInit: No disponible")

    try:
        from scapy.layers.sctp import SCTPChunkData
        print("✅ SCTPChunkData: Disponible")
    except ImportError:
        print("⚠️  SCTPChunkData: No disponible")

    try:
        from scapy.layers.sctp import SCTPChunkHeartbeat
        print("✅ SCTPChunkHeartbeat: Disponible")
    except ImportError:
        print("⚠️  SCTPChunkHeartbeat: No disponible")

    return True


if __name__ == "__main__":
    print("🚀 Test SCTP Simplificado")
    print("=" * 40)

    # Verificar componentes
    if not check_scapy_sctp():
        print("❌ No se puede continuar - SCTP no disponible")
        exit(1)

    print("\n⚠️  IMPORTANTE: Ejecuta el detector en otra terminal:")
    print("   sudo python3 unusual_protocol_detector.py")

    input("\nPresiona ENTER cuando el detector esté funcionando...")

    # Ejecutar tests
    test_basic_sctp()