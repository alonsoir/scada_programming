#!/usr/bin/env python3
"""
🚨 AEROSPACE SCADA - Industrial Alarm System
Sistema de alarmas configurable para SCADA industrial
"""

import asyncio
import time
import json
import csv
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlarmState(Enum):
    """Estados de alarma según estándares industriales"""
    NORMAL = "NORMAL"
    WARNING = "WARNING"      # Atención requerida
    CRITICAL = "CRITICAL"    # Acción inmediata requerida
    EMERGENCY = "EMERGENCY"  # Parada de emergencia


class AlarmPriority(Enum):
    """Prioridades según EEMUA 191 (estándar industrial)"""
    LOW = 1      # Información
    MEDIUM = 2   # Warning - respuesta en minutos
    HIGH = 3     # Critical - respuesta inmediata
    URGENT = 4   # Emergency - respuesta en segundos


@dataclass
class AlarmConfig:
    """Configuración de una alarma individual"""
    tag_name: str
    description: str
    
    # Umbrales de alarma
    warning_low: Optional[float] = None
    warning_high: Optional[float] = None
    critical_low: Optional[float] = None
    critical_high: Optional[float] = None
    emergency_low: Optional[float] = None
    emergency_high: Optional[float] = None
    
    # Configuración avanzada
    enabled: bool = True
    deadband: float = 1.0  # Histéresis para evitar oscilaciones
    delay_seconds: float = 2.0  # Delay antes de activar alarma
    auto_acknowledge: bool = False  # Auto-ack cuando vuelve a normal
    
    # Prioridad y acciones
    priority: AlarmPriority = AlarmPriority.MEDIUM
    message_template: str = "{tag_name}: {description} - Value: {value}"
    actions: List[str] = None  # Acciones a ejecutar
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []


@dataclass
class AlarmEvent:
    """Evento de alarma individual"""
    id: str
    tag_name: str
    timestamp: datetime
    state: AlarmState
    previous_state: AlarmState
    value: float
    message: str
    priority: AlarmPriority
    acknowledged: bool = False
    ack_timestamp: Optional[datetime] = None
    ack_user: Optional[str] = None
    auto_cleared: bool = False


