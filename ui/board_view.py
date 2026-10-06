from typing import Any
import streamlit as st
import streamlit.components.v1 as components

from src.visualization import generate_board_and_eval_html


def render_board_view(node: dict[str, Any], headers: dict[str, str], total_ply: int) -> None:
    white_player = headers.get("white", "White")
    white_elo = headers.get("white_elo", "?")
    black_player = headers.get("black", "Black")
    black_elo = headers.get("black_elo", "?")

    st.markdown(
        f"<p style='font-size: 0.95rem; color: #000; margin-bottom: 8px; font-weight: 600; font-family: sans-serif; text-align: center;'>"
        f"White: {white_player} <span style='font-weight: 400; color: #555;'>({white_elo})</span> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Black: {black_player} <span style='font-weight: 400; color: #555;'>({black_elo})</span>"
        f"</p>",
        unsafe_allow_html=True,
    )

    raw_html = generate_board_and_eval_html(
        fen=node["fen"],
        from_sq=node.get("from_sq"),
        to_sq=node.get("to_sq"),
        label=node.get("label", "Best Move"),
        cp_eval_white=node.get("cp_eval_white", 0),
        flipped=st.session_state.get("flipped", False),
        size=400,
    )
    components.html(raw_html, height=420)

    current_ply: int = st.session_state.get("current_ply", 0)
    max_ply: int = max(0, total_ply - 1)

    new_ply = st.slider(
        label="Timeline",
        min_value=0,
        max_value=max_ply,
        value=min(current_ply, max_ply),
        format="Ply %d",
        label_visibility="collapsed",
        key="board_timeline_slider",
    )

    if new_ply != current_ply:
        st.session_state.current_ply = new_ply
        st.rerun()

    col_start, col_prev, col_next, col_end = st.columns(4)

    with col_start:
        if st.button("<< Start", use_container_width=True, disabled=(current_ply == 0)):
            st.session_state.current_ply = 0
            st.rerun()

    with col_prev:
        if st.button("< Prev", use_container_width=True, disabled=(current_ply == 0)):
            st.session_state.current_ply = max(0, current_ply - 1)
            st.rerun()

    with col_next:
        if st.button("Next >", use_container_width=True, disabled=(current_ply >= max_ply)):
            st.session_state.current_ply = min(max_ply, current_ply + 1)
            st.rerun()

    with col_end:
        if st.button("End >>", use_container_width=True, disabled=(current_ply >= max_ply)):
            st.session_state.current_ply = max_ply
            st.rerun()
