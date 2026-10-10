import json, os, math, time, urllib.parse, urllib.request, copy, threading, html, re
from datetime import datetime
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT=Path(__file__).parent
STATE=Path(os.environ.get('TRADING_RADAR_STATE_PATH',str(ROOT/'state.json')))
STATE.parent.mkdir(parents=True,exist_ok=True)
UNIVERSE=['AAPL','MSFT','NVDA','AMZN','META','GOOGL','AVGO','TSLA','AMD','NFLX','ORCL','CRM','ADBE','INTC','QCOM','TXN','MU','AMAT','LRCX','KLAC','PANW','CRWD','NOW','PLTR','UBER','ABNB','BKNG','JPM','BAC','GS','MS','V','MA','AXP','WMT','COST','HD','LOW','NKE','MCD','SBUX','KO','PEP','PG','JNJ','LLY','MRK','ABBV','UNH','XOM','CVX','CAT','GE','BA','RTX','DE','NEE','LIN','BTC/USD','ETH/USD','MNQ1!']
# Erweiterte US-Aktien-Auswahlliste. Kein Anspruch auf vollständige Börsenabdeckung.
DISCOVERY_SYMBOLS=['ADP', 'ABT', 'ACN', 'AEP', 'AFL', 'AIG', 'ALL', 'AME', 'AMP', 'AMT', 'ANET', 'AON', 'APD', 'APO', 'APP', 'APTV', 'ARE', 'ARM', 'ASML', 'ATO', 'AVB', 'AXP', 'AZN', 'BABA', 'BAX', 'BBY', 'BDX', 'BEN', 'BIIB', 'BLK', 'BMY', 'BNTX', 'BR', 'BRK.B', 'BSX', 'C', 'CAG', 'CARR', 'CB', 'CBOE', 'CDNS', 'CEG', 'CF', 'CHD', 'CHRW', 'CHTR', 'CI', 'CL', 'CLX', 'CMCSA', 'CME', 'CMI', 'CNC', 'COF', 'COP', 'COR', 'CPB', 'CPRT', 'CRH', 'CSCO', 'CSX', 'CTAS', 'CTSH', 'CTVA', 'CVS', 'CVX', 'D', 'DAL', 'DD', 'DELL', 'DG', 'DGX', 'DHI', 'DHR', 'DIS', 'DLR', 'DLTR', 'DOCU', 'DOV', 'DOW', 'DPZ', 'DRI', 'DTE', 'DUK', 'DVN', 'DXCM', 'EA', 'EBAY', 'ECL', 'ED', 'EFX', 'EL', 'EMR', 'ENPH', 'EOG', 'EQIX', 'EQR', 'EQT', 'ERIE', 'ES', 'ESS', 'ETN', 'EW', 'EXC', 'EXPD', 'EXPE', 'F', 'FANG', 'FAST', 'FCX', 'FDX', 'FE', 'FICO', 'FIS', 'FISV', 'FITB', 'FMC', 'FOXA', 'FSLR', 'FTNT', 'GD', 'GDDY', 'GILD', 'GIS', 'GL', 'GPN', 'GRMN', 'GWW', 'HAL', 'HAS', 'HBAN', 'HCA', 'HES', 'HIG', 'HLT', 'HOLX', 'HON', 'HPQ', 'HRL', 'HSY', 'HUM', 'HWM', 'IBM', 'ICE', 'IDXX', 'IEX', 'ILMN', 'INCY', 'IP', 'IPG', 'IQV', 'IR', 'IRM', 'ISRG', 'IT', 'ITW', 'IVZ', 'J', 'JAZZ', 'JBHT', 'JCI', 'JKHY', 'K', 'KDP', 'KEY', 'KEYS', 'KHC', 'KIM', 'KKR', 'KMB', 'KMI', 'KMX', 'KR', 'KVUE', 'LEN', 'LH', 'LKQ', 'LMT', 'LNT', 'LRCX', 'LVS', 'LW', 'LYB', 'LYV', 'MAR', 'MAS', 'MCHP', 'MCK', 'MCO', 'MDB', 'MDT', 'MET', 'MGM', 'MKC', 'MKTX', 'MLM', 'MMC', 'MMM', 'MO', 'MOS', 'MPC', 'MPWR', 'MRNA', 'MSI', 'MTB', 'MTCH', 'MTD', 'NDAQ', 'NDSN', 'NEM', 'NET', 'NOC', 'NRG', 'NSC', 'NTAP', 'NTRS', 'NUE', 'NVR', 'NWSA', 'O', 'ODFL', 'OKE', 'OMC', 'ON', 'ORLY', 'OTIS', 'OXY', 'PAYC', 'PAYX', 'PCAR', 'PCG', 'PEG', 'PFE', 'PFG', 'PH', 'PHM', 'PKG', 'PNC', 'PNR', 'PPG', 'PPL', 'PRU', 'PSA', 'PTC', 'PWR', 'PYPL', 'Q', 'RCL', 'REG', 'REGN', 'RF', 'RHI', 'RMD', 'ROK', 'ROL', 'ROP', 'ROST', 'RSG', 'RTO', 'RVTY', 'SBAC', 'SCHW', 'SHW', 'SJM', 'SLB', 'SMCI', 'SNA', 'SNPS', 'SO', 'SPG', 'SPGI', 'SRE', 'STE', 'STLD', 'STT', 'STX', 'STZ', 'SWK', 'SWKS', 'SYF', 'SYK', 'SYY', 'T', 'TAP', 'TDG', 'TDY', 'TECH', 'TEL', 'TER', 'TFC', 'TGT', 'TJX', 'TMO', 'TMUS', 'TPR', 'TRGP', 'TRMB', 'TROW', 'TRV', 'TSCO', 'TSN', 'TT', 'TTC', 'TTD', 'TYL', 'UAL', 'UDR', 'UHS', 'ULTA', 'UNP', 'UPS', 'URI', 'USB', 'VICI', 'VLO', 'VMC', 'VRSK', 'VRSN', 'VRTX', 'VTR', 'VTRS', 'VZ', 'WAB', 'WAT', 'WBA', 'WBD', 'WDC', 'WELL', 'WFC', 'WM', 'WMB', 'WMT', 'WRB', 'WST', 'WTW', 'WY', 'WYNN', 'XEL', 'XYL', 'YUM', 'ZBH', 'ZBRA', 'ZS']
DISCOVERY_UNIVERSE=list(dict.fromkeys(UNIVERSE+DISCOVERY_SYMBOLS))
KNOWN_NAMES={'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corporation', 'NVDA': 'NVIDIA Corporation', 'AMZN': 'Amazon.com Inc.', 'META': 'Meta Platforms Inc.', 'GOOGL': 'Alphabet Inc.', 'AVGO': 'Broadcom Inc.', 'TSLA': 'Tesla Inc.', 'AMD': 'Advanced Micro Devices Inc.', 'NFLX': 'Netflix Inc.', 'ORCL': 'Oracle Corporation', 'CRM': 'Salesforce Inc.', 'ADBE': 'Adobe Inc.', 'INTC': 'Intel Corporation', 'QCOM': 'Qualcomm Inc.', 'TXN': 'Texas Instruments Inc.', 'MU': 'Micron Technology Inc.', 'AMAT': 'Applied Materials Inc.', 'LRCX': 'Lam Research Corporation', 'KLAC': 'KLA Corporation', 'PANW': 'Palo Alto Networks Inc.', 'CRWD': 'CrowdStrike Holdings Inc.', 'NOW': 'ServiceNow Inc.', 'PLTR': 'Palantir Technologies Inc.', 'UBER': 'Uber Technologies Inc.', 'ABNB': 'Airbnb Inc.', 'BKNG': 'Booking Holdings Inc.', 'JPM': 'JPMorgan Chase & Co.', 'BAC': 'Bank of America Corporation', 'GS': 'Goldman Sachs Group Inc.', 'MS': 'Morgan Stanley', 'V': 'Visa Inc.', 'MA': 'Mastercard Incorporated', 'AXP': 'American Express Company', 'WMT': 'Walmart Inc.', 'COST': 'Costco Wholesale Corporation', 'HD': 'Home Depot Inc.', 'LOW': "Lowe's Companies Inc.", 'NKE': 'Nike Inc.', 'MCD': "McDonald's Corporation", 'SBUX': 'Starbucks Corporation', 'KO': 'Coca-Cola Company', 'PEP': 'PepsiCo Inc.', 'PG': 'Procter & Gamble Company', 'JNJ': 'Johnson & Johnson', 'LLY': 'Eli Lilly and Company', 'MRK': 'Merck & Co. Inc.', 'ABBV': 'AbbVie Inc.', 'UNH': 'UnitedHealth Group Incorporated', 'XOM': 'Exxon Mobil Corporation', 'CVX': 'Chevron Corporation', 'CAT': 'Caterpillar Inc.', 'GE': 'GE Aerospace', 'BA': 'Boeing Company', 'RTX': 'RTX Corporation', 'DE': 'Deere & Company', 'NEE': 'NextEra Energy Inc.', 'LIN': 'Linde plc', 'BTC/USD': 'Bitcoin / US-Dollar', 'ETH/USD': 'Ethereum / US-Dollar', 'MNQ1!': 'Micro E-mini Nasdaq-100 Future'}
DEFAULT={"cash":100.0,"start":100.0,"budget":100.0,"per_trade":20.0,"positions":[],"history":[],"watch":DISCOVERY_UNIVERSE,"key":"","auto":False,"last_auto_check":"Noch nie","next_auto_check":"–","scan_index":0,"scan_results":{},"scanned_total":0,"version":"V8.3.2","weak_trend_checks":{},"rocket_cooldown":{},"mnq_contracts":1,"event_log":[],"favorites":[],"names":KNOWN_NAMES.copy(),"alerts":[]}
def load():
    if not STATE.exists(): STATE.write_text(json.dumps(copy.deepcopy(DEFAULT),indent=2))
    d=json.loads(STATE.read_text())
    for k,v in DEFAULT.items(): d.setdefault(k,copy.deepcopy(v))
    # Neue Scanner-Werte aus Updates auch in bestehende state.json übernehmen.
    for sym in DISCOVERY_UNIVERSE:
        if sym not in d['watch']: d['watch'].append(sym)
    d.setdefault('names',{}).update({k:v for k,v in KNOWN_NAMES.items() if k not in d.get('names',{})})
    d['version']='V8.3.2'; d['mnq_contracts']=1
    for p in d.get('positions',[]):
        if p.get('symbol')=='MNQ1!': p.setdefault('contracts',4)
    return d

