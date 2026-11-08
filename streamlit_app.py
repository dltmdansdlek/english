import time

import streamlit as st


st.set_page_config(
    page_title="Wayfinder | English Directions",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Baloo+2:wght@600;700;800&display=swap');
    :root { --ink: #20302b; --paper: #fffaf0; --grass: #b8dca8; --grass-dark: #75ad70; --road: #e7e8df; --teal: #167d73; --coral: #ef745e; --yellow: #f4cb62; }
    .stApp { background: #f7f2e7; color: var(--ink); font-family: 'Atkinson Hyperlegible', sans-serif; }
    .block-container { max-width: 1480px; padding: 1.25rem 2.4rem 2rem; }
    h1, h2, h3, button { font-family: 'Baloo 2', sans-serif !important; }
    h1 { color: var(--ink); font-size: clamp(2.6rem, 4vw, 4rem) !important; line-height: .9 !important; letter-spacing: 0 !important; }
    .eyebrow { color: var(--teal); font-weight: 700; font-size: 1rem; text-transform: uppercase; letter-spacing: .12em; }
    .subtitle { color: #53645d; font-size: 1.13rem; margin-top: -.5rem; margin-bottom: 1rem; }
    .map-frame { background: var(--paper); border: 3px solid var(--ink); border-radius: 18px; padding: 9px; box-shadow: 7px 7px 0 #c6d9cd; }
    .map-frame svg { display: block; width: 100%; height: auto; border-radius: 10px; }
    .panel { background: #fffdf7; border: 2px solid #d6e0d7; border-radius: 14px; padding: 1.1rem 1.25rem; margin-bottom: 1rem; }
    .panel-title { font-family: 'Baloo 2'; font-size: 1.45rem; font-weight: 700; margin-bottom: .35rem; }
    .status { background: #d7eee1; border-radius: 12px; padding: .8rem 1rem; font-weight: 700; font-size: 1.12rem; margin: .7rem 0 1rem; }
    .direction { color: var(--coral); font-size: 1.65rem; }
    .hint { color: #53645d; font-size: .95rem; line-height: 1.35; }
    .stButton > button { border: 2px solid var(--ink); border-radius: 10px; min-height: 3.8rem; font-size: 1.12rem; font-weight: 700; color: var(--ink); background: #fffdf7; box-shadow: 0 4px 0 var(--ink); transition: transform .12s, box-shadow .12s; }
    .stButton > button:hover { border-color: var(--ink); color: var(--ink); background: #fff1c8; transform: translateY(2px); box-shadow: 0 2px 0 var(--ink); }
    .stButton > button:active { transform: translateY(4px); box-shadow: none; }
    .reset-button button { background: var(--coral) !important; color: white !important; }
    .tree-button button { min-height: 2.75rem; font-size: 1rem; background: #edf5e6; box-shadow: 0 3px 0 #77967b; }
    .clear-button button { min-height: 2.75rem; font-size: 1rem; background: #edf0ea; box-shadow: 0 3px 0 #7b8980; }
    .legend { display: flex; flex-wrap: wrap; gap: .75rem; margin-top: .75rem; color: #53645d; font-size: .95rem; }
    .legend span { display: inline-flex; align-items: center; gap: .35rem; }
    .dot { width: .8rem; height: .8rem; display: inline-block; border-radius: 50%; border: 2px solid var(--ink); }
    .road-dot { background: var(--road); } .building-dot { background: var(--grass); } .pin-dot { background: var(--yellow); }
    @media (max-width: 800px) { .block-container { padding: 1rem .7rem; } h1 { font-size: 2.8rem !important; } .map-frame { padding: 5px; } }
    </style>
    """,
    unsafe_allow_html=True,
)


BUILDINGS = [
    ("Park", "🌳", 48, 50), ("School", "🏫", 292, 50), ("Bookstore", "📚", 536, 50), ("Museum", "🏛", 780, 50),
    ("Library", "📖", 48, 242), ("Fruit Store", "🍎", 292, 242), ("Bank", "🏦", 536, 242), ("Zoo", "🦁", 780, 242),
    ("Ice Cream Shop", "🍦", 48, 434), ("Bike Shop", "🚲", 292, 434), ("Shoe Store", "👟", 536, 434), ("Flower Shop", "🌷", 780, 434),
]
ROAD_X = (265, 509, 753)
ROAD_Y = (120, 312, 504, 601)
DIRECTIONS = ("E", "S", "W", "N")
ARROWS = {"E": "→", "S": "↓", "W": "←", "N": "↑"}
PINS = {
    "A": (238, 112), "B": (292, 112), "C": (726, 112), "D": (780, 112),
    "E": (238, 304), "F": (292, 304), "G": (726, 304), "H": (780, 304),
    "I": (238, 496), "J": (780, 496),
}


def map_svg(position, direction, trees):
    parts = [
        '<svg viewBox="0 0 1000 730" role="img" aria-label="Town map with twelve places and ten planting points">',
        '<rect width="1000" height="730" fill="#d9efdf"/>',
        '<text x="500" y="23" text-anchor="middle" font-family="Baloo 2" font-size="16" font-weight="700" fill="#167d73">NORTH ↑</text>',
    ]
    for x in (238, 482, 726):
        parts.append(f'<rect x="{x}" y="34" width="54" height="594" fill="#e7e8df"/>')
    for y in (190, 382, 574):
        parts.append(f'<rect x="30" y="{y}" width="940" height="54" fill="#e7e8df"/>')
    for x in ROAD_X:
        parts.append(f'<path d="M {x} 34 V 628" stroke="#c8cec5" stroke-width="2" stroke-dasharray="8 9"/>')
    for y in (190, 382, 574):
        parts.append(f'<path d="M 30 {y + 27} H 970" stroke="#c8cec5" stroke-width="2" stroke-dasharray="8 9"/>')
    for name, icon, x, y in BUILDINGS:
        parts.append(f'<rect x="{x}" y="{y}" width="190" height="140" rx="18" fill="#b8dca8" stroke="#75ad70" stroke-width="4"/>')
        parts.append(f'<text x="{x + 95}" y="{y + 57}" text-anchor="middle" font-size="38">{icon}</text>')
        parts.append(f'<text x="{x + 95}" y="{y + 100}" text-anchor="middle" font-family="Atkinson Hyperlegible" font-size="18" font-weight="700" fill="#20302b">{name}</text>')
    for label, (x, y) in PINS.items():
        tree = "🌳" if label in trees else ""
        parts.append(f'<circle cx="{x}" cy="{y}" r="17" fill="#f4cb62" stroke="#20302b" stroke-width="3"/>')
        parts.append(f'<text x="{x}" y="{y + 6}" text-anchor="middle" font-family="Baloo 2" font-size="18" font-weight="800" fill="#20302b">{label}</text>')
        if tree:
            parts.append(f'<text x="{x + 19}" y="{y - 14}" font-size="22">{tree}</text>')
    lane, level = position
    px, py = ROAD_X[lane], ROAD_Y[level]
    parts.append(f'<circle cx="{px}" cy="{py}" r="27" fill="#ef745e" stroke="#20302b" stroke-width="4"/>')
    parts.append(f'<text x="{px}" y="{py + 10}" text-anchor="middle" font-size="34" font-weight="700" fill="white">{ARROWS[direction]}</text>')
    parts.append('<text x="509" y="632" text-anchor="middle" font-family="Atkinson Hyperlegible" font-size="16" font-weight="700" fill="#53645d">START</text>')
    parts.append('</svg>')
    return "".join(parts)


def reset_explorer():
    st.session_state.position = (1, 3)
    st.session_state.direction = "N"


def turn(step):
    current = DIRECTIONS.index(st.session_state.direction)
    st.session_state.direction = DIRECTIONS[(current + step) % len(DIRECTIONS)]


def move_forward():
    now = time.monotonic()
    if now - st.session_state.last_move < 0.3:
        return
    lane, level = st.session_state.position
    changes = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    lane_change, level_change = changes[st.session_state.direction]
    next_position = (lane + lane_change, level + level_change)
    if 0 <= next_position[0] < len(ROAD_X) and 0 <= next_position[1] < len(ROAD_Y):
        st.session_state.position = next_position
    st.session_state.last_move = now


for key, default in (("position", (1, 3)), ("direction", "N"), ("trees", set()), ("last_move", 0.0)):
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown('<div class="eyebrow">Grade 5 English · Directions</div>', unsafe_allow_html=True)
st.title("Wayfinder")
st.markdown('<div class="subtitle">Listen carefully. Follow the directions. Find the place.</div>', unsafe_allow_html=True)

map_column, control_column = st.columns([1.8, 1], gap="large")
with map_column:
    st.markdown('<div class="map-frame">' + map_svg(st.session_state.position, st.session_state.direction, st.session_state.trees) + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="legend"><span><i class="dot road-dot"></i> road</span><span><i class="dot building-dot"></i> place</span><span><i class="dot pin-dot"></i> planting point</span></div>', unsafe_allow_html=True)

with control_column:
    st.markdown('<div class="panel"><div class="panel-title">Your explorer</div>', unsafe_allow_html=True)
    facing = {"N": "North", "E": "East", "S": "South", "W": "West"}[st.session_state.direction]
    st.markdown(f'<div class="status">Facing <span class="direction">{ARROWS[st.session_state.direction]}</span> {facing}<br><small>One press = one block</small></div>', unsafe_allow_html=True)
    left, forward, right = st.columns(3)
    with left:
        if st.button("↶\nTurn left", use_container_width=True):
            turn(-1)
            st.rerun()
    with forward:
        if st.button("↑\nGo straight", use_container_width=True):
            move_forward()
            st.rerun()
    with right:
        if st.button("↷\nTurn right", use_container_width=True):
            turn(1)
            st.rerun()
    st.markdown('<div class="hint">Turn left and right change only the explorer’s direction. They do not move the explorer.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-title">After the answer</div><div class="hint">Choose a planting point after the group finishes speaking.</div>', unsafe_allow_html=True)
    point_columns = st.columns(5)
    for index, label in enumerate(PINS):
        with point_columns[index % 5]:
            st.markdown('<div class="tree-button">', unsafe_allow_html=True)
            if st.button(f"🌳 {label}", key=f"tree_{label}", use_container_width=True):
                st.session_state.trees.add(label)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    clear_column, reset_column = st.columns(2)
    with clear_column:
        st.markdown('<div class="clear-button">', unsafe_allow_html=True)
        if st.button("Clear trees", use_container_width=True):
            st.session_state.trees.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with reset_column:
        st.markdown('<div class="reset-button">', unsafe_allow_html=True)
        if st.button("↺ Start again", use_container_width=True):
            reset_explorer()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