class AlarmEngine:
    """Motor de alarmas industrial"""
    
    def __init__(self, config_file: str = "config/alarms.json"):
        self.config_file = Path(config_file)
        self.alarms_config: Dict[str, AlarmConfig] = {}
        self.current_states: Dict[str, AlarmState] = {}
        self.active_alarms: Dict[str, AlarmEvent] = {}
        self.alarm_history: List[AlarmEvent] = []
        self.alarm_timers: Dict[str, float] = {}  # Para delays
        
        # Callbacks para notificaciones
        self.alarm_callbacks: List[Callable] = []
        
        # Estadísticas
        self.stats = {
            'total_alarms': 0,
            'active_count': 0,
            'acknowledged_count': 0,
            'last_critical': None
        }
        
        # Cargar configuración
        self.load_config()
    
    def load_config(self):
        """Cargar configuración de alarmas desde archivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                for tag_name, config in config_data.items():
                    # Convertir dict a AlarmConfig
                    if 'priority' in config:
                        config['priority'] = AlarmPriority(config['priority'])
                    
                    self.alarms_config[tag_name] = AlarmConfig(
                        tag_name=tag_name,
                        **config
                    )
                    self.current_states[tag_name] = AlarmState.NORMAL
                
                logger.info(f"Cargadas {len(self.alarms_config)} configuraciones de alarma")
            else:
                # Crear configuración por defecto
                self.create_default_config()
                
        except Exception as e:
            logger.error(f"Error cargando configuración de alarmas: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Crear configuración por defecto para tags aeroespaciales"""
        default_alarms = {
            'engine_temp_1': AlarmConfig(
                tag_name='engine_temp_1',
                description='Temperatura Motor 1',
                warning_high=90.0,
                critical_high=110.0,
                emergency_high=130.0,
                priority=AlarmPriority.HIGH,
                message_template="⚠️ {description}: {value:.1f}°C - Límite: {limit}°C"
            ),
            'engine_temp_2': AlarmConfig(
                tag_name='engine_temp_2',
                description='Temperatura Motor 2',
                warning_high=90.0,
                critical_high=110.0,
                emergency_high=130.0,
                priority=AlarmPriority.HIGH
            ),
            'hydraulic_pressure': AlarmConfig(
                tag_name='hydraulic_pressure',
                description='Presión Hidráulica',
                warning_low=185.0,
                critical_low=175.0,
                emergency_low=160.0,
                warning_high=215.0,
                critical_high=225.0,
                priority=AlarmPriority.URGENT,
                delay_seconds=1.0
            ),
            'fuel_pressure': AlarmConfig(
                tag_name='fuel_pressure',
                description='Presión Combustible',
                warning_low=47.0,
                critical_low=45.0,
                emergency_low=40.0,
                priority=AlarmPriority.HIGH
            ),
            'cabin_temp': AlarmConfig(
                tag_name='cabin_temp',
                description='Temperatura Cabina',
                warning_low=16.0,
                warning_high=28.0,
                critical_low=10.0,
                critical_high=35.0,
                priority=AlarmPriority.LOW,
                delay_seconds=10.0
            )
        }
        
        # Convertir a diccionario para guardar
        self.alarms_config = default_alarms
        for tag_name in default_alarms:
            self.current_states[tag_name] = AlarmState.NORMAL
        
        self.save_config()
    
    def save_config(self):
        """Guardar configuración actual"""
        try:
            # Crear directorio si no existe
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convertir AlarmConfig a dict
            config_dict = {}
            for tag_name, config in self.alarms_config.items():
                config_data = asdict(config)
                config_data['priority'] = config.priority.value
                config_dict[tag_name] = config_data
            
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
                
            logger.info("Configuración de alarmas guardada")
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def evaluate_tag(self, tag_name: str, value: float) -> Optional[AlarmEvent]:
        """Evaluar un tag y generar alarma si es necesario"""
        if tag_name not in self.alarms_config:
            return None
        
        config = self.alarms_config[tag_name]
        if not config.enabled:
            return None
        
        current_time = time.time()
        new_state = self._determine_alarm_state(config, value)
        current_state = self.current_states[tag_name]
        
        # Verificar si cambió el estado
        if new_state != current_state:
            # Implementar delay antes de cambiar estado
            timer_key = f"{tag_name}_{new_state.value}"
            
            if timer_key not in self.alarm_timers:
                self.alarm_timers[timer_key] = current_time
                return None
            
            # Verificar si ha pasado el tiempo de delay
            if current_time - self.alarm_timers[timer_key] < config.delay_seconds:
                return None
            
            # Limpiar timer
            del self.alarm_timers[timer_key]
            
            # Generar evento de alarma
            event = self._create_alarm_event(config, value, new_state, current_state)
            
            # Actualizar estado
            self.current_states[tag_name] = new_state
            
            # Procesar evento
            self._process_alarm_event(event)
            
            return event
        
        return None
    
    def _determine_alarm_state(self, config: AlarmConfig, value: float) -> AlarmState:
        """Determinar el estado de alarma basado en el valor"""
        # Verificar emergency first (mayor prioridad)
        if config.emergency_high is not None and value >= config.emergency_high:
            return AlarmState.EMERGENCY
        if config.emergency_low is not None and value <= config.emergency_low:
            return AlarmState.EMERGENCY
        
        # Verificar critical
        if config.critical_high is not None and value >= config.critical_high:
            return AlarmState.CRITICAL
        if config.critical_low is not None and value <= config.critical_low:
            return AlarmState.CRITICAL
        
        # Verificar warning
        if config.warning_high is not None and value >= config.warning_high:
            return AlarmState.WARNING
        if config.warning_low is not None and value <= config.warning_low:
            return AlarmState.WARNING
        
        return AlarmState.NORMAL
    
    def _create_alarm_event(self, config: AlarmConfig, value: float, 
                           new_state: AlarmState, previous_state: AlarmState) -> AlarmEvent:
        """Crear evento de alarma"""
        # Generar ID único
        event_id = f"{config.tag_name}_{int(time.time() * 1000)}"
        
        # Generar mensaje
        message = config.message_template.format(
            tag_name=config.tag_name,
            description=config.description,
            value=value,
            limit=self._get_active_limit(config, new_state)
        )
        
        event = AlarmEvent(
            id=event_id,
            tag_name=config.tag_name,
            timestamp=datetime.now(),
            state=new_state,
            previous_state=previous_state,
            value=value,
            message=message,
            priority=config.priority,
            auto_cleared=(new_state == AlarmState.NORMAL)
        )
        
        return event
    
    def _get_active_limit(self, config: AlarmConfig, state: AlarmState) -> str:
        """Obtener el límite que se está violando"""
        if state == AlarmState.WARNING:
            if config.warning_high is not None:
                return f"{config.warning_high}"
            if config.warning_low is not None:
                return f"{config.warning_low}"
        elif state == AlarmState.CRITICAL:
            if config.critical_high is not None:
                return f"{config.critical_high}"
            if config.critical_low is not None:
                return f"{config.critical_low}"
        elif state == AlarmState.EMERGENCY:
            if config.emergency_high is not None:
                return f"{config.emergency_high}"
            if config.emergency_low is not None:
                return f"{config.emergency_low}"
        return "N/A"
    
    def _process_alarm_event(self, event: AlarmEvent):
        """Procesar evento de alarma"""
        # Añadir al histórico
        self.alarm_history.append(event)
        
        # Actualizar alarmas activas
        if event.state != AlarmState.NORMAL:
            self.active_alarms[event.tag_name] = event
        else:
            # Alarma regresó a normal
            if event.tag_name in self.active_alarms:
                old_event = self.active_alarms[event.tag_name]
                
                # Auto-acknowledge si está configurado
                config = self.alarms_config[event.tag_name]
                if config.auto_acknowledge:
                    old_event.acknowledged = True
                    old_event.ack_timestamp = datetime.now()
                    old_event.ack_user = "SYSTEM"
                
                del self.active_alarms[event.tag_name]
        
        # Actualizar estadísticas
        self._update_statistics(event)
        
        # Ejecutar callbacks
        for callback in self.alarm_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error en callback de alarma: {e}")
        
        # Log del evento
        logger.info(f"ALARM: {event.state.value} - {event.message}")
    
    def _update_statistics(self, event: AlarmEvent):
        """Actualizar estadísticas de alarmas"""
        self.stats['total_alarms'] += 1
        self.stats['active_count'] = len(self.active_alarms)
        self.stats['acknowledged_count'] = len([a for a in self.active_alarms.values() if a.acknowledged])
        
        if event.priority in [AlarmPriority.HIGH, AlarmPriority.URGENT]:
            self.stats['last_critical'] = event.timestamp
    
    def acknowledge_alarm(self, tag_name: str, user: str = "OPERATOR") -> bool:
        """Reconocer una alarma activa"""
        if tag_name in self.active_alarms:
            alarm = self.active_alarms[tag_name]
            alarm.acknowledged = True
            alarm.ack_timestamp = datetime.now()
            alarm.ack_user = user
            
            logger.info(f"Alarma reconocida: {tag_name} por {user}")
            return True
        
        return False
    
    def get_active_alarms(self) -> List[AlarmEvent]:
        """Obtener alarmas activas ordenadas por prioridad"""
        alarms = list(self.active_alarms.values())
        return sorted(alarms, key=lambda x: x.priority.value, reverse=True)
    
    def get_alarm_history(self, hours: int = 24) -> List[AlarmEvent]:
        """Obtener histórico de alarmas de las últimas N horas"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [event for event in self.alarm_history if event.timestamp >= cutoff]
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas del sistema de alarmas"""
        return {
            **self.stats,
            'config_count': len(self.alarms_config),
            'history_count': len(self.alarm_history),
            'unacknowledged_count': len([a for a in self.active_alarms.values() if not a.acknowledged])
        }


