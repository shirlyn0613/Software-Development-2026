from __future__ import annotations

import html
import smtplib
import ssl
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import streamlit as st

try:
    import folium
    from streamlit.components.v1 import html as st_html
except Exception:  # pragma: no cover
    folium = None
    st_html = None


API_URL = "https://api.openweathermap.org/data/2.5/weather"
LOG_FILE = Path("alert_log.txt")

CITY_TREE = {
    "China": {
        "Beijing": ["Beijing"],
        "Shanghai": ["Shanghai"],
        "Guangdong": ["Guangzhou", "Shenzhen", "Zhuhai", "Foshan"],
        "Hubei": ["Wuhan", "Yichang", "Jingzhou"],
        "Jiangsu": ["Nanjing", "Suzhou", "Wuxi"],
        "Zhejiang": ["Hangzhou", "Ningbo", "Wenzhou"],
        "Sichuan": ["Chengdu", "Mianyang", "Leshan"],
        "Shaanxi": ["Xi'an", "Xianyang", "Baoji"],
        "Yunnan": ["Kunming", "Chuxiong"],
        "Shanxi": ["Taiyuan", "Xinzhou"],
        "Fujian": ["Fuzhou", "Xiamen", "Sanming"],
        "Hainan": ["Haikou", "Sanya"],
        "Tianjin": ["Tianjin"],
        "Chongqing": ["Chongqing"],
    },
    "United States": {
        "California": ["Los Angeles", "San Francisco", "San Diego"],
        "New York": ["New York", "Buffalo", "Albany"],
        "Texas": ["Houston", "Dallas", "Austin"],
    },
    "United Kingdom": {
        "England": ["London", "Manchester", "Birmingham"],
        "Scotland": ["Edinburgh", "Glasgow"],
    },
}

STATUS_STYLES = {
    "Normal": {
        "chip": "#16a34a",
        "fill": "#bbf7d0",
        "soft": "#ecfdf3",
        "text": "#14532d",
        "label": "Green: Normal",
    },
    "Moderate": {
        "chip": "#d97706",
        "fill": "#fef3c7",
        "soft": "#fffbeb",
        "text": "#78350f",
        "label": "Yellow: Moderate",
    },
    "Heavy - ALERT": {
        "chip": "#dc2626",
        "fill": "#fecaca",
        "soft": "#fef2f2",
        "text": "#7f1d1d",
        "label": "Red: ALERT",
    },
}


@dataclass
class WeatherRecord:
    city: str
    query_city: str
    rainfall: float
    level: str
    color: str
    temperature: float | None
    humidity: int | None
    condition: str
    latitude: float | None
    longitude: float | None
    timestamp: datetime


def safe_float(value: Any, default: float | None = None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def check_alert(rainfall: float) -> tuple[str, str]:
    if rainfall < 10:
        return "Normal", "green"
    if rainfall < 20:
        return "Moderate", "yellow"
    return "Heavy - ALERT", "red"


def fetch_weather(city: str, api_key: str) -> tuple[WeatherRecord | None, str | None]:
    """Fetch current weather and rainfall information from OpenWeatherMap."""
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(API_URL, params=params, timeout=12)
        response.raise_for_status()
        data = response.json()

        rain = data.get("rain", {})
        rainfall_1h = safe_float(rain.get("1h"), 0.0) or 0.0
        rainfall_3h = safe_float(rain.get("3h"), 0.0) or 0.0
        rainfall = rainfall_1h if rainfall_1h else rainfall_3h / 3.0 if rainfall_3h else 0.0
        level, color = check_alert(rainfall)

        weather_items = data.get("weather") or [{}]
        condition = str(weather_items[0].get("description", "Unknown")).title()
        coord = data.get("coord", {})
        main = data.get("main", {})

        return (
            WeatherRecord(
                city=data.get("name", city),
                query_city=city,
                rainfall=rainfall,
                level=level,
                color=color,
                temperature=safe_float(main.get("temp")),
                humidity=int(main["humidity"]) if main.get("humidity") is not None else None,
                condition=condition,
                latitude=safe_float(coord.get("lat")),
                longitude=safe_float(coord.get("lon")),
                timestamp=datetime.now(),
            ),
            None,
        )
    except requests.exceptions.HTTPError as exc:
        return None, f"{city}: HTTP error - {exc}"
    except requests.exceptions.RequestException as exc:
        return None, f"{city}: Request error - {exc}"
    except ValueError:
        return None, f"{city}: Invalid JSON response."
    except Exception as exc:
        return None, f"{city}: Unexpected error - {exc}"


def log_alert(record: WeatherRecord) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"[{timestamp}] {record.city} | Rainfall: {record.rainfall:.2f} mm/h | "
        f"Level: {record.level}\n"
    )
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(line)


