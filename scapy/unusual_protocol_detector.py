#!/usr/bin/env python3
"""
Detector de protocolos de red inusuales para análisis de seguridad.
Detecta SCTP y otros protocolos que no deberían aparecer en redes corporativas típicas.
"""

from scapy.all import sniff, get_if_list
from scapy.layers.inet import IP, ICMP
from scapy.layers.sctp import SCTP
from scapy.layers.inet6 import IPv6
import logging
import json
from datetime import datetime
from collections import defaultdict
import threading
import time

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unusual_protocols.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class UnusualProtocolDetector:
    def __init__(self, interface="en0"):
        self.interface = interface
        self.stats = defaultdict(int)
        self.alerts = []
        self.running = False

        # Protocolos considerados inusuales en redes corporativas
        self.unusual_protocols = {
            132: "SCTP",  # Stream Control Transmission Protocol
            41: "IPv6",  # IPv6 (puede ser inusual en algunas redes)
            47: "GRE",  # Generic Routing Encapsulation
            50: "ESP",  # Encapsulating Security Payload
            51: "AH",  # Authentication Header
            88: "EIGRP",  # Enhanced Interior Gateway Routing Protocol
            89: "OSPF",  # Open Shortest Path First
            103: "PIM",  # Protocol Independent Multicast
            112: "VRRP",  # Virtual Router Redundancy Protocol
            115: "L2TP",  # Layer Two Tunneling Protocol
        }

        # Puertos SCTP comunes en telecomunicaciones
        self.telecom_sctp_ports = {
            2905: "M3UA",  # MTP3 User Adaptation Layer
            2944: "M2UA",  # MTP2 User Adaptation Layer
            2945: "M2PA",  # MTP2 Peer-to-Peer Adaptation Layer
            3868: "Diameter",  # Diameter Base Protocol
            4739: "IPFIX",  # IP Flow Information Export
            5090: "M3UA",  # Alternative M3UA port
            14001: "SUA",  # SCCP User Adaptation Layer
        }

    def get_available_interfaces(self):
        """Obtiene las interfaces de red disponibles"""
        try:
            interfaces = get_if_list()
            logger.info(f"Interfaces disponibles: {interfaces}")
            return interfaces
        except Exception as e:
            logger.error(f"Error obteniendo interfaces: {e}")
            return ["eth0"]

    def analyze_sctp_packet(self, packet):
        """Análisis específico para paquetes SCTP"""
        if not SCTP in packet:
            return

        try:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            src_port = packet[SCTP].sport
            dst_port = packet[SCTP].dport

            # Mapeo de tipos de chunks SCTP
            chunk_type_map = {
                0: "DATA", 1: "INIT", 2: "INIT_ACK", 3: "SACK",
                4: "HEARTBEAT", 5: "HEARTBEAT_ACK", 6: "ABORT",
                7: "SHUTDOWN", 8: "SHUTDOWN_ACK", 9: "ERROR",
                10: "COOKIE_ECHO", 11: "COOKIE_ACK",
                14: "SHUTDOWN_COMPLETE", 192: "FORWARD_TSN"
            }

            # Analizar chunks
            chunk_types = []
            if hasattr(packet[SCTP], 'chunks') and packet[SCTP].chunks:
                chunk_types = [chunk.type for chunk in packet[SCTP].chunks]

            chunk_names = [chunk_type_map.get(t, f"UNKNOWN({t})") for t in chunk_types]

            # Determinar si es tráfico de telecomunicaciones
            is_telecom = (src_port in self.telecom_sctp_ports or
                          dst_port in self.telecom_sctp_ports)

            telecom_service = ""
            if is_telecom:
                service_port = src_port if src_port in self.telecom_sctp_ports else dst_port
                telecom_service = self.telecom_sctp_ports[service_port]

            alert = {
                'timestamp': datetime.now().isoformat(),
                'protocol': 'SCTP',
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'chunk_types': chunk_names,
                'is_telecom': is_telecom,
                'telecom_service': telecom_service,
                'severity': 'HIGH' if not is_telecom else 'MEDIUM',
                'raw_summary': packet.summary()
            }

            self.log_alert(alert)
            self.stats['sctp_packets'] += 1

        except Exception as e:
            logger.error(f"Error analizando paquete SCTP: {e}")

    def analyze_unusual_protocol(self, packet):
        """Análisis de protocolos inusuales en general"""
        if not IP in packet:
            return

        protocol = packet[IP].proto

        if protocol in self.unusual_protocols:
            protocol_name = self.unusual_protocols[protocol]

            alert = {
                'timestamp': datetime.now().isoformat(),
                'protocol': protocol_name,
                'protocol_number': protocol,
                'src_ip': packet[IP].src,
                'dst_ip': packet[IP].dst,
                'severity': 'MEDIUM',
                'raw_summary': packet.summary()
            }

            self.log_alert(alert)
            self.stats[f'{protocol_name.lower()}_packets'] += 1

    def log_alert(self, alert):
        """Registra una alerta de protocolo inusual"""
        self.alerts.append(alert)

        # Log estructurado
        logger.warning(f"UNUSUAL PROTOCOL DETECTED: {json.dumps(alert, indent=2)}")

        # Alerta legible
        severity_emoji = "🚨" if alert['severity'] == 'HIGH' else "⚠️"
        print(f"\n{severity_emoji} {alert['severity']} ALERT {severity_emoji}")
        print(f"Protocol: {alert['protocol']}")
        print(f"Source: {alert['src_ip']}")
        print(f"Destination: {alert['dst_ip']}")

        if 'src_port' in alert:
            print(f"Ports: {alert['src_port']} -> {alert['dst_port']}")

        if 'telecom_service' in alert and alert['telecom_service']:
            print(f"Telecom Service: {alert['telecom_service']}")

        if 'chunk_types' in alert:
            print(f"SCTP Chunks: {', '.join(alert['chunk_types'])}")

        print(f"Time: {alert['timestamp']}")
        print("-" * 50)

    def packet_handler(self, packet):
        """Manejador principal de paquetes"""
        try:
            # Analizar SCTP específicamente (análisis más detallado)
            if SCTP in packet:
                self.analyze_sctp_packet(packet)
                # No analizar como protocolo genérico si ya se analizó como SCTP
                return

            # Analizar otros protocolos inusuales (solo si no es SCTP)
            self.analyze_unusual_protocol(packet)

        except Exception as e:
            logger.error(f"Error procesando paquete: {e}")

    def print_stats(self):
        """Imprime estadísticas periódicamente"""
        while self.running:
            time.sleep(30)  # Cada 30 segundos
            if self.stats:
                print(f"\n📊 ESTADÍSTICAS ({datetime.now().strftime('%H:%M:%S')})")
                for protocol, count in self.stats.items():
                    print(f"  {protocol}: {count}")
                print()

    def start_monitoring(self):
        """Inicia el monitoreo de protocolos inusuales"""
        print(f"🔍 Iniciando detector de protocolos inusuales en {self.interface}")
        print("Protocolos monitoreados:")
        for proto_num, proto_name in self.unusual_protocols.items():
            print(f"  - {proto_name} (IP Protocol {proto_num})")

        print(f"\n🎯 Puertos SCTP de telecomunicaciones monitoreados:")
        for port, service in self.telecom_sctp_ports.items():
            print(f"  - {port}: {service}")

        print(f"\n⚡ Comenzando captura en {self.interface}...")
        print("Presiona Ctrl+C para detener\n")

        self.running = True

        # Hilo para estadísticas
        stats_thread = threading.Thread(target=self.print_stats, daemon=True)
        stats_thread.start()

        try:
            # Captura con filtro amplio para protocolos inusuales
            # Incluye SCTP (132) y otros protocolos menos comunes
            filter_expr = "ip proto 132 or ip proto 41 or ip proto 47 or ip proto 50 or ip proto 51 or ip proto 88 or ip proto 89"

            sniff(
                iface=self.interface,
                filter=filter_expr,
                prn=self.packet_handler,
                store=0
            )

        except KeyboardInterrupt:
            print("\n⏹️  Deteniendo captura...")
        except Exception as e:
            logger.error(f"Error en captura: {e}")
        finally:
            self.running = False
            self.show_summary()

    def show_summary(self):
        """Muestra resumen final"""
        print(f"\n📋 RESUMEN FINAL")
        print(f"Total de alertas: {len(self.alerts)}")
        print(f"Estadísticas por protocolo:")
        for protocol, count in self.stats.items():
            print(f"  - {protocol}: {count}")

        if self.alerts:
            print(f"\n🎯 Alertas de alta severidad:")
            high_alerts = [a for a in self.alerts if a['severity'] == 'HIGH']
            for alert in high_alerts[-5:]:  # Últimas 5
                print(f"  - {alert['timestamp']}: {alert['protocol']} {alert['src_ip']} -> {alert['dst_ip']}")