def save(d):
    tmp=STATE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(d,indent=2),encoding='utf-8')
    tmp.replace(STATE)
def effective_key(d):
    return os.environ.get('TWELVE_DATA_API_KEY','').strip() or d.get('key','').strip()

def td(path, key):
    url='https://api.twelvedata.com'+path+('&' if '?' in path else '?')+'apikey='+urllib.parse.quote(key)
    req=urllib.request.Request(url,headers={'User-Agent':'TradingRadar/1.6'})
    with urllib.request.urlopen(req,timeout=12) as r: return json.loads(r.read())

def quote_symbol(sym,key):
    # TradingView nennt den fortlaufenden Micro-E-mini-Nasdaq-100-Future MNQ1!.
    # Twelve Data listet Futures derzeit nicht in seinen normalen Referenzlisten;
    # deshalb nutzen wir fuer diesen einen Paper-Wert den Yahoo-Frontmonat MNQ=F.
    if sym=='MNQ1!':
        url='https://query1.finance.yahoo.com/v8/finance/chart/MNQ=F?interval=15m&range=5d'
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 TradingRadar/1.6'})
        with urllib.request.urlopen(req,timeout=12) as r: q=json.loads(r.read())
        try:
            closes=[float(x) for x in q['chart']['result'][0]['indicators']['quote'][0]['close'] if x is not None]
        except Exception:
            return {'symbol':sym,'error':'MNQ-Marktdaten derzeit nicht verfuegbar'}
        vals=[{'close':str(x)} for x in closes[-30:][::-1]]
    else:
        q=td('/time_series?symbol='+urllib.parse.quote(sym)+'&interval=15min&outputsize=30&timezone=UTC',key)
        vals=q.get('values',[])
    if not vals: return {'symbol':sym,'error':q.get('message','Keine Marktdaten erhalten')[:120]}
    closes=[float(x['close']) for x in vals][::-1]
    if len(closes)<15: return {'symbol':sym,'error':'Zu wenige Kursdaten'}
    # Zeitpunkt der letzten Börsenkerze, nicht bloß Zeitpunkt der API-Abfrage.
    candle_ts=None
    if sym!='MNQ1!':
        try:
            from datetime import timezone
            candle_ts=datetime.fromisoformat(vals[0]['datetime'].replace('Z','+00:00'))
            if candle_ts.tzinfo is None: candle_ts=candle_ts.replace(tzinfo=timezone.utc)
            candle_ts=candle_ts.timestamp()
        except (KeyError,ValueError,TypeError,OverflowError): pass
    else:
        # MNQ ist nur Beobachtungswert, ohne geprüfte Kerzenzeit.
        candle_ts=None
    p=closes[-1]; ma5=sum(closes[-5:])/5; ma15=sum(closes[-15:])/15
    mom=(p/closes[-6]-1)*100
    rets=[closes[i]/closes[i-1]-1 for i in range(1,len(closes))]
    vol=(sum((x-sum(rets)/len(rets))**2 for x in rets)/max(1,len(rets)-1))**.5*100
    score=50+(12 if p>ma5 else -12)+(12 if ma5>ma15 else -12)+max(-16,min(16,mom*2))-min(12,vol*2)
    score=max(0,min(100,round(score)))
    risk='Niedrig' if vol<2 else ('Mittel' if vol<4 else 'Hoch')
    signal='KAUFEN' if score>=75 else ('BEOBACHTEN' if score>=55 else 'MEIDEN')
    return add_momentum_labels({'symbol':sym,'price':p,'score':score,'risk':risk,'signal':signal,'mom':round(mom,2),'vol':round(vol,2),'seen':time.time(),'candle_ts':candle_ts}, closes)


def log_event(d, text, kind='INFO'):
    d.setdefault('event_log', []).append({
        'time': berlin_now().strftime('%d.%m.%Y %H:%M:%S'),
        'kind': kind,
        'text': text
    })
    d['event_log'] = d['event_log'][-300:]

def add_momentum_labels(x, closes):
    """Früherkennung: DIP -> Umkehr -> Ausbruch aus dem Keller."""
    if len(closes) < 15:
        return x
    recent = closes[-15:]
    low = min(recent)
    high = max(recent)
    p = closes[-1]
    prev = closes[-2]
    ma5 = sum(closes[-5:]) / 5
    ma10 = sum(closes[-10:]) / 10
    recovery = ((p / low) - 1) * 100 if low else 0
    range_pct = ((high / low) - 1) * 100 if low else 0

    stage = ''
    # DIP: nahe dem 15-Kerzen-Tief, aber erste Stabilisierung.
    if p <= low * 1.015 and p >= prev:
        stage = 'DIP'
    # FRÜHSIGNAL: klar vom Tief gelöst + kurzfristige Umkehr.
    if recovery >= 1.0 and p > ma5 and p > prev:
        stage = 'FRÜHSIGNAL'
    # AUSBRUCH: kräftige Erholung aus einem vorher breiten Tiefbereich.
    if recovery >= 2.5 and range_pct >= 3.0 and p > ma5 > ma10:
        stage = '🚀 AUSBRUCH AUS DEM KELLER'

    x['stage'] = stage
    x['recovery'] = round(recovery, 2)
    x['chart'] = [round(v, 5) for v in closes[-30:]]
    if stage == '🚀 AUSBRUCH AUS DEM KELLER':
        x['score'] = max(x.get('score', 0), 80)
        x['signal'] = 'KAUFEN'
    elif stage == 'FRÜHSIGNAL':
        x['score'] = max(x.get('score', 0), 65)
        if x['signal'] == 'MEIDEN':
            x['signal'] = 'BEOBACHTEN'
    return x

def market(d):
    key=effective_key(d)
    if not key: return []
    held=[p['symbol'] for p in d.get('positions',[])]
    universe=d.get('watch') or DISCOVERY_UNIVERSE
    # Basic Twelve Data accounts are easily rate-limited. Keep each cycle at max. 7 requests.
    slots=max(1,7-len(set(held)))
    i=int(d.get('scan_index',0))%len(universe)
    batch=[]
    while len(batch)<slots and len(batch)<len(universe):
        s=universe[i%len(universe)]; i+=1
        if s not in held and s not in batch: batch.append(s)
    symbols=list(dict.fromkeys(held+batch))[:7]
    results=dict(d.get('scan_results',{}))
    for sym in symbols:
        try:
            x=quote_symbol(sym,key)
            if 'price' not in x: raise ValueError(x.get('error','Kein Kurs verfügbar'))
            results[sym]=x
        except Exception as e:
            old=results.get(sym,{})
            # Alten Kurs zur Anzeige behalten, aber Fehler sichtbar machen und nie als frisch deklarieren.
            results[sym]={**old,'symbol':sym,'fetch_error':str(e)[:120], 'failed_at':time.time()}
    d['scan_index']=i%len(universe); d['scan_results']=results
    d['scanned_total']=len([x for x in results.values() if 'price' in x])
    for x in results.values():
        if x.get('stage') in ('FRÜHSIGNAL','🚀 AUSBRUCH AUS DEM KELLER') and x.get('seen',0)>time.time()-1800:
            k=x['symbol']+':'+x['stage']
            if not any(a.get('key')==k for a in d.get('alerts',[])[-60:]):
                d.setdefault('alerts',[]).append({'key':k,'symbol':x['symbol'],'stage':x['stage'],'time':berlin_now().strftime('%d.%m.%Y %H:%M')})
    d['alerts']=d.get('alerts',[])[-100:]
    # Keep recent successful candidates; held positions always stay visible.
    vals=list(results.values())
    good=[x for x in vals if 'price' in x]
    errs=[x for x in vals if 'error' in x and x.get('symbol') in symbols]
    return sorted(good,key=lambda x:(x.get('seen',0)>time.time()-1800,x.get('stage')=='🚀 AUSBRUCH AUS DEM KELLER',x.get('stage')=='FRÜHSIGNAL',x.get('mom',0),x.get('score',-1)),reverse=True)[:25]+errs