def init_state() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("last_alert_signature", {})


def refresh_component() -> None:
    try:
        from streamlit_autorefresh import st_autorefresh

        st_autorefresh(interval=5 * 60 * 1000, key="rainfall_autorefresh")
    except Exception:
        pass


def append_history(records: list[WeatherRecord]) -> None:
    for record in records:
        st.session_state.history.append(
            {
                "time": record.timestamp,
                "city": record.city,
                "rainfall": record.rainfall,
                "level": record.level,
                "temperature": record.temperature,
                "humidity": record.humidity,
            }
        )
    st.session_state.history = st.session_state.history[-200:]


def build_forecast(frame: pd.DataFrame, city: str) -> pd.DataFrame:
    city_frame = frame[frame["city"] == city].sort_values("time").copy()
    if len(city_frame) < 3:
        return pd.DataFrame()

    city_frame["time"] = pd.to_datetime(city_frame["time"])
    city_frame["minute_index"] = (
        city_frame["time"] - city_frame["time"].min()
    ).dt.total_seconds() / 60.0
    x = city_frame["minute_index"].tolist()
    y = city_frame["rainfall"].tolist()

    if len(set(x)) < 2:
        return pd.DataFrame()

    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denominator = sum((xi - x_mean) ** 2 for xi in x)
    slope = numerator / denominator if denominator else 0.0
    intercept = y_mean - slope * x_mean

    step = max(5.0, x[-1] - x[-2]) if len(x) >= 2 else 5.0
    future_rows = []
    for index in range(1, 4):
        future_x = x[-1] + step * index
        predicted = max(0.0, intercept + slope * future_x)
        future_rows.append(
            {
                "time": city_frame["time"].iloc[-1] + pd.Timedelta(minutes=step * index),
                "rainfall": predicted,
                "kind": "Forecast",
            }
        )

    actual = city_frame[["time", "rainfall"]].copy()
    actual["kind"] = "Actual"
    return pd.concat([actual, pd.DataFrame(future_rows)], ignore_index=True)


def send_email_notification(
    smtp_host: str,
    smtp_port: int,
    sender: str,
    password: str,
    recipient: str,
    record: WeatherRecord,
) -> tuple[bool, str]:
    try:
        message = EmailMessage()
        message["Subject"] = f"Rainfall Alert: {record.city}"
        message["From"] = sender
        message["To"] = recipient
        message.set_content(
            f"Red alert triggered for {record.city}.\n"
            f"Rainfall: {record.rainfall:.2f} mm/h\n"
            f"Status: {record.level}\n"
            f"Time: {record.timestamp:%Y-%m-%d %H:%M:%S}"
        )

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=12) as server:
            server.starttls(context=context)
            server.login(sender, password)
            server.send_message(message)
        return True, "Email sent."
    except Exception as exc:
        return False, f"Email failed: {exc}"


def send_sms_notification(
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str,
    record: WeatherRecord,
) -> tuple[bool, str]:
    try:
        from twilio.rest import Client  # type: ignore

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=(
                f"Rainfall alert for {record.city}: "
                f"{record.rainfall:.2f} mm/h ({record.level})"
            ),
            from_=from_number,
            to=to_number,
        )
        return True, "SMS sent."
    except Exception as exc:
        return False, f"SMS failed: {exc}"


def render_map(records: list[WeatherRecord]) -> None:
    if folium is None or st_html is None:
        st.caption("Map visualization is unavailable in this environment.")
        return

    geo_records = [item for item in records if item.latitude is not None and item.longitude is not None]
    if not geo_records:
        st.caption("No map coordinates returned yet.")
        return

    center_lat = sum(item.latitude or 0.0 for item in geo_records) / len(geo_records)
    center_lon = sum(item.longitude or 0.0 for item in geo_records) / len(geo_records)
    zoom = 4 if len(geo_records) > 1 else 7
    rainfall_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    for record in geo_records:
        popup = folium.Popup(
            (
                f"<b>{html.escape(record.city)}</b><br>"
                f"Rainfall: {record.rainfall:.2f} mm/h<br>"
                f"Status: {record.level}<br>"
                f"Condition: {html.escape(record.condition)}"
            ),
            max_width=240,
        )
        icon_color = "red" if record.color == "red" else "orange" if record.color == "yellow" else "green"
        folium.CircleMarker(
            location=[record.latitude, record.longitude],
            radius=8,
            color=icon_color,
            fill=True,
            fill_color=icon_color,
            fill_opacity=0.9,
            popup=popup,
            tooltip=record.city,
        ).add_to(rainfall_map)

    legend = """
    <div style="
        position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%);
        z-index: 9999; background: rgba(255,255,255,0.95); padding: 5px 12px;
        border-radius: 999px; font-size: 11px; color: #111827;">
      <span style="color:#16a34a;">●</span> Green&nbsp;&nbsp;
      <span style="color:#d97706;">●</span> Yellow&nbsp;&nbsp;
      <span style="color:#dc2626;">●</span> Red
    </div>
    """
    rainfall_map.get_root().html.add_child(folium.Element(legend))
    st_html(rainfall_map._repr_html_(), height=360, scrolling=False)


