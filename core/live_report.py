import os
from datetime import datetime

def generate_live_report(all_results):
    """
    Generates an HTML report for Phase 2 Live Confirmation including Data Diagnostics.
    """
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%H:%M:%S')
    
    # Calculate Data Accuracy Stats
    total_scanned = len(all_results)
    confirmed_setups = [s for s in all_results if s['status'].startswith('CONFIRMED')]
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Phase 2: Live Market Confirmation - {date_str}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; color: #333; }}
        .header {{ background-color: #1e272e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #bdc3c7; }}
        .long-card {{ border-left-color: #27ae60; }}
        .short-card {{ border-left-color: #c0392b; }}
        .badge {{ padding: 5px 10px; border-radius: 4px; font-weight: bold; font-size: 0.9em; }}
        .bg-green {{ background-color: #d5f5e3; color: #27ae60; }}
        .bg-red {{ background-color: #fadbd8; color: #c0392b; }}
        .bg-yellow {{ background-color: #fcf3cf; color: #f1c40f; }}
        .bg-grey {{ background-color: #ebedef; color: #7f8c8d; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; }}
        .levels-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 15px; }}
        .level-box {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; border: 1px solid #e9ecef; }}
        .level-label {{ font-size: 0.85em; color: #6c757d; text-transform: uppercase; letter-spacing: 1px; }}
        .level-val {{ font-size: 1.4em; font-weight: bold; margin-top: 5px; color: #2c3e50; }}
        .entry-val {{ color: #0984e3; }}
        .diag-table {{ font-size: 0.9em; }}
        .diag-table td {{ padding: 8px; }}
    </style>
</head>
<body>

<div class="header">
    <h1>🎯 Phase 2: Live Market Confirmation</h1>
    <p>Generated on {date_str} at {time_str} | Scanned {total_scanned} stocks</p>
</div>

<div class="card">
    <h2>Data Availability & Diagnostics</h2>
    <p>Tracking the availability of real-time metrics across all {total_scanned} watchlist symbols.</p>
    <table class="diag-table">
        <tr>
            <th>Symbol</th>
            <th>Data Accuracy</th>
            <th>Missing Metrics</th>
            <th>Status / LTP</th>
            <th>VWAP</th>
            <th>OR Range</th>
            <th>Vol Spike</th>
            <th>Daily ATR</th>
        </tr>
"""

    for s in all_results:
        acc_color = "#27ae60" if "OK" in s['data_accuracy'] else ("#f1c40f" if "PARTIAL" in s['data_accuracy'] else "#c0392b")
        missing_str = ", ".join(s['missing_metrics']) if s['missing_metrics'] else "None"
        or_range_str = f"H:{s['or_high']} L:{s['or_low']}" if s['or_high'] != 'N/A' else 'N/A'
        
        html += f"""
        <tr>
            <td><strong>{s['symbol']}</strong></td>
            <td style="color:{acc_color}; font-weight:bold;">{s['data_accuracy']}</td>
            <td style="color:#7f8c8d; font-size:0.9em;">{missing_str}</td>
            <td>{s['status']} @ ₹{s['latest_close']}</td>
            <td>{s['vwap']}</td>
            <td>{or_range_str}</td>
            <td>{s['vol_mult']}x</td>
            <td>{s['atr']}</td>
        </tr>
        """
        
    html += """
    </table>
</div>

"""

    if not confirmed_setups:
        html += """
        <div class="card">
            <h2>No Confirmed Breakouts Yet</h2>
            <p>None of the stocks have triggered a valid Opening Range Breakout with VWAP and Volume confirmation.</p>
        </div>
        """
    else:
        for setup in confirmed_setups:
            direction = setup['direction']
            card_class = "long-card" if direction == "LONG" else "short-card"
            badge_class = "bg-green" if direction == "LONG" else "bg-red"
            
            levels = setup['levels']
            sizing = setup['sizing']
            
            acc_color = "#27ae60" if "OK" in setup['data_accuracy'] else "#f1c40f"
            
            html += f"""
            <div class="card {card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h2 style="margin: 0;">{setup['symbol']}</h2>
                    <div>
                        <span class="badge {badge_class}" style="margin-right:10px;">{setup['status']}</span>
                    </div>
                </div>
                
                <p><strong>Confirmed Breakout:</strong> {setup['breakout_time']} @ ₹{setup['breakout_price']} | <strong>Data Accuracy:</strong> <span style="color:{acc_color}; font-weight:bold;">{setup['data_accuracy']}</span></p>
                
                <div class="levels-grid">
                    <div class="level-box">
                        <div class="level-label">ENTRY PRICE</div>
                        <div class="level-val entry-val">₹{levels['entry']}</div>
                    </div>
                    <div class="level-box" style="border-color: #ff7675;">
                        <div class="level-label">STOP LOSS</div>
                        <div class="level-val" style="color: #d63031;">₹{levels['stop_loss']}</div>
                    </div>
                    <div class="level-box" style="border-color: #55efc4;">
                        <div class="level-label">TARGET 1 (1.5R)</div>
                        <div class="level-val" style="color: #00b894;">₹{levels['target_1']}</div>
                    </div>
                    <div class="level-box" style="border-color: #55efc4;">
                        <div class="level-label">TARGET 2 (2.5R)</div>
                        <div class="level-val" style="color: #00b894;">₹{levels['target_2']}</div>
                    </div>
                </div>
                
                <table>
                    <tr>
                        <th>OR High</th>
                        <th>OR Low</th>
                        <th>VWAP @ Breakout</th>
                        <th>Volume Spike</th>
                        <th>Daily ATR Used</th>
                    </tr>
                    <tr>
                        <td>₹{setup['or_high']}</td>
                        <td>₹{setup['or_low']}</td>
                        <td>₹{round(setup['vwap_at_breakout'], 2)}</td>
                        <td>{setup['volume_multiplier']}x Average</td>
                        <td>{setup['atr']}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 15px; padding: 15px; background: #eef2f5; border-radius: 6px;">
                    <strong>Position Sizing:</strong> Buy <strong>{sizing['quantity']} shares</strong> 
                    (Value: ₹{sizing['position_value']}) | Max Risk: ₹{sizing['max_loss']}
                    {f" <span style='color:#d63031;font-size:0.9em;'>(CAPPED AT MAX %)</span>" if sizing['capped'] else ""}
                </div>
            </div>
            """
            
    html += """
</body>
</html>
"""
    
    # Save the report
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "premarket_reports")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, f"Phase2_Confirmation_{date_str}.html")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    return report_path
