from nba_api.stats.endpoints import scoreboardv2, leaguegamefinder, boxscoretraditionalv3, playergamelog
from datetime import datetime, timedelta
import pandas as pd
import time

# --- CONFIGURATION ---
today_dt = datetime.now()
target_date = today_dt.strftime('%Y-%m-%d') 
four_months_ago = today_dt - timedelta(days=120)

sb = scoreboardv2.ScoreboardV2(game_date=target_date)
games = sb.get_dict()['resultSets'][0]['rowSet']

print(f"--- NBA PROPHET: Injury & Context Bot ({target_date}) ---")

for game in games:
    home_team_id, away_team_id, matchup_name = game[6], game[7], game[5]
    
    # Fetch H2H History
    history = leaguegamefinder.LeagueGameFinder(team_id_nullable=home_team_id, vs_team_id_nullable=away_team_id).get_data_frames()[0]
    history['GAME_DATE'] = pd.to_datetime(history['GAME_DATE'])
    past_h2h = history[history['GAME_DATE'].dt.date < today_dt.date()]

    if not past_h2h.empty and past_h2h.iloc[0]['GAME_DATE'] > four_months_ago:
        last_game_id = past_h2h.iloc[0]['GAME_ID']
        print(f"\n🔍 Matchup: {matchup_name} (H2H: {past_h2h.iloc[0]['GAME_DATE'].date()})")

        # Fetch Box Score
        box = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=last_game_id).get_data_frames()[0]
        box['min_float'] = box['minutes'].apply(lambda x: float(x.split(':')[0]) if isinstance(x, str) and ':' in x else 0)
        
        # 1. Identify Missing Key Players (Absence Logic)
        # We look for players who played 25+ mins in H2H but might be out now
        heavy_hitters = box[box['min_float'] > 25]
        
        for _, p in box[box['min_float'] > 15].iterrows():
            p_id = p['personId']
            p_name = f"{p['firstName']} {p['familyName']}"
            
            # Fetch Last 5
            try:
                log_data = playergamelog.PlayerGameLog(player_id=p_id).get_data_frames()
                if not log_data or log_data[0].empty:
                    print(f"   ❌ {p_name}: [ABSENT] - Not in recent game logs.")
                    continue
                
                log = log_data[0].head(5)
                
                # Stats & Combos
                l5_pts, l5_reb, l5_ast = log['PTS'].mean(), log['REB'].mean(), log['AST'].mean()
                l5_pra, l5_pa = l5_pts + l5_reb + l5_ast, l5_pts + l5_ast
                
                h2h_pts, h2h_reb, h2h_ast = p['points'], p['reboundsTotal'], p['assists']
                h2h_pra, h2h_pa = h2h_pts + h2h_reb + h2h_ast, h2h_pts + h2h_ast
                h2h_min = p['min_float']
                
                avg_min = log['MIN'].apply(lambda x: float(x.split(':')[0]) if isinstance(x, str) and ':' in x else float(x)).mean()

                findings = []

                # Recommendation Logic (Now always shows stats even with Minute Drop)
                if l5_pra < h2h_pra:
                    findings.append(f"📉 [UNDER PRA] H2H: {h2h_pra} -> L5: {l5_pra:.1f} (Trend: Down)")
                elif l5_pra > h2h_pra:
                    findings.append(f"🔥 [OVER PRA] H2H: {h2h_pra} -> L5: {l5_pra:.1f} (Trend: Up)")

                # Contextual Alerts
                if h2h_min > (avg_min + 7):
                    findings.append(f"⚠️ [CAUTION] Minute Drop: {h2h_min:.0f}m -> {avg_min:.1f}m (Role Decrease)")
                
                if h2h_min < (avg_min - 5):
                    findings.append(f"🚀 [OPPORTUNITY] Role Expansion: {h2h_min:.0f}m -> {avg_min:.1f}m (Filling Gap?)")

                if findings:
                    print(f"   ⭐ {p_name}:")
                    for f in findings:
                        print(f"      {f}")
                
                time.sleep(0.4) # Rate limiting
                
            except Exception:
                continue