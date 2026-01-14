````markdown
# 🏀 CourtMetrics: Elite H2H Breakdown

CourtMetrics is a high-performance NBA scouting and player-prop analysis tool built to identify performance trends. It automates the process of fetching historical Head-to-Head (H2H) matchups and cross-references them with a player's recent form (Last 5 games) to provide a clear picture of how a player matches up against specific opponents.

## 🚀 Features

- **Smart H2H Filtering:** Automatically fetches and displays matchups from the last 4 months to ensure data relevance.
- **Player-Centric Venue Logic:** Intelligent tracking of (HOME) vs (AWAY) status. The tool correctly identifies if the player was home or away based on their specific team, regardless of the overall game matchup.
- **Speed & Stability:** Integrated game-level caching and normalized API fetching to reduce latency and prevent "Read Timeout" errors and drastically reduce load times.
- **Visual UI:** Custom CSS "Command Center" interface designed for high-visibility stat tracking and dark-mode optimization.
- **Shooting Efficiency:** Detailed breakdown of 2-pointer and 3-pointer attempts/makes for every historical matchup.
- **Delta Metrics:** Real-time calculation of performance variance (L5 Average vs. H2H performance) to highlight "blowout" or "under-performance" trends.

## 🛠️ Tech Stack

- **Python 3.13**
- **Streamlit** (Web Interface)
- **NBA_API** (Direct Data Source)
- **Pandas** (Data Processing & Normalization)
- **Pytz** (Timezone Management)

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ryan7zoom/court-metrics.git](https://github.com/ryan7zoom/court-metrics.git)
   cd court-metrics
   ```
````

2. **Install dependencies:**

```bash
pip install streamlit nba_api pandas pytz

```

3. **Run the application:**

```bash
streamlit run app.py

```

## 📋 Usage

1. **Select Date:** Use the sidebar to choose the date of the NBA games you want to analyze.
2. **Generate:** Click "Generate Report" to start the automated scouting process.
3. **Analyze:** Expand game sections to see individual player "Command Centers."
4. **Interpret:** Compare the "Today" venue status with historical H2H stats and check the Delta metrics for point, rebound, and assist trends.
