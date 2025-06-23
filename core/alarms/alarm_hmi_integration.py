#!/usr/bin/env python3
"""
🚨 HMI Integration - Sistema de Alarmas para SCADA Web
Integra el sistema de alarmas con la interfaz web existente
"""

import dash
from dash import html, dcc, Input, Output, State, callback, dash_table
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
import json

# Importar nuestro sistema de alarmas
from core.alarms.alarm_system import AlarmEngine, AlarmState, AlarmPriority


class AlarmHMIIntegration:
    """Integración del sistema de alarmas con HMI web"""

    def __init__(self, alarm_engine: AlarmEngine):
        self.alarm_engine = alarm_engine
        self.setup_alarm_callbacks()

    def setup_alarm_callbacks(self):
        """Configurar callbacks para alarmas"""

        def log_alarm_event(event):
            print(f"🚨 ALARM HMI: {event.state.value} - {event.message}")

        self.alarm_engine.add_alarm_callback(log_alarm_event)

    def create_alarm_banner(self):
        """Crear banner de alarmas para mostrar en la parte superior"""
        return html.Div([
            html.Div(id="alarm-banner", className="alarm-banner"),
            dcc.Interval(
                id='alarm-banner-interval',
                interval=1000,  # Actualizar cada segundo
                n_intervals=0
            )
        ])

    def create_alarm_summary_card(self):
        """Crear tarjeta resumen de alarmas"""
        return html.Div([
            html.Div([
                html.H4("🚨 ALARMAS", className="card-title text-danger"),
                html.Div([
                    html.Div([
                        html.Div(id="alarm-count-critical", className="alarm-count critical"),
                        html.Small("Críticas", className="alarm-label")
                    ], className="col-3"),
                    html.Div([
                        html.Div(id="alarm-count-warning", className="alarm-count warning"),
                        html.Small("Advertencia", className="alarm-label")
                    ], className="col-3"),
                    html.Div([
                        html.Div(id="alarm-count-active", className="alarm-count active"),
                        html.Small("Activas", className="alarm-label")
                    ], className="col-3"),
                    html.Div([
                        html.Div(id="alarm-count-unack", className="alarm-count unack"),
                        html.Small("Sin ACK", className="alarm-label")
                    ], className="col-3"),
                ], className="row")
            ], className="card-body")
        ], className="card border-danger mb-3")

    def create_alarm_table(self):
        """Crear tabla de alarmas activas"""
        return html.Div([
            html.H5("📋 Alarmas Activas"),
            html.Div(id="alarm-table-container"),
            html.Div([
                html.Button("🔄 Refresh", id="alarm-refresh-btn",
                            className="btn btn-primary me-2"),
                html.Button("✅ ACK Selected", id="alarm-ack-btn",
                            className="btn btn-warning me-2"),
                html.Button("📊 Export Report", id="alarm-export-btn",
                            className="btn btn-success")
            ], className="mt-3")
        ], className="card-body")

    def create_alarm_history_chart(self):
        """Crear gráfico de tendencia de alarmas"""
        return html.Div([
            html.H5("📈 Tendencia de Alarmas (24h)"),
            dcc.Graph(id="alarm-trend-chart")
        ])

    def get_alarm_banner_content(self):
        """Obtener contenido del banner de alarmas"""
        active_alarms = self.alarm_engine.get_active_alarms()

        if not active_alarms:
            return html.Div(
                "✅ Sistema Normal - Sin Alarmas Activas",
                className="alert alert-success mb-0"
            )

        # Encontrar alarma de mayor prioridad
        highest_priority = max(active_alarms, key=lambda x: x.priority.value)

        # Determinar clase CSS según prioridad
        if highest_priority.priority == AlarmPriority.URGENT:
            alert_class = "alert alert-danger flashing"
        elif highest_priority.priority == AlarmPriority.HIGH:
            alert_class = "alert alert-danger"
        elif highest_priority.priority == AlarmPriority.MEDIUM:
            alert_class = "alert alert-warning"
        else:
            alert_class = "alert alert-info"

        # Contar alarmas no reconocidas
        unack_count = len([a for a in active_alarms if not a.acknowledged])

        message = f"🚨 {len(active_alarms)} Alarmas Activas"
        if unack_count > 0:
            message += f" ({unack_count} sin reconocer)"

        message += f" - Más crítica: {highest_priority.message}"

        return html.Div(message, className=f"{alert_class} mb-0")

    def get_alarm_summary_data(self):
        """Obtener datos resumen de alarmas"""
        active_alarms = self.alarm_engine.get_active_alarms()

        critical_count = len([a for a in active_alarms if a.priority in [AlarmPriority.HIGH, AlarmPriority.URGENT]])
        warning_count = len([a for a in active_alarms if a.priority == AlarmPriority.MEDIUM])
        unack_count = len([a for a in active_alarms if not a.acknowledged])

        return {
            'critical': critical_count,
            'warning': warning_count,
            'active': len(active_alarms),
            'unack': unack_count
        }

    def get_alarm_table_data(self):
        """Obtener datos para la tabla de alarmas"""
        active_alarms = self.alarm_engine.get_active_alarms()

        if not active_alarms:
            return html.Div("✅ No hay alarmas activas", className="alert alert-success")

        # Preparar datos para la tabla
        table_data = []
        for alarm in active_alarms:
            table_data.append({
                'Timestamp': alarm.timestamp.strftime('%H:%M:%S'),
                'Tag': alarm.tag_name,
                'Estado': alarm.state.value,
                'Prioridad': alarm.priority.name,
                'Valor': f"{alarm.value:.1f}",
                'Mensaje': alarm.message,
                'ACK': '✅' if alarm.acknowledged else '❌',
                'Usuario': alarm.ack_user or '-'
            })

        # Crear tabla con Dash DataTable
        return dash_table.DataTable(
            id='alarm-table',
            data=table_data,
            columns=[
                {'name': 'Hora', 'id': 'Timestamp'},
                {'name': 'Tag', 'id': 'Tag'},
                {'name': 'Estado', 'id': 'Estado'},
                {'name': 'Prioridad', 'id': 'Prioridad'},
                {'name': 'Valor', 'id': 'Valor'},
                {'name': 'Mensaje', 'id': 'Mensaje'},
                {'name': 'ACK', 'id': 'ACK'},
                {'name': 'Usuario', 'id': 'Usuario'}
            ],
            style_cell={
                'textAlign': 'left',
                'fontSize': '12px',
                'fontFamily': 'Arial'
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{Estado} = EMERGENCY'},
                    'backgroundColor': '#ffebee',
                    'color': 'red',
                    'fontWeight': 'bold'
                },
                {
                    'if': {'filter_query': '{Estado} = CRITICAL'},
                    'backgroundColor': '#fff3e0',
                    'color': 'darkorange',
                    'fontWeight': 'bold'
                },
                {
                    'if': {'filter_query': '{Estado} = WARNING'},
                    'backgroundColor': '#fffde7',
                    'color': 'orange'
                },
                {
                    'if': {'filter_query': '{ACK} = ❌'},
                    'backgroundColor': '#fce4ec'
                }
            ],
            style_header={
                'backgroundColor': '#f5f5f5',
                'fontWeight': 'bold'
            },
            row_selectable='multi',
            selected_rows=[],
            page_size=10,
            sort_action='native'
        )

    def get_alarm_trend_chart(self):
        """Crear gráfico de tendencia de alarmas"""
        # Obtener histórico de 24 horas
        history = self.alarm_engine.get_alarm_history(hours=24)

        if not history:
            fig = go.Figure()
            fig.update_layout(
                title="📈 Tendencia de Alarmas (24h)",
                xaxis_title="Tiempo",
                yaxis_title="Número de Alarmas",
                annotations=[{
                    'text': 'Sin datos históricos disponibles',
                    'x': 0.5,
                    'y': 0.5,
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False
                }]
            )
            return fig

        # Agrupar por hora
        df = pd.DataFrame([{
            'timestamp': event.timestamp,
            'state': event.state.value,
            'priority': event.priority.value
        } for event in history])

        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_counts = df.groupby(['hour', 'state']).size().unstack(fill_value=0)

        fig = go.Figure()

        # Añadir líneas para cada tipo de alarma
        colors = {
            'WARNING': '#ff9800',
            'CRITICAL': '#f44336',
            'EMERGENCY': '#d32f2f'
        }

        for state in ['WARNING', 'CRITICAL', 'EMERGENCY']:
            if state in hourly_counts.columns:
                fig.add_trace(go.Scatter(
                    x=hourly_counts.index,
                    y=hourly_counts[state],
                    mode='lines+markers',
                    name=state,
                    line=dict(color=colors[state], width=3),
                    marker=dict(size=6)
                ))

        fig.update_layout(
            title="📈 Tendencia de Alarmas (24h)",
            xaxis_title="Tiempo",
            yaxis_title="Número de Alarmas por Hora",
            hovermode='x unified',
            height=300
        )

        return fig

    def process_tag_data(self, tag_data: dict):
        """Procesar datos de tags y evaluar alarmas"""
        alarm_events = []

        for tag_name, value in tag_data.items():
            if isinstance(value, (int, float)):
                event = self.alarm_engine.evaluate_tag(tag_name, value)
                if event:
                    alarm_events.append(event)

        return alarm_events

    def acknowledge_selected_alarms(self, selected_rows, table_data, user="OPERATOR"):
        """Reconocer alarmas seleccionadas"""
        if not selected_rows or not table_data:
            return False

        ack_count = 0
        for row_idx in selected_rows:
            if row_idx < len(table_data):
                tag_name = table_data[row_idx]['Tag']
                if self.alarm_engine.acknowledge_alarm(tag_name, user):
                    ack_count += 1

        return ack_count > 0

    def export_alarm_report(self):
        """Exportar reporte de alarmas"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"alarm_report_{timestamp}.csv"

        try:
            self.alarm_engine.export_alarm_report(filename, hours=24)
            return filename
        except Exception as e:
            return f"Error: {str(e)}"


def get_alarm_css():
    """CSS adicional para alarmas"""
    return """
    .alarm-banner {
        position: sticky;
        top: 0;
        z-index: 1000;
    }

    .flashing {
        animation: flash 1s infinite;
    }

    @keyframes flash {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.5; }
    }

    .alarm-count {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 5px;
    }

    .alarm-count.critical {
        background-color: #ffebee;
        color: #d32f2f;
        border: 2px solid #f44336;
    }

    .alarm-count.warning {
        background-color: #fff8e1;
        color: #f57c00;
        border: 2px solid #ff9800;
    }

    .alarm-count.active {
        background-color: #e3f2fd;
        color: #1976d2;
        border: 2px solid #2196f3;
    }

    .alarm-count.unack {
        background-color: #fce4ec;
        color: #c2185b;
        border: 2px solid #e91e63;
    }

    .alarm-label {
        display: block;
        text-align: center;
        color: #666;
        font-weight: normal;
    }
    """


# Ejemplo de integración
def create_alarm_integrated_layout(alarm_hmi: AlarmHMIIntegration):
    """Crear layout integrado con alarmas"""
    return html.Div([
        # Banner de alarmas (sticky top)
        alarm_hmi.create_alarm_banner(),

        # Contenido principal
        html.Div([
            # Resumen de alarmas
            alarm_hmi.create_alarm_summary_card(),

            # Dos columnas: tabla y gráfico
            html.Div([
                html.Div([
                    alarm_hmi.create_alarm_table()
                ], className="col-8"),

                html.Div([
                    alarm_hmi.create_alarm_history_chart()
                ], className="col-4")
            ], className="row"),

        ], className="container-fluid p-3"),

        # CSS personalizado
        html.Style(children=get_alarm_css())
    ])


if __name__ == "__main__":
    # Ejemplo de uso
    alarm_engine = AlarmEngine()
    alarm_hmi = AlarmHMIIntegration(alarm_engine)

    # Simular algunos datos
    test_data = {
        'engine_temp_1': 115.0,  # Critical
        'hydraulic_pressure': 170.0,  # Critical low
        'cabin_temp': 25.0  # Normal
    }

    events = alarm_hmi.process_tag_data(test_data)
    print(f"Eventos generados: {len(events)}")

    # Mostrar resumen
    summary = alarm_hmi.get_alarm_summary_data()
    print(f"Resumen de alarmas: {summary}")