def render_city_card(record: WeatherRecord) -> str:
    style = STATUS_STYLES[record.level]
    temperature = f"{record.temperature:.2f} C" if record.temperature is not None else "--"
    humidity = f"{record.humidity}%" if record.humidity is not None else "--"
    return (
        f'<div class="city-card">'
        f'<div class="city-title">📍 {html.escape(record.city)}</div>'
        f'<div class="card-label">Rainfall</div>'
        f'<div class="rainfall-value">{record.rainfall:.2f} mm/h</div>'
        f'<div class="status-bar" style="background:{style["fill"]};color:{style["text"]};">'
        f'{style["label"]}'
        f"</div>"
        f'<div class="category">Category: {record.level}</div>'
        f'<div class="city-detail"><b>Temp:</b> {temperature}</div>'
        f'<div class="city-detail"><b>Humidity:</b> {humidity}</div>'
        f'<div class="city-detail"><b>Condition:</b> {html.escape(record.condition)}</div>'
        f"</div>"
    )


def load_recent_log(limit: int = 20) -> str:
    if not LOG_FILE.exists():
        return "No alert log yet."
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[-limit:]) if lines else "No alert log yet."


def render_controls() -> tuple[str, list[str], dict[str, Any]]:
    control_cols = st.columns([1.1, 1.2, 1.2, 1.8, 1])
    countries = list(CITY_TREE)
    country = control_cols[0].selectbox("Country", countries, index=countries.index("China"))

    provinces = list(CITY_TREE[country])
    default_province = "Beijing" if country == "China" else provinces[0]
    province = control_cols[1].selectbox(
        "Province / Region",
        provinces,
        index=provinces.index(default_province),
    )

    city_options = CITY_TREE[country][province]
    default_city = "Beijing" if country == "China" and province == "Beijing" else city_options[0]
    primary_city = control_cols[2].selectbox(
        "City",
        city_options,
        index=city_options.index(default_city),
    )

    all_country_cities = [
        city
        for province_cities in CITY_TREE[country].values()
        for city in province_cities
        if city != primary_city
    ]
    comparison = control_cols[3].multiselect(
        "Comparison Cities",
        all_country_cities,
        default=[],
    )
    refresh = control_cols[4].button("Refresh All Data", use_container_width=True)

    api_key = st.text_input("OpenWeatherMap API Key", type="password")

    notification_config: dict[str, Any] = {}
    with st.expander("Optional alert notifications"):
        left, right = st.columns(2)
        with left:
            notification_config["enable_email"] = st.checkbox("Email alerts")
            notification_config["smtp_host"] = st.text_input("SMTP host", value="smtp.gmail.com")
            notification_config["smtp_port"] = st.number_input(
                "SMTP port", min_value=1, max_value=65535, value=587, step=1
            )
            notification_config["email_sender"] = st.text_input("Sender email")
            notification_config["email_password"] = st.text_input("Email password", type="password")
            notification_config["email_recipient"] = st.text_input("Recipient email")
        with right:
            notification_config["enable_sms"] = st.checkbox("SMS alerts")
            notification_config["twilio_sid"] = st.text_input("Twilio SID")
            notification_config["twilio_token"] = st.text_input("Twilio token", type="password")
            notification_config["twilio_from"] = st.text_input("SMS from number")
            notification_config["twilio_to"] = st.text_input("SMS to number")

    if refresh:
        st.rerun()

    selected_cities = [primary_city, *comparison]
    return api_key, selected_cities, notification_config


def handle_red_alerts(records: list[WeatherRecord], config: dict[str, Any]) -> None:
    for record in records:
        if record.level != "Heavy - ALERT":
            continue

        alert_signature = f"{record.city}:{record.timestamp:%Y-%m-%d %H:%M}"
        if st.session_state.last_alert_signature.get(record.city) == alert_signature:
            continue

        log_alert(record)
        st.session_state.last_alert_signature[record.city] = alert_signature
        st.warning(f"Red alert triggered for {record.city}.")

        if config.get("enable_email") and config.get("email_sender") and config.get("email_recipient"):
            _, message = send_email_notification(
                config["smtp_host"],
                int(config["smtp_port"]),
                config["email_sender"],
                config.get("email_password", ""),
                config["email_recipient"],
                record,
            )
            st.caption(message)

        if config.get("enable_sms") and config.get("twilio_sid") and config.get("twilio_to"):
            _, message = send_sms_notification(
                config["twilio_sid"],
                config.get("twilio_token", ""),
                config.get("twilio_from", ""),
                config["twilio_to"],
                record,
            )
            st.caption(message)


