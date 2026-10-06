from typing import Any
import streamlit as st
from config import MOVE_DESCRIPTIONS
from src.visualization import create_telemetry_figure


def render_telemetry_view(
    node: dict[str, Any], positions: list[dict[str, Any]], current_ply: int
) -> None:
    move_num = node.get("move_number", 1)
    color_label = node.get("color", "white").upper()
    san_label = node.get("san", "-")

    st.markdown(f"### Move {move_num} ({color_label}): `{san_label}`")

    m1, m2, m3 = st.columns(3)

    cp_loss: int = int(node.get("cp_loss", 0))
    loss_display = "Forced Mate" if cp_loss >= 1000 else f"{cp_loss} CP Loss"
    label_quality = node.get("label", "Best Move")
    m1.metric("Quality", label_quality, loss_display, delta_color="inverse")

    risk_pct: float = float(node.get("blunder_risk_pct", 0.0))
    m2.metric("ML Risk", f"{risk_pct:.1f}%")

    cp_white: int = int(node.get("cp_eval_white", 0))
    eval_pawns = cp_white / 100.0
    if abs(eval_pawns) >= 9.0:
        eval_display = "White Mate" if eval_pawns > 0 else "Black Mate"
    else:
        eval_display = f"{eval_pawns:+.2f} pawns"
    m3.metric("Eval", eval_display)

    description = MOVE_DESCRIPTIONS.get(label_quality, "Analisis langkah catur.")
    st.caption(f"**{label_quality}**: {description}")

    best_move_san = node.get("best_move", "-")
    if label_quality in ["Mistake", "Blunder"] and best_move_san != "-":
        st.info(f"Recommended Alternative: **{best_move_san}**.")

    telemetry_fig = create_telemetry_figure(positions, current_ply)
    
    telemetry_fig.update_layout(
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#000000")
    )

    st.plotly_chart(telemetry_fig, use_container_width=True)

    st.markdown(
        "<p style='font-size:0.80rem; font-weight:700; color:#000000; letter-spacing:0.5px; margin-top:8px; margin-bottom:4px;'>"
        "TACTICAL COMPLEXITY"
        "</p>",
        unsafe_allow_html=True,
    )
    t1, t2, t3 = st.columns(3)
    t1.metric("Center Tension", f"{node.get('tactical_tension', 0)}")
    t2.metric("Hanging Pieces", f"{node.get('hanging_pieces', 0)}")

    material_balance = node.get("material_balance", 0)
    t3.metric("Material Balance", f"{material_balance:+d}")
