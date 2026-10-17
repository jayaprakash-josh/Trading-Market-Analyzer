# Trading Market Analyzer - Architecture Flow

This document outlines the dual-phase architecture of the NSE day-trading system.

```mermaid
graph TD
    %% Phase 1A: Overnight Pre-Market Analysis
    subgraph Phase 1A: Overnight Analyzer [premarket_1_overnight.py]
        A[Load WATCHLIST] --> B(Fetch Global Cues & FII/DII)
        B --> C{Multithreaded Stock Scan}
        
        C --> D[Fetch Technicals & Sector RS]
        C --> E[Fetch News Sentiment]
        
        D & E --> F[Quant Engine: Deterministic Bias]
        F --> G[Risk Filter: Hard Vetoes]
        G --> H[LLM News Catalyst Classifier]
        
        H --> I[(Save phase1a_overnight_results.json)]
        H --> J[Generate Overnight Report]
    end

    %% Phase 1B: Pre-Open Scanner
    subgraph Phase 1B: Pre-Open Scanner [premarket_2_preopen.py]
        K((9:00 AM Loop)) --> L[Load phase1a_overnight_results.json]
        L --> M{Scan Pre-Open Every 60s}
        
        M --> N[Fetch Live NSE IEP & Options PCR]
        N --> O[Re-calculate Quant Engine Score]
        O --> P[Final Bias: Bullish/Bearish/Wait]
        
        P --> Q[(Save phase1_results.json)]
        P --> R[Update Pre-Open Report]
        
        R --> S{Is time > 9:15 AM?}
        S -->|No| M
        S -->|Yes| T((Stop Pre-Open Scanner))
    end

    %% Phase 2: Live Market Confirmation
    subgraph Phase 2: Live Confirmation Engine [live_confirm.py]
        U1((Start 9:15 AM Loop)) --> V1[Load phase1_results.json]
        V1 --> W1{Scan Market Every 60s}
        
        W1 --> X1[Fetch Intraday 5m Candles]
        X1 --> Y1[Detect Opening Range 15m]
        Y1 --> Z1[Calculate Live VWAP]
        Z1 --> A2{Check Breakout?}
        
        A2 -->|Yes, Volume > 1.3x| B2[Load ATR from JSON]
        A2 -->|No| W1
        
        B2 --> C2[Calculate Stop Loss & Target]
        C2 --> D2[Calculate Position Sizing]
        D2 --> E2[Alert CONFIRMED Setup]
        E2 --> F2[Generate Live Report]
        
        F2 --> G2{Is time > 9:45 AM?}
        G2 -->|No| W1
        G2 -->|Yes| H2((Stop Scanner))
    end
    
    Q -.->|Handoff Pre-calculated Data| V1
```