def portfolio(d, quotes):
    qmap={x['symbol']:x for x in quotes if 'price' in x}
    val=d['cash']; rows=[]; grouped={}
    for pos in d['positions']:
        sym=pos['symbol']
        if sym not in grouped:
            grouped[sym]={'symbol':sym,'qty':0.0,'cost':0.0,'buys':0}
        g=grouped[sym];g['qty']+=pos['qty'];g['cost']+=pos['cost'];g['buys']+=1
    for sym,pos in grouped.items():
        entry=pos['cost']/pos['qty'] if pos['qty'] else 0
        q=qmap.get(sym,{})
        price=q.get('price',entry)
        age=int(max(0,time.time()-float(q.get('seen',0) or 0))) if q.get('seen') else None
        candle_age=int(max(0,time.time()-float(q.get('candle_ts',0) or 0))) if q.get('candle_ts') else None
        reliable=age is not None and age<=900 and candle_age is not None and candle_age<=1800 and not q.get('fetch_error')
        cur=pos['qty']*price if sym!='MNQ1!' else pos['cost']
        pnl=cur-pos['cost'];val+=cur
        pct=(cur/pos['cost']-1)*100 if pos['cost'] and sym!='MNQ1!' else 0
        score=q.get('score')
        if sym=='MNQ1!':decision,reason='HALTEN','MNQ-Abrechnung ausgesetzt'
        elif not reliable:decision,reason='DATEN FEHLEN','Keine ausreichend frischen Börsenkurse – Automatik gesperrt'
        elif pct<=-4:decision,reason='VERKAUFEN',f'Stop-Loss erreicht ({pct:+.2f} %)'
        elif pct>=7:decision,reason='VERKAUFEN',f'Gewinnziel erreicht ({pct:+.2f} %)'
        elif score is not None and score<45:
            confirmed=d.get('weak_trend_checks',{}).get(sym,0)>=2
            decision,reason=('VERKAUFEN',f'Score {score}, Abwärtstrend zweimal bestätigt') if confirmed else ('BEOBACHTEN',f'Score {score} niedrig – Trendbestätigung abwarten')
        elif score is None:decision,reason='HALTEN','Noch keine aktuelle Scanner-Prüfung'
        else:decision,reason='HALTEN',f'Score {score}, Ergebnis {pct:+.2f} %'
        seen=q.get('seen')
        checked=datetime.fromtimestamp(seen,ZoneInfo('Europe/Berlin')).strftime('%d.%m. %H:%M') if seen else '–'
        rows.append({**pos,'entry':entry,'price':price,'value':cur,'pnl':pnl,'pnlpct':pct,'score':score,'decision':decision,'reason':reason,'checked':checked,'cost':pos['cost'],'data_ok':reliable,'age_seconds':age,'candle_age_seconds':candle_age,'fetch_error':q.get('fetch_error'),'has_quote':bool(q)})
    rows.sort(key=lambda x:x['pnlpct'],reverse=True)
    return val,rows

