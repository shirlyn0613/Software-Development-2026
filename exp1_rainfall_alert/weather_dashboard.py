"""Streamlit dashboard for the rainfall monitoring system."""

from __future__ import annotations

import html
from datetime import datetime

import folium
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html as st_html

from city_tree import CITY_TREE
from weather_alert import check_alert, log_alert
from weather_monitor import get_weather_data


STATUS_STYLES = {
    "Green": {"fill": "#bbf7d0", "text": "#14532d", "label": "Green: Normal"},
    "Yellow": {"fill": "#fef3c7", "text": "#78350f", "label": "Yellow: Moderate"},
    "Red": {"fill": "#fecaca", "text": "#7f1d1d", "label": "Red: ALERT"},
    "Unknown": {"fill": "#e5e7eb", "text": "#374151", "label": "Unknown"},
}


def init_state() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("last_alert_signature", {})


def refresh_component() -> None:
    try:
        from streamlit_autorefresh import st_autorefresh

        st_autorefresh(interval=5 * 60 * 1000, key="rainfall_autorefresh")
    except Exception:
        pass


def get_city_coordinates(record: dict) -> tuple[float | None, float | None]:
    raw = record.get("raw") or {}
    coord = raw.get("coord") or {}
    return coord.get("lat"), coord.get("lon")


def fetch_city_record(city: str, api_key: str) -> dict:
    data = get_weather_data(city, api_key)
    if "error" in data:
        return {
            "city": city,
            "rainfall": 0.0,
            "temperature": None,
            "humidity": None,
            "condition": data["error"],
            "alert": {"level": "Unknown", "color": "gray", "message": data["error"]},
            "timestamp": datetime.now(),
            "raw": {},
        }

    rainfall = data["rainfall_mm_per_hour"]
    alert = check_alert(rainfall)
    if alert["level"] in {"Yellow", "Red"}:
        log_alert(data["city"], rainfall, alert["level"])

    raw = data.get("raw") or {}
    weather_items = raw.get("weather") or [{}]
    main = raw.get("main") or {}

    return {
        "city": data["city"],
        "rainfall": rainfall,
        "temperature": data["temperature_celsius"],
        "humidity": main.get("humidity"),
        "condition": str(weather_items[0].get("description", "Unknown")).title(),
        "alert": alert,
        "timestamp": datetime.now(),
        "raw": raw,
    }


def append_history(records: list[dict]) -> None:
    for record in records:
        st.session_state.history.append(
            {
                "time": record["timestamp"],
                "city": record["city"],
                "rainfall": record["rainfall"],
                "level": record["alert"]["level"],
                "temperature": record["temperature"],
                "humidity": record["humidity"],
            }
        )
    st.session_state.history = st.session_state.history[-200:]


def render_map(records: list[dict]) -> None:
    geo_records = []
    for record in records:
        lat, lon = get_city_coordinates(record)
        if lat is not None and lon is not None:
            geo_records.append((record, lat, lon))

    if not geo_records:
        st.caption("No map coordinates returned yet.")
        return

    center_lat = sum(item[1] for item in geo_records) / len(geo_records)
    center_lon = sum(item[2] for item in geo_records) / len(geo_records)
    rainfall_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=4 if len(geo_records) > 1 else 7,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    for record, lat, lon in geo_records:
        level = record["alert"]["level"]
        icon_color = "red" if level == "Red" else "orange" if level == "Yellow" else "green"
        popup = folium.Popup(
            (
                f"<b>{html.escape(record['city'])}</b><br>"
                f"Rainfall: {record['rainfall']:.2f} mm/h<br>"
                f"Status: {level}<br>"
                f"Condition: {html.escape(record['condition'])}"
            ),
            max_width=240,
        )
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color=icon_color,
            fill=True,
            fill_color=icon_color,
            fill_opacity=0.9,
            popup=popup,
            tooltip=record["city"],
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


