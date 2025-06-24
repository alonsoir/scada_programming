#!/usr/bin/env python3
"""
Analizador de logs del detector de protocolos inusuales.
Genera reportes de seguridad a partir de los logs capturados.
"""

import json
import re
from collections import defaultdict, Counter
from datetime import datetime
import argparse


class SCTPLogAnalyzer:
    def __init__(self, log_file="unusual_protocols.log"):
        self.log_file = log_file
        self.alerts = []
        self.stats = defaultdict(int)
        self.timeline = []

    def parse_logs(self):
        """Parsea los logs y extrae alertas JSON"""
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    # Buscar líneas con JSON
                    if "UNUSUAL PROTOCOL DETECTED:" in line:
                        try:
                            # Extraer JSON de la línea
                            json_start = line.find('{')
                            if json_start != -1:
                                json_str = line[json_start:]
                                alert = json.loads(json_str)
                                self.alerts.append(alert)
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            print(f"❌ Archivo de log no encontrado: {self.log_file}")
            return False

        print(f"✅ Parseadas {len(self.alerts)} alertas del log")
        return True

    def analyze_security_threats(self):
        """Analiza las amenazas de seguridad detectadas"""

        # Contadores de amenazas
        high_severity = [a for a in self.alerts if a.get('severity') == 'HIGH']
        suspicious_ports = Counter()
        external_ips = Counter()
        telecom_abuse = []

        for alert in self.alerts:
            # Puertos sospechosos
            if alert.get('severity') == 'HIGH' and 'dst_port' in alert:
                suspicious_ports[alert['dst_port']] += 1

            # IPs externas (no privadas)
            src_ip = alert.get('src_ip', '')
            if not (src_ip.startswith('192.168.') or
                    src_ip.startswith('10.') or
                    src_ip.startswith('172.16.') or
                    src_ip.startswith('127.')):
                external_ips[src_ip] += 1

            # Abuso de puertos de telecomunicaciones
            if (alert.get('is_telecom') and
                    not src_ip.startswith('192.168.1.')):  # No desde tu red local
                telecom_abuse.append(alert)

        return {
            'high_severity_count': len(high_severity),
            'suspicious_ports': dict(suspicious_ports.most_common(10)),
            'external_ips': dict(external_ips.most_common(10)),
            'telecom_abuse': telecom_abuse[:5]  # Top 5
        }

    def generate_timeline(self):
        """Genera timeline de eventos"""
        timeline = []
        for alert in sorted(self.alerts, key=lambda x: x.get('timestamp', '')):
            try:
                dt = datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00'))
                timeline.append({
                    'time': dt.strftime('%H:%M:%S'),
                    'severity': alert.get('severity', 'UNKNOWN'),
                    'src_ip': alert.get('src_ip', 'N/A'),
                    'dst_port': alert.get('dst_port', 'N/A'),
                    'service': alert.get('telecom_service', 'Unknown')
                })
            except:
                continue
        return timeline

    def generate_report(self):
        """Genera reporte completo de seguridad"""
        if not self.parse_logs():
            return

        threats = self.analyze_security_threats()
        timeline = self.generate_timeline()

        print("\n" + "=" * 60)
        print("🛡️  REPORTE DE SEGURIDAD - PROTOCOLOS INUSUALES")
        print("=" * 60)

        # Resumen ejecutivo
        print(f"\n📊 RESUMEN EJECUTIVO:")
        print(f"   Total de alertas: {len(self.alerts)}")
        print(f"   Alertas de alta severidad: {threats['high_severity_count']}")
        print(f"   IPs externas detectadas: {len(threats['external_ips'])}")
        print(f"   Abuso de puertos telecom: {len(threats['telecom_abuse'])}")

        # Amenazas principales
        print(f"\n🚨 AMENAZAS PRINCIPALES:")

        if threats['suspicious_ports']:
            print(f"   Puertos sospechosos más usados:")
            for port, count in list(threats['suspicious_ports'].items())[:5]:
                threat_level = "🔥 CRÍTICO" if port in [1337, 31337, 4444] else "⚠️ SOSPECHOSO"
                print(f"     - Puerto {port}: {count} intentos {threat_level}")

        if threats['external_ips']:
            print(f"   IPs externas más activas:")
            for ip, count in list(threats['external_ips'].items())[:3]:
                print(f"     - {ip}: {count} conexiones")

        # Abuso de telecomunicaciones
        if threats['telecom_abuse']:
            print(f"\n📡 ABUSO DE PROTOCOLOS DE TELECOMUNICACIONES:")
            for abuse in threats['telecom_abuse']:
                print(f"   - {abuse['src_ip']} → Puerto {abuse['dst_port']} ({abuse['telecom_service']})")

        # Timeline de eventos críticos
        print(f"\n⏰ TIMELINE DE EVENTOS CRÍTICOS:")
        high_events = [t for t in timeline if t['severity'] == 'HIGH']
        for event in high_events[-10:]:  # Últimos 10 eventos críticos
            print(f"   {event['time']} - {event['src_ip']} → Puerto {event['dst_port']}")

        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES DE SEGURIDAD:")

        if threats['high_severity_count'] > 0:
            print("   1. 🚨 URGENTE: Investigar puertos sospechosos (1337, 31337, 4444)")
            print("      - Estos son puertos comunes de backdoors y malware")

        if threats['external_ips']:
            print("   2. 🔒 Bloquear IPs externas con tráfico SCTP")
            print("      - SCTP no debería usarse hacia Internet desde redes corporativas")

        if threats['telecom_abuse']:
            print("   3. 📋 Auditar equipos de telecomunicaciones")
            print("      - Verificar equipos autorizados en la red")

        print("   4. 🔍 Monitoreo continuo recomendado")
        print("      - Ejecutar detector 24/7 en modo producción")

        # Estadísticas detalladas
        print(f"\n📈 ESTADÍSTICAS DETALLADAS:")
        protocol_stats = Counter(alert.get('protocol') for alert in self.alerts)
        for protocol, count in protocol_stats.items():
            print(f"   {protocol}: {count} detecciones")

        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Analizador de logs SCTP')
    parser.add_argument('--log', default='unusual_protocols.log',
                        help='Archivo de log a analizar')
    parser.add_argument('--json', action='store_true',
                        help='Salida en formato JSON')

    args = parser.parse_args()

    analyzer = SCTPLogAnalyzer(args.log)

    if args.json:
        # Salida JSON para procesamiento automático
        if analyzer.parse_logs():
            threats = analyzer.analyze_security_threats()
            print(json.dumps(threats, indent=2))
    else:
        # Reporte legible
        analyzer.generate_report()


if __name__ == "__main__":
    main()