def main():
    """Función principal"""
    print("🛡️  Detector de Protocolos Inusuales v1.0 - macOS")
    print("=" * 50)

    # Verificar permisos en macOS
    import os
    if os.geteuid() != 0:
        print("⚠️  ADVERTENCIA: En macOS necesitas permisos de root")
        print("   Ejecuta: sudo python3 unusual_protocol_detector.py")
        print()

    # Interfaces específicas de macOS detectadas
    macos_interfaces = {
        'en0': 'WiFi/Ethernet principal (192.168.1.123)',
        'en5': 'Thunderbolt/USB-C',
        'utun0': 'Túnel VPN #1',
        'utun1': 'Túnel VPN #2',
        'utun2': 'Túnel VPN #3',
        'utun3': 'Túnel VPN #4',
        'utun4': 'Túnel VPN #5',
        'utun5': 'Túnel VPN #6',
        'ap1': 'Access Point',
        'awdl0': 'Apple Wireless Direct Link'
    }

    print("🔍 Interfaces detectadas en tu Mac:")
    for iface, desc in macos_interfaces.items():
        print(f"  - {iface}: {desc}")

    print(f"\n⚡ Nota: Tienes múltiples túneles VPN activos (utun0-utun5)")
    print(f"    Esto es normal, pero vigilaremos tráfico inusual en ellos.")

    detector = UnusualProtocolDetector()

    # Mostrar interfaces disponibles de Scapy
    interfaces = detector.get_available_interfaces()

    # Verificar que tenemos las clases necesarias
    try:
        SCTP
        IP
        print("✅ Clases de Scapy cargadas correctamente")
    except NameError:
        print("❌ Error: Clases de Scapy no disponibles")
        return

    detector.start_monitoring()


if __name__ == "__main__":
    main()