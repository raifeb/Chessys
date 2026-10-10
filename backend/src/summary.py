from typing import Any, Optional

def calculate_player_stats(moves: list[dict[str, Any]]) -> dict[str, Optional[float]]:
    if not moves:
        return {"acpl": 0.0, "accuracy": 100.0, "total_moves": 0.0}

    evaluated_losses = [m["cp_loss"] for m in moves if m.get("cp_loss") is not None]
    if not evaluated_losses:
        return {
            "acpl": None,
            "accuracy": None,
            "total_moves": float(len(moves)),
        }

    total_cp_loss = sum(evaluated_losses)
    acpl = total_cp_loss / len(evaluated_losses)
    accuracy = max(0.0, min(100.0, 100.0 - (acpl * 0.31)))

    return {
        "acpl": round(float(acpl), 1),
        "accuracy": round(float(accuracy), 1),
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
    white_stats: dict[str, Optional[float]],
    black_stats: dict[str, Optional[float]],
    w_err: dict[str, int],
    b_err: dict[str, int],
) -> str:
    w_name = headers.get("white", "White")
    b_name = headers.get("black", "Black")
    if white_stats.get("acpl") is None or black_stats.get("acpl") is None:
        return (
            f"Evaluasi engine tidak tersedia untuk pertandingan {w_name} vs {b_name}. "
            "Hanya telemetri risiko model ML yang dihitung."
        )
    diff_acpl = abs(white_stats["acpl"] - black_stats["acpl"])
    cleaner = w_name if white_stats["acpl"] <= black_stats["acpl"] else b_name

    total_w_err = sum(w_err.values())
    total_b_err = sum(b_err.values())
    endgame_delta = b_err["Endgame"] - w_err["Endgame"]

    if endgame_delta > 0:
        phase_insight = (
            f"Pemisahan keunggulan terjadi di Endgame (31+). {b_name} mencatatkan "
            f"{b_err['Endgame']} deviasi suboptimal berbanding {w_err['Endgame']} dari {w_name}, "
            f"menjadikan penurunan akurasi babak akhir sebagai faktor penentu hasil."
        )
    elif endgame_delta < 0:
        phase_insight = (
            f"Fluktuasi posisi memuncak di Endgame (31+), di mana {w_name} membuat "
            f"{w_err['Endgame']} kesalahan yang memberi ruang inisiatif bagi {b_name}."
        )
    else:
        phase_insight = (
            "Tingkat kesalahan terdistribusi seimbang antara kedua pemain "
            "tanpa adanya keruntuhan posisi tunggal di satu fase."
        )

    best_accuracy = max(white_stats["accuracy"], black_stats["accuracy"])

    return (
        f"Efisiensi Eksekusi: {cleaner} mempertahankan stabilitas posisi lebih solid dengan keunggulan selisih "
        f"{diff_acpl:.1f} CP Loss dan tingkat akurasi {best_accuracy:.1f}%.\n\n"
        f"Fase Kritis: {phase_insight}\n\n"
        f"Total Deviasi Posisi: {w_name} ({total_w_err} error) vs {b_name} ({total_b_err} error)."
    )
