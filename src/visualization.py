import math
from typing import Any, Optional
import chess
import chess.svg
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import MOVE_COLORS


def calculate_eval_bar_percentage(eval_cp: int) -> float:
    clamped_cp = max(-1500, min(1500, eval_cp))
    try:
        pct = 100.0 / (1.0 + math.exp(-0.004 * clamped_cp))
    except OverflowError:
        pct = 95.0 if clamped_cp > 0 else 5.0
    return max(5.0, min(95.0, pct))


def generate_board_and_eval_html(
    fen: str,
    from_sq: Optional[str] = None,
    to_sq: Optional[str] = None,
    label: str = "Best Move",
    cp_eval_white: int = 0,
    flipped: bool = False,
    size: int = 380,
    **kwargs: Any,
) -> str:
    board = chess.Board(fen)
    arrows: list[chess.svg.Arrow] = []

    if from_sq and to_sq:
        try:
            arrow_color = MOVE_COLORS.get(label, "#555555cc")
            arrows.append(
                chess.svg.Arrow(
                    chess.parse_square(from_sq),
                    chess.parse_square(to_sq),
                    color=arrow_color,
                )
            )
        except ValueError:
            pass

    check_sq = board.king(board.turn) if board.is_check() else None

    board_svg = chess.svg.board(
        board=board,
        orientation=chess.BLACK if flipped else chess.WHITE,
        arrows=arrows,
        check=check_sq,
        size=size,
    )

    white_pct = calculate_eval_bar_percentage(cp_eval_white)
    if flipped:
        white_pct = 100.0 - white_pct

    if abs(cp_eval_white) < 5000:
        eval_label = f"{cp_eval_white / 100:+.1f}"
    else:
        eval_label = "M" if cp_eval_white > 0 else "-M"

    return f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 14px; margin: auto; padding: 4px 0;">
        <div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
            <div style="width: 22px; height: {size}px; background-color: #000000; border-radius: 6px; overflow: hidden; position: relative; border: 1px solid #000;">
                <div style="width: 100%; height: {white_pct:.1f}%; background-color: #ffffff; position: absolute; bottom: 0; transition: height 0.25s ease;"></div>
            </div>
            <span style="font-size: 11px; font-weight: 700; color: #000000; font-family: monospace;">{eval_label}</span>
        </div>
        <div style="display: inline-block; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; line-height: 0;">
            {board_svg}
        </div>
    </div>
    """


def create_telemetry_figure(
    positions: list[dict[str, Any]], current_ply: int
) -> go.Figure:
    plies = [p["ply"] for p in positions]
    evals = [min(max(p.get("cp_eval_white", 0) / 100.0, -8.0), 8.0) for p in positions]
    risks = [p.get("blunder_risk_pct", 0.0) for p in positions]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        row_heights=[0.55, 0.45],
        subplot_titles=("Evaluation Advantage (Pawns)", "Cognitive Blunder Risk (%)"),
    )

    fig.add_trace(
        go.Scatter(
            x=plies,
            y=evals,
            mode="lines",
            name="Stockfish Eval",
            line=dict(color="#000000", width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 0, 0, 0.1)",
            hovertemplate="Ply %{x}<br>Eval: %{y:+.2f} pawns<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=plies,
            y=risks,
            mode="lines",
            name="Risk %",
            line=dict(color="#000000", width=2),
            hovertemplate="Ply %{x}<br>Risk: %{y:.1f}%<extra></extra>",
        ),
        row=2,
        col=1,
    )

    blunder_positions = [
        p for p in positions if p.get("label") in ["Blunder", "Mistake"]
    ]
    if blunder_positions:
        blunder_plies = [p["ply"] for p in blunder_positions]
        blunder_risks = [p.get("blunder_risk_pct", 0.0) for p in blunder_positions]
        blunder_texts = [
            f"{p.get('label')} ({p.get('san')})" for p in blunder_positions
        ]

        fig.add_trace(
            go.Scatter(
                x=blunder_plies,
                y=blunder_risks,
                mode="markers",
                name="Critical Error",
                marker=dict(symbol="x", size=8, color="#000000", line=dict(width=1.5)),
                text=blunder_texts,
                hovertemplate="%{text}<br>Ply %{x}<br>Risk: %{y:.1f}%<extra></extra>",
            ),
            row=2,
            col=1,
        )

    for row_idx in (1, 2):
        fig.add_vline(
            x=current_ply,
            line_width=1.5,
            line_dash="dash",
            line_color="#cccccc",
            row=row_idx,
            col=1,
        )

    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=25, b=10),
        template="plotly_white",
        showlegend=False,
    )
    fig.update_xaxes(title_text="Ply", row=2, col=1)
    fig.update_yaxes(title_text="Pawns", range=[-8.5, 8.5], row=1, col=1)
    fig.update_yaxes(title_text="Risk %", range=[0, 105], row=2, col=1)

    return fig


_calculate_eval_bar_percentage = calculate_eval_bar_percentage
create_telemetry_timeline = create_telemetry_figure
