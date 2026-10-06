# Chessys

Chessys is a machine learning pipeline and interactive web application designed to evaluate chess positions and predict the empirical probability of a blunder. The system relies on tactical feature extraction and a calibrated gradient boosting model to provide quantitative risk assessments for specific board states.

## Methodology

The core logic focuses on extracting deterministic positional and tactical features from chess positions to predict the `is_blunder` target variable. 

### Feature Extraction
The model relies on 12 engineered features representing the current state of the board:
- `material_balance`: Net material difference between white and black.
- `tactical_tension`: Number of active attacks and captures available.
- `hanging_pieces`: Number of undefended pieces under attack.
- `king_openness`: Degree of exposure of the king.
- `legal_moves_count`: Total valid moves available.
- `mobility_ratio`: Ratio of available squares between players.
- `absolute_pins`: Number of pieces pinned to the king.
- `is_check`: Boolean indicator if the current king is in check.
- `has_queen_turn` / `has_queen_opp`: Boolean indicators for queen presence.
- `player_elo`: Elo rating bracket of the player.
- `ply`: The current half-move number (game phase proxy).

### Modeling and Calibration
1. **Algorithm**: XGBoost Classifier tailored for tabular data with continuous and discrete features.
2. **Imbalance Handling**: Optimized for F2-Score utilizing positive class weighting.
3. **Probability Calibration**: The raw model output is calibrated using Platt Scaling (Sigmoid calibration) via 5-fold cross-validation. This ensures that the predicted probabilities map accurately to empirical blunder fractions (Brier Score evaluation).
4. **Explainability**: Feature importance extraction identifies the main drivers of blunder risk in any given position.

## Project Structure

```text
.
├── app.py                   # Streamlit web interface entry point
├── config.py                # Global application configuration
├── artifacts/               # Serialized models and metadata
│   ├── blunder_xgb_raw.joblib
│   ├── blunder_calibrated.joblib
│   ├── model_config.json
│   └── feature_names.json
├── data/                    # Dataset storage (ignored in version control)
│   ├── raw/                 
│   └── processed/           # Parquet partitions (train, val, test)
├── notebooks/               # Research and training lifecycle
│   ├── 1_eda.ipynb          # Exploratory Data Analysis
│   ├── 2_preprocess.ipynb   # Data cleaning and feature engineering
│   ├── 3_model.ipynb        # XGBoost training and threshold optimization
│   └── 4_eval.ipynb         # Model calibration and test set evaluation
├── src/                     # Core computational logic
│   ├── extractor.py         # Tactical feature extraction engine
│   └── visualization.py     # UI rendering components (Plotly/Board)
└── .streamlit/              # UI configuration (Black & White theme)
    └── config.toml
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/raifeb/Chessys.git
   cd Chessys
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To launch the interactive prediction interface:

```bash
streamlit run app.py
```

## UI & Formatting Standard

This repository adheres to a strict professional standard:
- **Visuals**: A global black-and-white (grayscale) theme is enforced via `.streamlit/config.toml` and Plotly layouts.
- **Codebase**: PEP-8 compliance, `snake_case` variable naming, and no trivial comments.
- **Text**: Absence of emojis or decorative text across the UI and codebase to maintain a focused, analytical environment.

