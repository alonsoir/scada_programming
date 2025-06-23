#!/usr/bin/env python3
"""
🚀 AEROSPACE SCADA HMI with Industrial Alarm System
Interfaz web moderna con sistema de alarmas integrado
"""

import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import asyncio
import threading
import time
from datetime import datetime, timedelta
from collections import deque
import logging

# Importar nuestros módulos
from core.protocols.modbus_client import ModbusClient

# Importar sistema de alarmas (crear estos imports después)
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simular imports de alarmas (hasta que creemos los archivos)
try:
    from core.alarms.alarm_system import AlarmEngine, AlarmState, AlarmPriority
    from core.alarms.alarm_hmi_integration import AlarmHMIIntegration

    ALARMS_AVAILABLE = True
except ImportError:
    ALARMS_AVAILABLE = False
    print("⚠️ Sistema de alarmas no disponible - ejecutando sin alarmas")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedSCADAHMI:
    def __init__(self, plc_host='127.0.0.1', plc_port=5020):
        self.plc_host = plc_host
        self.plc_port = plc_port
        self.client = ModbusClient(host=plc_host, port=plc_port)
        self.is_connected = False

        # Buffer para datos históricos
        self.max_points = 100
        self.historical_data = {
            'timestamps': deque(maxlen=self.max_points),
            'engine_temp_1': deque(maxlen=self.max_points),
            'engine_temp_2': deque(maxlen=self.max_points),
            'cabin_temp': deque(maxlen=self.max_points),
            'hydraulic_pressure': deque(maxlen=self.max_points),
            'fuel_pressure': deque(maxlen=self.max_points),
            'oil_pressure': deque(maxlen=self.max_points),
        }

        # Datos actuales
        self.current_data = {}

        # Sistema de alarmas
        if ALARMS_AVAILABLE:
            self.alarm_engine = AlarmEngine()
            self.alarm_hmi = AlarmHMIIntegration(self.alarm_engine)
        else:
            self.alarm_engine = None
            self.alarm_hmi = None

        # Configurar Dash app
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        """Configurar el layout mejorado con alarmas"""
        self.app.layout = html.Div([
            # Banner de alarmas (si está disponible)
            self.create_alarm_banner() if ALARMS_AVAILABLE else html.Div(),

            # Título principal
            html.Div([
                html.H1("🚀 AEROSPACE SCADA SYSTEM",
                        style={'color': 'white', 'textAlign': 'center', 'marginBottom': '20px'}),
                html.Hr(style={'borderColor': 'white'}),
            ], style={
                'background': 'linear-gradient(90deg, #1e3c72 0%, #2a5298 100%)',
                'color': 'white',
                'padding': '20px',
                'margin': '-8px -8px 20px -8px'
            }),

            # Estado de conexión mejorado
            html.Div([
                html.Div(id="connection-status",
                         style={'padding': '10px', 'borderRadius': '5px', 'marginBottom': '10px'}),
                html.Div([
                    html.Button("🔄 Reconectar", id="reconnect-btn",
                                style={'padding': '8px 16px', 'marginRight': '10px'},
                                n_clicks=0),
                    html.Button("🚨 Test Alarma", id="test-alarm-btn",
                                style={'padding': '8px 16px', 'marginRight': '10px'},
                                n_clicks=0) if ALARMS_AVAILABLE else html.Div(),
                    html.Button("✅ ACK Todas", id="ack-all-btn",
                                style={'padding': '8px 16px', 'marginRight': '10px'},
                                n_clicks=0) if ALARMS_AVAILABLE else html.Div(),
                ])
            ], style={'marginBottom': '20px'}),

            # Resumen de alarmas (si está disponible)
            self.create_alarm_summary() if ALARMS_AVAILABLE else html.Div(),

            # Métricas principales
            html.Div([
                # Temperaturas
                html.Div([
                    html.Div([
                        html.H4("🌡️ TEMPERATURAS", style={'color': '#dc3545', 'marginBottom': '15px'}),
                        html.Div([
                            html.Div([
                                html.Div(id="temp-engine-1",
                                         style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'textAlign': 'center'}),
                                html.Small("Motor 1",
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666'}),
                                html.Div(id="temp-engine-1-status", className="status-indicator-small")
                            ], style={'width': '33%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="temp-engine-2",
                                         style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'textAlign': 'center'}),
                                html.Small("Motor 2",
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666'}),
                                html.Div(id="temp-engine-2-status", className="status-indicator-small")
                            ], style={'width': '33%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="temp-cabin",
                                         style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'textAlign': 'center'}),
                                html.Small("Cabina",
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666'}),
                                html.Div(id="temp-cabin-status", className="status-indicator-small")
                            ], style={'width': '33%', 'display': 'inline-block'}),
                        ])
                    ], style={'padding': '20px'})
                ], style={'border': '2px solid #dc3545', 'borderRadius': '10px', 'marginBottom': '20px',
                          'backgroundColor': 'white', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),

                # Presiones
                html.Div([
                    html.Div([
                        html.H4("🔧 PRESIONES", style={'color': '#ffc107', 'marginBottom': '15px'}),
                        html.Div([
                            html.Div([
                                html.Div(id="pressure-hydraulic",
                                         style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'textAlign': 'center'}),
                                html.Small("Hidráulica",
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666'}),
                                html.Div(id="pressure-hydraulic-status", className="status-indicator-small")
                            ], style={'width': '33%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="pressure-fuel",
                                         style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'textAlign': 'center'}),
                                html.Small("Combustible",
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666'}),
                                html.Div(id="pressure-fuel-status", className="status-indicator-small")
                            ], style={'width': '33%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="pressure-oil",
                                         style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'textAlign': 'center'}),
                                html.Small("Aceite",
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666'}),
                                html.Div(id="pressure-oil-status", className="status-indicator-small")
                            ], style={'width': '33%', 'display': 'inline-block'}),
                        ])
                    ], style={'padding': '20px'})
                ], style={'border': '2px solid #ffc107', 'borderRadius': '10px', 'marginBottom': '20px',
                          'backgroundColor': 'white', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),

                # Estados de sistemas
                html.Div([
                    html.Div([
                        html.H4("💧 SISTEMAS", style={'color': '#28a745', 'marginBottom': '15px'}),
                        html.Div([
                            html.Div([
                                html.Div(id="pump-1-status",
                                         style={'width': '50px', 'height': '50px', 'borderRadius': '50%',
                                                'margin': '0 auto', 'display': 'flex', 'alignItems': 'center',
                                                'justifyContent': 'center', 'fontWeight': 'bold', 'color': 'white'}),
                                html.Small("Bomba 1", style={'display': 'block', 'textAlign': 'center', 'color': '#666',
                                                             'marginTop': '5px'})
                            ], style={'width': '25%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="pump-2-status",
                                         style={'width': '50px', 'height': '50px', 'borderRadius': '50%',
                                                'margin': '0 auto', 'display': 'flex', 'alignItems': 'center',
                                                'justifyContent': 'center', 'fontWeight': 'bold', 'color': 'white'}),
                                html.Small("Bomba 2", style={'display': 'block', 'textAlign': 'center', 'color': '#666',
                                                             'marginTop': '5px'})
                            ], style={'width': '25%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="emergency-status",
                                         style={'width': '50px', 'height': '50px', 'borderRadius': '50%',
                                                'margin': '0 auto', 'display': 'flex', 'alignItems': 'center',
                                                'justifyContent': 'center', 'fontWeight': 'bold', 'color': 'white'}),
                                html.Small("Emergencia",
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666',
                                                  'marginTop': '5px'})
                            ], style={'width': '25%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="system-ready",
                                         style={'width': '50px', 'height': '50px', 'borderRadius': '50%',
                                                'margin': '0 auto', 'display': 'flex', 'alignItems': 'center',
                                                'justifyContent': 'center', 'fontWeight': 'bold', 'color': 'white'}),
                                html.Small("Sistema", style={'display': 'block', 'textAlign': 'center', 'color': '#666',
                                                             'marginTop': '5px'})
                            ], style={'width': '25%', 'display': 'inline-block'}),
                        ])
                    ], style={'padding': '20px'})
                ], style={'border': '2px solid #28a745', 'borderRadius': '10px', 'marginBottom': '20px',
                          'backgroundColor': 'white', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
            ]),

            # Gráficos en tiempo real
            html.Div([
                html.Div([
                    dcc.Graph(id="temperature-chart")
                ], style={'width': '50%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Graph(id="pressure-chart")
                ], style={'width': '50%', 'display': 'inline-block'}),
            ], style={'marginBottom': '20px'}),

            # Tabla de alarmas activas (si está disponible)
            self.create_alarm_table() if ALARMS_AVAILABLE else html.Div(),

            # Contadores y estadísticas
            html.Div([
                html.Div([
                    html.H4("📈 ESTADÍSTICAS", style={'color': '#17a2b8', 'marginBottom': '15px'}),
                    html.Div([
                        html.Div([
                            html.H5(id="flight-hours", style={'color': '#007bff', 'textAlign': 'center'}),
                            html.Small("Horas de Vuelo", style={'display': 'block', 'textAlign': 'center'})
                        ], style={'width': '33%', 'display': 'inline-block'}),
                        html.Div([
                            html.H5(id="cycles-count", style={'color': '#007bff', 'textAlign': 'center'}),
                            html.Small("Ciclos Totales", style={'display': 'block', 'textAlign': 'center'})
                        ], style={'width': '33%', 'display': 'inline-block'}),
                        html.Div([
                            html.H5(id="alarm-stats", style={'color': '#007bff', 'textAlign': 'center'}),
                            html.Small("Alarmas 24h", style={'display': 'block', 'textAlign': 'center'})
                        ], style={'width': '33%', 'display': 'inline-block'}) if ALARMS_AVAILABLE else html.Div(),
                    ])
                ], style={'padding': '20px'})
            ], style={'border': '1px solid #ddd', 'borderRadius': '10px', 'backgroundColor': 'white',
                      'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),

            # Intervalo para actualización automática
            dcc.Interval(
                id='interval-component',
                interval=2000,  # Actualizar cada 2 segundos
                n_intervals=0
            ),

            # CSS personalizado mejorado
            html.Style(children=self.get_enhanced_css())
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa'})

    def create_alarm_banner(self):
        """Crear banner de alarmas"""
        return html.Div([
            html.Div(id="alarm-banner-content"),
        ], id="alarm-banner", style={
            'position': 'sticky',
            'top': '0',
            'zIndex': '1000',
            'marginBottom': '10px'
        })

    def create_alarm_summary(self):
        """Crear resumen de alarmas"""
        return html.Div([
            html.Div([
                html.H4("🚨 SISTEMA DE ALARMAS", style={'color': '#dc3545', 'marginBottom': '15px'}),
                html.Div([
                    html.Div([
                        html.Div(id="alarm-count-critical", className="alarm-count critical"),
                        html.Small("Críticas", className="alarm-label")
                    ], style={'width': '25%', 'display': 'inline-block'}),
                    html.Div([
                        html.Div(id="alarm-count-warning", className="alarm-count warning"),
                        html.Small("Advertencia", className="alarm-label")
                    ], style={'width': '25%', 'display': 'inline-block'}),
                    html.Div([
                        html.Div(id="alarm-count-active", className="alarm-count active"),
                        html.Small("Activas", className="alarm-label")
                    ], style={'width': '25%', 'display': 'inline-block'}),
                    html.Div([
                        html.Div(id="alarm-count-unack", className="alarm-count unack"),
                        html.Small("Sin ACK", className="alarm-label")
                    ], style={'width': '25%', 'display': 'inline-block'}),
                ])
            ], style={'padding': '20px'})
        ], style={'border': '2px solid #dc3545', 'borderRadius': '10px', 'marginBottom': '20px',
                  'backgroundColor': 'white', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'})

    def create_alarm_table(self):
        """Crear tabla de alarmas activas"""
        return html.Div([
            html.Div([
                html.H4("📋 ALARMAS ACTIVAS", style={'marginBottom': '15px'}),
                html.Div(id="alarm-table-content"),
            ], style={'padding': '20px'})
        ], style={'border': '1px solid #ddd', 'borderRadius': '10px', 'marginBottom': '20px',
                  'backgroundColor': 'white'})

    def get_enhanced_css(self):
        """CSS mejorado con alarmas"""
        return """
        .alarm-count {
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 5px;
            border: 2px solid;
        }

        .alarm-count.critical {
            background-color: #ffebee;
            color: #d32f2f;
            border-color: #f44336;
        }

        .alarm-count.warning {
            background-color: #fff8e1;
            color: #f57c00;
            border-color: #ff9800;
        }

        .alarm-count.active {
            background-color: #e3f2fd;
            color: #1976d2;
            border-color: #2196f3;
        }

        .alarm-count.unack {
            background-color: #fce4ec;
            color: #c2185b;
            border-color: #e91e63;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }

        .alarm-label {
            display: block;
            text-align: center;
            color: #666;
            font-weight: normal;
            font-size: 0.9rem;
        }

        .status-indicator-small {
            width: 15px;
            height: 15px;
            border-radius: 50%;
            margin: 5px auto;
            background-color: #28a745;
        }

        .status-indicator-small.warning {
            background-color: #ffc107;
        }

        .status-indicator-small.critical {
            background-color: #dc3545;
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.3; }
        }

        .flashing {
            animation: flash 1s infinite;
        }

        @keyframes flash {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.5; }
        }
        """

    def setup_callbacks(self):
        """Configurar callbacks de Dash"""

        @self.app.callback(
            [
                # Outputs existentes
                Output('connection-status', 'children'),
                Output('connection-status', 'style'),
                Output('temp-engine-1', 'children'),
                Output('temp-engine-2', 'children'),
                Output('temp-cabin', 'children'),
                Output('pressure-hydraulic', 'children'),
                Output('pressure-fuel', 'children'),
                Output('pressure-oil', 'children'),
                Output('pump-1-status', 'children'),
                Output('pump-1-status', 'style'),
                Output('pump-2-status', 'children'),
                Output('pump-2-status', 'style'),
                Output('emergency-status', 'children'),
                Output('emergency-status', 'style'),
                Output('system-ready', 'children'),
                Output('system-ready', 'style'),
                Output('flight-hours', 'children'),
                Output('cycles-count', 'children'),
                Output('temperature-chart', 'figure'),
                Output('pressure-chart', 'figure'),

                # Outputs nuevos para alarmas (si están disponibles)
            ] + ([
                Output('alarm-banner-content', 'children'),
                Output('alarm-count-critical', 'children'),
                Output('alarm-count-warning', 'children'),
                Output('alarm-count-active', 'children'),
                Output('alarm-count-unack', 'children'),
                Output('alarm-table-content', 'children'),
                Output('alarm-stats', 'children'),
            ] if ALARMS_AVAILABLE else []),
            [
                Input('interval-component', 'n_intervals'),
                Input('reconnect-btn', 'n_clicks'),
            ] + ([
                Input('test-alarm-btn', 'n_clicks'),
                Input('ack-all-btn', 'n_clicks'),
            ] if ALARMS_AVAILABLE else [])
        )
        def update_dashboard(*args):
            return self.update_all_components()

    def update_all_components(self):
        """Actualizar todos los componentes del dashboard"""
        # Verificar conexión
        if not self.is_connected:
            asyncio.run(self.connect_to_plc())

        # Leer datos actuales
        data = asyncio.run(self.read_plc_data())

        if not data:
            return self.get_error_state()

        # Procesar alarmas si están disponibles
        if ALARMS_AVAILABLE and self.alarm_hmi:
            alarm_events = self.alarm_hmi.process_tag_data(data)

        # Actualizar datos históricos
        now = datetime.now()
        self.historical_data['timestamps'].append(now)
        for key, value in data.items():
            if key in self.historical_data:
                self.historical_data[key].append(value)

        # Preparar datos base
        base_data = self.get_base_dashboard_data(data)

        # Añadir datos de alarmas si están disponibles
        if ALARMS_AVAILABLE:
            alarm_data = self.get_alarm_dashboard_data()
            return base_data + alarm_data
        else:
            return base_data

    def get_base_dashboard_data(self, data):
        """Obtener datos base del dashboard"""
        # Estado de conexión
        conn_status = "🟢 Conectado al PLC - Datos actualizándose en tiempo real"
        conn_style = {'padding': '10px', 'borderRadius': '5px', 'marginBottom': '10px', 'backgroundColor': '#d4edda',
                      'color': '#155724', 'border': '1px solid #c3e6cb'}

        # Temperaturas
        temp1 = f"{data.get('engine_temp_1', 0):.1f}°C"
        temp2 = f"{data.get('engine_temp_2', 0):.1f}°C"
        temp_cabin = f"{data.get('cabin_temp', 0):.1f}°C"

        # Presiones
        press_hyd = f"{data.get('hydraulic_pressure', 0):.1f} bar"
        press_fuel = f"{data.get('fuel_pressure', 0):.1f} bar"
        press_oil = f"{data.get('oil_pressure', 0):.1f} bar"

        # Estados de bombas y sistemas
        pump1_on = data.get('pump_1_status', False)
        pump2_on = data.get('pump_2_status', False)
        emergency = data.get('emergency_stop', False)
        system_ok = data.get('system_ready', False)

        status_on_style = {'width': '50px', 'height': '50px', 'borderRadius': '50%', 'margin': '0 auto',
                           'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'fontWeight': 'bold',
                           'color': 'white', 'backgroundColor': '#28a745'}
        status_off_style = {'width': '50px', 'height': '50px', 'borderRadius': '50%', 'margin': '0 auto',
                            'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'fontWeight': 'bold',
                            'color': 'white', 'backgroundColor': '#dc3545'}

        # Contadores
        flight_hrs = f"{data.get('flight_hours', 0):,} hrs"
        cycles = f"{data.get('cycles_count', 0):,}"

        # Crear gráficos
        temp_chart = self.create_temperature_chart()
        pressure_chart = self.create_pressure_chart()

        return [
            conn_status, conn_style,
            temp1, temp2, temp_cabin,
            press_hyd, press_fuel, press_oil,
            "ON" if pump1_on else "OFF",
            status_on_style if pump1_on else status_off_style,
            "ON" if pump2_on else "OFF",
            status_on_style if pump2_on else status_off_style,
            "STOP" if emergency else "OK",
            status_off_style if emergency else status_on_style,
            "RDY" if system_ok else "OFF",
            status_on_style if system_ok else status_off_style,
            flight_hrs, cycles,
            temp_chart, pressure_chart
        ]

    def get_alarm_dashboard_data(self):
        """Obtener datos específicos de alarmas"""
        if not ALARMS_AVAILABLE or not self.alarm_hmi:
            return []

        # Banner de alarmas
        banner_content = self.alarm_hmi.get_alarm_banner_content()

        # Resumen de alarmas
        summary = self.alarm_hmi.get_alarm_summary_data()

        # Tabla de alarmas
        table_content = self.alarm_hmi.get_alarm_table_data()

        # Estadísticas de alarmas
        history_24h = self.alarm_engine.get_alarm_history(hours=24)
        alarm_stats = f"{len(history_24h)}"

        return [
            banner_content,
            str(summary['critical']),
            str(summary['warning']),
            str(summary['active']),
            str(summary['unack']),
            table_content,
            alarm_stats
        ]

    def get_error_state(self):
        """Retornar estado de error cuando no hay conexión"""
        conn_status = "🔴 Sin conexión al PLC - Verificar que esté ejecutándose"
        conn_style = {'padding': '10px', 'borderRadius': '5px', 'marginBottom': '10px', 'backgroundColor': '#f8d7da',
                      'color': '#721c24', 'border': '1px solid #f5c6cb'}

        no_data = "--"
        status_off_style = {'width': '50px', 'height': '50px', 'borderRadius': '50%', 'margin': '0 auto',
                            'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'fontWeight': 'bold',
                            'color': 'white', 'backgroundColor': '#dc3545'}

        empty_chart = go.Figure()
        empty_chart.update_layout(title="Sin datos disponibles")

        base_error = [
            conn_status, conn_style,
            no_data, no_data, no_data,  # Temperaturas
            no_data, no_data, no_data,  # Presiones
            "OFF", status_off_style, "OFF", status_off_style,  # Bombas
            "OFF", status_off_style, "OFF", status_off_style,  # Estados
            no_data, no_data,  # Contadores
            empty_chart, empty_chart  # Gráficos
        ]

        if ALARMS_AVAILABLE:
            alarm_error = [
                html.Div("🔴 Sin conexión - Alarmas no disponibles", className="alert alert-danger"),
                "0", "0", "0", "0",  # Contadores de alarmas
                html.Div("Sin datos de alarmas", className="alert alert-warning"),
                "0"  # Estadísticas
            ]
            return base_error + alarm_error

        return base_error

    async def connect_to_plc(self):
        """Conectar al PLC"""
        try:
            self.is_connected = await self.client.connect()
            if self.is_connected:
                logger.info("HMI conectado al PLC")
            return self.is_connected
        except Exception as e:
            logger.error(f"Error conectando HMI al PLC: {e}")
            self.is_connected = False
            return False

    async def read_plc_data(self):
        """Leer datos del PLC"""
        try:
            if not self.is_connected:
                return {}

            data = await self.client.read_all_tags()
            self.current_data = data
            return data

        except Exception as e:
            logger.error(f"Error leyendo datos del PLC: {e}")
            self.is_connected = False
            return {}

    def create_temperature_chart(self):
        """Crear gráfico de temperaturas"""
        fig = go.Figure()

        if len(self.historical_data['timestamps']) == 0:
            fig.update_layout(title="🌡️ Temperaturas en Tiempo Real", height=400)
            return fig

        timestamps = list(self.historical_data['timestamps'])

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=list(self.historical_data['engine_temp_1']),
            mode='lines+markers',
            name='Motor 1',
            line=dict(color='#ff6b6b', width=3)
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=list(self.historical_data['engine_temp_2']),
            mode='lines+markers',
            name='Motor 2',
            line=dict(color='#4ecdc4', width=3)
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=list(self.historical_data['cabin_temp']),
            mode='lines+markers',
            name='Cabina',
            line=dict(color='#45b7d1', width=2)
        ))

        fig.update_layout(
            title="🌡️ Temperaturas en Tiempo Real",
            xaxis_title="Tiempo",
            yaxis_title="Temperatura (°C)",
            hovermode='x unified',
            height=400
        )

        return fig

    def create_pressure_chart(self):
        """Crear gráfico de presiones"""
        fig = go.Figure()

        if len(self.historical_data['timestamps']) == 0:
            fig.update_layout(title="🔧 Presiones en Tiempo Real", height=400)
            return fig

        timestamps = list(self.historical_data['timestamps'])

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=list(self.historical_data['hydraulic_pressure']),
            mode='lines+markers',
            name='Hidráulica',
            line=dict(color='#f39c12', width=3)
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=list(self.historical_data['fuel_pressure']),
            mode='lines+markers',
            name='Combustible',
            line=dict(color='#e74c3c', width=3)
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=list(self.historical_data['oil_pressure']),
            mode='lines+markers',
            name='Aceite',
            line=dict(color='#9b59b6', width=3)
        ))

        fig.update_layout(
            title="🔧 Presiones en Tiempo Real",
            xaxis_title="Tiempo",
            yaxis_title="Presión (bar)",
            hovermode='x unified',
            height=400
        )

        return fig

    def run(self, host='127.0.0.1', port=8050, debug=False):
        """Ejecutar el servidor web HMI"""
        logger.info(f"🌐 Iniciando SCADA HMI Avanzado en http://{host}:{port}")
        print(f"\n🚀 AEROSPACE SCADA HMI with ALARMS")
        print(f"🌐 Accede desde tu navegador: http://{host}:{port}")
        print(f"📡 Conectando a PLC en {self.plc_host}:{self.plc_port}")
        print(f"🚨 Sistema de alarmas: {'✅ ACTIVO' if ALARMS_AVAILABLE else '❌ NO DISPONIBLE'}")
        print("🔄 La interfaz se actualiza automáticamente cada 2 segundos")
        print("🛑 Presiona Ctrl+C para detener\n")

        self.app.run(host=host, port=port, debug=debug)


def main():
    """Función principal"""
    # Crear y ejecutar HMI avanzado
    hmi = AdvancedSCADAHMI(plc_host='127.0.0.1', plc_port=5020)

    try:
        hmi.run(host='127.0.0.1', port=8050, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 SCADA HMI detenido por el usuario")
    except Exception as e:
        logger.error(f"Error ejecutando HMI: {e}")


if __name__ == "__main__":
    main()