def render_dashboard() -> None:
    st.set_page_config(page_title="Rainfall Monitor", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding: 1.45rem 1.8rem 2.1rem;}
        header[data-testid="stHeader"] {background: transparent;}
        .app-title {
            font-size: 1.8rem; font-weight: 750; color: #111827; margin: 0 0 0.9rem;
        }
        .map-title {
            font-size: 0.98rem; font-weight: 700; color: #374151; margin: 1rem 0 0.45rem;
        }
        .city-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 14px; margin-top: 1rem;
        }
        .city-card {
            background: #ffffff; border: 1px solid #e5e7eb; border-radius: 6px;
            padding: 12px 13px 13px; min-height: 188px;
            box-shadow: 0 1px 2px rgba(15,23,42,0.04);
        }
        .city-title {font-size: 1.03rem; font-weight: 740; color: #111827; margin-bottom: 12px;}
        .card-label {font-size: 0.75rem; color: #6b7280; margin-bottom: 2px;}
        .rainfall-value {font-size: 1.35rem; color: #111827; line-height: 1.2; margin-bottom: 10px;}
        .status-bar {
            text-align: center; border-radius: 6px; padding: 7px 8px;
            font-size: 0.82rem; font-weight: 750; margin-bottom: 7px;
        }
        .category {font-size: 0.68rem; color: #9ca3af; margin-bottom: 11px;}
        .city-detail {font-size: 0.72rem; color: #374151; margin-top: 7px;}
        div[data-testid="stMetric"] {
            background: #ffffff; border: 1px solid #e5e7eb; border-radius: 6px;
            padding: 12px 14px;
        }
        div[data-testid="stButton"] button {height: 2.45rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_state()
    refresh_component()

    st.markdown('<div class="app-title">Rainfall Monitor - Multi City</div>', unsafe_allow_html=True)
    api_key, cities, notification_config = render_controls()

    if not api_key:
        st.info("Enter your OpenWeatherMap API key to load live rainfall data. Default location is China / Beijing / Beijing.")
        return

    records: list[WeatherRecord] = []
    errors: list[str] = []
    for city in cities:
        record, error = fetch_weather(city, api_key)
        if record:
            records.append(record)
        if error:
            errors.append(error)

    if errors and not records:
        for error in errors:
            st.error(error)
        return

    append_history(records)
    handle_red_alerts(records, notification_config)

    st.markdown('<div class="map-title">Weather Map</div>', unsafe_allow_html=True)
    render_map(records)

    card_html = '<div class="city-grid">' + "".join(render_city_card(record) for record in records) + "</div>"
    st.markdown(card_html, unsafe_allow_html=True)

    st.divider()
    history_tab, forecast_tab, log_tab = st.tabs(["History", "Prediction", "Alert Log"])

    with history_tab:
        history = pd.DataFrame(st.session_state.history)
        if history.empty:
            st.caption("History appears after data is loaded.")
        else:
            history["time"] = pd.to_datetime(history["time"])
            focus_city = st.selectbox("Focus city", sorted(history["city"].unique()))
            focus = history[history["city"] == focus_city].copy()
            st.line_chart(focus.set_index("time")[["rainfall"]])
            st.dataframe(
                focus.tail(10)[["time", "city", "rainfall", "level", "temperature", "humidity"]],
                use_container_width=True,
                hide_index=True,
            )

    with forecast_tab:
        history = pd.DataFrame(st.session_state.history)
        if history.empty:
            st.caption("Prediction appears after a few refresh cycles.")
        else:
            history["time"] = pd.to_datetime(history["time"])
            forecast_city = st.selectbox("Prediction city", sorted(history["city"].unique()), key="forecast_city")
            forecast = build_forecast(history, forecast_city)
            if forecast.empty:
                st.caption("Need at least three readings to create a simple trend prediction.")
            else:
                st.line_chart(forecast.set_index("time")[["rainfall"]])
                estimate = forecast[forecast["kind"] == "Forecast"]["rainfall"].iloc[-1]
                level, _ = check_alert(estimate)
                st.metric("Next trend estimate", f"{estimate:.2f} mm/h", level)

    with log_tab:
        st.code(load_recent_log(), language="text")
        if errors:
            st.subheader("Fetch errors")
            for error in errors:
                st.error(error)


if __name__ == "__main__":
    render_dashboard()