# Test simple
def simple_test():
    """Test simple del sistema de alarmas"""
    print("🧪 Iniciando test simple del sistema de alarmas...")
    
    # Crear motor de alarmas
    alarm_engine = AlarmEngine()
    print(f"✅ Motor creado con {len(alarm_engine.alarms_config)} configuraciones")
    
    # Callback para mostrar alarmas
    def alarm_notification(event: AlarmEvent):
        print(f"🚨 {event.state.value}: {event.message}")
    
    alarm_engine.alarm_callbacks.append(alarm_notification)
    
    # Simular algunos valores
    test_cases = [
        ('engine_temp_1', 85.0, "Normal"),
        ('engine_temp_1', 95.0, "Warning"),
        ('engine_temp_1', 115.0, "Critical"),
        ('hydraulic_pressure', 170.0, "Critical low"),
    ]
    
    for tag, value, description in test_cases:
        print(f"\n📊 Testing {tag} = {value} ({description})")
        event = alarm_engine.evaluate_tag(tag, value)
        if event:
            print(f"   ✅ Evento generado")
        else:
            print(f"   📝 Sin cambio de estado")
        
        time.sleep(0.5)
    
    # Mostrar resumen
    active = alarm_engine.get_active_alarms()
    print(f"\n📈 RESUMEN:")
    print(f"   Alarmas activas: {len(active)}")
    print(f"   Total eventos: {len(alarm_engine.alarm_history)}")
    
    return alarm_engine


if __name__ == "__main__":
    simple_test()
