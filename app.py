import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import scoreboardv2, leaguegamefinder, boxscoretraditionalv3, playergamelog
from nba_api.stats.static import teams
from datetime import datetime, timedelta
import pytz
import time

# Page Config
st.set_page_config(page_title="CourtMetrics", layout="wide")

# High-Visibility CSS
st.markdown("""
    <style>
    .h2h-command-center {
        background-color: #0e1117;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #ff4b4b;
        margin-bottom: 25px;
        color: #ffffff;
    }
    .player-title {
        font-size: 26px !important;
        font-weight: 800;
        color: #ff4b4b;
        text-transform: uppercase;
    }
    .stat-line {
        font-size: 19px;
        color: #fafafa;
        line-height: 1.7;
    }
    .stat-highlight {
        color: #00ffcc;
        font-weight: bold;
        font-size: 21px;
    }
    .venue-tag-home { color: #00ff88; font-weight: bold; }
    .venue-tag-away { color: #ffcc00; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏀 CourtMetrics: Elite Breakdown")

nba_teams = teams.get_teams()
team_map = {team['id']: team['full_name'] for team in nba_teams}

# Global Caches to prevent redundant API hits
game_box_cache = {}

def safe_fetch(endpoint_class, normalize=True, cache_key=None, **kwargs):
    if cache_key and cache_key in game_box_cache:
        return game_box_cache[cache_key]

    for i in range(3):
        try:
            df = endpoint_class(**kwargs, timeout=30).get_data_frames()[0]
            if normalize:
                df.columns = [c.lower() for c in df.columns]
            if cache_key:
                game_box_cache[cache_key] = df
            return df
        except Exception:
            time.sleep(1)
    return pd.DataFrame()

with st.sidebar:
    st.header("Settings")
    now = datetime.now(pytz.timezone('US/Eastern'))
    target_date = st.date_input("Matchup Date", now.date(), format="DD/MM/YYYY")

if st.button("Generate Report"):
    sb_df = safe_fetch(scoreboardv2.ScoreboardV2, game_date=target_date.strftime('%Y-%m-%d'))
    
    if sb_df.empty:
        st.warning(f"No games found.")
    
    for _, game in sb_df.iterrows():
        home_id, away_id = game['home_team_id'], game['visitor_team_id']
        home_name, away_name = team_map.get(home_id), team_map.get(away_id)
        
        with st.expander(f"🏟️ {away_name} @ {home_name} (HOME)", expanded=True):
            four_months_ago = target_date - timedelta(days=120)
            history = safe_fetch(leaguegamefinder.LeagueGameFinder, team_id_nullable=home_id, vs_team_id_nullable=away_id)
            
            if not history.empty:
                history['game_date'] = pd.to_datetime(history['game_date'])
                recent_h2h = history[(history['game_date'].dt.date < target_date) & 
                                     (history['game_date'].dt.date >= four_months_ago)].copy()

                if not recent_h2h.empty:
                    latest_game_id = recent_h2h.iloc[0]['game_id']
                    box_latest = safe_fetch(boxscoretraditionalv3.BoxScoreTraditionalV3, 
                                            game_id=latest_game_id, 
                                            cache_key=f"box_{latest_game_id}")
                    
                    if box_latest.empty: continue
                    box_latest['min_val'] = box_latest['minutes'].apply(lambda x: float(str(x).split(':')[0]) if ':' in str(x) else 0)
                    
                    for _, p in box_latest[box_latest['min_val'] > 18].iterrows():
                        p_id, p_team_id = p['personid'], p['teamid']
                        p_name = f"{p['firstname']} {p['familyname']}"
                        
                        curr_v = "(HOME)" if p_team_id == home_id else "(AWAY)"
                        curr_class = "venue-tag-home" if curr_v == "(HOME)" else "venue-tag-away"

                        logs = safe_fetch(playergamelog.PlayerGameLog, player_id=p_id)
                        if logs.empty: continue
                        l5 = logs.head(5)
                        l5_pts, l5_reb, l5_ast = l5['pts'].mean(), l5['reb'].mean(), l5['ast'].mean()
                        l5_min = l5['min'].apply(lambda x: float(str(x).split(':')[0]) if ':' in str(x) else float(x)).mean()

                        st.markdown(f'<div class="player-title">⭐ {p_name} <span class="{curr_class}" style="font-size:16px;">{curr_v} TODAY</span></div>', unsafe_allow_html=True)

                        top_h2h_stats = None
                        unique_games = recent_h2h.groupby('game_id').first().reset_index().sort_values('game_date', ascending=False)

                        for idx, h2h_game in unique_games.iterrows():
                            # Venue Logic
                            is_player_team_row = (h2h_game['team_id'] == p_team_id)
                            match_str = h2h_game['matchup'].upper()
                            is_home = "VS." in match_str if is_player_team_row else "@" in match_str
                            
                            v_label, v_class = ("(HOME)", "venue-tag-home") if is_home else ("(AWAY)", "venue-tag-away")

                            h_id = h2h_game['game_id']
                            h2h_box = safe_fetch(boxscoretraditionalv3.BoxScoreTraditionalV3, 
                                                 game_id=h_id, 
                                                 cache_key=f"box_{h_id}")
                            
                            p_match = h2h_box[h2h_box['personid'] == p_id]
                            
                            if not p_match.empty:
                                pm = p_match.iloc[0]
                                pts, reb, ast = pm['points'], pm['reboundstotal'], pm['assists']
                                pra = pts + reb + ast
                                
                                # Re-calculating shooting numbers
                                fgm, fga = pm['fieldgoalsmade'], pm['fieldgoalsattempted']
                                fg3m, fg3a = pm['threepointersmade'], pm['threepointersattempted']
                                fg2m, fg2a = fgm - fg3m, fga - fg3a
                                
                                if top_h2h_stats is None: top_h2h_stats = (pts, reb, ast, pra)

                                st.markdown(f"""
                                <div class="h2h-command-center">
                                    <div class="stat-line">
                                        <b>MATCHUP ({h2h_game['game_date'].strftime('%d/%m/%Y')}) <span class="{v_class}">{v_label}</span>:</b><br>
                                        <span class="stat-highlight">{pts} PTS | {reb} REB | {ast} AST | {pra} PRA</span><br>
                                        <b>MINUTES:</b> {pm['minutes']} (L5 Avg: {l5_min:.1f}m) | 
                                        <b>2P:</b> {fg2m}/{fg2a} | <b>3P:</b> {fg3m}/{fg3a}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                        if top_h2h_stats:
                            hp, hr, ha, hpra = top_h2h_stats
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("Points (L5)", f"{l5_pts:.1f}", f"{l5_pts-hp:.1f} vs H2H")
                            c2.metric("Rebounds (L5)", f"{l5_reb:.1f}", f"{l5_reb-hr:.1f} vs H2H")
                            c3.metric("Assists (L5)", f"{l5_ast:.1f}", f"{l5_ast-ha:.1f} vs H2H")
                            c4.metric("PRA (L5)", f"{l5_pts+l5_reb+l5_ast:.1f}", f"{(l5_pts+l5_reb+l5_ast)-hpra:.1f} vs H2H")

                        st.divider()
                        time.sleep(0.15)