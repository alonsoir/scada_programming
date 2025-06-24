#!/usr/bin/env python3
"""
Generador de tráfico SCTP de prueba para validar la detección.
Simula diferentes tipos de tráfico SCTP legítimo e inusual.
"""

from scapy.all import send
from scapy.layers.inet import IP
from scapy.layers.sctp import SCTP
import time
import random

# Verificar qué chunks SCTP están disponibles
try:
    from scapy.layers.sctp import SCTPChunkData, SCTPChunkInit

    CHUNKS_AVAILABLE = True
except ImportError:
    print("⚠️  Algunos chunks SCTP específicos no están disponibles")
    CHUNKS_AVAILABLE = False

# Intentar importar chunks adicionales si están disponibles
try:
    from scapy.layers.sctp import SCTPChunkHeartbeat

    HEARTBEAT_AVAILABLE = True
except ImportError:
    HEARTBEAT_AVAILABLE = False


class SCTPTestGenerator:
    def __init__(self, target_ip="8.8.8.8"):  # DNS Google - pasa por en0
        self.target_ip = target_ip
        self.source_ip = "192.168.1.123"  # Tu IP actual

        # Puertos de telecomunicaciones para simular
        self.telecom_ports = {
            2905: "M3UA",
            2944: "M2UA",
            3868: "Diameter",
            14001: "SUA"
        }

        # Puertos sospechosos (no estándar)
        self.suspicious_ports = [1337, 31337, 4444, 8080]

    def generate_telecom_sctp(self):
        """Genera tráfico SCTP legítimo de telecomunicaciones"""
        print("🔧 Generando tráfico SCTP de telecomunicaciones...")

        for port, service in self.telecom_ports.items():
            print(f"  Enviando {service} en puerto {port}")

            # SCTP básico (si chunks específicos no están disponibles)
            if CHUNKS_AVAILABLE:
                try:
                    packet = IP(src=self.source_ip, dst=self.target_ip) / \
                             SCTP(sport=random.randint(1024, 65535), dport=port) / \
                             SCTPChunkInit()
                except:
                    # Fallback a SCTP básico
                    packet = IP(src=self.source_ip, dst=self.target_ip) / \
                             SCTP(sport=random.randint(1024, 65535), dport=port)
            else:
                # SCTP básico sin chunks específicos
                packet = IP(src=self.source_ip, dst=self.target_ip) / \
                         SCTP(sport=random.randint(1024, 65535), dport=port)

            try:
                send(packet, verbose=0)
                time.sleep(0.5)
            except Exception as e:
                print(f"    Error enviando {service}: {e}")

    def generate_suspicious_sctp(self):
        """Genera tráfico SCTP sospechoso"""
        print("⚠️  Generando tráfico SCTP sospechoso...")

        for port in self.suspicious_ports:
            print(f"  Enviando SCTP a puerto sospechoso {port}")

            # SCTP básico (más compatible)
            if CHUNKS_AVAILABLE:
                try:
                    packet = IP(src=self.source_ip, dst=self.target_ip) / \
                             SCTP(sport=random.randint(1024, 65535), dport=port) / \
                             SCTPChunkData(data=b"SUSPICIOUS_DATA")
                except:
                    packet = IP(src=self.source_ip, dst=self.target_ip) / \
                             SCTP(sport=random.randint(1024, 65535), dport=port)
            else:
                packet = IP(src=self.source_ip, dst=self.target_ip) / \
                         SCTP(sport=random.randint(1024, 65535), dport=port)

            try:
                send(packet, verbose=0)
                time.sleep(0.5)
            except Exception as e:
                print(f"    Error enviando a puerto {port}: {e}")

    def generate_heartbeat_flood(self):
        """Simula un posible ataque de flood SCTP"""
        print("🚨 Generando flood de SCTP (simulando ataque)...")

        for i in range(5):  # Solo 5 paquetes para no saturar
            if HEARTBEAT_AVAILABLE:
                try:
                    packet = IP(src=self.source_ip, dst=self.target_ip) / \
                             SCTP(sport=random.randint(1024, 65535),
                                  dport=random.randint(1024, 65535)) / \
                             SCTPChunkHeartbeat()
                except:
                    # Fallback a SCTP básico
                    packet = IP(src=self.source_ip, dst=self.target_ip) / \
                             SCTP(sport=random.randint(1024, 65535),
                                  dport=random.randint(1024, 65535))
            else:
                # SCTP básico sin heartbeat específico
                packet = IP(src=self.source_ip, dst=self.target_ip) / \
                         SCTP(sport=random.randint(1024, 65535),
                              dport=random.randint(1024, 65535))

            try:
                send(packet, verbose=0)
                time.sleep(0.1)
            except Exception as e:
                print(f"    Error en heartbeat {i + 1}: {e}")

    def generate_external_sctp(self):
        """Simula tráfico SCTP desde IPs externas"""
        print("🌐 Simulando tráfico SCTP desde IPs externas...")

        external_ips = ["10.0.0.1", "172.16.0.1", "8.8.8.8"]

        for ext_ip in external_ips:
            print(f"  Simulando desde {ext_ip}")

            if CHUNKS_AVAILABLE:
                try:
                    packet = IP(src=ext_ip, dst=self.target_ip) / \
                             SCTP(sport=3868, dport=random.randint(1024, 65535)) / \
                             SCTPChunkInit()
                except:
                    packet = IP(src=ext_ip, dst=self.target_ip) / \
                             SCTP(sport=3868, dport=random.randint(1024, 65535))
            else:
                packet = IP(src=ext_ip, dst=self.target_ip) / \
                         SCTP(sport=3868, dport=random.randint(1024, 65535))

            try:
                send(packet, verbose=0)
                time.sleep(0.3)
            except Exception as e:
                print(f"    Error desde {ext_ip}: {e}")

    def run_all_tests(self):
        """Ejecuta todos los tests de tráfico SCTP"""
        print("🧪 INICIANDO TESTS DE TRÁFICO SCTP")
        print("=" * 50)
        print("⚠️  IMPORTANTE: Ejecuta el detector en otra terminal ANTES de este test")
        print("   sudo python3 unusual_protocol_detector.py")
        print()

        input("Presiona ENTER cuando el detector esté ejecutándose...")

        print("\n🚀 Comenzando generación de tráfico de prueba...")

        # Test 1: Tráfico legítimo
        self.generate_telecom_sctp()
        print("✅ Test 1 completado - Tráfico de telecomunicaciones")
        time.sleep(2)

        # Test 2: Tráfico sospechoso
        self.generate_suspicious_sctp()
        print("✅ Test 2 completado - Tráfico sospechoso")
        time.sleep(2)

        # Test 3: Posible ataque
        self.generate_heartbeat_flood()
        print("✅ Test 3 completado - Flood de heartbeat")
        time.sleep(2)

        # Test 4: IPs externas
        self.generate_external_sctp()
        print("✅ Test 4 completado - IPs externas")

        print("\n🎯 TESTS COMPLETADOS")
        print("Revisa la terminal del detector para ver las alertas generadas")