HTML=r"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trading Radar</title><style>
body{font-family:system-ui;background:#07111f;color:#eaf1ff;margin:0}header{padding:18px 5%;background:#0c1b2d;position:sticky;top:0}.wrap{max-width:1550px;margin:auto;padding:22px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}.card{background:#102238;border:1px solid #203b5b;border-radius:16px;padding:16px;margin-bottom:14px}.big{font-size:28px;font-weight:800}.green{color:#42df91}.red{color:#ff6677}.yellow{color:#ffd15c}button,input{font:inherit;border-radius:10px;padding:10px;border:1px solid #34506d}button{background:#19b873;color:white;font-weight:700;cursor:pointer}.danger{background:#c53e50}.muted{color:#9db0c7}.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.trade{display:grid;grid-template-columns:1.2fr .8fr .8fr .8fr .8fr;gap:8px;padding:10px 0;border-top:1px solid #233c58}#status{margin-top:10px;font-weight:700}@media(max-width:700px){.trade{grid-template-columns:1fr 1fr}.hideM{display:none}}
nav.tabs{display:flex;gap:9px;overflow-x:auto;margin:18px 0 14px;padding-bottom:6px}button.tab{background:#14263b;color:#c3d4e7;border:1px solid #2c4661;white-space:nowrap;padding:13px 17px}button.tab.active{background:#0869d5;border-color:#27d39a;color:#fff}.controlbar{display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:#10283d}.controlbar strong{font-size:23px;color:#42df91;font-variant-numeric:tabular-nums}.statusline{padding:10px 14px;margin:10px 0 14px;background:#0f2134;border-radius:10px}.kpis .card{background:linear-gradient(145deg,#142c46,#0e1d30);min-height:86px}.kpis .big{margin-top:8px}header{z-index:10;border-bottom:1px solid #294560}button:hover{filter:brightness(1.13)}[data-tab]{display:none}[data-tab].visible{display:block}.trade{line-height:1.5}@media(max-width:700px){.wrap{padding:12px}.controlbar{justify-content:flex-start}.tabs{position:sticky;top:56px;background:#07111f;z-index:9}}.price-up{color:#22c55e;font-weight:700}.price-down{color:#ef4444;font-weight:700}.price-flat{color:inherit;font-weight:700}</style><style>.kpis{grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}.kpis .card{margin-bottom:0}.dashboard-grid{grid-template-columns:minmax(0,2.1fr) minmax(290px,1fr);gap:16px;align-items:start}.dashboard-grid.visible{display:grid}.dash-main,.dash-side{min-width:0}.panel-title{display:flex;justify-content:space-between;align-items:center;gap:12px}.panel-title h3{margin:4px 0 14px}.panel-title select{background:#132a43;color:#eaf1ff;border:1px solid #35516c;border-radius:9px;padding:8px}.holdings{width:100%;border-collapse:collapse;font-size:13px;white-space:nowrap}.holdings th{text-align:left;font-size:12px;color:#c6d4e8;font-weight:500;padding:13px 9px;border-bottom:1px solid #29435b}.holdings td{padding:13px 9px;border-bottom:1px solid #29435b;vertical-align:middle}.holdings small{display:block;color:#9db0c7}.holdings button{padding:8px 9px;font-size:12px;background:#0869d5}.holdings button.danger{background:#c83c4d}.holdings .signal{border-radius:7px;background:#145c43;padding:7px;color:#d6ffe7;display:inline-block}.holdings .signal.warning{background:#775a1e;color:#ffe6a2}.holdings .signal.sell{background:#8c273b;color:#fff}.table-scroll{overflow-x:auto}.fine{font-size:12px}.dash-bottom{display:grid;grid-template-columns:1fr 1fr;gap:14px}.quick-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px}.quick-actions button{font-size:13px;padding:13px 8px}button.secondary{background:#182e49;border:1px solid #365574}.linkbutton{background:transparent;color:#55a9ff;font-weight:500;padding:5px;border:0}.preview-row{display:grid;grid-template-columns:1.2fr .9fr .5fr auto;gap:8px;align-items:center;padding:12px 0;border-bottom:1px solid #29435b;font-size:13px}.preview-row small{color:#9db0c7;display:block}.preview-row button{font-size:12px;padding:8px;background:#0b9b59}.activity-row{padding:11px 0;border-bottom:1px solid #29435b;font-size:12px}.activity-row .green,.activity-row .red{font-weight:700}@media(max-width:1050px){.kpis{grid-template-columns:repeat(3,minmax(0,1fr))}.dashboard-grid.visible{grid-template-columns:1fr}}@media(max-width:620px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.dash-bottom{grid-template-columns:1fr}.panel-title{flex-wrap:wrap}}</style></head><body><header><b>📈 Trading Radar V8.3.2</b> <span class="muted">Paper-Trading · kein Echtgeld</span></header><div class="wrap">
<nav class="tabs" aria-label="Bereiche"><button class="tab active" onclick="showTab('depot')">📊 Depot</button><button class="tab" onclick="showTab('scanner')">🔎 Top-Chancen</button><button class="tab" onclick="showTab('rocket')">🚀 Raketen-Radar</button><button class="tab" onclick="showTab('log')">📋 Protokoll</button><button class="tab" onclick="showTab('settings')">⚙️ Einstellungen</button></nav>
<div class="card controlbar"><span>Automatik: <b id="quickAuto">AUS</b></span><button onclick="toggleAuto()">Automatik AN / AUS</button><span>Prüfung in <strong id="countdown">--:--</strong></span><span id="freshness">Kurse noch nicht geprüft</span><span id="quickScan">Scanner –</span></div>
<div id="status" class="muted statusline">Bereit.</div>
<div class="grid kpis"><div class="card">Depotwert<div id="value" class="big">–</div><span id="pnl"></span></div><div class="card">Freies Kapital<div id="cash" class="big">–</div></div><div class="card">Offene Positionen<div id="count" class="big">–</div></div><div class="card">Gesamtergebnis<div id="totalResult" class="big">–</div></div><div class="card">Automatik<div id="auto" class="big">AUS</div><small id="nextMini">–</small></div></div>
<div class="card" data-tab="settings"><h3>Einstellungen</h3><div class="row"><input id="key" type="password" placeholder="Twelve Data API-Key"><button onclick="setKey()">API-Key speichern</button><label>Budget € <input id="budget" type="number" value="100" style="width:75px"></label><label>pro Trade € <input id="per" type="number" value="20" style="width:70px"></label><button onclick="settings()">Speichern</button><button onclick="toggleAuto()">Automatik AN/AUS</button><button class="danger" onclick="resetAll()">Test zurücksetzen</button></div><p class="muted">Die App handelt nur virtuell. Tipp: Hinterlege TWELVE_DATA_API_KEY später einmal bei Render; dann bleibt der Schlüssel bei Updates erhalten. Trades werden zusätzlich in diesem Browser gesichert und nach einem Deploy automatisch wiederhergestellt.</p><p class="muted">Automatik-Scanner: rund um die Uhr, alle 15 Minuten. Aktienorders nur mit ausreichend frischen Kursdaten; außerhalb der Börsenzeiten können Kursdaten fehlen. Auf dem kostenlosen Render-Tarif kann der Dienst bei Inaktivität schlafen; solange diese Seite geöffnet ist, stößt sie die Prüfung regelmäßig an.</p><div class="row"><span>Letzte automatische Prüfung: <b id="lastcheck">–</b></span><span>Nächste Prüfung: <b id="nextcheck">–</b></span></div></div>
<div class="card" data-tab="settings"><h3>Virtuelles Kapital verwalten</h3>
<p class="muted">Ein- und Auszahlungen ändern nur dein freies virtuelles Kapital. Offene Trades bleiben bestehen. Das Handelsbudget wird separat eingestellt.</p>
<div class="row"><label>Betrag € <input id="capitalAmount" type="number" min="0.01" step="0.01" value="100" style="width:115px"></label>
<button onclick="changeCapital('deposit')">+ Einzahlen</button>
<button onclick="changeCapital('withdraw')">− Entnehmen</button></div>
<p class="muted">Startkapital für die Gewinnberechnung anpassen, ohne offene Trades zu schließen:</p>
<div class="row"><label>Neues Startkapital € <input id="newStart" type="number" min="0" step="0.01" value="100" style="width:115px"></label>
<button onclick="changeCapital('start')">Startkapital ändern</button></div></div>
<div class="card" data-tab="scanner"><h3>Markt-Scanner · Top-Chancen</h3><p class="muted">Rotierender Scanner: pro Prüfung wird ein neuer Teil der Beobachtungsliste analysiert, um das API-Limit einzuhalten. Bereits geprüfte Kandidaten bleiben im Ranking. MNQ wird weiterhin beobachtet. Erweiterte Aktienliste, rotierend und API-schonend; keine vollständige Echtzeit-Marktabdeckung. Frühwarnstufen: DIP → FRÜHSIGNAL → 🚀 AUSBRUCH AUS DEM KELLER.</p><div id="scaninfo" class="muted"></div><div id="radar">API-Key eintragen und „Markt aktualisieren“ drücken.</div><br><button id="refreshBtn" onclick="refreshMarket()">Markt aktualisieren</button></div>
<div class="card" data-tab="scanner"><h3>Aktie suchen und virtuell kaufen</h3><p class="muted">Kürzel oder Firmenname suchen; Kauf nur mit verfügbaren Kursdaten. Keine Echtgeld-Orders.</p><div class="row"><input id="stockSearch" placeholder="z. B. NVDA oder NVIDIA" style="min-width:220px"><button onclick="searchStock()">Suchen</button></div><div id="searchResult" class="muted"></div></div>
<div class="card" data-tab="scanner"><h3>⭐ Meine Beobachtungsliste</h3><div id="favorites"></div></div>
<div class="card" data-tab="rocket"><h3>🚀 Raketen-Radar und Frühwarnungen</h3><p class="muted">Heuristische Hinweise, keine zuverlässige Vorhersage. Kursveränderungen basieren auf 15-Minuten-Kerzen.</p><div id="alerts"></div></div>
<div class="card" data-tab="scanner"><h3>📈 Kursverlauf</h3><div id="chartTitle" class="muted">Aktie im Scanner anklicken.</div><svg id="priceChart" viewBox="0 0 600 180" style="width:100%;max-height:220px;background:#081525;border-radius:12px"></svg></div>
<section data-tab="depot" class="dashboard-grid"><div class="dash-main"><div class="card"><div class="panel-title"><h3>Mein Depot (<span id="depotCount">0</span> Positionen)</h3><label>Sortierung: <select id="depotSort" onchange="render(S)"><option value="pnl">Gewinn/Verlust</option><option value="name">Aktie</option><option value="score">Score</option></select></label></div><div class="table-scroll"><table class="holdings"><thead><tr><th>Aktie</th><th>Kurs</th><th>Einstieg</th><th>Käufe</th><th>Investiert</th><th>Aktueller Wert</th><th>G/V (€)</th><th>G/V (%)</th><th>Score</th><th>Empfehlung</th><th>Aktion</th></tr></thead><tbody id="positions"></tbody></table></div><p class="muted fine">Gewinnmitnahme +7 % · Stop-Loss −4 % · Score unter 45 nur mit bestätigtem Abwärtstrend. Alle Trades virtuell.</p></div><div class="dash-bottom"><div class="card"><h3>Marktüberblick</h3><div id="marketOverview"></div></div><div class="card"><h3>Schnelle Aktionen</h3><div class="quick-actions"><button onclick="showTab('settings')">＋ Virtuell einzahlen</button><button class="danger" onclick="showTab('settings')">－ Virtuell entnehmen</button><button class="secondary" onclick="exportBackup()">⇩ Sicherung herunterladen</button><button class="secondary" onclick="showTab('log')">⇧ Sicherung wiederherstellen</button></div></div></div><div class="card"><h3>Statistik abgeschlossener Trades</h3><div id="stats"></div></div></div><aside class="dash-side"><div class="card"><div class="panel-title"><h3>Top-Chancen</h3><button class="linkbutton" onclick="showTab('scanner')">Mehr anzeigen →</button></div><div id="topPreview"></div></div><div class="card"><div class="panel-title"><h3>Letzte Aktivitäten</h3><button class="linkbutton" onclick="showTab('log')">Mehr anzeigen →</button></div><div id="recentPreview"></div></div></aside></section>
<div class="card" data-tab="log"><h3>Protokoll</h3><div class="row"><input id="restoreFile" type="file" accept=".json,application/json"><button onclick="importBackup()">Sicherung wiederherstellen</button></div><p class="muted">Wichtig: Erst eine aktuelle Sicherung herunterladen. Wiederherstellen ersetzt Depot, Trades und Protokoll durch die ausgewählte Sicherung.</p><button onclick="exportBackup()">Sicherung herunterladen</button><p class="muted">Bitte Sicherung vor jedem Update herunterladen. Render Free speichert Daten nicht dauerhaft.</p><h4>Käufe und Verkäufe (neueste zuerst)</h4><div id="history" class="muted"></div><hr><h4>Systemereignisse</h4><div id="events" class="muted"></div></div>
</div><script>
let S={}; let SEARCH=null; let activeTab='depot';
function showTab(t){activeTab=t;document.querySelectorAll('[data-tab]').forEach(e=>e.classList.toggle('visible',e.dataset.tab===t));document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.getAttribute('onclick')==="showTab('"+t+"')"));}
let autoCheckRunning=false, lastCheckAttempt=0;
function countdownTick(){
 const el=document.getElementById('countdown');if(!el)return;
 if(!S.auto){el.textContent='AUS';return}
 if(autoCheckRunning){el.textContent='Prüfung läuft …';return}
 if(!S._last_auto_ts){el.textContent='Prüfung bereit';return}
 const seconds=Math.max(0,Math.ceil(S._last_auto_ts+900-Date.now()/1000));
 if(seconds===0){el.textContent='Prüfung fällig';return}
 el.textContent=String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');
}
setInterval(countdownTick,1000);
async function api(path,opt){
  let r=await fetch(path,opt);
  let data=await r.json();
  if(data.error) throw new Error(data.error);
  return data;
}
function esc(x){return String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function euro(x){return Number(x).toLocaleString('de-DE',{style:'currency',currency:'EUR'})}
function msg(t,bad=false){status.textContent=t;status.className=bad?'red':'green'}
function backupState(s){try{localStorage.setItem('tradingRadarBackupV6',JSON.stringify({favorites:s.favorites,names:s.names,alerts:s.alerts,cash:s.cash,start:s.start,budget:s.budget,per_trade:s.per_trade,positions:s.positions,history:s.history,auto:s.auto,event_log:s.event_log,scan_results:s.scan_results,scan_index:s.scan_index}))}catch(e){}}
async function load(){try{S=await api('/api/state');let raw=localStorage.getItem('tradingRadarBackupV6');if(raw&&S.positions.length===0&&S.history.length===0){let b=JSON.parse(raw);if((b.positions&&b.positions.length)||(b.history&&b.history.length)){S=await api('/api/restore',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({backup:b})})}}render(S);backupState(S)}catch(e){msg('Fehler: '+e.message,true)}}
function render(s){
 backupState(s);
 value.textContent=euro(s.value);let pp=s.value-s.start;pnl.textContent=(pp>=0?'+':'')+euro(pp)+' seit Start';pnl.className=pp>=0?'green':'red';cash.textContent=euro(s.cash);count.textContent=s.position_rows.length;auto.textContent=s.auto?'AN':'AUS';auto.className='big '+(s.auto?'green':'red');budget.value=s.budget;per.value=s.per_trade;document.getElementById('newStart').value=s.start;lastcheck.textContent=s.last_auto_check||'Noch nie';nextcheck.textContent=s.next_auto_check||'–';quickAuto.textContent=s.auto?'AN':'AUS';quickAuto.className=s.auto?'green':'red';quickScan.textContent='Geprüfte Werte: '+(s.scanned_total||0)+' / '+(s.watch?.length||0);freshness.textContent=(s.position_rows||[]).some(x=>!x.data_ok)?'⚠️ Einige Kurse veraltet':'✓ Positionskurse aktuell';countdownTick();showTab(activeTab);
 scaninfo.textContent='Analysierte Werte im aktuellen Scan-Speicher: '+(s.scanned_total||0)+' / '+(s.watch?.length||0)+' · API-Key: '+(s.api_key_source||'–');
  const stocks=(s.market||[]);
  radar.innerHTML=stocks.length?stocks.map(x=>x.error?`<div class="trade"><b>${esc(x.symbol)}</b><span class="red">Fehler</span><span>${esc(x.error)}</span></div>`:`<div class="trade"><b title="${esc((s.names||{})[x.symbol]||x.symbol)}" style="cursor:help">${esc(x.symbol)}</b><span>${euro(x.price)}</span><span class="${x.score>=75?'green':x.score>=55?'yellow':'red'}">${x.score}/100</span><span>${esc(x.risk)} · ${Number(x.mom||0).toFixed(2)}% / 75 Min.</span><span><b>${esc(x.signal)}</b><small>${esc(x.stage||'')}</small><div class="row"><button onclick="buy('${esc(x.symbol)}')" ${x.symbol==='MNQ1!'?'disabled':''}>Virtuell kaufen</button><button onclick="favorite('${esc(x.symbol)}')">${(s.favorites||[]).includes(x.symbol)?'★':'☆'}</button><button onclick="chart('${esc(x.symbol)}')">Chart</button></div></span></div>`).join(''):'Noch keine Marktdaten.';
  favorites.innerHTML=(s.favorites||[]).map(x=>`<span style="display:inline-block;margin:5px"><b title="${esc((s.names||{})[x]||x)}">${esc(x)}</b> <button onclick="favorite('${esc(x)}')">Entfernen</button> <button onclick="chart('${esc(x)}')">Chart</button></span>`).join('')||'Noch keine Favoriten.';
  alerts.innerHTML=(s.alerts||[]).slice(-12).reverse().map(x=>`<div>${esc(x.time)} · <b>${esc(x.symbol)}</b> · ${esc(x.stage)}</div>`).join('')||'Noch keine neuen Frühwarnungen.';
  const closed=(s.history||[]).filter(x=>typeof x.pnl==='number'); const wins=closed.filter(x=>x.pnl>0);const net=closed.reduce((a,x)=>a+x.pnl,0);
  stats.textContent=closed.length?`${closed.length} abgeschlossene Trades · ${wins.length} Gewinne · Trefferquote ${(100*wins.length/closed.length).toFixed(1)} % · Ergebnis ${euro(net)}`:'Noch keine abgeschlossenen Trades mit Ergebnisdaten.';

 const rows=[...(s.position_rows||[])]; const sortBy=document.getElementById('depotSort').value;
 if(sortBy==='name')rows.sort((a,b)=>a.symbol.localeCompare(b.symbol)); else if(sortBy==='score')rows.sort((a,b)=>(b.score??-1)-(a.score??-1));else rows.sort((a,b)=>b.pnlpct-a.pnlpct);
 depotCount.textContent=rows.length;
 positions.innerHTML=rows.length?rows.map(x=>`<tr><td><b>${esc(x.symbol)}</b><small>${esc((s.names||{})[x.symbol]||'')}</small></td><td>${euro(x.price)}${!x.data_ok?'<small class="yellow">Kurs ungeprüft</small>':''}</td><td>${euro(x.entry)}</td><td>${x.buys||1}</td><td>${euro(x.cost)}</td><td>${euro(x.value)}</td><td class="${x.pnl>=0?'green':'red'}">${euro(x.pnl)}</td><td class="${x.pnlpct>=0?'green':'red'}">${x.pnlpct.toFixed(2)}%</td><td>${x.score??'–'}</td><td><span class="signal ${x.decision==='VERKAUFEN'?'sell':x.decision==='BEOBACHTEN'?'warning':''}" title="${esc(x.reason)}">${esc(x.decision)}</span><small title="${esc(x.reason)}">${esc(x.reason).slice(0,44)}</small></td><td><button onclick="buy('${esc(x.symbol)}')">Kaufen</button> <button class="danger" onclick="sell('${esc(x.symbol)}')">Verkaufen</button> <button class="secondary" onclick="partialSell('${esc(x.symbol)}')">Teilweise</button></td></tr>`).join(''):'<tr><td colspan="11">Keine offenen virtuellen Positionen.</td></tr>';
 totalResult.textContent=(pp>=0?'+':'')+euro(pp);totalResult.className='big '+(pp>=0?'green':'red');nextMini.textContent=s.next_auto_check||'–';
 const candidates=Object.values(s.scan_results||{}).filter(x=>x&&x.price&&x.score!=null&&x.symbol!=='MNQ1!').sort((a,b)=>b.score-a.score).slice(0,5);
 topPreview.innerHTML=candidates.length?candidates.map(x=>`<div class="preview-row"><div><b>${esc(x.symbol)}</b><small>${esc((s.names||{})[x.symbol]||'')}</small></div><span>${euro(x.price)}</span><b class="${x.score>=75?'green':'yellow'}">${x.score}</b><button onclick="buy('${esc(x.symbol)}')">Kaufen</button></div>`).join(''):'Noch keine geprüften Top-Chancen.';
 const recent=(s.history||[]).filter(x=>/KAUF|VERKAUF|TEILVERKAUF/.test(x.text||'')).slice(-5).reverse();
 recentPreview.innerHTML=recent.length?recent.map(x=>`<div class="activity-row"><span>${esc(x.time)} · </span><b class="${/VERKAUF/.test(x.text)?'red':'green'}">${/VERKAUF/.test(x.text)?'Verkauf':'Kauf'}</b> · ${esc(x.text||'')}</div>`).join(''):'Noch keine Trades.';
 marketOverview.textContent='Analysierte Werte: '+(s.scanned_total||0)+' von '+(s.watch?.length||0)+' · Weitere Kurse im Reiter Top-Chancen.';
 document.getElementById('history').innerHTML=(s.history||[]).filter(x=>/KAUF|VERKAUF|TEILVERKAUF/.test(x.text||'')).slice().reverse().slice(0,80).map(x=>`<div>${esc(x.time)} · ${esc(x.text)}</div>`).join('')||'Noch keine Trades.'; document.getElementById('events').innerHTML=[...(s.event_log||[]).filter(x=>x.kind!=='TRADE'),...(s.history||[]).filter(x=>!/KAUF|VERKAUF|TEILVERKAUF/.test(x.text||'')).map(x=>({...x,kind:'KAPITAL / SYSTEM'}))].slice().reverse().slice(0,80).map(x=>`<div>${esc(x.time)} · ${esc(x.kind)} · ${esc(x.text)}</div>`).join('')||'Noch keine Systemereignisse.';
}
function exportBackup(){const a=document.createElement('a');const data={...S,key:undefined,market:undefined,position_rows:undefined};const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});a.href=URL.createObjectURL(blob);a.download='trading-radar-sicherung-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
async function importBackup(){
 const f=document.getElementById('restoreFile').files[0];
 if(!f){msg('Bitte zuerst die Wiederherstellungsdatei auswählen.',true);return}
 if(!confirm('Depot, Trades und Protokoll durch diese Sicherung ersetzen? Vorher bitte die aktuelle Sicherung herunterladen.'))return;
 try{
   const b=JSON.parse(await f.text());
   S=await api('/api/import-backup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({backup:b})});
   render(S);msg('Sicherung wiederhergestellt. Bitte Positionen und Kapital prüfen.');
 }catch(e){msg('Wiederherstellung fehlgeschlagen: '+e.message,true)}
}
async function refreshMarket(){
 let b=document.getElementById('refreshBtn'); b.disabled=true; b.textContent='Aktualisiere …'; msg('Marktdaten werden geladen …');
 try{S=await api('/api/refresh',{method:'POST'});render(S);msg(S.auto?'Markt aktualisiert – Automatik wurde geprüft.':'Markt aktualisiert.')}
 catch(e){msg('Fehler beim Aktualisieren: '+e.message,true)}
 finally{b.disabled=false;b.textContent='Markt aktualisieren'}
}
async function buy(s){if(s==='MNQ1!'){msg('MNQ-Kauf gesperrt: Futures-Abrechnung noch nicht korrekt.',true);return}if(!confirm(s+' für bis zu '+euro(S.per_trade)+' virtuell kaufen? Bei -4 % wären das ungefähr '+euro(S.per_trade*.04)+' Verlust (ohne Gebühren).'))return;try{const old=(S.positions||[]).filter(p=>p.symbol===s).reduce((n,p)=>n+Number(p.cost||0),0);const next=await api('/api/buy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:s})});render(next);const now=(next.positions||[]).filter(p=>p.symbol===s).reduce((n,p)=>n+Number(p.cost||0),0);msg(now>old?s+' virtuell gekauft.':s+' wurde nicht gekauft – bitte Kurs und Budget prüfen.',now<=old)}catch(e){msg('Fehler: '+e.message,true)}}
async function favorite(s){try{S=await api('/api/favorite',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:s})});render(S)}catch(e){msg(e.message,true)}}
function chart(s){const x=(S.market||[]).find(x=>x.symbol===s)||((S.scan_results||{})[s]);chartTitle.textContent=s+' · '+((S.names||{})[s]||'')+' · letzte bis zu 30 Kurspunkte';const a=x?.chart||[];if(a.length<2){priceChart.innerHTML='';chartTitle.textContent+=' · Noch kein Kursverlauf verfügbar';return}const lo=Math.min(...a),hi=Math.max(...a),r=hi-lo||1;const points=a.map((v,i)=>`${10+i*580/(a.length-1)},${160-(v-lo)/r*140}`).join(' ');priceChart.innerHTML=`<polyline points="${points}" fill="none" stroke="#42df91" stroke-width="3"/>`;}
async function searchStock(){try{let q=stockSearch.value.trim();if(!q)return;searchResult.textContent='Suche läuft …';SEARCH=await api('/api/search?q='+encodeURIComponent(q));searchResult.innerHTML=SEARCH.error?esc(SEARCH.error):`<p><b>${esc(SEARCH.symbol)}</b> – ${esc(SEARCH.name)} · Kurs ${euro(SEARCH.price)} · Score ${SEARCH.score}/100</p><button onclick="buySearch()">Für ${euro(S.per_trade)} virtuell kaufen</button><button onclick="favorite('${esc(SEARCH.symbol)}')">☆ Beobachten</button>`}catch(e){searchResult.textContent=e.message}}
async function buySearch(){if(!SEARCH||SEARCH.error)return;await buy(SEARCH.symbol)}
async function sell(s){
 if(!(S.position_rows||[]).find(p=>p.symbol===s)?.data_ok){msg('Verkauf gesperrt: Kein frischer Börsenkurs.',true);return}
 if(!confirm('Wirklich die GESAMTE Position '+s+' virtuell verkaufen?'))return;
 await submitSell(s,100);
}
async function partialSell(s){
 const x=(S.position_rows||[]).find(p=>p.symbol===s);
 if(!x){msg('Position nicht gefunden.',true);return}
 if(!x.data_ok){msg('Teilverkauf gesperrt: Kein frischer Börsenkurs.',true);return}
 const suggestion=x.pnlpct>=7?50:x.pnlpct>0?25:25;
 const why=x.pnlpct>=7?'Gewinnziel erreicht – einen Teilgewinn sichern und den Rest halten.':x.pnlpct>0?'Kleinen Gewinn sichern und den Rest weiter beobachten.':'Vorsicht: Bei Verlust kann ein Teilverkauf das Risiko reduzieren; bei Stop-Loss ist ein vollständiger Ausstieg vorgesehen.';
 const input=prompt(s+' · Aktueller Wert '+euro(x.value)+'\nVorschlag: '+suggestion+' %\nGrund: '+why+'\n\nWie viel Prozent möchtest du verkaufen? (1–99)',String(suggestion));
 if(input===null)return;
 const pct=Number(input.replace(',','.'));
 if(!Number.isFinite(pct)||pct<=0||pct>=100){msg('Bitte einen Anteil zwischen 1 und 99 % eingeben.',true);return}
 const proceeds=x.value*pct/100, cost=x.cost*pct/100;
 if(!confirm(s+' · '+pct+' % verkaufen?\nVoraussichtlicher Erlös: '+euro(proceeds)+'\nVoraussichtliches Ergebnis: '+euro(proceeds-cost)+'\nRestwert im Depot: '+euro(x.value-proceeds)+'\n(Kurs kann sich geändert haben)'))return;
 await submitSell(s,pct);
}
async function submitSell(s,percent){
 try{S=await api('/api/sell',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:s,percent})});render(S);msg(s+' · '+percent+' % virtuell verkauft.')}catch(e){msg('Fehler: '+e.message,true)}
}

