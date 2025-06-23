#!/usr/bin/env python3
"""
Ejecutor del HMI Web desde la raíz del proyecto
"""

import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import asyncio
import threading
import time
from datetime import datetime, timedelta
from collections import deque
import logging

# Importar nuestro cliente Modbus (desde raíz funciona directamente)
from core.protocols.modbus_client import ModbusClient

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SCADAWebHMI:
    def __init__(self, plc_host='127.0.0.1', plc_port=5020):
        self.plc_host = plc_host
        self.plc_port = plc_port
        self.client = ModbusClient(host=plc_host, port=plc_port)
        self.is_connected = False

        # Buffer para datos históricos (últimas 100 lecturas)
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

        # Configurar Dash app
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()

        # Hilo para lectura de datos
        self.data_thread = None
        self.stop_reading = False

    def setup_layout(self):
        """Configurar el layout de la interfaz web"""
        self.app.layout = html.Div([
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

            # Estado de conexión
            html.Div([
                html.Div(id="connection-status",
                         style={'padding': '10px', 'borderRadius': '5px', 'marginBottom': '10px'}),
                html.Button("🔄 Reconectar", id="reconnect-btn",
                            style={'padding': '8px 16px', 'marginLeft': '10px'},
                            n_clicks=0)
            ], style={'marginBottom': '20px'}),

            # Métricas principales - Cards
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
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666'})
                            ], style={'width': '33%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="temp-engine-2",
                                         style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'textAlign': 'center'}),
                                html.Small("Motor 2",
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666'})
                            ], style={'width': '33%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="temp-cabin",
                                         style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'textAlign': 'center'}),
                                html.Small("Cabina", style={'display': 'block', 'textAlign': 'center', 'color': '#666'})
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
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666'})
                            ], style={'width': '33%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="pressure-fuel",
                                         style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'textAlign': 'center'}),
                                html.Small("Combustible",
                                           style={'display': 'block', 'textAlign': 'center', 'color': '#666'})
                            ], style={'width': '33%', 'display': 'inline-block'}),
                            html.Div([
                                html.Div(id="pressure-oil",
                                         style={'fontSize': '2.5rem', 'fontWeight': 'bold', 'textAlign': 'center'}),
                                html.Small("Aceite", style={'display': 'block', 'textAlign': 'center', 'color': '#666'})
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

            # Contadores y estadísticas
            html.Div([
                html.Div([
                    html.H4("📈 ESTADÍSTICAS", style={'color': '#17a2b8', 'marginBottom': '15px'}),
                    html.Div([
                        html.Div([
                            html.H5(id="flight-hours", style={'color': '#007bff', 'textAlign': 'center'}),
                            html.Small("Horas de Vuelo", style={'display': 'block', 'textAlign': 'center'})
                        ], style={'width': '50%', 'display': 'inline-block'}),
                        html.Div([
                            html.H5(id="cycles-count", style={'color': '#007bff', 'textAlign': 'center'}),
                            html.Small("Ciclos Totales", style={'display': 'block', 'textAlign': 'center'})
                        ], style={'width': '50%', 'display': 'inline-block'}),
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
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa'})

    def setup_callbacks(self):
        """Configurar callbacks de Dash para actualización automática"""

        @self.app.callback(
            [Output('connection-status', 'children'),
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
             Output('pressure-chart', 'figure')],
            [Input('interval-component', 'n_intervals'),
             Input('reconnect-btn', 'n_clicks')]
        )
        def update_dashboard(n_intervals, reconnect_clicks):
            return self.update_all_components()

    def update_all_components(self):
        """Actualizar todos los componentes del dashboard"""
        # Verificar conexión
        if not self.is_connected:
            asyncio.run(self.connect_to_plc())

        # Leer datos actuales
        data = asyncio.run(self.read_plc_data())

        if not data:
            # Sin conexión - mostrar estado de error
            return self.get_error_state()

        # Actualizar datos históricos
        now = datetime.now()
        self.historical_data['timestamps'].append(now)
        for key, value in data.items():
            if key in self.historical_data:
                self.historical_data[key].append(value)

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

        return (
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
        )

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

        return (
            conn_status, conn_style,
            no_data, no_data, no_data,  # Temperaturas
            no_data, no_data, no_data,  # Presiones
            "OFF", status_off_style, "OFF", status_off_style,  # Bombas
            "OFF", status_off_style, "OFF", status_off_style,  # Estados
            no_data, no_data,  # Contadores
            empty_chart, empty_chart  # Gráficos
        )

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

        # Convertir timestamps a lista
        timestamps = list(self.historical_data['timestamps'])

        # Añadir líneas de temperatura
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
        logger.info(f"🌐 Iniciando HMI Web en http://{host}:{port}")
        print(f"\n🚀 AEROSPACE SCADA HMI")
        print(f"🌐 Accede desde tu navegador: http://{host}:{port}")
        print(f"📡 Conectando a PLC en {self.plc_host}:{self.plc_port}")
        print("🔄 La interfaz se actualiza automáticamente cada 2 segundos")
        print("🛑 Presiona Ctrl+C para detener\n")

        self.app.run(host=host, port=port, debug=debug)


def main():
    """Función principal"""
    # Crear y ejecutar HMI
    hmi = SCADAWebHMI(plc_host='127.0.0.1', plc_port=5020)

    try:
        hmi.run(host='127.0.0.1', port=8050, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 HMI Web detenido por el usuario")
    except Exception as e:
        logger.error(f"Error ejecutando HMI: {e}")


if __name__ == "__main__":
    main()