def main():
    print("🧪 Generador de Tráfico SCTP de Prueba")
    print("=" * 40)

    # Verificar que Scapy puede crear paquetes SCTP
    try:
        from scapy.layers.sctp import SCTP
        from scapy.layers.inet import IP
        print("✅ Scapy SCTP básico disponible")

        if CHUNKS_AVAILABLE:
            print("✅ Chunks SCTP específicos disponibles")
        else:
            print("⚠️  Chunks SCTP específicos no disponibles - usando SCTP básico")

        if HEARTBEAT_AVAILABLE:
            print("✅ SCTP Heartbeat disponible")
        else:
            print("⚠️  SCTP Heartbeat no disponible - usando alternativas")

    except ImportError as e:
        print(f"❌ Error: Scapy SCTP no disponible: {e}")
        return

    generator = SCTPTestGenerator()

    print(f"\n🎯 Generando tráfico hacia: {generator.target_ip} (DNS Google)")
    print(f"📡 Desde: {generator.source_ip}")
    print("✅ Este tráfico pasará por en0 y será detectado por el monitor")

    choice = input("\n¿Qué test quieres ejecutar?\n"
                   "1. Solo telecomunicaciones (legítimo)\n"
                   "2. Solo sospechoso\n"
                   "3. Todos los tests\n"
                   "Opción (1-3): ")

    if choice == "1":
        generator.generate_telecom_sctp()
    elif choice == "2":
        generator.generate_suspicious_sctp()
    elif choice == "3":
        generator.run_all_tests()
    else:
        print("Opción inválida")


if __name__ == "__main__":
    main()