async function setKey(){try{render(await api('/api/key',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:key.value})}));key.value='';msg('API-Key gespeichert.')}catch(e){msg('Fehler: '+e.message,true)}}
async function settings(){try{render(await api('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({budget:+budget.value,per_trade:+per.value})}));msg('Budget-Einstellungen gespeichert.')}catch(e){msg('Fehler: '+e.message,true)}}
async function changeCapital(action){
  const amount=Number(action==='start'?document.getElementById('newStart').value:document.getElementById('capitalAmount').value);
  if(!Number.isFinite(amount)||(action==='start'?amount<0:amount<=0)){msg('Bitte einen gültigen Betrag eingeben.',true);return}
  const label=action==='deposit'?'einzahlen':action==='withdraw'?'entnehmen':'als neues Startkapital setzen';
  if(!confirm(euro(amount)+' virtuell '+label+'?'))return;
  try{
    S=await api('/api/capital',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,amount})});
    render(S);msg('Kapitaländerung gespeichert.');
  }catch(e){msg('Fehler: '+e.message,true)}
}
async function toggleAuto(){try{S=await api('/api/auto',{method:'POST'});render(S);msg(S.auto?'Automatik AN. Sie prüft im Zeitfenster höchstens alle 15 Minuten.':'Automatik AUS.')}catch(e){msg('Fehler: '+e.message,true)}}
async function resetAll(){if(confirm('Paper-Depot wirklich auf 100 € zurücksetzen?'))try{render(await api('/api/reset',{method:'POST'}));msg('Paper-Test zurückgesetzt.')}catch(e){msg('Fehler: '+e.message,true)}}
async function autoTick(){
 if(autoCheckRunning || !S.auto)return;
 const now=Date.now();
 if(now-lastCheckAttempt<15000)return;
 // Ask the server for the authoritative schedule. It enforces the trading window
 // and 15-minute interval, so tab changes cannot create duplicate orders.
 lastCheckAttempt=now;autoCheckRunning=true;countdownTick();
 try{
   const next=await api('/api/auto-check',{method:'POST'});
   S=next;render(S);
   if(S._last_auto_ts && Date.now()/1000-S._last_auto_ts<30)msg('Automatische Prüfung abgeschlossen.');
   else if(!S._last_auto_ts)msg('Prüfung noch nicht durchgeführt: API-Schlüssel und Kursdaten prüfen.');
 }catch(e){msg('Automatische Prüfung fehlgeschlagen: '+e.message,true)}
 finally{autoCheckRunning=false;countdownTick()}
}
load();
setInterval(()=>{
 if(!S.auto||autoCheckRunning)return;
 const due=!S._last_auto_ts || Date.now()/1000>=Number(S._last_auto_ts)+900;
 if(due)autoTick();
},5000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden){countdownTick();if(S.auto)autoTick()}});

