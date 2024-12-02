import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import re
import io

# Set page config
st.set_page_config(
    page_title="Environmental Monitoring Dashboard", page_icon="🌡️", layout="wide"
)

# Custom CSS
st.markdown(
    """
    <style>
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""",
    unsafe_allow_html=True,
)


def process_environmental_data(text):
    # Initialize lists to store the data
    measurements = []

    # Regular expressions for all measurements in one group
    pattern = (
        r"Humidity out: (\d+\.\d+) %\s*"
        r"Temperature out: (\d+\.\d+) \*C\s*"
        r"Humidity IN: (\d+\.\d+) %\s*"
        r"Temperature IN: (\d+\.\d+) \*C\s*"
        r"CO2: (\d+\.\d+)\s+ppm"
    )

    # Find all matches
    matches = re.finditer(pattern, text)

    # Process each complete set of measurements
    for match in matches:
        measurements.append(
            {
                "Humidity_Out": float(match.group(1)),
                "Temperature_Out": float(match.group(2)),
                "Humidity_In": float(match.group(3)),
                "Temperature_In": float(match.group(4)),
                "CO2": float(match.group(5)),
            }
        )

    # Create DataFrame from the list of dictionaries
    df = pd.DataFrame(measurements)

    # Add timestamp column (simulated)
    base_time = datetime.now() - timedelta(hours=len(df))
    df["timestamp"] = [base_time + timedelta(hours=x) for x in range(len(df))]

    return df


def read_file_with_encoding(file_content):
    # Try different encodings
    encodings = ["utf-8", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            return file_content.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError("Failed to decode file with any encoding")


# Title
st.title("🌡️ Environmental Monitoring Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload sensor data file", type=["txt"])

if uploaded_file is not None:
    try:
        # Read the file content with different encodings
        file_content = uploaded_file.read()
        data_text = read_file_with_encoding(file_content)

        # Process the data
        df = process_environmental_data(data_text)

        # Create three columns for statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### Temperature Statistics")
            temp_stats = pd.DataFrame(
                {
                    "Indoor": [
                        df["Temperature_In"].min(),
                        df["Temperature_In"].mean(),
                        df["Temperature_In"].max(),
                    ],
                    "Outdoor": [
                        df["Temperature_Out"].min(),
                        df["Temperature_Out"].mean(),
                        df["Temperature_Out"].max(),
                    ],
                },
                index=["Min", "Average", "Max"],
            ).round(2)
            st.dataframe(temp_stats, use_container_width=True)

        with col2:
            st.markdown("### Humidity Statistics")
            humid_stats = pd.DataFrame(
                {
                    "Indoor": [
                        df["Humidity_In"].min(),
                        df["Humidity_In"].mean(),
                        df["Humidity_In"].max(),
                    ],
                    "Outdoor": [
                        df["Humidity_Out"].min(),
                        df["Humidity_Out"].mean(),
                        df["Humidity_Out"].max(),
                    ],
                },
                index=["Min", "Average", "Max"],
            ).round(2)
            st.dataframe(humid_stats, use_container_width=True)

        with col3:
            st.markdown("### CO2 Statistics")
            co2_stats = pd.DataFrame(
                {"CO2 (ppm)": [df["CO2"].min(), df["CO2"].mean(), df["CO2"].max()]},
                index=["Min", "Average", "Max"],
            ).round(2)
            st.dataframe(co2_stats, use_container_width=True)

        # Create metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Indoor Temperature",
                f"{df['Temperature_In'].iloc[-1]:.1f}°C",
                f"{df['Temperature_In'].iloc[-1] - df['Temperature_In'].iloc[-2]:.1f}°C",
            )
        with col2:
            st.metric(
                "Indoor Humidity",
                f"{df['Humidity_In'].iloc[-1]:.1f}%",
                f"{df['Humidity_In'].iloc[-1] - df['Humidity_In'].iloc[-2]:.1f}%",
            )
        with col3:
            st.metric(
                "Outdoor Temperature",
                f"{df['Temperature_Out'].iloc[-1]:.1f}°C",
                f"{df['Temperature_Out'].iloc[-1] - df['Temperature_Out'].iloc[-2]:.1f}°C",
            )
        with col4:
            st.metric(
                "Outdoor Humidity",
                f"{df['Humidity_Out'].iloc[-1]:.1f}%",
                f"{df['Humidity_Out'].iloc[-1] - df['Humidity_Out'].iloc[-2]:.1f}%",
            )
        with col5:
            st.metric(
                "CO2 Level",
                f"{df['CO2'].iloc[-1]:.0f} ppm",
                f"{df['CO2'].iloc[-1] - df['CO2'].iloc[-2]:.0f} ppm",
            )

        # Update the layout and chart configuration in the plotting section

        # Create main chart
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=(
                "<span style='color: white'>Temperature & Humidity</span>",
                "<span style='color: white'>CO2 Levels</span>",
            ),
        )

        # Temperature and Humidity plot
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["Temperature_In"],
                name="Indoor Temp",
                line=dict(color="#FF9900", width=2),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["Temperature_Out"],
                name="Outdoor Temp",
                line=dict(color="#FF99FF", width=2),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["Humidity_In"],
                name="Indoor Humidity",
                line=dict(color="#0099FF", width=2),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["Humidity_Out"],
                name="Outdoor Humidity",
                line=dict(color="#00FFFF", width=2),
            ),
            row=1,
            col=1,
        )

        # CO2 plot
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["CO2"],
                name="CO2",
                line=dict(color="#FF0000", width=2),
            ),
            row=2,
            col=1,
        )

        # Update layout for dark theme
        fig.update_layout(
            height=800,
            showlegend=True,
            plot_bgcolor="rgba(26,28,36,0.8)",
            paper_bgcolor="rgba(26,28,36,0.8)",
            legend=dict(
                yanchor="top",
                y=1.2,
                xanchor="left",
                x=0.01,
                orientation="h",
                font=dict(color="white"),
            ),
            font=dict(color="white"),
        )

        # Update axes for dark theme
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
            linecolor="rgba(128,128,128,0.2)",
            tickfont=dict(color="white"),
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
            linecolor="rgba(128,128,128,0.2)",
            tickfont=dict(color="white"),
            title_font=dict(color="white"),
        )

        # Add y-axis titles
        fig.update_yaxes(title_text="Temperature (°C) / Humidity (%)", row=1, col=1)
        fig.update_yaxes(title_text="CO2 (ppm)", row=2, col=1)

        # Update hover template
        fig.update_traces(
            hovertemplate="<b>%{y:.1f}</b><br>%{x}<extra></extra>",
            hoverlabel=dict(
                bgcolor="rgba(26,28,36,0.8)",
                font_color="white",
                font_size=12,
                bordercolor="white",
            ),
        )
        # Show plot
        st.plotly_chart(fig, use_container_width=True)

        # Add CO2 threshold warning
        if df["CO2"].iloc[-1] > 1000:
            st.warning(
                f"⚠️ CO2 levels are above 1000 ppm (Current: {df['CO2'].iloc[-1]:.0f} ppm)"
            )

        # Show data table
        st.subheader("📊 Raw Data")
        display_df = df.drop("timestamp", axis=1).round(2)
        st.dataframe(display_df)

    except Exception as e:
        st.error(f"Error processing the file: {str(e)}")
        st.error("Please make sure the file format matches the expected structure.")

else:
    st.info("Please upload a sensor data file to begin visualization")
