import os
from datetime import datetime

# The 8 funds we identified in our strategy document
RECOMMENDED_FUNDS = {
    "FLEXI": [
        {"name": "Parag Parikh Flexi Cap Fund", "type": "Flexi-Cap", "cagr": "~22%", "aum": "₹70,000+ Cr", "rationale": "Deep value investing. Holds 25% in US stocks (Alphabet, MSFT) for global diversification. Doesn't chase momentum. Best for conservative lump sum deployment."},
        {"name": "HDFC Flexi Cap Fund", "type": "Flexi-Cap", "cagr": "~24%", "aum": "₹60,000+ Cr", "rationale": "Value-tilted strategy. Underperforms in bubbles, but crashes much less during corrections due to avoiding overvalued stocks. Deep liquidity."}
    ],
    "MID": [
        {"name": "Motilal Oswal Midcap Fund", "type": "Mid-Cap", "cagr": "~30%", "aum": "₹15,000+ Cr", "rationale": "Aggressive, concentrated portfolio (25-30 stocks). High alpha generator. Crashes hard during dips, providing excellent entry points."},
        {"name": "Kotak Emerging Equity Fund", "type": "Mid-Cap", "cagr": "~25%", "aum": "₹45,000+ Cr", "rationale": "Highly diversified (65+ stocks). Smoother ride than Motilal Oswal. The safest way to play the mid-cap space."}
    ],
    "SMALL": [
        {"name": "Quant Small Cap Fund", "type": "Small-Cap", "cagr": "~35%", "aum": "₹25,000+ Cr", "rationale": "Hyper-aggressive quantitative model. High churn. Only to be bought on extreme dips (>15% drawdown) as it falls violently during crashes."},
        {"name": "Nippon India Small Cap", "type": "Small-Cap", "cagr": "~30%", "aum": "₹50,000+ Cr", "rationale": "Largest small-cap fund in India. Very broad basket (150+ stocks) which acts almost like an index fund. Less volatile than Quant."}
    ],
    "LIQUID": [
        {"name": "HDFC Money Market Fund", "type": "Liquid/Debt", "cagr": "~7.5% (1Y)", "aum": "Huge", "rationale": "Your war-chest. Park your capital here while waiting for a dip. T+1 redemption."},
        {"name": "Parag Parikh Liquid Fund", "type": "Liquid/Debt", "cagr": "~7.0% (1Y)", "aum": "Moderate", "rationale": "Alternative war-chest. Allows instant redemption for amounts up to ₹50,000."}
    ]
}

