import time

import streamlit as st


st.set_page_config(
    page_title="영어 길 안내 지도",
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
    .history-box { background: #f3f6ed; border: 2px dashed #9cb49d; border-radius: 10px; padding: .7rem .85rem; white-space: pre-line; font-family: 'Atkinson Hyperlegible', sans-serif; font-size: 1rem; line-height: 1.55; }
    .result-box { border-radius: 10px; padding: .75rem .9rem; font-weight: 700; margin-top: .75rem; }
    .result-success { background: #d7eee1; color: #17634e; }
    .result-failure { background: #fff0d4; color: #865625; }
    .stButton > button { border: 2px solid var(--ink); border-radius: 10px; min-height: 3.8rem; font-size: 1.12rem; font-weight: 700; color: var(--ink); background: #fffdf7; box-shadow: 0 4px 0 var(--ink); transition: transform .12s, box-shadow .12s; }
    .stButton > button:hover { border-color: var(--ink); color: var(--ink); background: #fff1c8; transform: translateY(2px); box-shadow: 0 2px 0 var(--ink); }
    .stButton > button:active { transform: translateY(4px); box-shadow: none; }
    .reset-button button { background: var(--coral) !important; color: white !important; }
    .tree-button button { min-height: 2.75rem; font-size: 1rem; background: #edf5e6; box-shadow: 0 3px 0 #77967b; }
    .clear-button button { min-height: 2.75rem; font-size: 1rem; background: #edf0ea; box-shadow: 0 3px 0 #7b8980; }
    .undo-button button { min-height: 2.75rem; font-size: 1rem; background: #fff1c8; box-shadow: 0 3px 0 #a98134; }
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
# Every character position is the center of a four-way intersection.
# Even levels are beside buildings; odd levels are four-way intersections.
ROAD_Y = (120, 217, 313, 409, 505, 601)
DIRECTIONS = ("E", "S", "W", "N")
ARROWS = {"E": "→", "S": "↓", "W": "←", "N": "↑"}
PINS = {
    "A": (238, 112), "B": (292, 112), "C": (726, 112), "D": (780, 112),
    "E": (238, 304), "F": (292, 304), "G": (726, 304), "H": (780, 304),
    "I": (238, 496), "J": (780, 496),
}
TARGET_POSITIONS = {
    "A": (0, 1), "B": (0, 1), "C": (2, 1), "D": (2, 1),
    "E": (0, 3), "F": (0, 3), "G": (2, 3), "H": (2, 3),
    "I": (0, 5), "J": (2, 5),
}
TARGET_LABELS = tuple(PINS)


def map_svg(position, direction, trees, side_mode):
    parts = [
        '<svg viewBox="0 0 1000 730" role="img" aria-label="Town map with twelve places and ten planting points">',
        '<rect width="1000" height="730" fill="#d9efdf"/>',
        '<text x="500" y="23" text-anchor="middle" font-family="Baloo 2" font-size="16" font-weight="700" fill="#167d73">북쪽 ↑</text>',
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
            parts.append(f'<text x="{x + 25}" y="{y - 18}" font-size="30">{tree}</text>')
    lane, level = position
    px, py = ROAD_X[lane], ROAD_Y[level]
    if side_mode:
        side_dx = {"E": 34, "W": -34}.get(direction, 0)
        side_dy = {"N": -34, "S": 34}.get(direction, 0)
        px += side_dx
        py += side_dy
    parts.append(f'<circle cx="{px}" cy="{py}" r="27" fill="#ef745e" stroke="#20302b" stroke-width="4"/>')
    parts.append(f'<text x="{px}" y="{py + 10}" text-anchor="middle" font-size="34" font-weight="700" fill="white">{ARROWS[direction]}</text>')
    parts.append('<text x="509" y="632" text-anchor="middle" font-family="Atkinson Hyperlegible" font-size="16" font-weight="700" fill="#53645d">START</text>')
    parts.append('</svg>')
    return "".join(parts)


def reset_explorer():
    st.session_state.position = (1, 5)
    st.session_state.direction = "N"
    st.session_state.pending_turn_steps = 0
    st.session_state.pending_turn_origin = "N"
    st.session_state.turn_origin_position = (1, 5)
    st.session_state.side_mode = False
    st.session_state.side_choice = None


def capture_snapshot():
    st.session_state.action_snapshots.append(
        {
            "position": st.session_state.position,
            "direction": st.session_state.direction,
            "move_history": list(st.session_state.move_history),
            "pending_turn_steps": st.session_state.pending_turn_steps,
            "pending_turn_origin": st.session_state.pending_turn_origin,
            "turn_origin_position": st.session_state.turn_origin_position,
            "side_mode": st.session_state.side_mode,
            "side_choice": st.session_state.side_choice,
        }
    )


def clear_side_choice():
    if st.session_state.side_choice is not None:
        if st.session_state.move_history and st.session_state.move_history[-1].startswith("It's on your"):
            st.session_state.move_history.pop()
        st.session_state.side_choice = None


def commit_pending_turn():
    turn_steps = st.session_state.pending_turn_steps % 4
    turn_action = {1: "Turn right", 2: "Turn around", 3: "Turn left"}.get(turn_steps)
    if turn_action:
        st.session_state.move_history.append(turn_action)
    st.session_state.pending_turn_steps = 0
    st.session_state.pending_turn_origin = st.session_state.direction
    st.session_state.turn_origin_position = st.session_state.position
    st.session_state.side_mode = False


def turn(step):
    capture_snapshot()
    clear_side_choice()
    if st.session_state.pending_turn_steps == 0:
        st.session_state.pending_turn_origin = st.session_state.direction
        st.session_state.turn_origin_position = st.session_state.position
    current = DIRECTIONS.index(st.session_state.direction)
    st.session_state.pending_turn_steps = (st.session_state.pending_turn_steps + step) % 4
    st.session_state.direction = DIRECTIONS[(current + step) % len(DIRECTIONS)]
    st.session_state.position = st.session_state.turn_origin_position
    st.session_state.side_mode = st.session_state.pending_turn_steps != 0
    st.session_state.result_message = ""
    st.session_state.result_success = False


def move_forward():
    now = time.monotonic()
    if now - st.session_state.last_move < 0.3:
        return
    lane, level = st.session_state.position
    changes = {"N": (0, -2), "S": (0, 2), "E": (1, 0), "W": (-1, 0)}
    lane_change, level_change = changes[st.session_state.direction]
    next_position = (lane + lane_change, level + level_change)
    if 0 <= next_position[0] < len(ROAD_X) and 0 <= next_position[1] < len(ROAD_Y):
        capture_snapshot()
        clear_side_choice()
        commit_pending_turn()
        st.session_state.move_history.append("Go straight")
        st.session_state.position = next_position
        st.session_state.result_message = ""
        st.session_state.result_success = False
    st.session_state.last_move = now


def undo_action():
    if not st.session_state.action_snapshots:
        return
    snapshot = st.session_state.action_snapshots.pop()
    st.session_state.position = snapshot["position"]
    st.session_state.direction = snapshot["direction"]
    st.session_state.move_history = snapshot["move_history"]
    st.session_state.pending_turn_steps = snapshot["pending_turn_steps"]
    st.session_state.pending_turn_origin = snapshot["pending_turn_origin"]
    st.session_state.turn_origin_position = snapshot["turn_origin_position"]
    st.session_state.side_mode = snapshot["side_mode"]
    st.session_state.side_choice = snapshot["side_choice"]
    st.session_state.result_message = ""
    st.session_state.result_success = False


def grouped_history(history):
    groups = []
    for action in history:
        if groups and groups[-1][0] == action:
            groups[-1] = (action, groups[-1][1] + 1)
        else:
            groups.append((action, 1))
    number_words = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    lines = []
    for index, (action, count) in enumerate(groups, 1):
        distance = f" {number_words.get(count, str(count))} blocks" if action == "Go straight" and count > 1 else ""
        lines.append(f"{index}. {action}{distance}.")
    return "\n".join(lines)


def target_side_from_position(target, position, direction):
    lane, level = position
    target_x, _ = PINS[target]
    road_x = ROAD_X[lane]
    if direction == "N":
        return "left" if target_x < road_x else "right"
    if direction == "S":
        return "right" if target_x < road_x else "left"
    target_y = PINS[target][1]
    road_y = ROAD_Y[level]
    if direction == "E":
        return "left" if target_y < road_y else "right"
    if direction == "W":
        return "left" if target_y > road_y else "right"
    return None


def choose_target_side(target, side):
    capture_snapshot()
    side_action = f"It's on your {side}."
    if st.session_state.move_history and st.session_state.move_history[-1].startswith("It's on your"):
        st.session_state.move_history[-1] = side_action
    else:
        st.session_state.move_history.append(side_action)
    st.session_state.side_choice = side
    st.session_state.result_message = ""
    st.session_state.result_success = False
    if target == "선택하세요":
        st.session_state.result_message = "먼저 목표 지점을 선택해 주세요."
        st.session_state.result_success = False
    elif not st.session_state.side_mode:
        st.session_state.result_message = "건물 옆까지 이동한 뒤 방향을 선택해 주세요."
        st.session_state.result_success = False
    elif st.session_state.position != TARGET_POSITIONS[target]:
        st.session_state.result_message = f"아직 {target} 지점 옆이 아니에요. 이동 기록과 현재 위치를 살펴보세요."
        st.session_state.result_success = False
    elif target_side_from_position(target, st.session_state.position, st.session_state.direction) != side:
        st.session_state.result_message = "목적지가 어느 쪽에 있는지 다시 확인해 보세요."
        st.session_state.result_success = False
    else:
        st.session_state.result_message = f"{target} 지점에 도착했어요!"
        st.session_state.result_success = True
        st.session_state.trees.add(target)


for key, default in (
    ("position", (1, 5)), ("direction", "N"), ("trees", set()), ("last_move", 0.0),
    ("move_history", []), ("action_snapshots", []), ("result_message", ""), ("result_success", False),
    ("show_side_choice", False), ("pending_turn_steps", 0), ("pending_turn_origin", "N"),
    ("turn_origin_position", (1, 5)), ("side_mode", False), ("side_choice", None),
):
    if key not in st.session_state:
        st.session_state[key] = default

if not all(isinstance(snapshot, dict) for snapshot in st.session_state.action_snapshots):
    st.session_state.action_snapshots = []

position = st.session_state.position
if (
    not isinstance(position, (tuple, list))
    or len(position) != 2
    or not all(isinstance(value, int) for value in position)
    or not 0 <= position[0] < len(ROAD_X)
    or not 0 <= position[1] < len(ROAD_Y)
):
    reset_explorer()

st.markdown('<div class="eyebrow">초등학교 5학년 영어 · 길 안내 활동</div>', unsafe_allow_html=True)
st.title("길 안내 지도")
st.markdown('<div class="subtitle">친구의 안내를 듣고 이동해 목적지를 찾아보세요.</div>', unsafe_allow_html=True)

map_column, control_column = st.columns([1.8, 1], gap="large")
with map_column:
    st.markdown('<div class="map-frame">' + map_svg(st.session_state.position, st.session_state.direction, st.session_state.trees, st.session_state.side_mode) + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="legend"><span><i class="dot road-dot"></i> 도로</span><span><i class="dot building-dot"></i> 장소</span><span><i class="dot pin-dot"></i> 나무 심기 지점</span></div>', unsafe_allow_html=True)

with control_column:
    st.markdown('<div class="panel"><div class="panel-title">활동 모드</div>', unsafe_allow_html=True)
    activity_mode = st.radio(
        "활동 모드",
        ("경로 준비", "발표 듣고 찾기"),
        key="activity_mode",
        horizontal=True,
        label_visibility="collapsed",
    )
    if activity_mode == "경로 준비":
        selected_target = st.selectbox("목표 지점", ("선택하세요",) + TARGET_LABELS, key="prep_target")
        st.markdown('<div class="hint">이동하기 전에 나무를 심을 목표 지점을 선택하세요.</div>', unsafe_allow_html=True)
    else:
        selected_target = st.session_state.get("answer_target", "선택하세요")
        st.markdown('<div class="hint">목표 지점은 숨겨져 있습니다. 친구의 발표를 들으며 이동하세요.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-title">캐릭터 이동</div>', unsafe_allow_html=True)
    facing = {"N": "북쪽", "E": "동쪽", "S": "남쪽", "W": "서쪽"}[st.session_state.direction]
    st.markdown(f'<div class="status">현재 바라보는 방향 <span class="direction">{ARROWS[st.session_state.direction]}</span> {facing}<br><small>한 번 누르면 한 블록 이동합니다.</small></div>', unsafe_allow_html=True)
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
    st.markdown('<div class="hint">회전하면 해당 방향의 가로 도로 쪽으로 이동해 양옆 장소를 살펴볼 수 있습니다. 다시 회전하면 처음 사거리 기준으로 위치를 바꿉니다.</div>', unsafe_allow_html=True)
    undo_column, reset_column = st.columns(2)
    with undo_column:
        st.markdown('<div class="undo-button">', unsafe_allow_html=True)
        if st.button("↶ 한 단계 되돌리기", use_container_width=True, disabled=not st.session_state.move_history):
            undo_action()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with reset_column:
        st.markdown('<div class="reset-button">', unsafe_allow_html=True)
        if st.button("↺ 다시 하기", use_container_width=True):
            reset_explorer()
            st.session_state.move_history.clear()
            st.session_state.action_snapshots.clear()
            st.session_state.result_message = ""
            st.session_state.result_success = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-title">목적지 방향 선택</div>', unsafe_allow_html=True)
    if activity_mode == "발표 듣고 찾기":
        selected_target = st.selectbox("발표가 끝난 뒤 정답 지점", ("선택하세요",) + TARGET_LABELS, key="answer_target")
    st.markdown('<div class="hint">이동을 마친 뒤 캐릭터가 바라보는 방향을 기준으로 목적지의 위치를 선택하세요.</div>', unsafe_allow_html=True)
    if st.button("목적지 방향 선택", use_container_width=True):
        st.session_state.show_side_choice = True
        st.rerun()
    if st.session_state.show_side_choice:
        side_left, side_right = st.columns(2)
        with side_left:
            if st.button("It's on your left.", use_container_width=True):
                choose_target_side(selected_target, "left")
                st.rerun()
        with side_right:
            if st.button("It's on your right.", use_container_width=True):
                choose_target_side(selected_target, "right")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-title">이동 기록</div>', unsafe_allow_html=True)
    if st.session_state.move_history:
        st.markdown(f'<div class="history-box">{grouped_history(st.session_state.move_history)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="hint">연속으로 누른 Go straight는 한 문장으로 묶어 표시합니다.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="hint">아직 이동 기록이 없습니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.result_message:
        result_class = "result-success" if st.session_state.result_success else "result-failure"
        st.markdown(f'<div class="result-box {result_class}">{st.session_state.result_message}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-title">나무 표시</div><div class="hint">목표 지점에 정확히 도착하면 큰 나무가 자동으로 표시됩니다.</div>', unsafe_allow_html=True)
    st.markdown('<div class="clear-button">', unsafe_allow_html=True)
    if st.button("나무 모두 지우기", use_container_width=True):
        st.session_state.trees.clear()
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
