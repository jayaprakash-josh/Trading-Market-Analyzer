import os
from datetime import datetime
from config import TIERS, TRADING_CAPITAL, RISK_PER_TRADE_PERCENT
import json

def generate_html_report(results, fii_dii, global_cues):
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%H:%M:%S')
    
    # Create reports directory inside the project docs folder
    project_root = os.path.dirname(os.path.dirname(__file__))
    reports_dir = os.path.join(project_root, "docs", "premarket_reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    filepath = os.path.join(reports_dir, f"Premarket_Report_{date_str}.html")
    
    # Helper to colorize signals
    def get_signal_color(signal):
        sig = str(signal).upper()
        if "LONG" in sig: return "#00b894" # Green
        if "SHORT" in sig: return "#d63031" # Red
        return "#feca57" # Yellow for WAIT/NO-TRADE

    # HTML Template
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NSE Pre-Market Report | {date_str}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 20px; }}
            h1, h2, h3, h4 {{ color: #ffffff; margin-top: 0; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header-panel {{ background-color: #1e1e1e; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid #0984e3; display: flex; justify-content: space-between; }}
            
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; background-color: #1e1e1e; border-radius: 8px; overflow: hidden; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #2d2d2d; }}
            th {{ background-color: #2d2d2d; font-weight: 600; }}
            tr:hover {{ background-color: #252525; }}
            
            .card {{ background-color: #1e1e1e; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .card-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2d2d2d; padding-bottom: 10px; margin-bottom: 15px; }}
            .badge {{ padding: 5px 10px; border-radius: 4px; font-weight: bold; color: #fff; }}
            
            .metrics-panel {{ background-color: #181818; padding: 15px; border-radius: 6px; margin: 20px 0 10px 0; border: 1px solid #333; }}
            .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; }}
            .metric-box {{ border-left: 3px solid #6c5ce7; padding-left: 10px; position: relative; }}
            .metric-label {{ font-size: 0.8em; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 4px; }}
            .metric-value {{ font-size: 1.1em; font-weight: bold; color: #fff; }}
            
            .text-green {{ color: #00b894; font-weight: bold; }}
            .text-red {{ color: #d63031; font-weight: bold; }}
            .text-yellow {{ color: #fdcb6e; font-weight: bold; }}
            
            .alert-box {{ background-color: rgba(214, 48, 49, 0.1); border-left: 4px solid #d63031; padding: 10px; margin-top: 15px; }}
            
            .components-table {{ width: 100%; border: none; margin-top: 10px; }}
            .components-table th, .components-table td {{ padding: 8px 10px; font-size: 0.9em; }}
            .components-table tr {{ border-bottom: 1px solid #333; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-panel">
                <div>
                    <h1>NSE Pre-Market Trade Analysis</h1>
                    <p style="margin:0;">Generated at: <strong>{date_str} 09:10:00 (Pre-Open Snapshot)</strong></p>
                    <p style="margin-top:5px; font-size: 0.85em; color: #aaa;">Deterministic scoring. Post-open confirmation required for Phase 2 execution.</p>
                </div>
            </div>
            
            <h2>Master Watchlist Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Final Bias</th>
                        <th>Stock</th>
                        <th>Bias Strength</th>
                        <th>Data Quality</th>
                        <th>Tradeability</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Sort results by bias strength
    sorted_results = sorted(results, key=lambda x: abs(x.get('quant_bias', {}).get('bias_strength', 0)), reverse=True)
    
    # Populate Summary Table
    for res in sorted_results:
        final_bias = res.get('final_bias', 'UNKNOWN').upper()
        q_bias = res.get('quant_bias', {})
        strength = q_bias.get('bias_strength', 0)
        direction = q_bias.get('direction', 'NEUTRAL')
        
        quality = res.get('data_quality', 0)
        alignment = q_bias.get('evidence', {}).get('alignment', 0)
        tradeability = res.get('tradeability', 'UNKNOWN')
        
        color = get_signal_color(final_bias)
        trade_color = "#00b894" if tradeability == "OK" else ("#d63031" if "BLOCKED" in tradeability else "#fdcb6e")
        
        html += f"""
                    <tr>
                        <td><span class="badge" style="background-color: {color}">{final_bias}</span></td>
                        <td><strong>{res['symbol']}</strong></td>
                        <td><strong>{strength}</strong> <span style="font-size:0.8em; color:#888;">({direction})</span></td>
                        <td>{quality}%</td>
                        <td style="color: {trade_color}; font-weight: bold;">{tradeability}</td>
                    </tr>
        """
        
    html += """
                </tbody>
            </table>
            
            <h2>Detailed Trade Setups</h2>
    """
    
    # Generate HTML for each stock (sorted by bias strength)
    for res in sorted_results:
        symbol = res['symbol']
        q_bias = res.get('quant_bias', {})
        
        # --- DATA FETCH DIAGNOSTICS ---
        tech_err = res.get('technicals', {}).get('error')
        if tech_err:
            tech_diag = f'<span style="color:#d63031">FAILED</span> <span style="color:#888">({tech_err})</span>'
        else:
            tech_diag = '<span style="color:#00b894">SUCCESS</span>'
            
        sector_name = res.get('sector_data', {}).get('sector_name', '')
        if 'Fallback' in sector_name:
            sec_diag = f'<span style="color:#fdcb6e">FALLBACK</span> <span style="color:#888">(Primary sector index failed, using Nifty 50)</span>'
        elif res.get('sector_data', {}).get('error') or sector_name == 'Unknown Sector':
            sec_diag = '<span style="color:#d63031">FAILED</span> <span style="color:#888">(No sector data)</span>'
        else:
            sec_diag = '<span style="color:#00b894">SUCCESS</span>'
            
        nse_err = res.get('nse_data', {}).get('error')
        if nse_err:
            nse_diag = f'<span style="color:#d63031">FAILED</span> <span style="color:#888">({nse_err})</span>'
        elif not res.get('nse_data', {}).get('pre_open_iep'):
            nse_diag = '<span style="color:#fdcb6e">PARTIAL</span> <span style="color:#888">(Pre-open IEP missing, market may be closed)</span>'
        else:
            nse_diag = '<span style="color:#00b894">SUCCESS</span>'
            
        news_err = res.get('llm_analysis', {}).get('error')
        if res.get('llm_analysis', {}).get('status') == 'DISABLED':
            news_diag = '<span style="color:#aaa">DISABLED</span> <span style="color:#888">(Dev Mode: Groq LLM bypassed)</span>'
        elif news_err:
            news_diag = f'<span style="color:#d63031">FAILED</span> <span style="color:#888">({news_err})</span>'
        elif not res.get('news'):
            news_diag = '<span style="color:#fdcb6e">NO NEWS</span> <span style="color:#888">(No recent articles found)</span>'
        else:
            news_diag = '<span style="color:#00b894">SUCCESS</span>'

        # --- METRICS TEXT FORMATTING ---
        tech = res.get('technicals', {})
        nse = res.get('nse_data', {})
        sect = res.get('sector_data', {})
        
        trend_val = f"{tech.get('Close',0)} vs EMA20({tech.get('EMA_20',0)})" if not tech_err else "N/A"
        rs_val = f"{sect.get('rs_vs_sector_20d', 'N/A')}"
        if isinstance(sect.get('rs_vs_sector_20d'), (int, float)):
            rs_val += "%"
        vol_val = f"RVOL: {tech.get('RVOL', 'N/A')}x"
        pre_val = f"Gap: {nse.get('pre_open_gap_percent', 'N/A')}%" if nse.get('pre_open_gap_percent') else "N/A"
        pcr_val = f"PCR: {nse.get('options_pcr', 'N/A')} | Ban: {'Yes' if nse.get('is_fno_banned') else 'No'}"
        vix_val = global_cues.get("INDIA_VIX", {}).get("1d_change", "N/A")
        nifty_val = global_cues.get("NIFTY_50", {}).get("1d_change", "N/A")
        vix_str = f"VIX Change: {vix_val}% | Nifty 1D: {nifty_val}%"
        
        tradeability = res.get('tradeability', 'UNKNOWN')
        tradeability_class = 'badge-green' if tradeability == 'OK' else 'badge-red'
        final_bias = res.get('final_bias', 'UNKNOWN')
        bias_class = 'text-green' if 'LONG' in final_bias else ('text-red' if 'SHORT' in final_bias else 'text-yellow')
        q_dir = q_bias.get('direction', 'NEUTRAL')
        q_dir_class = 'text-green' if q_dir == 'BULLISH' else ('text-red' if q_dir == 'BEARISH' else 'text-yellow')
        bias_strength_val = round(float(q_bias.get('bias_strength', 0)), 2)
        data_quality_val = res.get('data_quality', 0)
        
        html_template = """
        <div class="stock-card">
            <div class="stock-header">
                <div>
                    <h2>{symbol}</h2>
                    <span class="badge {tradeability_class}">{tradeability}</span>
                </div>
                <div style="text-align: right;">
                    <div class="bias-text {bias_class}">
                        {final_bias}
                    </div>
                </div>
            </div>
            
            <div class="metrics-panel" style="margin-top: 15px;">
                <div class="metrics-grid">
                    <div class="metric-box">
                        <span class="metric-label">Bias Strength</span>
                        <span class="metric-value {q_dir_class}">{bias_strength_val} / 10</span>
                    </div>
                    <div class="metric-box">
                        <span class="metric-label">Quant Direction</span>
                        <span class="metric-value">{q_dir}</span>
                    </div>
                    <div class="metric-box">
                        <span class="metric-label">Data Quality Score</span>
                        <span class="metric-value">{data_quality_val}%</span>
                    </div>
                </div>
            </div>
            
            <div style="background-color: #2a2a2a; padding: 12px; margin-top: 15px; border-radius: 4px; border-left: 4px solid #ffb142;">
                <h5 style="margin:0 0 8px 0; color:#ffb142; font-size: 0.9em;">DATA FETCH DIAGNOSTICS (What data we acquired)</h5>
                <ul style="margin:0; padding-left: 20px; font-size: 0.85em; color: #ddd; line-height: 1.6;">
                    <li><strong>Technicals & Volume:</strong> {tech_diag}</li>
                    <li><strong>Sector Index & RS:</strong> {sec_diag}</li>
                    <li><strong>Pre-Open & Derivatives:</strong> {nse_diag}</li>
                    <li><strong>News & Catalyst:</strong> {news_diag}</li>
                </ul>
            </div>
            
            <div style="margin-top: 15px; background-color: #181818; padding: 15px; border-radius: 6px; border: 1px solid #333;">
                <h4 style="margin-top:0; color:#aaa; border-bottom:1px solid #333; padding-bottom:5px;">ALL SCORING METRICS EXPLAINED</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <strong style="color:#fff;">1. Trend (Price vs EMA20):</strong> <span style="color:#0984e3">{trend_val}</span><br>
                        <small style="color:#888; display:block; margin-top:3px;">Determines the immediate direction of the asset. Trading with the trend significantly increases win rate probability.</small>
                    </div>
                    <div>
                        <strong style="color:#fff;">2. Sector RS (20D):</strong> <span style="color:#0984e3">{rs_val}</span><br>
                        <small style="color:#888; display:block; margin-top:3px;">Relative Strength vs its Sector. Institutional funds buy strong sectors. Buying an outperforming stock in a strong sector yields maximum alpha.</small>
                    </div>
                    <div>
                        <strong style="color:#fff;">3. RVOL (Relative Volume):</strong> <span style="color:#0984e3">{vol_val}</span><br>
                        <small style="color:#888; display:block; margin-top:3px;">Compares today's volume to the 20-day average. &gt;1.5x signals heavy institutional accumulation/distribution validating the price move.</small>
                    </div>
                    <div>
                        <strong style="color:#fff;">4. Pre-Open Gap & Imbalance:</strong> <span style="color:#0984e3">{pre_val}</span><br>
                        <small style="color:#888; display:block; margin-top:3px;">The 9:00-9:08 AM matched institutional orders. A strong gap with a large buy imbalance indicates immediate overnight sentiment shock.</small>
                    </div>
                    <div>
                        <strong style="color:#fff;">5. Options PCR & F&O:</strong> <span style="color:#0984e3">{pcr_val}</span><br>
                        <small style="color:#888; display:block; margin-top:3px;">Put-Call Ratio. &lt;0.8 is Bullish (Call writers are trapped), &gt;1.2 is Bearish. Checks if the stock is banned from F&O trading due to high OI.</small>
                    </div>
                    <div>
                        <strong style="color:#fff;">6. Market Regime (VIX & Nifty):</strong> <span style="color:#0984e3">{vix_str}</span><br>
                        <small style="color:#888; display:block; margin-top:3px;">India VIX measures market fear and expected volatility. High VIX requires smaller position sizing and wider stops. Nifty determines macro tailwinds.</small>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 15px; background-color: #181818; padding: 15px; border-radius: 6px; border: 1px solid #333;">
                <h4 style="margin-top:0; color:#0984e3; border-bottom:1px solid #333; padding-bottom:5px;">7. AI CATALYST CLASSIFICATION (News)</h4>
        """
        html += html_template.format(
            symbol=symbol,
            tradeability=tradeability,
            tradeability_class=tradeability_class,
            final_bias=final_bias,
            bias_class=bias_class,
            q_dir_class=q_dir_class,
            bias_strength_val=bias_strength_val,
            q_dir=q_dir,
            data_quality_val=data_quality_val,
            tech_diag=tech_diag,
            sec_diag=sec_diag,
            nse_diag=nse_diag,
            news_diag=news_diag,
            trend_val=trend_val,
            rs_val=rs_val,
            vol_val=vol_val,
            pre_val=pre_val,
            pcr_val=pcr_val,
            vix_str=vix_str
        )
        
        llm = res.get('llm_analysis', {})
        if llm.get('status') == 'DISABLED':
            html += """
                <div style="background-color:#161616; padding: 12px; border-radius: 4px; border-left: 3px solid #636e72;">
                    <strong style="color:#b2bec3;">LLM CATALYST CLASSIFIER: DISABLED (DEV MODE)</strong>
                    <p style="margin:5px 0 0 0; font-size: 0.85em; color: #888;">Groq LLM call was bypassed. Catalyst score defaulted to 0.0 (Neutral). Set <code>ENABLE_LLM = True</code> in <code>config.py</code> for production pre-market runs.</p>
                </div>
                """
        elif llm and "error" not in llm:
            llm_dir = llm.get('direction', 'N/A').upper()
            llm_dir_color = '#00b894' if llm_dir == 'POSITIVE' else '#d63031'
            llm_sev = llm.get('severity', 'N/A').upper()
            llm_sev_color = '#fdcb6e' if llm_sev != 'NONE' else '#aaa'
            llm_conflict = "YES" if llm.get('conflicts_with_bias') else "NO"
            llm_conflict_color = '#d63031' if llm.get('conflicts_with_bias') else '#00b894'
            llm_comment = llm.get('comment', 'No comment provided.')
            
            html += f"""
                <div style="background-color:#111; padding: 12px; border-radius: 4px; border-left: 3px solid #0984e3;">
                    <div style="display:flex; justify-content: space-between; margin-bottom: 8px;">
                        <div><strong style="color:#aaa">Sentiment:</strong> <span style="color: {llm_dir_color}">{llm_dir}</span></div>
                        <div><strong style="color:#aaa">Severity:</strong> <span style="color: {llm_sev_color}">{llm_sev}</span></div>
                        <div><strong style="color:#aaa">Conflict with Quant:</strong> <span style="color: {llm_conflict_color}">{llm_conflict}</span></div>
                    </div>
                    <p style="margin:0; font-size: 0.9em; line-height: 1.4;"><strong>AI Conclusion:</strong> {llm_comment}</p>
                </div>
                <small style="color:#888; display:block; margin-top:8px;">The LLM scans raw Google News headlines to determine if a recent catalyst contradicts our mathematical Bias Score.</small>
                """
        else:
            html += f"""
                <p style="color:#888; margin: 10px 0 0 0;">No material news / Analysis failed.</p>
                <small style="color:#666; display:block; margin-top:8px;">(The LLM checks for catalysts. If none are found, or the fetch failed, this defaults to neutral.)</small>
                """
            
        html += """
            </div>
        </div>
        """
        
    html += """
        </div>
    </body>
    </html>
    """
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
        
    return filepath
