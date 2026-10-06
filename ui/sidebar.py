from typing import Callable
import streamlit as st
from config import check_system_readiness

SAMPLE_PGN: str = """[Event "Live Chess"]
[Site "Chess.com"]
[Date "2026.02.15"]
[White "Player_White"]
[Black "Player_Black"]
[Result "1-0"]
[WhiteElo "1750"]
[BlackElo "1720"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. b4 Bxb4 5. c3 Ba5 6. d4 exd4 7. O-O Nge7
8. Ng5 d5 9. exd5 Ne5 10. Bb3 h6 11. Qxd4 N7g6 12. Re1 O-O 13. Rxe5 Nxe5
14. Qxe5 hxg5 15. Bxg5 Qd6 16. Qe4 Qg6 17. Qxg6 fxg6 18. d6+ Kh7 19. Be7 Re8
20. Bf7 Bf5 21. Bxe8 Rxe8 22. Na3 cxd6 23. Bxd6 Bxc3 24. Rc1 Bb2 1-0"""


def render_sidebar(on_analyze_callback: Callable[[str], bool]) -> None:
    with st.sidebar:
        st.markdown("### Data Input")

        tab_paste, tab_upload = st.tabs(["Manual PGN", "Upload File"])
        pgn_content = ""

        with tab_paste:
            pgn_text_area = st.text_area(
                label="Paste Notasi PGN:",
                height=150,
                placeholder="1. e4 e5 2. Nf3 Nc6...",
                key="manual_pgn_input",
            )
            if pgn_text_area.strip():
                pgn_content = pgn_text_area.strip()

        with tab_upload:
            uploaded_file = st.file_uploader(
                label="Pilih file .pgn",
                type=["pgn"],
                help="Unggah file PGN dari platform catur (Chess.com, Lichess, dll).",
            )
            if uploaded_file is not None:
                raw_bytes = uploaded_file.getvalue()
                try:
                    pgn_content = raw_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        pgn_content = raw_bytes.decode("latin-1")
                    except Exception:
                        st.error("Format encoding file tidak didukung.")

        if st.button("Load Demo", use_container_width=True):
            with st.spinner("Memproses langkah pertandingan demo..."):
                if on_analyze_callback(SAMPLE_PGN.strip()):
                    st.rerun()

        st.divider()

        col_process, col_flip = st.columns(2)
        with col_process:
            btn_process = st.button(
                "Analyze", type="primary", use_container_width=True
            )
        with col_flip:
            if st.button("Flip Board", use_container_width=True):
                st.session_state.flipped = not st.session_state.get("flipped", False)
                st.rerun()

        if btn_process:
            cleaned_pgn = pgn_content.strip()
            if cleaned_pgn:
                with st.spinner("Menjalankan analisis..."):
                    if on_analyze_callback(cleaned_pgn):
                        st.rerun()
            else:
                st.warning("Silakan masukkan teks PGN, upload file, atau klik 'Load Demo'.")

        with st.expander("System Status", expanded=False):
            readiness = check_system_readiness()
            st.caption(f"**Stockfish Engine:** {'Ready' if readiness['stockfish'] else 'Not Found'}")
            st.caption(f"**Model ML Calibrated:** {'Ready' if readiness['model'] else 'Not Found'}")
            st.caption(f"**Fitur Taktis:** {'Ready' if readiness['feature_names'] else 'Not Found'}")