</script></body></html>"""

CACHE=[]

AUTO_INTERVAL=15*60
AUTO_LOCK=threading.RLock()

def berlin_now():
    return datetime.now(ZoneInfo('Europe/Berlin'))

def in_auto_window(now=None):
    # Scanner ist 24/7 aktiv. Order-Sicherheit regelt quote_is_fresh.
    return True

def auto_due(d, now_ts=None):
    now_ts=now_ts or time.time()
    return now_ts-float(d.get('_last_auto_ts',0) or 0)>=AUTO_INTERVAL

def next_check_text(d):
    if not d.get('auto'): return 'Automatik AUS'
    last=float(d.get('_last_auto_ts',0) or 0)
    if not last: return 'Jetzt'
    remain=max(0,int(AUTO_INTERVAL-(time.time()-last)))
    return 'Jetzt' if remain<=0 else f'in ca. {max(1,(remain+59)//60)} Min.'

def run_auto_check(force=False):
    global CACHE
    with AUTO_LOCK:
        d=load()
        if not d.get('auto') or not effective_key(d): return d
        if not force and not auto_due(d): 
            d['next_auto_check']=next_check_text(d); save(d); return d
        CACHE.clear(); CACHE.extend(market(d)); log_event(d,'Automatischer Markt-Scan ausgeführt.','SCAN')
        if CACHE:
            auto_step(d)
            d['_last_auto_ts']=time.time()
            d['last_auto_check']=berlin_now().strftime('%d.%m.%Y %H:%M')
        d['next_auto_check']=next_check_text(d)
        save(d)
        return d

def scheduler_loop():
    while True:
        try: run_auto_check(False)
        except Exception as e:
            try:
                d=load(); log_event(d,'Auto-Check Fehler: '+str(e),'FEHLER'); save(d)
            except Exception: pass
            print('Auto-Check:',e)
        time.sleep(60)

def view(d, refresh=False):
    global CACHE
    if refresh: CACHE=market(d)
    val,rows=portfolio(d,list(d.get('scan_results',{}).values()))
    return {**d,'key':'***' if effective_key(d) else '', 'value':val,'position_rows':rows,'market':CACHE,'server_time':time.time(),'auto_interval':AUTO_INTERVAL,'api_key_source':'Render' if os.environ.get('TWELVE_DATA_API_KEY') else ('App' if d.get('key') else 'Fehlt')}

def quote_is_fresh(x):
    if not isinstance(x,dict) or x.get('fetch_error') or 'price' not in x: return False
    try:
        return (time.time()-float(x.get('seen',0))<=900 and
                time.time()-float(x.get('candle_ts',0))<=1800 and
                float(x['price'])>0)
    except (TypeError,ValueError,OverflowError): return False

def auto_step(d):
    global CACHE
    if not d['auto'] or not CACHE: return
    q={x['symbol']:x for x in CACHE if quote_is_fresh(x)}
    weak=d.setdefault('weak_trend_checks',{})
    cooldown=d.setdefault('rocket_cooldown',{})
    for p in list({p['symbol']:p for p in d['positions']}.values()):
        sym=p['symbol']
        if sym=='MNQ1!': continue
        x=q.get(sym)
        if not x: continue
        lots=[lot for lot in d['positions'] if lot['symbol']==sym]
        ch=x['price']*sum(lot['qty'] for lot in lots)/sum(lot['cost'] for lot in lots)-1
        chart=x.get('chart',[])
        # Confirmation must use two distinct fresh market checks, not repeated stale observations.
        down=(x.get('score',100)<45 and len(chart)>=10 and
              chart[-1]<sum(chart[-5:])/5<sum(chart[-10:])/10 and
              float(x.get('mom',0))<0)
        weak[sym]=min(2,weak.get(sym,0)+1) if down else 0
        reason=None
        if ch<=-.04: reason='Stop-Loss bei -4 %'
        elif ch>=.07: reason='Gewinnziel bei +7 %'
        elif weak[sym]>=2: reason='Score unter 45 und Abwärtstrend zweimal bestätigt'
        if reason:
            execute_sell(d,sym,x['price'],'Automatik',1.0,reason=reason)
            weak.pop(sym,None)
    invested=sum(p['cost'] for p in d['positions'])
    for x in CACHE:
        sym=x.get('symbol')
        if sym=='MNQ1!' or not quote_is_fresh(x) or x.get('risk')=='Hoch': continue
        if any(p['symbol']==sym for p in d['positions']): continue
        rocket=(x.get('stage')=='🚀 AUSBRUCH AUS DEM KELLER' and x.get('score',0)>=80
                and x.get('mom',0)>0 and len(x.get('chart',[]))>=15)
        standard=x.get('score',0)>=75
        if not (rocket or standard): continue
        # Do not immediately repurchase a rocket repeatedly after an automatic exit.
        if rocket and time.time()-float(cooldown.get(sym,0))<24*3600: continue
        amt=min(d['per_trade'],d['cash'],max(0,d['budget']-invested))
        if amt>=5:
            execute_buy(d,sym,x['price'],amt,'Raketen-Radar' if rocket else 'Automatik')
            if rocket: cooldown[sym]=time.time()
            invested+=amt

def execute_buy(d,sym,price,amt,src='Manuell'):
    if sym=='MNQ1!': raise ValueError('MNQ-Käufe sind bis zur korrekten Futures-Abrechnung gesperrt.')
    amt=min(float(amt),d['cash'])
    if amt<=0:return
    contracts=1 if sym=='MNQ1!' else None
    d['positions'].append({'symbol':sym,'entry':price,'qty':amt/price,'cost':amt,**({'contracts':contracts} if contracts else {})});d['cash']-=amt
    desc=f'{src}: KAUF {sym} · {amt:.2f} € @ {price:.2f}'+(' · 1 MNQ-Kontrakt (Paper)' if sym=='MNQ1!' else '')
    d['history'].append({'time':time.strftime('%d.%m.%Y %H:%M'),'text':desc}); log_event(d,desc,'TRADE')

def execute_sell(d,sym,price,src='Manuell',fraction=1.0,reason=None):
    if not math.isfinite(price) or price<=0: raise ValueError('Ungültiger Verkaufskurs.')
    if not math.isfinite(fraction) or not 0<fraction<=1: raise ValueError('Verkaufsanteil muss über 0 und höchstens 100 % sein.')
    lots=[p for p in d['positions'] if p['symbol']==sym]
    if not lots: raise ValueError('Keine offene Position für '+sym)
    total_cost=sum(p['cost'] for p in lots)
    total_qty=sum(p['qty'] for p in lots)
    sold_qty=total_qty*fraction
    sold_cost=total_cost*fraction
    proceeds=sold_qty*price
    pnl=proceeds-sold_cost
    if fraction>=1-1e-10:
        d['positions']=[p for p in d['positions'] if p['symbol']!=sym]
    else:
        for p in lots:
            p['qty']*=1-fraction
            p['cost']*=1-fraction
            p['entry']=p['cost']/p['qty']
    d['cash']+=proceeds
    pct=pnl/sold_cost*100 if sold_cost else 0
    desc=f'{src}: {"TEILVERKAUF" if fraction<1 else "VERKAUF"} {sym} ({fraction*100:.1f} %) @ {price:.2f} · Erlös {proceeds:.2f} € · Ergebnis {pnl:+.2f} € ({pct:+.2f} %)'
    if reason: desc+=' · Grund: '+reason
    d['history'].append({'time':berlin_now().strftime('%d.%m.%Y %H:%M'),'text':desc,'pnl':pnl,'pnlpct':pct,'symbol':sym,'proceeds':proceeds,'cost':sold_cost,'fraction':fraction})
    log_event(d,desc,'TRADE')


class H(BaseHTTPRequestHandler):
 def sendj(self,o,status=200):
  b=json.dumps(o).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',len(b));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  path=urllib.parse.urlparse(self.path).path.rstrip('/') or '/'
  if path in ('/','/index.html'):
   b=HTML.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',len(b));self.end_headers();self.wfile.write(b)
  elif path=='/api/state':self.sendj(view(load()))
  elif path=='/api/search':
   try:
    d=load(); key=effective_key(d)
    if not key: raise ValueError('API-Key fehlt')
    q=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('q',[''])[0].strip()[:80]
    if not q: raise ValueError('Suchbegriff fehlt')
    symbol=q.upper(); name=symbol
    if not re.fullmatch(r'[A-Z0-9./!-]{1,24}',symbol):
     data=td('/symbol_search?symbol='+urllib.parse.quote(q)+'&outputsize=10',key)
     items=data.get('data',[]) if isinstance(data,dict) else []
     if not items: raise ValueError('Keine passende Aktie gefunden. Versuche das Börsenkürzel.')
     symbol=items[0]['symbol'];name=items[0].get('instrument_name',symbol)
    if symbol=='MNQ1!': raise ValueError('MNQ kann nur beobachtet werden')
    x=quote_symbol(symbol,key)
    if 'error' in x: raise ValueError(x['error'])
    d.setdefault('names',{})[symbol]=name
    d.setdefault('scan_results',{})[symbol]=x
    if symbol not in d['watch']: d['watch'].append(symbol)
    global CACHE
    CACHE=[v for v in CACHE if v.get('symbol')!=symbol]+[x]
    save(d);self.sendj({**x,'name':name})
   except Exception as e:self.sendj({'error':str(e)},400)
  elif path=='/favicon.ico':
   self.send_response(204);self.end_headers()
  else:self.send_error(404)
 def do_HEAD(self):
  path=urllib.parse.urlparse(self.path).path.rstrip('/') or '/'
  if path in ('/','/index.html'):
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.end_headers()
  else:self.send_error(404)
 def body(self):
  n=int(self.headers.get('Content-Length',0));return json.loads(self.rfile.read(n) or b'{}')
 def do_POST(self):
  with AUTO_LOCK:
   return self._do_POST_locked()
 def _do_POST_locked(self):
  d=load()
  try:
   if self.path=='/api/key':
    newkey=self.body().get('key','').strip()
    if not newkey: raise ValueError('Kein API-Key eingegeben.')
    d['key']=newkey
   elif self.path=='/api/settings':
    b=self.body();d['budget']=max(0,float(b['budget']));d['per_trade']=max(1,float(b['per_trade']))
   elif self.path=='/api/capital':
     b=self.body();action=b.get('action');amount=float(b.get('amount',0))
     if not math.isfinite(amount) or amount<0 or amount>100000000: raise ValueError('Ungültiger Betrag.')
     if action in ('deposit','withdraw') and amount<0.01: raise ValueError('Betrag muss mindestens 0,01 € sein.')
     if action=='deposit':
      d['cash']=round(d['cash']+amount,2);d['start']=round(d['start']+amount,2)
      desc=f'Virtuelle Einzahlung +{amount:.2f} €'
     elif action=='withdraw':
      if amount>d['cash']+0.000001: raise ValueError('Nicht genügend freies Kapital. Offene Trades werden nicht verkauft.')
      d['cash']=round(d['cash']-amount,2);d['start']=round(d['start']-amount,2)
      desc=f'Virtuelle Entnahme -{amount:.2f} €'
     elif action=='start':
      # Startkapital ist die Bezugsgröße der Gewinnanzeige, kein zusätzlicher Geldfluss.
      d['start']=round(amount,2)
      desc=f'Startkapital-Bezugswert auf {amount:.2f} € gesetzt (kein Geldfluss)'
     else: raise ValueError('Unbekannte Kapitalaktion.')
     d['history'].append({'time':berlin_now().strftime('%d.%m.%Y %H:%M'),'text':desc})
     log_event(d,desc,'KAPITAL')
   elif self.path=='/api/auto':
    d['auto']=not d['auto'];d['next_auto_check']=next_check_text(d)
   elif self.path=='/api/reset':
    key=d.get('key',''); oldevents=d.get('event_log',[]); d=copy.deepcopy(DEFAULT);d['key']=key;d['event_log']=oldevents[-250:];log_event(d,'Paper-Test zurückgesetzt; API-Konfiguration beibehalten.','SYSTEM')
   elif self.path=='/api/refresh':
    if not effective_key(d): raise ValueError('Twelve Data API-Key fehlt.')
    CACHE.clear();CACHE.extend(market(d));log_event(d,'Markt manuell aktualisiert.','SCAN')
    if not CACHE: raise ValueError('Keine Marktdaten erhalten.')
    if d.get('auto'):
     auto_step(d);d['_last_auto_ts']=time.time();d['last_auto_check']=berlin_now().strftime('%d.%m.%Y %H:%M');d['next_auto_check']=next_check_text(d)
   elif self.path=='/api/auto-check':
    d=run_auto_check(False)
   elif self.path=='/api/import-backup':
    backup=self.body().get('backup',{})
    if not isinstance(backup,dict): raise ValueError('Ungültige Sicherung.')
    for k in ('cash','start','budget','per_trade','positions','history'):
     if k not in backup: raise ValueError('Sicherung unvollständig: '+k)
    if not isinstance(backup['positions'],list) or not isinstance(backup['history'],list): raise ValueError('Trades oder Protokoll ungültig.')
    if len(backup['positions'])>1000 or len(backup['history'])>10000: raise ValueError('Sicherung zu groß.')
    for k in ('cash','start','budget','per_trade'):
     v=float(backup[k])
     if not math.isfinite(v) or v<0 or v>100000000: raise ValueError('Ungültiges Kapital.')
    for pos in backup['positions']:
     if not isinstance(pos,dict) or not all(k in pos for k in ('symbol','entry','qty','cost')): raise ValueError('Ungültiger Trade.')
     if not isinstance(pos['symbol'],str) or len(pos['symbol'])>40: raise ValueError('Ungültiges Symbol.')
     for k in ('entry','qty','cost'):
      v=float(pos[k])
      if not math.isfinite(v) or v<=0 or v>100000000: raise ValueError('Ungültige Position.')
    for k in ('cash','start','budget','per_trade','positions','history','event_log','scan_results','scan_index','favorites','names','alerts'):
     if k in backup: d[k]=copy.deepcopy(backup[k])
    d['history'].append({'time':berlin_now().strftime('%d.%m.%Y %H:%M'),'text':'Depot aus ausgewählter Sicherungsdatei wiederhergestellt.'})
    log_event(d,'Depot aus Sicherungsdatei wiederhergestellt.','SYSTEM')
   elif self.path=='/api/restore':
    b=self.body(); backup=b.get('backup',{})
    for k in ('cash','start','budget','per_trade','positions','history','auto','event_log','scan_results','scan_index','favorites','names','alerts'):
     if k in backup: d[k]=backup[k]
    d['history'].append({'time':time.strftime('%d.%m.%Y %H:%M'),'text':'Browser-Sicherung nach Update wiederhergestellt.'})
   elif self.path=='/api/favorite':
    sym=str(self.body().get('symbol','')).upper().strip()
    if not re.fullmatch(r'[A-Z0-9./!-]{1,24}',sym): raise ValueError('Ungültiges Kürzel')
    fav=d.setdefault('favorites',[])
    if sym in fav: fav.remove(sym)
    else: fav.append(sym)
   elif self.path=='/api/buy':
    sym=self.body()['symbol'];x=next((x for x in CACHE if x.get('symbol')==sym and 'price' in x and quote_is_fresh(x)),None)
    if not x: raise ValueError('Kein ausreichend frischer Börsenkurs. Bitte später erneut prüfen.')
    invested=sum(p['cost'] for p in d['positions']);amt=min(d['per_trade'],d['cash'],max(0,d['budget']-invested))
    if amt<1: raise ValueError('Nicht genügend freies Kapital oder Budget.')
    execute_buy(d,sym,x['price'],amt)
   elif self.path=='/api/sell':
    b=self.body();sym=b['symbol'];percent=float(b.get('percent',100));x=next((x for x in CACHE if x.get('symbol')==sym and 'price' in x and quote_is_fresh(x)),None);p=next((p for p in d['positions'] if p['symbol']==sym),None);
    if sym=='MNQ1!': raise ValueError('MNQ-Verkauf ausgesetzt: Kontraktabrechnung ungeklärt.')
    if p and not x: raise ValueError('Kein frischer Kurs für den Verkauf. Bitte Markt aktualisieren.')
    execute_sell(d,sym,x['price'],fraction=percent/100) if p else None
   save(d);self.sendj(view(d))
  except Exception as e:
   self.sendj({'error':str(e),**view(d)})
 def log_message(self,*a):pass

if __name__=='__main__':
 port=int(os.environ.get('PORT','10000'))
 print(f'Trading Radar läuft auf Port {port}')
 threading.Thread(target=scheduler_loop,daemon=True).start()
 HTTPServer(('0.0.0.0',port),H).serve_forever()