def render_city_card(record: dict) -> str:
    level = record["alert"]["level"]
    style = STATUS_STYLES.get(level, STATUS_STYLES["Unknown"])
    temperature = f"{record['temperature']:.2f} C" if record["temperature"] is not None else "--"
    humidity = f"{record['humidity']}%" if record["humidity"] is not None else "--"
    return (
        f'<div class="city-card">'
        f'<div class="city-title">{html.escape(record["city"])}</div>'
        f'<div class="card-label">Rainfall</div>'
        f'<div class="rainfall-value">{record["rainfall"]:.2f} mm/h</div>'
        f'<div class="status-bar" style="background:{style["fill"]};color:{style["text"]};">'
        f'{style["label"]}'
        f"</div>"
        f'<div class="category">Category: {level}</div>'
        f'<div class="city-detail"><b>Temp:</b> {temperature}</div>'
        f'<div class="city-detail"><b>Humidity:</b> {humidity}</div>'
        f'<div class="city-detail"><b>Condition:</b> {html.escape(record["condition"])}</div>'
        f"</div>"
    )


def render_controls() -> tuple[str, list[str]]:
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

    if refresh:
        st.rerun()

    return api_key, [primary_city, *comparison]


def main() -> None:
    st.set_page_config(page_title="Rainfall Monitor", layout="wide")
    st.markdown(
        """
        <style>
        .block-container {padding: 1.45rem 1.8rem 2.1rem;}
        header[data-testid="stHeader"] {background: transparent;}
        .app-title {font-size: 1.8rem; font-weight: 750; color: #111827; margin: 0 0 0.9rem;}
        .map-title {font-size: 0.98rem; font-weight: 700; color: #374151; margin: 1rem 0 0.45rem;}
        .city-grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin-top: 1rem;}
        .city-card {background: #ffffff; border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px 13px 13px; min-height: 188px; box-shadow: 0 1px 2px rgba(15,23,42,0.04);}
        .city-title {font-size: 1.03rem; font-weight: 740; color: #111827; margin-bottom: 12px;}
        .card-label {font-size: 0.75rem; color: #6b7280; margin-bottom: 2px;}
        .rainfall-value {font-size: 1.35rem; color: #111827; line-height: 1.2; margin-bottom: 10px;}
        .status-bar {text-align: center; border-radius: 6px; padding: 7px 8px; font-size: 0.82rem; font-weight: 750; margin-bottom: 7px;}
        .category {font-size: 0.68rem; color: #9ca3af; margin-bottom: 11px;}
        .city-detail {font-size: 0.72rem; color: #374151; margin-top: 7px;}
        div[data-testid="stButton"] button {height: 2.45rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_state()
    refresh_component()

    st.markdown('<div class="app-title">Rainfall Monitor - Multi City</div>', unsafe_allow_html=True)
    api_key, cities = render_controls()

    if not api_key:
        st.info("Enter your OpenWeatherMap API key to load live rainfall data. Default location is China / Beijing / Beijing.")
        return

    records = [fetch_city_record(city, api_key) for city in cities]
    append_history(records)

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
            st.dataframe(focus.tail(10), use_container_width=True, hide_index=True)

    with forecast_tab:
        history = pd.DataFrame(st.session_state.history)
        if len(history) < 3:
            st.caption("Prediction appears after a few refresh cycles.")
        else:
            history["time"] = pd.to_datetime(history["time"])
            forecast_city = st.selectbox("Prediction city", sorted(history["city"].unique()), key="forecast_city")
            focus = history[history["city"] == forecast_city].tail(3)
            estimate = max(0.0, focus["rainfall"].mean())
            st.metric("Next trend estimate", f"{estimate:.2f} mm/h", check_alert(estimate)["level"])
            st.line_chart(focus.set_index("time")[["rainfall"]])

    with log_tab:
        if st.session_state.history:
            st.code(open("alert_log.txt", encoding="utf-8").read(), language="text")


if __name__ == "__main__":
    main()
