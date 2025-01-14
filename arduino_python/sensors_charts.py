import streamlit as st
import serial
import time
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
from collections import deque

class SensorDataCollector:
    def __init__(self, port='COM11', baudrate=9600, max_points=100):
        self.serial_port = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        self.max_points = max_points
        
        # Initialize deques for storing data
        self.timestamps = deque(maxlen=max_points)
        self.co2_values = deque(maxlen=max_points)
        self.temp_in_values = deque(maxlen=max_points)
        self.temp_out_values = deque(maxlen=max_points)
        self.hum_in_values = deque(maxlen=max_points)
        self.hum_out_values = deque(maxlen=max_points)
        
        # Store latest values for metrics
        self.latest_values = {
            'co2': 0,
            'temp_in': 0,
            'temp_out': 0,
            'hum_in': 0,
            'hum_out': 0
        }

    def parse_line(self, line):
        """Parse a single line of sensor data"""
        try:
            if "Humidity" in line:
                parts = line.split(':')
                sensor_type = 'IN' if 'IN' in parts[0] else 'OUT'
                
                humidity_part = parts[1].split('%')[0].strip()
                humidity = float(humidity_part)
                
                temp_part = parts[2].split('*')[0].strip()
                temperature = float(temp_part)
                
                return {
                    'type': 'env',
                    'sensor': sensor_type,
                    'humidity': humidity,
                    'temperature': temperature
                }
            elif "CO2" in line:
                co2_value = float(line.split(':')[1].split('ppm')[0].strip())
                return {
                    'type': 'co2',
                    'value': co2_value
                }
        except Exception as e:
            return None

    def read_data(self):
        """Read a single data point from serial port"""
        if self.serial_port.in_waiting:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    data = self.parse_line(line)
                    if data:
                        current_time = datetime.now()
                        self.timestamps.append(current_time)
                        
                        if data['type'] == 'co2':
                            self.co2_values.append(data['value'])
                            self.latest_values['co2'] = data['value']
                        elif data['type'] == 'env':
                            if data['sensor'] == 'IN':
                                self.temp_in_values.append(data['temperature'])
                                self.hum_in_values.append(data['humidity'])
                                self.latest_values['temp_in'] = data['temperature']
                                self.latest_values['hum_in'] = data['humidity']
                            else:
                                self.temp_out_values.append(data['temperature'])
                                self.hum_out_values.append(data['humidity'])
                                self.latest_values['temp_out'] = data['temperature']
                                self.latest_values['hum_out'] = data['humidity']
                        return True
            except Exception as e:
                pass
        return False

    def get_data_for_plots(self):
        """Get current data in format suitable for plotting"""
        return {
            'timestamps': list(self.timestamps),
            'co2': list(self.co2_values),
            'temp_in': list(self.temp_in_values),
            'temp_out': list(self.temp_out_values),
            'hum_in': list(self.hum_in_values),
            'hum_out': list(self.hum_out_values)
        }

    def close(self):
        """Close the serial connection"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

def create_figures(data):
    """Create plotly figures for the dashboard"""
    fig = make_subplots(rows=3, cols=1,
                       subplot_titles=('CO2 Levels', 'Temperature', 'Humidity'),
                       vertical_spacing=0.1)
    
    # Add CO2 trace
    fig.add_trace(
        go.Scatter(x=data['timestamps'], y=data['co2'],
                  name="CO2", line=dict(color='blue')),
        row=1, col=1
    )
    
    # Add temperature traces
    fig.add_trace(
        go.Scatter(x=data['timestamps'], y=data['temp_in'],
                  name="Temperature IN", line=dict(color='red')),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=data['timestamps'], y=data['temp_out'],
                  name="Temperature OUT", line=dict(color='green')),
        row=2, col=1
    )
    
    # Add humidity traces
    fig.add_trace(
        go.Scatter(x=data['timestamps'], y=data['hum_in'],
                  name="Humidity IN", line=dict(color='red')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=data['timestamps'], y=data['hum_out'],
                  name="Humidity OUT", line=dict(color='green')),
        row=3, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        margin=dict(t=100)  # Add more top margin for metrics
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="PPM", row=1, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=2, col=1)
    fig.update_yaxes(title_text="Humidity (%)", row=3, col=1)
    
    return fig

def main():
    st.set_page_config(
        page_title="Sensor Data Dashboard",
        page_icon="🌡️",
        layout="wide"
    )
    
    # Custom CSS for metric boxes
    st.markdown("""
        <style>
        .metric-box {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 16px;
            color: #555;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'collector' not in st.session_state:
        st.session_state.collector = SensorDataCollector(port='COM11', baudrate=9600)
    
    # Create columns for metrics
    cols = st.columns(5)
    
    # Create placeholder HTML for each metric
    metric_html = """
        <div class="metric-box">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{unit}</div>
        </div>
    """
    
    metrics_config = [
        {"label": "CO2", "key": "co2", "unit": "ppm"},
        {"label": "Indoor Temperature", "key": "temp_in", "unit": "°C"},
        {"label": "Outdoor Temperature", "key": "temp_out", "unit": "°C"},
        {"label": "Indoor Humidity", "key": "hum_in", "unit": "%"},
        {"label": "Outdoor Humidity", "key": "hum_out", "unit": "%"}
    ]
    
    # Create placeholder elements
    metric_placeholders = []
    for i, metric in enumerate(metrics_config):
        metric_placeholders.append(cols[i].empty())
    
    # Create placeholder for charts
    chart_placeholder = st.empty()
    
    try:
        while True:
            # Read new data
            st.session_state.collector.read_data()
            
            # Update metrics
            for i, metric in enumerate(metrics_config):
                value = st.session_state.collector.latest_values[metric["key"]]
                html = metric_html.format(
                    label=metric["label"],
                    value=f"{value:.1f}",
                    unit=metric["unit"]
                )
                metric_placeholders[i].markdown(html, unsafe_allow_html=True)
            
            # Update charts
            plot_data = st.session_state.collector.get_data_for_plots()
            fig = create_figures(plot_data)
            chart_placeholder.plotly_chart(fig, use_container_width=True)
            
            # Short sleep to prevent high CPU usage
            time.sleep(0.1)
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        if 'collector' in st.session_state:
            st.session_state.collector.close()

if __name__ == "__main__":
    main()