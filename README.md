# 🏀 CourtMetrics: Elite H2H Breakdown

CourtMetrics is a high-performance NBA scouting and player-prop analysis tool. It automates the process of fetching historical Head-to-Head (H2H) matchups and cross-references them with a player's recent form.

## 🚀 Features

- **Smart H2H Filtering:** Automatically fetches and displays matchups from the last 4 months.
- **Player-Centric Venue Logic:** Intelligent tracking of (HOME) vs (AWAY) status per player.
- **Speed & Stability:** Integrated game-level caching to prevent timeouts.
- **Elite Visual UI:** Custom CSS interface for high-visibility stat tracking.

## 🛠️ Tech Stack

- **Python 3.13**
- **Streamlit**
- **NBA_API**
- **Pandas**

## 📦 Installation & Setup

1. **Clone the repository:**

```bash
git clone https://github.com/ryan7zoom/court-metrics.git
cd court-metrics

```

2. **Install dependencies:**

```bash
pip install streamlit nba_api pandas pytz

```

3. **Run the application:**

```bash
streamlit run app.py

```

## 📋 Usage

1. **Select Date:** Use the sidebar to choose the date of the NBA games.
2. **Generate:** Click "Generate Report" to start.
3. **Analyze:** Expand game sections to see player stats.
