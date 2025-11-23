import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium

# =========================
# CẤU HÌNH APP
# =========================
st.set_page_config(
    page_title="ITS - Công nghệ bản đồ & tìm đường",
    layout="wide"
)

st.title("🧭 ITS – Demo Công nghệ Bản đồ & Tìm đường (Dijkstra)")
st.markdown(
    """
Ứng dụng minh họa mô hình **bản đồ nút–cạnh** và thuật toán **Dijkstra**  
để tìm đường đi ngắn nhất giữa hai điểm trong mạng lưới giao thông nhỏ.
"""
)

# =========================
# KHỞI TẠO SESSION STATE
# =========================
if "path" not in st.session_state:
    st.session_state.path = None
if "total_distance" not in st.session_state:
    st.session_state.total_distance = None
if "start_node" not in st.session_state:
    st.session_state.start_node = None
if "end_node" not in st.session_state:
    st.session_state.end_node = None

# =========================
# 1. TẠO ĐỒ THỊ NÚT – CẠNH
# =========================
nodes = {
    "A": {"name": "Nút A", "lat": 10.8015, "lon": 106.7140},
    "B": {"name": "Nút B", "lat": 10.8050, "lon": 106.7165},
    "C": {"name": "Nút C", "lat": 10.8075, "lon": 106.7100},
    "D": {"name": "Nút D", "lat": 10.8105, "lon": 106.7200},
    "E": {"name": "Nút E", "lat": 10.8030, "lon": 106.7215},
    "F": {"name": "Nút F", "lat": 10.7995, "lon": 106.7180},
}

edges = [
    ("A", "B", 0.8),
    ("A", "C", 1.1),
    ("B", "D", 1.0),
    ("B", "E", 0.9),
    ("C", "D", 1.3),
    ("C", "F", 0.7),
    ("D", "E", 0.6),
    ("E", "F", 0.9),
]

G = nx.Graph()
for nid, info in nodes.items():
    G.add_node(nid, **info)
for u, v, dist in edges:
    G.add_edge(u, v, distance=dist)

# =========================
# 2. GIAO DIỆN BÊN TRÁI
# =========================
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("⚙️ Cấu hình tìm đường")

    all_nodes = list(nodes.keys())
    start_node = st.selectbox("Chọn điểm đi (Origin)", all_nodes, index=0)
    end_node = st.selectbox("Chọn điểm đến (Destination)", all_nodes, index=3)

    algo = st.radio(
        "Thuật toán sử dụng",
        ["Dijkstra (Shortest Path)"],
        index=0,
    )

    run = st.button("🚀 Tìm đường")

# =========================
# 3. XỬ LÝ KHI BẤM NÚT
# =========================
if run:
    if start_node == end_node:
        st.warning("Điểm đi và điểm đến đang trùng nhau, hãy chọn khác nhé!")
        st.session_state.path = None
        st.session_state.total_distance = None
    else:
        try:
            path = nx.shortest_path(G, start_node, end_node, weight="distance")

            total_distance = 0.0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                total_distance += G[u][v]["distance"]

            # LƯU VÀO SESSION_STATE
            st.session_state.path = path
            st.session_state.total_distance = total_distance
            st.session_state.start_node = start_node
            st.session_state.end_node = end_node

        except nx.NetworkXNoPath:
            st.error("Không tồn tại đường đi giữa hai nút này trong đồ thị!")
            st.session_state.path = None
            st.session_state.total_distance = None

# =========================
# 4. HIỂN THỊ KẾT QUẢ TEXT
# =========================
if st.session_state.path is not None:
    st.success(
        f"Đường đi ngắn nhất từ **{st.session_state.start_node}** "
        f"đến **{st.session_state.end_node}**: "
        f"{' → '.join(st.session_state.path)}  \n"
        f"👉 Tổng chiều dài ≈ **{st.session_state.total_distance:.2f} km**"
    )

# =========================
# 5. VẼ BẢN ĐỒ
# =========================
center_lat = sum(n["lat"] for n in nodes.values()) / len(nodes)
center_lon = sum(n["lon"] for n in nodes.values()) / len(nodes)

m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

# Vẽ tất cả cạnh
for u, v, data in G.edges(data=True):
    folium.PolyLine(
        locations=[
            [nodes[u]["lat"], nodes[u]["lon"]],
            [nodes[v]["lat"], nodes[v]["lon"]],
        ],
        tooltip=f"{u} – {v} ({data['distance']} km)",
        weight=3,
        opacity=0.6,
    ).add_to(m)

# Vẽ đường đi tối ưu (nếu có)
if st.session_state.path is not None:
    path_latlngs = [
        [nodes[n]["lat"], nodes[n]["lon"]] for n in st.session_state.path
    ]
    folium.PolyLine(
        locations=path_latlngs,
        color="red",
        weight=6,
        opacity=0.9,
        tooltip="Đường đi ngắn nhất",
    ).add_to(m)

# Vẽ các nút
for nid, info in nodes.items():
    popup = f"{nid} - {info['name']}"
    if st.session_state.path is not None and nid in st.session_state.path:
        icon_color = "red" if nid in (st.session_state.start_node, st.session_state.end_node) else "green"
    else:
        icon_color = "blue"

    folium.Marker(
        location=[info["lat"], info["lon"]],
        popup=popup,
        tooltip=popup,
        icon=folium.Icon(color=icon_color),
    ).add_to(m)

with col_right:
    st.subheader("🗺️ Bản đồ mạng lưới & đường đi")
    st_folium(m, width=900, height=550)