def generate_mf_html_report(factors, composite_score, verdict, action, deploy_pct, data):
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%H:%M:%S')
    
    project_root = os.path.dirname(os.path.dirname(__file__))
    reports_dir = os.path.join(project_root, "docs", "mf_dip_reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    filepath = os.path.join(reports_dir, f"MF_Dip_Report_{date_str}.html")

    # Determine Verdict Color
    v_color = "#feca57" # Default yellow
    if "GENERATIONAL" in verdict.upper(): v_color = "#e84393" # Pink/Purple
    elif "STRONG BUY" in verdict.upper(): v_color = "#d63031" # Red
    elif "REAL CORRECTION" in verdict.upper(): v_color = "#e67e22" # Orange
    elif "MILD DIP" in verdict.upper(): v_color = "#f1c40f" # Yellow
    elif "NO OPPORTUNITY" in verdict.upper(): v_color = "#00b894" # Green (Safe)

    # Build the HTML template
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MF Dip Detector | {date_str}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 20px; }}
            h1, h2, h3 {{ color: #ffffff; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            .header-panel {{ background-color: #1e1e1e; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid {v_color}; display: flex; justify-content: space-between; align-items: center; }}
            
            .verdict-box {{ text-align: right; }}
            .verdict-title {{ font-size: 24px; font-weight: bold; color: {v_color}; margin-bottom: 5px; }}
            .verdict-score {{ font-size: 18px; color: #aaa; }}
            
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; background-color: #1e1e1e; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #2d2d2d; }}
            th {{ background-color: #2d2d2d; font-weight: 600; text-transform: uppercase; font-size: 14px; color: #bbb; }}
            tr:hover {{ background-color: #252525; }}
            
            .score-0 {{ color: #00b894; font-weight: bold; }}
            .score-1 {{ color: #f1c40f; font-weight: bold; }}
            .score-2 {{ color: #e67e22; font-weight: bold; }}
            .score-3 {{ color: #d63031; font-weight: bold; }}
            
            .action-panel {{ background-color: #1e1e1e; padding: 25px; border-radius: 8px; margin-bottom: 30px; border: 1px solid #333; }}
            .action-step {{ margin-bottom: 15px; font-size: 16px; line-height: 1.5; }}
            .highlight {{ color: #0984e3; font-weight: bold; }}
            
            .fund-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(450px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .fund-card {{ background-color: #1e1e1e; padding: 20px; border-radius: 8px; border-top: 4px solid #6c5ce7; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            .fund-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }}
            .fund-name {{ font-size: 18px; font-weight: bold; color: #fff; margin: 0; }}
            .fund-type {{ background-color: #2d2d2d; padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #0984e3; font-weight: bold; }}
            .fund-stats {{ display: flex; gap: 15px; margin-bottom: 15px; font-size: 14px; color: #aaa; }}
            .fund-stat-item strong {{ color: #fff; }}
            .fund-rationale {{ font-size: 14px; line-height: 1.5; color: #ccc; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-panel">
                <div>
                    <h1 style="margin:0 0 10px 0;">Mutual Fund Dip Detector</h1>
                    <p style="margin:0; color:#aaa;">Report Generated: <strong>{date_str} {time_str}</strong></p>
                    <p style="margin:5px 0 0 0; color:#aaa;">Nifty 50 Current Level: <strong>{data.get('nifty_price', 'N/A')}</strong></p>
                </div>
                <div class="verdict-box">
                    <div class="verdict-title">{verdict}</div>
                    <div class="verdict-score">Composite Score: <strong>{composite_score:.2f} / 3.00</strong></div>
                </div>
            </div>
            
            <h2>7-Factor Analysis</h2>
            <table>
                <thead>
                    <tr>
                        <th>Factor</th>
                        <th>Live Value</th>
                        <th>Raw Score</th>
                        <th>Signal Meaning</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add factors to table
    for f in factors:
        score_val = f['score']
        html += f"""
                    <tr>
                        <td><strong>{f['name']}</strong></td>
                        <td>{f['value']}</td>
                        <td class="score-{score_val}">{score_val} / 3</td>
                        <td>{f['label']}</td>
                    </tr>
        """
        
    html += f"""
                </tbody>
            </table>
            
            <h2>Action Plan</h2>
            <div class="action-panel">
    """
    
    if deploy_pct > 0:
        html += f"""
                <div class="action-step">✅ <strong>Step 1:</strong> Log into Zerodha Coin, Groww, or your AMC portal immediately.</div>
                <div class="action-step">✅ <strong>Step 2:</strong> Redeem {deploy_pct}% of your Liquid Fund War-Chest.</div>
                <div class="action-step">✅ <strong>Step 3:</strong> {action}</div>
                <div class="action-step" style="color: #d63031; font-weight: bold; margin-top: 20px;">⚠️ CUT-OFF REMINDER: Execute your payment via UPI before 2:00 PM to lock in today's crashed NAV!</div>
        """
    else:
        html += f"""
                <div class="action-step">✋ {action}</div>
                <div class="action-step">Market conditions do not warrant a lump-sum deployment at this time. Wait for a stronger fear signal (VIX spike) or deeper technical correction.</div>
        """
        
    html += """
            </div>
    """

    # Only show recommended funds if there is an action to deploy
    if deploy_pct > 0:
        html += """
            <h2>Investigated Fund Recommendations</h2>
            <p style="color: #aaa; margin-bottom: 20px;">Based on your current action plan, deploy capital into these selected funds. These funds have been pre-screened for AUM stability, alpha generation, and correction resilience.</p>
            <div class="fund-grid">
        """
        
        # Decide which funds to show based on the action required
        funds_to_show = []
        if "Flexi-Cap" in action:
            funds_to_show.extend(RECOMMENDED_FUNDS["FLEXI"])
        if "Mid-Cap" in action:
            funds_to_show.extend(RECOMMENDED_FUNDS["MID"])
        if "Small-Cap" in action:
            funds_to_show.extend(RECOMMENDED_FUNDS["SMALL"])
            
        for fund in funds_to_show:
            html += f"""
                <div class="fund-card">
                    <div class="fund-header">
                        <h3 class="fund-name">{fund['name']}</h3>
                        <span class="fund-type">{fund['type']}</span>
                    </div>
                    <div class="fund-stats">
                        <div class="fund-stat-item">5Y CAGR: <strong>{fund['cagr']}</strong></div>
                        <div class="fund-stat-item">AUM: <strong>{fund['aum']}</strong></div>
                    </div>
                    <div class="fund-rationale">
                        <strong>Why buy on dip?</strong> {fund['rationale']}
                    </div>
                </div>
            """
            
        html += """
            </div>
        """
        
    # Always show Liquid funds as a reminder
    html += """
            <h2>War-Chest Maintenance</h2>
            <p style="color: #aaa; margin-bottom: 20px;">Keep your idle monthly SIP money parked here while waiting for the next market correction.</p>
            <div class="fund-grid">
    """
    for fund in RECOMMENDED_FUNDS["LIQUID"]:
        html += f"""
            <div class="fund-card" style="border-top: 4px solid #00b894;">
                <div class="fund-header">
                    <h3 class="fund-name">{fund['name']}</h3>
                    <span class="fund-type">{fund['type']}</span>
                </div>
                <div class="fund-stats">
                    <div class="fund-stat-item">1Y Return: <strong>{fund['cagr']}</strong></div>
                </div>
                <div class="fund-rationale">
                    <strong>Usage:</strong> {fund['rationale']}
                </div>
            </div>
        """
        
    html += """
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
        
    return filepath
