from typing import Any, Optional, Union
import streamlit as st
import plotly.graph_objects as go


def calculate_player_stats(moves: list[dict[str, Any]]) -> dict[str, float]:
    if not moves:
        return {"acpl": 0.0, "accuracy": 100.0, "total_moves": 0.0}

    total_cp_loss = sum(m.get("cp_loss", 0) for m in moves)
    acpl = total_cp_loss / len(moves)
    accuracy = max(0.0, min(100.0, 100.0 - (acpl * 0.31)))

    return {
        "acpl": float(acpl),
        "accuracy": float(accuracy),
        "total_moves": float(len(moves)),
    }


def aggregate_phase_errors(moves: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"Opening": 0, "Middlegame": 0, "Endgame": 0}
    suboptimal_labels = {"Inaccuracy", "Mistake", "Blunder"}

    for m in moves:
        if m.get("label") in suboptimal_labels:
            move_num = m.get("move_number", 1)
            if move_num <= 10:
                counts["Opening"] += 1
            elif move_num <= 30:
                counts["Middlegame"] += 1
            else:
                counts["Endgame"] += 1

    return counts


def build_narrative(
    headers: dict[str, str],
    white_stats: dict[str, float],
    black_stats: dict[str, float],
    w_err: dict[str, int],
    b_err: dict[str, int],
) -> str:
    w_name = headers.get("white", "White")
    b_name = headers.get("black", "Black")
    diff_acpl = abs(white_stats["acpl"] - black_stats["acpl"])
    cleaner = w_name if white_stats["acpl"] <= black_stats["acpl"] else b_name

    total_w_err = sum(w_err.values())
    total_b_err = sum(b_err.values())
    endgame_delta = b_err["Endgame"] - w_err["Endgame"]

    if endgame_delta > 0:
        phase_insight = (
            f"Pemisahan keunggulan terjadi di **Endgame (31+)**. {b_name} mencatatkan "
            f"{b_err['Endgame']} deviasi suboptimal berbanding {w_err['Endgame']} dari {w_name}, "
            f"menjadikan penurunan akurasi babak akhir sebagai faktor penentu hasil."
        )
    elif endgame_delta < 0:
        phase_insight = (
            f"Fluktuasi posisi memuncak di **Endgame (31+)**, di mana {w_name} membuat "
            f"{w_err['Endgame']} kesalahan yang memberi ruang inisiatif bagi {b_name}."
        )
    else:
        phase_insight = (
            "Tingkat kesalahan terdistribusi seimbang antara kedua pemain "
            "tanpa adanya keruntuhan posisi tunggal di satu fase."
        )

    best_accuracy = max(white_stats["accuracy"], black_stats["accuracy"])

    return (
        f"**Post-Mortem Tactical Summary**\n\n"
        f"- **Efisiensi Eksekusi:** {cleaner} mempertahankan stabilitas posisi lebih solid dengan keunggulan selisih "
        f"**{diff_acpl:.1f} CP Loss** dan tingkat akurasi **{best_accuracy:.1f}%**.\n"
        f"- **Fase Kritis:** {phase_insight}\n"
        f"- **Total Deviasi Posisi:** {w_name} ({total_w_err} error) vs {b_name} ({total_b_err} error)."
    )


def render_match_summary(
    headers: Optional[dict[str, str]] = None,
    positions: Optional[list[dict[str, Any]]] = None,
    *args: Any,
    **kwargs: Any,
) -> None:
    resolved_headers: dict[str, str] = {}
    resolved_positions: list[dict[str, Any]] = []

    if "headers" in kwargs and isinstance(kwargs["headers"], dict):
        resolved_headers = kwargs["headers"]
    elif headers is not None and isinstance(headers, dict):
        resolved_headers = headers

    if "positions" in kwargs and isinstance(kwargs["positions"], list):
        resolved_positions = kwargs["positions"]
    elif positions is not None and isinstance(positions, list):
        resolved_positions = positions

    if not resolved_headers and isinstance(positions, dict):
        resolved_headers = positions
    if not resolved_positions and isinstance(headers, list):
        resolved_positions = headers

    for extra in args:
        if isinstance(extra, dict) and not resolved_headers:
            resolved_headers = extra
        elif isinstance(extra, list) and not resolved_positions:
            resolved_positions = extra

    headers = resolved_headers
    positions = resolved_positions

    st.markdown("### Post-Match Tactical Analytics")

    eco = headers.get("eco", "").strip()
    opening = headers.get("opening", "").strip()
    if eco and opening:
        opening_str = f"{eco} - {opening}"
    else:
        opening_str = opening or eco or "Custom / Uncategorized Opening"

    st.caption(f"Opening: **{opening_str}**")

    game_moves = [p for p in positions if p.get("ply", 0) > 0]
    white_moves = [p for p in game_moves if p.get("is_white") == 1]
    black_moves = [p for p in game_moves if p.get("is_white") == 0]

    white_stats = calculate_player_stats(white_moves)
    black_stats = calculate_player_stats(black_moves)

    w_err = aggregate_phase_errors(white_moves)
    b_err = aggregate_phase_errors(black_moves)

    w_name = headers.get("white", "White")
    b_name = headers.get("black", "Black")
    w_elo = headers.get("white_elo", "-")
    b_elo = headers.get("black_elo", "-")

    col_w, col_gap, col_b = st.columns([5, 1, 5])
    with col_w:
        st.markdown(f"**{w_name}** `({w_elo})`")
        m1, m2 = st.columns(2)
        m1.metric("Accuracy", f"{white_stats['accuracy']:.1f}%")
        m2.metric("ACPL", f"{white_stats['acpl']:.1f} CP")

    with col_b:
        st.markdown(f"**{b_name}** `({b_elo})`")
        m3, m4 = st.columns(2)
        m3.metric("Accuracy", f"{black_stats['accuracy']:.1f}%")
        m4.metric("ACPL", f"{black_stats['acpl']:.1f} CP")

    st.markdown("---")
    st.markdown("**Critical Error Distribution by Phase**")

    phases = ["Opening (1-10)", "Middlegame (11-30)", "Endgame (31+)"]
    fig = go.Figure(
        data=[
            go.Bar(
                name=f"White ({w_name})",
                x=phases,
                y=[w_err["Opening"], w_err["Middlegame"], w_err["Endgame"]],
                marker_color="#cccccc",
            ),
            go.Bar(
                name=f"Black ({b_name})",
                x=phases,
                y=[b_err["Opening"], b_err["Middlegame"], b_err["Endgame"]],
                marker_color="#000000",
            ),
        ]
    )

    max_val = max(max(w_err.values(), default=0), max(b_err.values(), default=0))
    fig.update_layout(
        barmode="group",
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Match Phase",
        yaxis_title="Suboptimal Moves Count",
        yaxis=dict(dtick=1, range=[0, max(3, max_val + 1)]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(build_narrative(headers, white_stats, black_stats, w_err, b_err))


_calculate_player_stats = calculate_player_stats
_aggregate_phase_errors = aggregate_phase_errors
_build_narrative = build_narrative
