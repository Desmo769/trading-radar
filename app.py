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
DEFAULT={"cash":100.0,"start":100.0,"budget":100.0,"per_trade":20.0,"positions":[],"history":[],"watch":DISCOVERY_UNIVERSE,"key":"","auto":False,"last_auto_check":"Noch nie","next_auto_check":"–","scan_index":0,"scan_results":{},"scanned_total":0,"version":"V8.3.17","weak_trend_checks":{},"rocket_cooldown":{},"mnq_contracts":1,"event_log":[],"favorites":[],"names":KNOWN_NAMES.copy(),"alerts":[]}
# Supabase ist die maßgebliche Speicherung, wenn beide Render-Variablen gesetzt sind.
# Bei Netzwerkfehlern niemals stillschweigend auf einen leeren lokalen Zustand zurückfallen.
SUPABASE_URL=os.environ.get('SUPABASE_URL','').strip().rstrip('/')
SUPABASE_SECRET_KEY=os.environ.get('SUPABASE_SECRET_KEY','').strip()
REMOTE_ENABLED=bool(SUPABASE_URL and SUPABASE_SECRET_KEY)
if bool(SUPABASE_URL)!=bool(SUPABASE_SECRET_KEY):
    raise RuntimeError('SUPABASE_URL und SUPABASE_SECRET_KEY müssen beide gesetzt sein')

def remote_request(method, payload=None):
    url=SUPABASE_URL+'/rest/v1/trading_radar_state'
    if method=='GET': url+='?id=eq.1&select=data'
    else: url+='?on_conflict=id'
    headers={'apikey':SUPABASE_SECRET_KEY,'Authorization':'Bearer '+SUPABASE_SECRET_KEY,
             'Content-Type':'application/json','Accept':'application/json'}
    if method!='GET': headers['Prefer']='resolution=merge-duplicates,return=minimal'
    body=None if payload is None else json.dumps(payload,ensure_ascii=False).encode('utf-8')
    req=urllib.request.Request(url,data=body,headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=15) as response:
        return json.loads(response.read() or b'null') if method=='GET' else None

def load():
    if REMOTE_ENABLED:
        rows=remote_request('GET')
        if not isinstance(rows,list): raise RuntimeError('Supabase-Antwort ungültig')
        # Neue Datenbank: erst ein Backup über die vorhandene Import-Funktion laden.
        d=copy.deepcopy(rows[0]['data']) if rows else copy.deepcopy(DEFAULT)
        d['_remote_initialized']=bool(rows)
    else:
        if not STATE.exists(): STATE.write_text(json.dumps(copy.deepcopy(DEFAULT),indent=2))
        d=json.loads(STATE.read_text())
    for k,v in DEFAULT.items(): d.setdefault(k,copy.deepcopy(v))
    for sym in DISCOVERY_UNIVERSE:
        if sym not in d['watch']: d['watch'].append(sym)
    d.setdefault('names',{}).update({k:v for k,v in KNOWN_NAMES.items() if k not in d.get('names',{})})
    d['version']='V8.3.17';d['mnq_contracts']=4
    for pos in d.get('positions',[]):
        if pos.get('symbol')=='MNQ1!': pos.setdefault('contracts',4)
        pos.setdefault('peak_price',pos.get('entry',0))
    return d

def save(d):
    data={k:v for k,v in d.items() if k!='_remote_initialized'}
    if REMOTE_ENABLED:
        remote_request('POST',[{'id':1,'data':data}])
    else:
        tmp=STATE.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(data,indent=2),encoding='utf-8')
        tmp.replace(STATE)
def effective_key(d):
    return (os.environ.get('TWELVE_DATA_API_KEY','').strip() or os.environ.get('twelve_data_api_key','').strip() or d.get('key','').strip())

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
            result=q['chart']['result'][0]; raw=result['indicators']['quote'][0]['close']; ticks=result.get('timestamp',[]); valid=[(t,float(v)) for t,v in zip(ticks,raw) if v is not None]; closes=[v for _,v in valid]; mnq_candle_ts=valid[-1][0] if valid else None
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
        # Originalzeit der letzten tatsächlich gelieferten MNQ-Kerze.
        candle_ts=mnq_candle_ts
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

# V8.3.13: Fail-closed product eligibility. A price alone is NOT evidence of an unleveraged instrument.
SPOT_CRYPTO={'BTC/USD','ETH/USD'}
CURATED_STOCKS=set(DISCOVERY_SYMBOLS)|{x for x in UNIVERSE if x not in SPOT_CRYPTO and x!='MNQ1!'}
LEVERAGED_SYMBOLS={'MNQ1!'}
LEVERAGED_MARKERS=('FUTURE','FUTURES','LEVERAGED','INVERSE','TURBO','WARRANT','OPTION','CFD','KNOCK-OUT','KNOCK OUT','BULL X','BEAR X')

def product_is_leveraged(sym, d=None):
    sym=str(sym or '').upper().strip()
    if sym in LEVERAGED_SYMBOLS: return True
    name=str((d or {}).get('names',{}).get(sym,'')).upper()
    return any(marker in name for marker in LEVERAGED_MARKERS)

def product_is_allowed(sym,d):
    sym=str(sym or '').upper().strip()
    if product_is_leveraged(sym,d): return False
    if sym in SPOT_CRYPTO: return True
    if not re.fullmatch(r'[A-Z][A-Z0-9.]{0,9}',sym): return False
    return sym in CURATED_STOCKS or sym in d.get('verified_stocks',[])

def extend_universe(d,key):
    # Symbolkatalog gelegentlich aktualisieren; bei API-Limit/Fehler bleibt die bestehende Liste.
    if d.get('verified_stocks') and time.time()-float(d.get('universe_updated_at',0) or 0)<7*86400: return
    d['universe_updated_at']=time.time()
    try:
        result=td('/stocks?country=United%20States&format=JSON',key)
        entries=result.get('data',[]) if isinstance(result,dict) else []
        symbols=[x.get('symbol','').upper() for x in entries if isinstance(x,dict)
                 and x.get('type') in ('Common Stock','Common Stocks','Equity')]
        symbols=[x for x in symbols if re.fullmatch(r'[A-Z][A-Z0-9.]{0,9}',x)]
        if len(symbols)>500:
            d['verified_stocks']=list(dict.fromkeys(symbols))
            watch=d.setdefault('watch',[])
            existing=set(watch)
            for sym in symbols:
                if sym not in existing: watch.append(sym);existing.add(sym)
            d['universe_updated_at']=time.time()
    except Exception:
        pass

def market(d):
    key=effective_key(d)
    if not key: return []
    extend_universe(d,key)
    held=list(dict.fromkeys(p['symbol'] for p in d.get('positions',[])))
    if len(held)>7:
        h=int(d.get('held_scan_index',0))%len(held)
        held=held[h:]+held[:h]
        d['held_scan_index']=(h+7)%len(held)
    universe=[s for s in (d.get('watch') or DISCOVERY_UNIVERSE) if product_is_allowed(s,d)]
    if not universe: universe=[s for s in DISCOVERY_UNIVERSE if product_is_allowed(s,d)]
    # Basic Twelve Data accounts are easily rate-limited. Keep each cycle at max. 7 requests.
    slots=max(1,8-min(7,len(set(held))))
    i=int(d.get('scan_index',0))%len(universe)
    batch=[]
    while len(batch)<slots and len(batch)<len(universe):
        s=universe[i%len(universe)]; i+=1
        if s not in held and s not in batch: batch.append(s)
    symbols=list(dict.fromkeys(held[:7]+batch))[:8]
    # Hebelprodukte werden nicht mehr als neue Scanner-Kandidaten ergänzt.
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
    good=[x for x in vals if 'price' in x and product_is_allowed(x.get('symbol'),d)]
    errs=[{'symbol':x.get('symbol'),'error':x.get('fetch_error')} for x in vals if x.get('fetch_error') and x.get('symbol') in symbols and product_is_allowed(x.get('symbol'),d)]
    held_quotes=[x for x in vals if x.get('symbol') in held and not product_is_allowed(x.get('symbol'),d) and 'price' in x]
    return sorted(good,key=lambda x:(x.get('seen',0)>time.time()-1800,x.get('stage')=='🚀 AUSBRUCH AUS DEM KELLER',x.get('stage')=='FRÜHSIGNAL',x.get('mom',0),x.get('score',-1)),reverse=True)[:25]+errs+held_quotes

def usd_eur_rate(d):
    rate=float(d.get('usd_eur_rate',0) or 0)
    if rate>0 and time.time()-float(d.get('usd_eur_rate_ts',0) or 0)<3600:return rate
    q=td('/exchange_rate?symbol=USD/EUR',effective_key(d))
    rate=float(q.get('rate',0) or 0)
    if not .5<rate<1.5: raise ValueError('USD/EUR-Umrechnung nicht verfügbar')
    d['usd_eur_rate']=rate;d['usd_eur_rate_ts']=time.time()
    return rate

def mnq_value(d,pos,price):
    # MNQ: 2 USD je Indexpunkt und Kontrakt, 4 Kontrakte.
    return float(pos['cost'])+(price-float(pos['entry']))*2*int(pos.get('contracts',4))*usd_eur_rate(d)

def portfolio(d, quotes):
    qmap={x['symbol']:x for x in quotes if 'price' in x}
    val=d['cash']; rows=[]; grouped={}
    for pos in d['positions']:
        sym=pos['symbol']
        if sym not in grouped:
            grouped[sym]={'symbol':sym,'qty':0.0,'cost':0.0,'buys':0}
        g=grouped[sym];g['qty']+=pos['qty'];g['cost']+=pos['cost'];g['buys']+=1;g['auto_qty']=g.get('auto_qty',0)+ (pos['qty'] if pos.get('auto_manage',pos.get('source','Automatik')!='Manuell') else 0)
    for sym,pos in grouped.items():
        entry=pos['cost']/pos['qty'] if pos['qty'] else 0
        q=qmap.get(sym,{})
        price=q.get('price',entry)
        age=int(max(0,time.time()-float(q.get('seen',0) or 0))) if q.get('seen') else None
        candle_age=int(max(0,time.time()-float(q.get('candle_ts',0) or 0))) if q.get('candle_ts') else None
        reliable=age is not None and age<=900 and candle_age is not None and candle_age<=1800 and not q.get('fetch_error')
        if sym=='MNQ1!' and (not d.get('usd_eur_rate') or time.time()-float(d.get('usd_eur_rate_ts',0) or 0)>3600): reliable=False
        cur=pos['qty']*price if sym!='MNQ1!' else pos['cost']+(price-entry)*2*int(next((p.get('contracts',4) for p in d['positions'] if p['symbol']==sym),4))*float(d.get('usd_eur_rate',0) or 0)
        pnl=cur-pos['cost'];val+=cur
        pct=(cur/pos['cost']-1)*100 if pos['cost'] else 0
        score=q.get('score')
        if sym=='MNQ1!' and not d.get('usd_eur_rate'):decision,reason='DATEN FEHLEN','USD/EUR-Kurs fehlt'
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
        rows.append({**pos,'entry':entry,'price':price,'value':cur,'pnl':pnl,'pnlpct':pct,'score':score,'decision':decision,'reason':reason,'checked':checked,'cost':pos['cost'],'data_ok':reliable,'age_seconds':age,'candle_age_seconds':candle_age,'fetch_error':q.get('fetch_error'),'has_quote':bool(q),'auto_manage':pos.get('auto_qty',0)>0,'manual_qty':pos['qty']-pos.get('auto_qty',0)})
    rows.sort(key=lambda x:x['pnlpct'],reverse=True)
    return val,rows

HTML=r"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trading Radar</title><style>
body{font-family:system-ui;background:#07111f;color:#eaf1ff;margin:0}header{padding:18px 5%;background:#0c1b2d;position:sticky;top:0}.wrap{max-width:1550px;margin:auto;padding:22px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}.card{background:#102238;border:1px solid #203b5b;border-radius:16px;padding:16px;margin-bottom:14px}.big{font-size:28px;font-weight:800}.green{color:#42df91}.red{color:#ff6677}.yellow{color:#ffd15c}button,input{font:inherit;border-radius:10px;padding:10px;border:1px solid #34506d}button{background:#19b873;color:white;font-weight:700;cursor:pointer}.danger{background:#c53e50}.muted{color:#9db0c7}.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.trade{display:grid;grid-template-columns:1.2fr .8fr .8fr .8fr .8fr;gap:8px;padding:10px 0;border-top:1px solid #233c58}#status{margin-top:10px;font-weight:700}@media(max-width:700px){.trade{grid-template-columns:1fr 1fr}.hideM{display:none}}
nav.tabs{display:flex;gap:9px;overflow-x:auto;margin:18px 0 14px;padding-bottom:6px}button.tab{background:#14263b;color:#c3d4e7;border:1px solid #2c4661;white-space:nowrap;padding:13px 17px}button.tab.active{background:#0869d5;border-color:#27d39a;color:#fff}.controlbar{display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:#10283d}.controlbar strong{font-size:23px;color:#42df91;font-variant-numeric:tabular-nums}.statusline{padding:10px 14px;margin:10px 0 14px;background:#0f2134;border-radius:10px}.kpis .card{background:linear-gradient(145deg,#142c46,#0e1d30);min-height:86px}.kpis .big{margin-top:8px}header{z-index:10;border-bottom:1px solid #294560}button:hover{filter:brightness(1.13)}[data-tab]{display:none}[data-tab].visible{display:block}.trade{line-height:1.5}@media(max-width:700px){.wrap{padding:12px}.controlbar{justify-content:flex-start}.tabs{position:sticky;top:56px;background:#07111f;z-index:9}}.price-up{color:#22c55e;font-weight:700}.price-down{color:#ef4444;font-weight:700}.price-flat{color:inherit;font-weight:700}</style><style>.kpis{grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}.kpis .card{margin-bottom:0}.dashboard-grid{grid-template-columns:minmax(0,2.1fr) minmax(290px,1fr);gap:16px;align-items:start}.dashboard-grid.visible{display:grid}.dash-main,.dash-side{min-width:0}.panel-title{display:flex;justify-content:space-between;align-items:center;gap:12px}.panel-title h3{margin:4px 0 14px}.panel-title select{background:#132a43;color:#eaf1ff;border:1px solid #35516c;border-radius:9px;padding:8px}.holdings{width:100%;border-collapse:collapse;font-size:13px;white-space:nowrap}.holdings th{text-align:left;font-size:12px;color:#c6d4e8;font-weight:500;padding:13px 9px;border-bottom:1px solid #29435b}.holdings td{padding:13px 9px;border-bottom:1px solid #29435b;vertical-align:middle}.holdings small{display:block;color:#9db0c7}.holdings button{padding:8px 9px;font-size:12px;background:#0869d5}.holdings button.danger{background:#c83c4d}.holdings .signal{border-radius:7px;background:#145c43;padding:7px;color:#d6ffe7;display:inline-block}.holdings .signal.warning{background:#775a1e;color:#ffe6a2}.holdings .signal.sell{background:#8c273b;color:#fff}.table-scroll{overflow-x:auto}.fine{font-size:12px}.dash-bottom{display:grid;grid-template-columns:1fr 1fr;gap:14px}.quick-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px}.quick-actions button{font-size:13px;padding:13px 8px}button.secondary{background:#182e49;border:1px solid #365574}.linkbutton{background:transparent;color:#55a9ff;font-weight:500;padding:5px;border:0}.preview-row{display:grid;grid-template-columns:1.2fr .9fr .5fr auto;gap:8px;align-items:center;padding:12px 0;border-bottom:1px solid #29435b;font-size:13px}.preview-row small{color:#9db0c7;display:block}.preview-row button{font-size:12px;padding:8px;background:#0b9b59}.activity-row{padding:11px 0;border-bottom:1px solid #29435b;font-size:12px}.activity-row .green,.activity-row .red{font-weight:700}@media(max-width:1050px){.kpis{grid-template-columns:repeat(3,minmax(0,1fr))}.dashboard-grid.visible{grid-template-columns:1fr}}@media(max-width:620px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.dash-bottom{grid-template-columns:1fr}.panel-title{flex-wrap:wrap}}</style><style>
.depot-full{overflow-x:visible}.holdings{white-space:normal;table-layout:fixed;font-size:12px}.holdings th,.holdings td{padding:7px 4px;overflow-wrap:anywhere}.holdings button{padding:5px 6px;margin:2px;font-size:11px}.depot-actions{display:flex;flex-wrap:wrap;gap:2px}.depot-actions button{flex:1 1 42%}.signal-hot{font-weight:900;color:#ffdf57;background:#6b3700;border:2px solid #ffa500;padding:6px;border-radius:8px;display:inline-block}.signal-rocket{font-weight:900;color:#b6ffe0;background:#0c5b38;border:2px solid #2effa1;padding:6px;border-radius:8px;display:inline-block}.chart-modal[hidden]{display:none}.chart-modal{position:fixed;inset:0;z-index:100;background:#000b;display:flex;align-items:center;justify-content:center;padding:15px}.chart-window{background:#102238;border:2px solid #456c91;border-radius:16px;padding:18px;width:min(850px,96vw);max-height:90vh;overflow-y:auto}#chanceSortPanel label{display:block;margin:9px 0}@media(max-width:850px){.holdings thead{display:none}.holdings,.holdings tbody,.holdings tr,.holdings td{display:block;width:100%;box-sizing:border-box}.holdings tr{border:1px solid #35516c;border-radius:10px;margin:10px 0;padding:8px}.holdings td{display:flex;justify-content:space-between;align-items:center;gap:8px}.holdings td:before{content:attr(data-label);font-weight:600;color:#9db0c7}.depot-actions{min-width:190px}}
</style><style>
.pro-monitor{overflow-x:auto}.pro-table{border-collapse:collapse;width:100%;font-size:13px}.pro-table th,.pro-table td{padding:10px 12px;border-bottom:1px solid #25405b;text-align:left;white-space:nowrap}.pro-table th{color:#9db0c7;font-size:11px;letter-spacing:.05em}.pro-table tbody tr:hover{background:#19314a}.pro-table button{font-size:12px;padding:7px}.pro-toolbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.pro-toolbar input,.pro-toolbar select{background:#0a1a2d;color:#fff;max-width:200px}.pro-link{background:none;border:0;color:#73baff;padding:2px}.pro-link:hover{text-decoration:underline}.pro-table small{display:block;color:#9db0c7}
</style></head><body><header><b>📈 Trading Radar V8.3.17</b> <span class="muted">Paper-Trading · kein Echtgeld</span></header><div class="wrap">
<nav class="tabs" aria-label="Bereiche" style="position:sticky;top:0;z-index:100;background:#081525;padding:8px 0;overflow-x:auto;flex-wrap:nowrap"><button class="tab active" onclick="showTab('depot')">📊 Depot</button><button class="tab" onclick="showTab('scanner')">🔎 Top-Chancen</button><button class="tab" onclick="showTab('rocket')">🚀 Raketen-Radar</button><button class="tab" onclick="showTab('log')">📋 Protokoll</button><button class="tab" onclick="showTab('settings')">⚙️ Einstellungen</button></nav>
<div class="card controlbar"><span>Automatik: <b id="quickAuto">AUS</b></span><span class="muted">Automatisch nach US-Börsenzeiten</span><span>Prüfung in <strong id="countdown">--:--</strong></span><span id="freshness">Kurse noch nicht geprüft</span><span id="quickScan">Scanner –</span></div>
<div id="status" class="muted statusline">Bereit.</div>
<div class="grid kpis"><div class="card">Depotwert<div id="value" class="big">–</div><span id="pnl"></span></div><div class="card">Freies Kapital<div id="cash" class="big">–</div></div><div class="card">Offene Positionen<div id="count" class="big">–</div></div><div class="card">Gesamtergebnis<div id="totalResult" class="big">–</div></div><div class="card">Automatik<div id="auto" class="big">AUS</div><small id="nextMini">–</small></div></div>
<div class="card" data-tab="settings"><h3>Einstellungen</h3><div class="row"><input id="key" type="password" placeholder="Twelve Data API-Key"><button onclick="setKey()">API-Key speichern</button><label>Budget € <input id="budget" type="number" value="100" style="width:75px"></label><label>pro Trade € <input id="per" type="number" value="20" style="width:70px"></label><button onclick="settings()">Speichern</button><span class="muted">Zeitplan automatisch aktiv · kein tägliches Einschalten erforderlich</span><button class="danger" onclick="resetAll()">Test zurücksetzen</button></div><p class="muted">Die App handelt nur virtuell. Tipp: Hinterlege TWELVE_DATA_API_KEY später einmal bei Render; dann bleibt der Schlüssel bei Updates erhalten. Trades werden zusätzlich in diesem Browser gesichert und nach einem Deploy automatisch wiederhergestellt.</p><p class="muted">Automatik-Scanner: während der regulären US-Börsensitzung alle 5 Minuten (API-schonend; kein Echtzeitstream). Automatische Orders nur zur regulären US-Börsensitzung (09:30–16:00 Uhr New York, Zeitumstellung berücksichtigt) und mit ausreichend frischen Kursdaten; außerhalb der Börsenzeiten können Kursdaten fehlen. Der Hintergrunddienst läuft auf Render Starter auch ohne geöffneten Browser. Feiertage und außerplanmäßige Börsenschließungen werden nicht als Handelskalender erkannt; automatische Orders erfordern frische Kursdaten.</p><div class="row"><span>Letzte automatische Prüfung: <b id="lastcheck">–</b></span><span>Nächste Prüfung: <b id="nextcheck">–</b></span></div></div>
<div class="card" data-tab="settings"><h3>Virtuelles Kapital verwalten</h3>
<p class="muted">Ein- und Auszahlungen ändern nur dein freies virtuelles Kapital. Offene Trades bleiben bestehen. Das Handelsbudget wird separat eingestellt.</p>
<div class="row"><label>Betrag € <input id="capitalAmount" type="number" min="0.01" step="0.01" value="100" style="width:115px"></label>
<button onclick="changeCapital('deposit')">+ Einzahlen</button>
<button onclick="changeCapital('withdraw')">− Entnehmen</button></div>
<p class="muted">Startkapital für die Gewinnberechnung anpassen, ohne offene Trades zu schließen:</p>
<div class="row"><label>Neues Startkapital € <input id="newStart" type="number" min="0" step="0.01" value="100" style="width:115px"></label>
<button onclick="changeCapital('start')">Startkapital ändern</button></div></div>
<div class="card" data-tab="scanner"><h3>Markt-Scanner · Top-Chancen</h3><button class="secondary" onclick="document.getElementById('chanceSortPanel').hidden=!document.getElementById('chanceSortPanel').hidden">Top Chancen sortieren nach</button><div id="chanceSortPanel" hidden class="card"><label><input type="radio" name="chanceSort" value="score" checked onchange="sortChances(this.value)"> Beste Bewertung zuerst</label><label><input type="radio" name="chanceSort" value="rocket" onchange="sortChances(this.value)"> 🚀 Raketen und Ausbrüche zuerst</label><label><input type="radio" name="chanceSort" value="signal" onchange="sortChances(this.value)"> Signalstärke zuerst</label><label><input type="radio" name="chanceSort" value="az" onchange="sortChances(this.value)"> Alphabetisch A–Z</label></div><p class="muted">Rotierender Scanner: pro Prüfung wird ein neuer Teil der Beobachtungsliste analysiert, um das API-Limit einzuhalten. Bereits geprüfte Kandidaten bleiben im Ranking. Hebelprodukte werden nicht als Kaufchancen angezeigt und können nicht gekauft werden. Erweiterte Aktienliste, rotierend und API-schonend; keine vollständige Echtzeit-Marktabdeckung. Frühwarnstufen: DIP → FRÜHSIGNAL → 🚀 AUSBRUCH AUS DEM KELLER.</p><div id="scaninfo" class="muted"></div><div id="radar">API-Key eintragen und „Markt aktualisieren“ drücken.</div><br><button id="refreshBtn" onclick="refreshMarket()">Markt aktualisieren</button></div>
<div class="card" data-tab="scanner"><h3>Aktie suchen und virtuell kaufen</h3><p class="muted">Kürzel oder Firmenname suchen; Kauf nur mit verfügbaren Kursdaten. Keine Echtgeld-Orders.</p><div class="row"><input id="stockSearch" placeholder="z. B. NVDA oder NVIDIA" style="min-width:220px"><button onclick="searchStock()">Suchen</button></div><div id="searchResult" class="muted"></div></div>
<div class="card" data-tab="scanner"><h3>⭐ Meine Beobachtungsliste</h3><div id="favorites"></div></div>
<div class="card" data-tab="rocket"><h3>🚀 Raketen-Radar und Frühwarnungen</h3><p class="muted">Heuristische Hinweise, keine zuverlässige Vorhersage. Kursveränderungen basieren auf 15-Minuten-Kerzen.</p><div id="alerts"></div></div>
<div class="card" data-tab="scanner"><h3>📈 Kursverlauf</h3><div id="chartTitle" class="muted">Aktie im Scanner anklicken.</div><svg id="priceChart" viewBox="0 0 600 180" style="width:100%;max-height:220px;background:#081525;border-radius:12px"></svg></div>
<section data-tab="depot" class="dashboard-grid"><div class="dash-main"><div class="card"><div class="panel-title"><h3>Mein Depot (<span id="depotCount">0</span> Positionen)</h3><label>Sortierung: <select id="depotSort" onchange="render(S)"><option value="pnl">Gewinn/Verlust</option><option value="name">Aktie</option><option value="score">Score</option></select></label></div><div id="depotChartPanel" class="card" style="display:none"><div class="row"><h3 id="depotChartTitle">Kursverlauf</h3><button class="secondary" onclick="document.getElementById('depotChartPanel').style.display='none'">Schließen</button></div><svg id="depotPriceChart" viewBox="0 0 600 180" style="width:100%;max-height:220px;background:#081525;border-radius:12px"></svg><p id="depotChartNote" class="muted fine"></p></div><div class="table-scroll depot-full"><table class="holdings"><thead><tr><th>Aktie</th><th>Kurs</th><th>Einstieg</th><th>Investiert</th><th>G/V (€)</th><th>G/V (%)</th><th>Signal</th><th>Aktionen</th></tr></thead><tbody id="positions"></tbody></table></div><p class="muted fine">Gewinnmitnahme +7 % · Stop-Loss −4 % (nicht garantiert) · Bestehende Hebelpositionen werden markiert. Alle Trades virtuell.</p></div><div class="dash-bottom"><div class="card"><h3>Marktüberblick</h3><div id="marketOverview"></div></div><div class="card"><h3>Schnelle Aktionen</h3><div class="quick-actions"><button onclick="showTab('settings')">＋ Virtuell einzahlen</button><button class="danger" onclick="showTab('settings')">－ Virtuell entnehmen</button><button class="secondary" onclick="exportBackup()">⇩ Sicherung herunterladen</button><button class="secondary" onclick="showTab('log')">⇧ Sicherung wiederherstellen</button></div></div></div><div class="card"><h3>Statistik abgeschlossener Trades</h3><div id="stats"></div></div></div><aside class="dash-side"><div class="card"><div class="panel-title"><h3>Top-Chancen</h3><button class="linkbutton" onclick="showTab('scanner')">Mehr anzeigen →</button></div><div id="topPreview"></div></div><div class="card"><div class="panel-title"><h3>Letzte Aktivitäten</h3><button class="linkbutton" onclick="showTab('log')">Mehr anzeigen →</button></div><div id="recentPreview"></div></div></aside></section>
<div class="card" data-tab="depot"><div class="panel-title"><h3>📡 Marktmonitor <small class="muted fine">· verfügbare Kursdaten, kein garantierter Echtzeitstream</small></h3><div class="pro-toolbar"><input id="monitorSearch" placeholder="Aktie / Kürzel filtern" aria-label="Marktmonitor filtern" oninput="renderMonitor(S)"><select id="monitorSort" aria-label="Marktmonitor sortieren" onchange="renderMonitor(S)"><option value="score">Score ↓</option><option value="momentum">Momentum ↓</option><option value="symbol">Kürzel A–Z</option></select><button class="secondary" onclick="refreshMarket()">Kurse prüfen</button></div></div><div class="muted fine" id="monitorInfo"></div><div class="pro-monitor"><table class="pro-table"><thead><tr><th>Aktie</th><th>Kurs</th><th>Momentum / 75 Min.</th><th>Score</th><th>Signal</th><th>Letzte Abfrage</th><th>Chart</th></tr></thead><tbody id="monitorRows"><tr><td colspan="7">Kurse werden geladen.</td></tr></tbody></table></div></div>

<div class="card" data-tab="log"><h3>Protokoll</h3><div class="row"><input id="restoreFile" type="file" accept=".json,application/json"><button onclick="importBackup()">Sicherung wiederherstellen</button></div><p class="muted">Wichtig: Erst eine aktuelle Sicherung herunterladen. Wiederherstellen ersetzt Depot, Trades und Protokoll durch die ausgewählte Sicherung.</p><button onclick="exportBackup()">Sicherung herunterladen</button><p class="muted">Bitte Sicherung vor jedem Update herunterladen. Render Free speichert Daten nicht dauerhaft.</p><details><summary style="cursor:pointer;padding:12px;font-weight:bold">Käufe und Verkäufe anzeigen</summary><div id="history" class="muted"></div></details><hr><details><summary style="cursor:pointer;padding:12px;font-weight:bold">Systemereignisse anzeigen</summary><div id="events" class="muted"></div></details></div>
</div><div id="chartModal" class="chart-modal" hidden><div class="chart-window"><div class="row" style="justify-content:space-between"><h3 id="modalChartTitle">Kursverlauf</h3><button class="secondary" onclick="closeChart()">✕ Schließen</button></div><p id="modalLive" class="muted">Kursdaten werden geladen.</p><div class="row"><button onclick="chartRange('1T')">1 Tag</button><button onclick="chartRange('1W')">1 Woche</button><button onclick="chartRange('1M')">1 Monat</button><button onclick="chartRange('3M')">3 Monate</button></div><svg id="modalChartSvg" viewBox="0 0 600 180" style="width:100%;height:220px;background:#081525;border-radius:12px"></svg><p id="modalChartNote" class="muted fine"></p></div></div><script>
let S={}; let SEARCH=null; let activeTab='depot';
function showTab(t){activeTab=t;document.querySelectorAll('[data-tab]').forEach(e=>e.classList.toggle('visible',e.dataset.tab===t));document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.getAttribute('onclick')==="showTab('"+t+"')"));}
let autoCheckRunning=false, lastCheckAttempt=0;
function countdownTick(){
 const el=document.getElementById('countdown');if(!el)return;
 if(!S.auto){el.textContent='Börse geschlossen';return}
 if(autoCheckRunning){el.textContent='Prüfung läuft …';return}
 if(!S._last_auto_ts){el.textContent='Prüfung bereit';return}
 const seconds=Math.max(0,Math.ceil(S._last_auto_ts+Number(S.auto_interval||300)-Date.now()/1000));
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
function isAllowedDisplay(sym){return (S.allowed_symbols||[]).includes(sym)}
function euro(x){return Number(x).toLocaleString('de-DE',{style:'currency',currency:'EUR'})}
function msg(t,bad=false){const el=document.getElementById('status');if(el){el.textContent=t;el.className='statusline '+(bad?'red':'green')}}
function backupState(s){try{localStorage.setItem('tradingRadarBackupV6',JSON.stringify({favorites:s.favorites,names:s.names,alerts:s.alerts,cash:s.cash,start:s.start,budget:s.budget,per_trade:s.per_trade,positions:s.positions,history:s.history,auto:s.auto,event_log:s.event_log,scan_results:s.scan_results,scan_index:s.scan_index}))}catch(e){}}
async function load(){try{S=await api('/api/state');let raw=localStorage.getItem('tradingRadarBackupV6');if(raw&&S.positions.length===0&&S.history.length===0){let b=JSON.parse(raw);if((b.positions&&b.positions.length)||(b.history&&b.history.length)){S=await api('/api/restore',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({backup:b})})}}render(S);backupState(S)}catch(e){msg('Fehler: '+e.message,true)}}
let LIVE_QUOTES_UI={};
let LIVE_STATUS_UI={};
async function refreshLive(){try{const live=await api('/api/live');LIVE_QUOTES_UI=live.quotes||{};LIVE_STATUS_UI=live;if(S&&S.scan_results){renderMonitor(S);drawChartModal()}}catch(e){LIVE_STATUS_UI={connected:false,message:'Live-Abfrage fehlgeschlagen'};if(S&&S.scan_results)renderMonitor(S)}}
setInterval(refreshLive,2000);
function renderMonitor(s){
 const q=(document.getElementById('monitorSearch')?.value||'').toLowerCase().trim();
 const sort=document.getElementById('monitorSort')?.value||'score';
 let rows=Object.values(s.scan_results||{}).filter(x=>x&&Number(x.price)>0&&isAllowedDisplay(x.symbol));
 if(q)rows=rows.filter(x=>String(x.symbol).toLowerCase().includes(q)||String((s.names||{})[x.symbol]||'').toLowerCase().includes(q));
 rows.sort((a,b)=>sort==='symbol'?a.symbol.localeCompare(b.symbol):sort==='momentum'?Number(b.mom||0)-Number(a.mom||0):Number(b.score||0)-Number(a.score||0));
 const live=LIVE_STATUS_UI;
 const sub=Number(live.subscribed_count||0),fresh=Number(live.fresh_count||0);
 const status=live.connected?'IEX verbunden':'IEX getrennt: '+(live.message||'Unbekannt');
 document.getElementById('monitorInfo').textContent=rows.length+' gespeicherte Scannerwerte · '+status+' · '+sub+' abonniert · '+fresh+' frische Live-Kurse (max. 20 Sek.) · Analyse alle 5 Minuten';
 const now=Date.now()/1000;
 document.getElementById('monitorRows').innerHTML=rows.slice(0,80).map(x=>{
  const l=LIVE_QUOTES_UI[x.symbol];
  const age=(l?.seen||x.seen)?Math.max(0,now-Number(l?.seen||x.seen)):null;
  const fresh=l?age!==null&&age<=20:age!==null&&age<=900&&!x.fetch_error;
  const signalFresh=Number(x.seen)>0&&now-Number(x.seen)<=900&&Number(x.candle_ts)>0&&now-Number(x.candle_ts)<=1800&&!x.fetch_error;
  const mom=Number(x.mom||0);
  const sym=JSON.stringify(String(x.symbol)).replace(/"/g,'&quot;');
  return '<tr><td><button class="pro-link" onclick="openMonitorChart('+sym+')"><b>'+esc(x.symbol)+'</b></button><small>'+esc((s.names||{})[x.symbol]||'')+'</small></td><td>'+(l?euro(l.price)+' <small class="green">IEX LIVE</small>':euro(x.price))+'</td><td class="'+(mom>=0?'green':'red')+'">'+(mom>=0?'+':'')+mom.toFixed(2)+' %</td><td>'+esc(x.score??'–')+'</td><td>'+(signalFresh?esc(x.signal||'–'):esc(x.signal||'–')+' <small class="yellow">(alt, kein Handelssignal)</small>')+'</td><td class="'+(fresh?'green':'yellow')+'">'+(age===null?'Unbekannt':Math.floor(age/60)+' Min.')+(fresh?'':' ⚠ veraltet')+'</td><td><button class="secondary" onclick="openMonitorChart('+sym+')">Chart</button></td></tr>';
 }).join('')||'<tr><td colspan="7">Keine passenden Kursdaten. Starte eine Marktprüfung.</td></tr>';
}
function openMonitorChart(sym){showTab('scanner');chart(sym);document.getElementById('priceChart')?.scrollIntoView({behavior:'smooth',block:'center'})}
function render(s){
 renderMonitor(s);
 backupState(s);
 value.textContent=euro(s.value);let pp=s.value-s.start;pnl.textContent=(pp>=0?'+':'')+euro(pp)+' seit Start';pnl.className=pp>=0?'green':'red';cash.textContent=euro(s.cash);count.textContent=s.position_rows.length;auto.textContent=s.auto?'AN':'AUS';auto.className='big '+(s.auto?'green':'red');budget.value=s.budget;per.value=s.per_trade;document.getElementById('newStart').value=s.start;lastcheck.textContent=s.last_auto_check||'Noch nie';nextcheck.textContent=s.next_auto_check||'–';quickAuto.textContent=s.auto?'AN':'AUS';quickAuto.className=s.auto?'green':'red';quickScan.textContent='Geprüfte Werte: '+(s.scanned_total||0)+' / '+(s.watch?.length||0);freshness.textContent=(s.position_rows||[]).some(x=>!x.data_ok)?'⚠️ Einige Kurse veraltet':'✓ Positionskurse aktuell';countdownTick();showTab(activeTab);
 scaninfo.textContent='Analysierte Werte im aktuellen Scan-Speicher: '+(s.scanned_total||0)+' / '+(s.watch?.length||0)+' · API-Key: '+(s.api_key_source||'–');
  const stocks=(s.market||[]);
  const chanceSort=localStorage.getItem('chanceSort')||'score';
  const rank=x=>x.stage==='🚀 AUSBRUCH AUS DEM KELLER'?3:/FRÜHSIGNAL|SCHNELL BEOBACHTEN/i.test(x.stage||x.signal||'')?2:x.score>=75?1:0;
  stocks.sort((a,b)=>chanceSort==='az'?String(a.symbol).localeCompare(String(b.symbol)):chanceSort==='rocket'?rank(b)-rank(a)||b.score-a.score:chanceSort==='signal'?rank(b)-rank(a)||b.score-a.score:b.score-a.score);
  radar.innerHTML=stocks.length?stocks.map(x=>x.error?`<div class="trade"><b>${esc(x.symbol)}</b><span class="red">Fehler</span><span>${esc(x.error)}</span></div>`:`<div class="trade"><b title="${esc((s.names||{})[x.symbol]||x.symbol)}" style="cursor:help">${esc(x.symbol)}</b><span>${euro(x.price)}</span><span class="${x.score>=75?'green':x.score>=55?'yellow':'red'}">${x.score}/100</span><span>${esc(x.risk)} · ${Number(x.mom||0).toFixed(2)}% / 75 Min.</span><span><b class="${x.stage==='🚀 AUSBRUCH AUS DEM KELLER'?'signal-rocket':/FRÜHSIGNAL|SCHNELL BEOBACHTEN/i.test(x.stage||x.signal||'')?'signal-hot':''}">${esc(x.stage==='🚀 AUSBRUCH AUS DEM KELLER'?'🚀 AUSBRUCH AUS DEM KELLER':x.signal)}</b><small>${esc(x.stage||'')}</small><div class="row"><button onclick="buy('${esc(x.symbol)}')">Virtuell kaufen</button><button onclick="favorite('${esc(x.symbol)}')">${(s.favorites||[]).includes(x.symbol)?'★':'☆'}</button><button onclick="chart('${esc(x.symbol)}')">Chart</button></div></span></div>`).join(''):'Noch keine Marktdaten.';
  favorites.innerHTML=(s.favorites||[]).map(x=>`<span style="display:inline-block;margin:5px"><b title="${esc((s.names||{})[x]||x)}">${esc(x)}</b> <button onclick="favorite('${esc(x)}')">Entfernen</button> <button onclick="chart('${esc(x)}')">Chart</button></span>`).join('')||'Noch keine Favoriten.';
  alerts.innerHTML=(s.alerts||[]).slice(-12).reverse().map(x=>`<div>${esc(x.time)} · <b>${esc(x.symbol)}</b> · ${esc(x.stage)}</div>`).join('')||'Noch keine neuen Frühwarnungen.';
  const closed=(s.history||[]).filter(x=>typeof x.pnl==='number'); const wins=closed.filter(x=>x.pnl>0);const net=closed.reduce((a,x)=>a+x.pnl,0);
  const today=new Date().toLocaleDateString('de-DE');const todays=closed.filter(x=>x.time&&x.time.startsWith(today));const dailyNet=todays.reduce((a,x)=>a+x.pnl,0);const dailyWins=todays.filter(x=>x.pnl>0).length;const dailyInfo='Heute: '+todays.length+' Verkäufe · '+dailyWins+' Gewinne · '+(todays.length?(100*dailyWins/todays.length).toFixed(1):'–')+' % Trefferquote · '+euro(dailyNet)+' | ';stats.textContent=dailyInfo+(closed.length?`${closed.length} abgeschlossene Trades · ${wins.length} Gewinne · Trefferquote ${(100*wins.length/closed.length).toFixed(1)} % · Ergebnis ${euro(net)}`:'Noch keine abgeschlossenen Trades mit Ergebnisdaten.');

 const rows=[...(s.position_rows||[])]; const sortBy=document.getElementById('depotSort').value;
 if(sortBy==='name')rows.sort((a,b)=>a.symbol.localeCompare(b.symbol)); else if(sortBy==='score')rows.sort((a,b)=>(b.score??-1)-(a.score??-1));else rows.sort((a,b)=>b.pnlpct-a.pnlpct);
 depotCount.textContent=rows.length;
 positions.innerHTML=rows.length?rows.map(x=>`<tr>
<td data-label="Aktie"><button class="linkbutton" onclick="chart('${esc(x.symbol)}')">📈 ${esc(x.symbol)}</button><small>${esc((s.names||{})[x.symbol]||'')}</small></td>
<td data-label="Kurs">${euro(x.price)}<small class="${x.data_ok?'green':'yellow'}">${x.data_ok?'Kurs geprüft':'Kurs veraltet'} · ${x.age_seconds==null?'unbekannt':Math.round(x.age_seconds)+' s'}</small></td>
<td data-label="Einstieg">${euro(x.entry)}</td>
<td data-label="Investiert">${euro(x.cost)}</td>
<td data-label="G/V €" class="${x.pnl>=0?'green':'red'}">${euro(x.pnl)}</td>
<td data-label="G/V %" class="${x.pnlpct>=0?'green':'red'}">${x.pnlpct.toFixed(2)} %</td>
<td data-label="Signal"><span class="signal ${x.decision==='VERKAUFEN'?'sell':x.decision==='BEOBACHTEN'?'warning':''}">${esc(x.decision)}</span><small title="${esc(x.reason)}">${esc(x.reason).slice(0,55)}</small></td>
<td data-label="Aktionen"><div class="depot-actions">${isAllowedDisplay(x.symbol)?`<button onclick="buy('${esc(x.symbol)}')">Kaufen</button>`:''}<button class="danger" onclick="quickSell('${esc(x.symbol)}')">Verkaufen</button><button class="secondary" onclick="chart('${esc(x.symbol)}')">Chart</button><button class="secondary" onclick="toggleManagement('${esc(x.symbol)}')">${x.auto_manage?'🤖 Bot AN':'🔒 Bot AUS'}</button></div>${x.manual_qty>0&&x.auto_manage?'<small>Gemischte Verwaltung</small>':''}</td>
</tr>`).join(''):'<tr><td colspan="8">Keine offenen virtuellen Positionen.</td></tr>';
 totalResult.textContent=(pp>=0?'+':'')+euro(pp);totalResult.className='big '+(pp>=0?'green':'red');nextMini.textContent=s.next_auto_check||'–';
 const candidates=Object.values(s.scan_results||{}).filter(x=>x&&x.price&&x.score!=null&&isAllowedDisplay(x.symbol)).sort((a,b)=>b.score-a.score).slice(0,5);
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
async function buy(s){if(!isAllowedDisplay(s)){msg('Hebelprodukt: Kauf gesperrt.',true);return}if(!confirm(s+' für bis zu '+euro(S.per_trade)+' virtuell kaufen? Bei -4 % wären das ungefähr '+euro(S.per_trade*.04)+' Verlust (ohne Gebühren).'))return;try{const old=(S.positions||[]).filter(p=>p.symbol===s).reduce((n,p)=>n+Number(p.cost||0),0);const next=await api('/api/buy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:s})});render(next);const now=(next.positions||[]).filter(p=>p.symbol===s).reduce((n,p)=>n+Number(p.cost||0),0);msg(now>old?s+' virtuell gekauft.':s+' wurde nicht gekauft – bitte Kurs und Budget prüfen.',now<=old)}catch(e){msg('Fehler: '+e.message,true)}}
async function favorite(s){try{S=await api('/api/favorite',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:s})});render(S)}catch(e){msg(e.message,true)}}
function sortChances(v){localStorage.setItem('chanceSort',v);document.getElementById('chanceSortPanel').hidden=true;render(S)}
async function toggleManagement(sym){const p=(S.position_rows||[]).find(x=>x.symbol===sym);if(!p)return;const enabled=!p.auto_manage;if(!confirm(sym+' · '+(enabled?'Automatischen Verkauf erlauben?':'Automatische Verkäufe sperren?')))return;try{S=await api('/api/management',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:sym,enabled})});render(S)}catch(e){msg(e.message,true)}}
async function quickSell(sym){const x=(S.position_rows||[]).find(p=>p.symbol===sym);if(!x)return;const v=prompt(sym+' · Wie viel verkaufen? 25, 50 oder 100 Prozent','100');if(v===null)return;const pct=Number(v);if(![25,50,100].includes(pct)){msg('Nur 25 %, 50 % oder 100 % auswählen.',true);return}if(!confirm(sym+' · '+pct+' % virtuell verkaufen?'))return;await submitSell(sym,pct)}
let openChartSymbol=null,openChartRange='1T';let liveChartPoints={};
function closeChart(){document.getElementById('chartModal').hidden=true;openChartSymbol=null}
function chartRange(v){openChartRange=v;drawChartModal()}
function drawChartModal(){if(!openChartSymbol)return;const sym=openChartSymbol;const x=(S.scan_results||{})[sym]||(S.market||[]).find(y=>y.symbol===sym)||{};const q=LIVE_QUOTES_UI[sym];const fresh=q&&Date.now()/1000-Number(q.seen||0)<=20;if(fresh){const arr=liveChartPoints[sym]||(liveChartPoints[sym]=[]);if(!arr.length||arr[arr.length-1].t!==q.seen){arr.push({t:q.seen,p:Number(q.price)});if(arr.length>100)arr.shift()}}document.getElementById('modalChartTitle').textContent='📈 '+sym;document.getElementById('modalLive').textContent=fresh?'Alpaca IEX · '+euro(q.price)+' · vor '+Math.round(Date.now()/1000-q.seen)+' s':'Kein aktueller IEX-Livekurs verfügbar';const a=(x.chart||[]).map(Number).filter(v=>Number.isFinite(v)&&v>0);const liveSeries=(liveChartPoints[sym]||[]).map(v=>v.p).filter(v=>Number.isFinite(v)&&v>0);const note=document.getElementById('modalChartNote');const svg=document.getElementById('modalChartSvg');note.textContent=openChartRange==='1T'?'15-Minuten-Kerzen · soweit vorhanden':'Für '+openChartRange+' liegen derzeit keine vollständigen historischen Daten vor; gezeigt werden nur verfügbare 15-Minuten-Kerzen';if(liveSeries.length>1){a.splice(0,a.length,...liveSeries);note.textContent='Live-Verlauf aus Alpaca-IEX-Ticks seit Öffnen dieser Sitzung · '+a.length+' Kurswerte; historische Zeiträume separat nicht vollständig verfügbar'}if(a.length===1){a.push(a[0]);note.textContent+=' · Bisher nur ein Kurswert'}if(a.length<2){svg.innerHTML='<text x="20" y="90" fill="#eaf1ff">Noch keine Kursdaten verfügbar.</text>';return}const entry=Number((S.position_rows||[]).find(p=>p.symbol===sym)?.entry||0);const lo=Math.min(...a,entry>0?entry:Infinity),hi=Math.max(...a,entry>0?entry:0),r=hi-lo||1;const points=a.map((v,i)=>(45+i*530/(a.length-1))+','+(145-(v-lo)/r*115)).join(' ');const ey=145-(entry-lo)/r*115;svg.innerHTML='<polyline points="'+points+'" fill="none" stroke="#42df91" stroke-width="3"/>'+(entry>0?'<line x1="45" x2="575" y1="'+ey+'" y2="'+ey+'" stroke="#ffd15c" stroke-dasharray="6 4"/>':'')}
function chart(s){openChartSymbol=s;openChartRange='1T';document.getElementById('chartModal').hidden=false;drawChartModal();return;const x=(S.market||[]).find(x=>x.symbol===s)||((S.scan_results||{})[s]);chartTitle.textContent=s+' · '+((S.names||{})[s]||'')+' · letzte bis zu 30 Kurspunkte';const a=x?.chart||[];if(a.length<2){priceChart.innerHTML='';chartTitle.textContent+=' · Noch kein Kursverlauf verfügbar';return}const lo=Math.min(...a),hi=Math.max(...a),r=hi-lo||1;const points=a.map((v,i)=>`${50+i*535/(a.length-1)},${145-(v-lo)/r*115}`).join(' ');const step=15;priceChart.innerHTML=`<line x1="50" y1="30" x2="50" y2="145" stroke="#9db0c7"/><line x1="50" y1="145" x2="585" y2="145" stroke="#9db0c7"/><text x="2" y="34" fill="#eaf1ff" font-size="11">${hi.toFixed(2)}</text><text x="2" y="145" fill="#eaf1ff" font-size="11">${lo.toFixed(2)}</text><text x="50" y="170" fill="#eaf1ff" font-size="11">älter</text><text x="530" y="170" fill="#eaf1ff" font-size="11">aktuell</text><polyline points="${points}" fill="none" stroke="#42df91" stroke-width="3"/>`+a.map((v,i)=>`<circle cx="${50+i*535/(a.length-1)}" cy="${145-(v-lo)/r*115}" r="6" fill="transparent"><title>Kerze ${i+1}/${a.length}: ${v.toFixed(3)} · Abstand zum neuesten Punkt ${(a.length-i-1)*15} Min.</title></circle>`).join('');}
function showDepotChart(sym){
 const x=(S.scan_results||{})[sym]||(S.market||[]).find(y=>y.symbol===sym);
 const panel=document.getElementById('depotChartPanel'),svg=document.getElementById('depotPriceChart');
 const pos=(S.position_rows||[]).find(y=>y.symbol===sym);
 panel.style.display='block';
 document.getElementById('depotChartTitle').textContent='📈 '+sym+' · Kursverlauf';
 const a=(x?.chart||[]).filter(v=>Number.isFinite(Number(v))&&Number(v)>0).map(Number);
 document.getElementById('depotChartNote').textContent='Bis zu 30 historische 15-Minuten-Kerzen · Einstieg '+(pos?euro(pos.entry):'unbekannt')+' · Kein Live-Chart';
 if(a.length<2){svg.innerHTML='<text x="20" y="90" fill="#eaf1ff">Kein verlässlicher Kursverlauf verfügbar.</text>';panel.scrollIntoView({behavior:'smooth',block:'center'});return;}
 const entry=Number(pos?.entry),lo=Math.min(...a,entry>0?entry:Infinity),hi=Math.max(...a,entry>0?entry:0),range=hi-lo||1;
 const pts=a.map((v,i)=>(50+i*535/(a.length-1))+','+(145-(v-lo)/range*115)).join(' ');
 const ey=145-(entry-lo)/range*115;
 svg.innerHTML='<line x1="50" y1="145" x2="585" y2="145" stroke="#9db0c7"/><polyline points="'+pts+'" fill="none" stroke="#42df91" stroke-width="3"/>'+(Number.isFinite(entry)&&entry>0?'<line x1="50" y1="'+ey+'" x2="585" y2="'+ey+'" stroke="#ffd15c" stroke-dasharray="6 4"/><text x="52" y="'+Math.max(12,ey-5)+'" fill="#ffd15c" font-size="11">Einstieg '+entry.toFixed(2)+'</text>':'');
 panel.scrollIntoView({behavior:'smooth',block:'center'});
}
async function searchStock(){try{let q=stockSearch.value.trim();if(!q)return;searchResult.textContent='Suche läuft …';SEARCH=await api('/api/search?q='+encodeURIComponent(q));searchResult.innerHTML=SEARCH.error?esc(SEARCH.error):`<p><b>${esc(SEARCH.symbol)}</b> – ${esc(SEARCH.name)} · Kurs ${euro(SEARCH.price)} · Score ${SEARCH.score}/100</p><button onclick="buySearch()">Für ${euro(S.per_trade)} virtuell kaufen</button><button onclick="favorite('${esc(SEARCH.symbol)}')">☆ Beobachten</button>`}catch(e){searchResult.textContent=e.message}}
async function buySearch(){if(!SEARCH||SEARCH.error)return;await buy(SEARCH.symbol)}
async function sell(s){
 if(!(S.position_rows||[]).find(p=>p.symbol===s)?.data_ok){msg('Verkauf noch nicht möglich: Kurs veraltet. Bitte Markt aktualisieren und erneut versuchen.',true);return}
 if(!confirm('Wirklich die GESAMTE Position '+s+' virtuell verkaufen?'))return;
 await submitSell(s,100);
}
async function partialSell(s){
 const x=(S.position_rows||[]).find(p=>p.symbol===s);
 if(!x){msg('Position nicht gefunden.',true);return}
 if(!x.data_ok){msg('Teilverkauf noch nicht möglich: Kurs veraltet. Bitte Markt aktualisieren und erneut versuchen.',true);return}
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
async function toggleAuto(){msg('Die Automatik wird jetzt vollständig nach US-Börsenzeiten gesteuert.');}
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
load();refreshLive();
setInterval(()=>{
 if(!S.auto||autoCheckRunning)return;
 const due=!S._last_auto_ts || Date.now()/1000>=Number(S._last_auto_ts)+Number(S.auto_interval||300);
 if(due)autoTick();
},5000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden){countdownTick();load()}});
setInterval(()=>{if(!document.hidden&&!autoCheckRunning)load()},30000);

</script></body></html>"""


# Alpaca IEX live stream: one server-side connection, no secrets in the browser.
# Standard-library WebSocket client avoids extra Render dependencies.
import socket, ssl, base64, hashlib, struct
LIVE_QUOTES={}
LIVE_LOCK=threading.RLock()
LIVE_STATUS={'connected':False,'message':'Verbinde ...','updated':0}
LIVE_MAX_SYMBOLS=30
LIVE_SUBSCRIBED=[]

def alpaca_symbols():
    try:
        d=load()
        held=[p.get('symbol') for p in d.get('positions',[])]
        favorites=d.get('favorites',[])
        watch=d.get('watch',[])
        return list(dict.fromkeys(x for x in held+favorites+watch
                                  if isinstance(x,str) and product_is_allowed(x,d)
                                  and '/' not in x and x!='MNQ1!' and x not in SPOT_CRYPTO))[:LIVE_MAX_SYMBOLS]
    except Exception:
        return ['AAPL','MSFT','NVDA','TSLA']

def ws_send(sock, obj):
    payload=json.dumps(obj,separators=(',',':')).encode()
    mask=os.urandom(4)
    n=len(payload)
    head=bytes([0x81,0x80|n]) if n<126 else (bytes([0x81,0x80|126])+struct.pack('!H',n) if n<65536 else bytes([0x81,0x80|127])+struct.pack('!Q',n))
    sock.sendall(head+mask+bytes(c^mask[i%4] for i,c in enumerate(payload)))

def ws_read_exact(sock,n):
    b=bytearray()
    while len(b)<n:
        part=sock.recv(n-len(b))
        if not part: raise ConnectionError('WebSocket geschlossen')
        b.extend(part)
    return bytes(b)

def ws_recv(sock):
    a,b=ws_read_exact(sock,2)
    opcode=a&15
    n=b&127
    if n==126: n=struct.unpack('!H',ws_read_exact(sock,2))[0]
    if n==127: n=struct.unpack('!Q',ws_read_exact(sock,8))[0]
    if n>2000000: raise ValueError('WebSocket-Nachricht zu groß')
    mask=ws_read_exact(sock,4) if b&128 else None
    data=ws_read_exact(sock,n)
    if mask: data=bytes(c^mask[i%4] for i,c in enumerate(data))
    return opcode,data

def alpaca_stream_loop():
    key=os.environ.get('ALPACA_API_KEY','').strip()
    secret=os.environ.get('ALPACA_SECRET_KEY','').strip()
    if not key or not secret:
        LIVE_STATUS.update(connected=False,message='Alpaca-Schlüssel fehlen')
        return
    while True:
        sock=None
        try:
            raw=socket.create_connection(('stream.data.alpaca.markets',443),timeout=15)
            sock=ssl.create_default_context().wrap_socket(raw,server_hostname='stream.data.alpaca.markets')
            token=base64.b64encode(os.urandom(16)).decode()
            req=('GET /v2/iex HTTP/1.1\r\nHost: stream.data.alpaca.markets\r\n'
                 'Upgrade: websocket\r\nConnection: Upgrade\r\n'
                 'Sec-WebSocket-Key: '+token+'\r\nSec-WebSocket-Version: 13\r\n\r\n')
            sock.sendall(req.encode())
            hdr=bytearray()
            while b'\r\n\r\n' not in hdr and len(hdr)<8192:
                hdr.extend(sock.recv(1))
            if b' 101 ' not in bytes(hdr).split(b'\r\n',1)[0]:
                raise ConnectionError('Alpaca WebSocket Handshake fehlgeschlagen')
            expected=base64.b64encode(hashlib.sha1((token+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
            if expected.lower() not in bytes(hdr).lower(): raise ConnectionError('WebSocket-Antwort ungültig')
            sock.settimeout(30)
            ws_send(sock,{'action':'auth','key':key,'secret':secret})
            symbols=alpaca_symbols()
            ws_send(sock,{'action':'subscribe','trades':symbols})
            subscribed=tuple(symbols)
            with LIVE_LOCK: LIVE_SUBSCRIBED[:]=symbols
            LIVE_STATUS.update(connected=False,message='IEX-Authentifizierung läuft')
            last_update=time.time()
            while True:
                try:
                    op,data=ws_recv(sock)
                except socket.timeout:
                    raise ConnectionError('IEX-Verbindung ohne neue Nachrichten')
                if op==8: raise ConnectionError('Alpaca hat Verbindung beendet')
                if op==9:
                    mask=os.urandom(4)
                    sock.sendall(bytes([0x8A,0x80|len(data)])+mask+bytes(c^mask[i%4] for i,c in enumerate(data)))
                    continue
                if op!=1: continue
                messages=json.loads(data)
                if not isinstance(messages,list): messages=[messages]
                for msg in messages:
                    if msg.get('T')=='error': raise ConnectionError(str(msg.get('msg','Alpaca-Fehler')))
                    if msg.get('T')=='success' and msg.get('msg')=='authenticated': LIVE_STATUS.update(connected=True,message='Alpaca IEX authentifiziert')
                    if msg.get('T')!='t': continue
                    sym=msg.get('S')
                    price=msg.get('p')
                    if not sym or not isinstance(price,(int,float)) or price<=0: continue
                    ts=msg.get('t')
                    try: seen=datetime.fromisoformat(ts.replace('Z','+00:00')).timestamp()
                    except Exception: seen=time.time()
                    with LIVE_LOCK: LIVE_QUOTES[sym]={'price':price,'seen':seen,'source':'Alpaca IEX'}
                    LIVE_STATUS['updated']=time.time()
                if time.time()-last_update>20:
                    new=tuple(alpaca_symbols())
                    if new!=subscribed:
                        ws_send(sock,{'action':'unsubscribe','trades':list(subscribed)})
                        ws_send(sock,{'action':'subscribe','trades':list(new)})
                        subscribed=new
                        with LIVE_LOCK: LIVE_SUBSCRIBED[:]=new
                    last_update=time.time()
        except Exception as e:
            LIVE_STATUS.update(connected=False,message=str(e)[:160])
            with LIVE_LOCK: LIVE_SUBSCRIBED.clear()
            print('Alpaca live:',str(e)[:160],flush=True)
        finally:
            if sock:
                try: sock.close()
                except Exception: pass
        time.sleep(5)

def live_view():
    now=time.time()
    with LIVE_LOCK:
        quotes={k:dict(v) for k,v in LIVE_QUOTES.items() if 0<=now-float(v.get('seen',0))<=20}
        subscribed=list(LIVE_SUBSCRIBED)
    return {'quotes':quotes,'connected':LIVE_STATUS['connected'],
            'message':LIVE_STATUS['message'],'source':'Alpaca IEX (nur Teilmarkt)',
            'updated':LIVE_STATUS['updated'],'subscribed':subscribed,
            'subscribed_count':len(subscribed),'fresh_count':len(quotes),
            'last_trade_age_seconds':round(now-LIVE_STATUS['updated']) if LIVE_STATUS['updated'] else None}


# V8.3.13: Trade decisions use only fresh, authenticated IEX trades.
# Indicator scores still come from separate 15-minute candle analysis.
LIVE_PEAKS={}
LIVE_SAMPLES={}
LIVE_LAST_ACTION={}
LIVE_LAST_TICK={}
LIVE_BUY_COOLDOWN=3600
LIVE_EXIT_COOLDOWN=24*3600

def live_paper_step():
    if not in_auto_window() or not LIVE_STATUS.get('connected'): return
    now=time.time()
    with LIVE_LOCK:
        quotes={sym:dict(q) for sym,q in LIVE_QUOTES.items()
                if 0<=now-float(q.get('seen',0))<=20}
    if not quotes: return
    with AUTO_LOCK:
        d=load()
        if not d.get('auto'): return
        changed=False
        cooldown=d.setdefault('live_exit_cooldown',{})
        # A trade tick is not proof of a fresh indicator signal.
        for sym,q in quotes.items():
            if not product_is_allowed(sym,d): continue
            # One execution per distinct market tick, never per scheduler iteration.
            tick_ts=float(q['seen'])
            if tick_ts<=LIVE_LAST_TICK.get(sym,0): continue
            LIVE_LAST_TICK[sym]=tick_ts
            price=float(q['price'])
            if not math.isfinite(price) or price<=0: continue
            lots=[p for p in d.get('positions',[]) if p.get('symbol')==sym]
            if lots:
                lots=[p for p in lots if p.get('auto_manage',p.get('source','Automatik')!='Manuell')]
                if not lots: continue
                cost=sum(float(p['cost']) for p in lots)
                qty=sum(float(p['qty']) for p in lots)
                if cost<=0 or qty<=0: continue
                entry=cost/qty
                prior_peaks=[p.get('peak_price') for p in lots]
                reason=trailing_exit(lots,price)
                # Save only when the high-water mark advances, not on every tick.
                if any(p.get('peak_price')!=old for p,old in zip(lots,prior_peaks)): changed=True
                if reason:
                    execute_sell(d,sym,price,'IEX Live-Automatik',1.0,reason=reason,auto_only=True)
                    cooldown[sym]=now
                    LIVE_LAST_ACTION[sym]=now
                    LIVE_PEAKS.pop(sym,None)
                    changed=True
                continue
            if now-float(cooldown.get(sym,0))<LIVE_EXIT_COOLDOWN: continue
            if now-LIVE_LAST_ACTION.get(sym,0)<LIVE_BUY_COOLDOWN: continue
            x=d.get('scan_results',{}).get(sym,{})
            if not quote_is_fresh(x) or x.get('risk')=='Hoch': continue
            if not isinstance(x.get('score'),(int,float)) or not isinstance(x.get('mom'),(int,float)): continue
            # Fast breakout confirmation: two distinct IEX trades at least 10 s apart,
            # minimum 0.3% rise, in addition to a fresh high-score candle signal.
            samples=LIVE_SAMPLES.setdefault(sym,[])
            samples.append((now,price))
            samples[:]=[(t,p) for t,p in samples if now-t<=90][-90:]
            prior=[p for t,p in samples if now-t>=10]
            breakout=bool(prior) and price>=min(prior)*1.003
            if not breakout or float(x.get('score',0))<75 or float(x.get('mom',0))<=0: continue
            invested=sum(float(p['cost']) for p in d['positions'])
            amt=min(float(d['per_trade']),float(d['cash']),max(0,float(d['budget'])-invested))
            if amt<5: continue
            execute_buy(d,sym,price,amt,'IEX Live-Signal')
            LIVE_LAST_ACTION[sym]=now
            LIVE_PEAKS[sym]=price
            changed=True
        if changed: save(d)

def live_paper_loop():
    while True:
        try: live_paper_step()
        except Exception as e:
            print('Live paper check:',str(e)[:160],flush=True)
        time.sleep(1)

CACHE=[]

AUTO_INTERVAL=5*60
AUTO_LOCK=threading.RLock()

def berlin_now():
    return datetime.now(ZoneInfo('Europe/Berlin'))

def in_auto_window(now=None):
    # Regular US session; handles differing EU/US daylight saving transitions.
    now=(now or berlin_now()).astimezone(ZoneInfo('America/New_York'))
    return now.weekday()<5 and (9*60+30)<=now.hour*60+now.minute<16*60

def auto_due(d, now_ts=None):
    now_ts=now_ts or time.time()
    return now_ts-float(d.get('_last_auto_ts',0) or 0)>=AUTO_INTERVAL

def next_check_text(d):
    if not in_auto_window(): return 'Börse geschlossen'
    last=float(d.get('_last_auto_ts',0) or 0)
    if not last: return 'Jetzt'
    remain=max(0,int(AUTO_INTERVAL-(time.time()-last)))
    return 'Live-Überwachung · nächste Signalanalyse jetzt' if remain<=0 else f'Live-Überwachung · Signalanalyse in ca. {max(1,(remain+59)//60)} Min.'

def run_auto_check(force=False):
    global CACHE
    with AUTO_LOCK:
        d=load()
        scheduled=in_auto_window()
        if d.get('auto') != scheduled:
            d['auto']=scheduled
            d['next_auto_check']='Jetzt' if scheduled else 'Börse geschlossen'
            save(d)
        if not scheduled or not effective_key(d): return d
        if not force and not auto_due(d): 
            d['next_auto_check']=next_check_text(d); save(d); return d
        CACHE.clear(); CACHE.extend(market(d)); log_event(d,'Automatischer Markt-Scan ausgeführt.','SCAN')
        # Live paper trades are processed on fresh IEX ticks by live_paper_loop.
        # Do not place stale-candle automatic orders here.
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
    # Display the schedule immediately even before the next background tick.
    d['auto']=in_auto_window()
    d['next_auto_check']=next_check_text(d)
    if refresh: CACHE=market(d)
    val,rows=portfolio(d,list(d.get('scan_results',{}).values()))
    return {**d,'leveraged_positions':[p['symbol'] for p in d.get('positions',[]) if product_is_leveraged(p.get('symbol'),d)],'allowed_symbols':[x for x in set(d.get('scan_results',{}))|set(d.get('favorites',[])) if product_is_allowed(x,d)],'unverified_positions':[p['symbol'] for p in d.get('positions',[]) if not product_is_allowed(p.get('symbol'),d) and not product_is_leveraged(p.get('symbol'),d)],'key':'***' if effective_key(d) else '', 'value':val,'position_rows':rows,'market':[x for x in CACHE if product_is_allowed(x.get('symbol'),d)],'server_time':time.time(),'auto_interval':AUTO_INTERVAL,'storage_source':'Supabase' if REMOTE_ENABLED else 'Lokal','api_key_source':'Render' if (os.environ.get('TWELVE_DATA_API_KEY') or os.environ.get('twelve_data_api_key')) else ('App' if d.get('key') else 'Fehlt')}

def quote_is_fresh(x):
    if not isinstance(x,dict) or x.get('fetch_error') or 'price' not in x: return False
    try:
        return (time.time()-float(x.get('seen',0))<=900 and
                time.time()-float(x.get('candle_ts',0))<=1800 and
                math.isfinite(float(x['price'])) and float(x['price'])>0 and
                (not x.get('chart') or (all(math.isfinite(float(v)) and float(v)>0 for v in x['chart'][-5:]) and
                0.5<=float(x['price'])/float(x['chart'][-1])<=1.5)))
    except (TypeError,ValueError,OverflowError): return False

def auto_step(d):
    global CACHE
    if not d['auto'] or not CACHE or not in_auto_window(): return
    try: usd_eur_rate(d)
    except Exception: pass
    q={x['symbol']:x for x in CACHE if quote_is_fresh(x)}
    weak=d.setdefault('weak_trend_checks',{})
    cooldown=d.setdefault('rocket_cooldown',{})
    for p in list({p['symbol']:p for p in d['positions']}.values()):
        sym=p['symbol']
        if sym=='MNQ1!' and (not d.get('usd_eur_rate') or time.time()-float(d.get('usd_eur_rate_ts',0) or 0)>3600): continue
        x=q.get(sym)
        if not x: continue
        lots=[lot for lot in d['positions'] if lot['symbol']==sym and lot.get('auto_manage',lot.get('source','Automatik')!='Manuell')]
        if not lots: continue
        ch=(sum((x['price']-float(lot['entry']))*2*int(lot.get('contracts',4))*float(d.get('usd_eur_rate',0)) for lot in lots)/sum(lot['cost'] for lot in lots)) if sym=='MNQ1!' else x['price']*sum(lot['qty'] for lot in lots)/sum(lot['cost'] for lot in lots)-1
        chart=x.get('chart',[])
        # Confirmation must use two distinct fresh market checks, not repeated stale observations.
        down=(x.get('score',100)<45 and len(chart)>=10 and
              chart[-1]<sum(chart[-5:])/5<sum(chart[-10:])/10 and
              float(x.get('mom',0))<0)
        weak[sym]=min(2,weak.get(sym,0)+1) if down else 0
        reason=None
        reason=trailing_exit(lots,x['price'])
        if reason is None and weak[sym]>=2 and ch<0:
            reason='Score unter 45 und Abwärtstrend zweimal bestätigt'
        if reason:
            execute_sell(d,sym,x['price'],'Automatik',1.0,reason=reason,auto_only=True)
            weak.pop(sym,None)
    invested=sum(p['cost'] for p in d['positions'])
    for x in CACHE:
        sym=x.get('symbol')
        if not product_is_allowed(sym,d): continue  # Keine neuen Hebelprodukte oder unklassifizierten Werte
        if not quote_is_fresh(x) or (sym!='MNQ1!' and x.get('risk')=='Hoch'): continue
        if any(p['symbol']==sym for p in d['positions']): continue
        rocket=(x.get('stage')=='🚀 AUSBRUCH AUS DEM KELLER' and x.get('score',0)>=80
                and x.get('mom',0)>0 and len(x.get('chart',[]))>=15)
        standard=(x.get('score',0)>=75 and float(x.get('mom',0) or 0)>0 and
                  len(x.get('chart',[]))>=10 and
                  x['chart'][-1]>sum(x['chart'][-5:])/5>sum(x['chart'][-10:])/10)
        if not (rocket or standard): continue
        # Do not immediately repurchase a rocket repeatedly after an automatic exit.
        if rocket and time.time()-float(cooldown.get(sym,0))<24*3600: continue
        amt=min(d['per_trade'],d['cash'],max(0,d['budget']-invested))
        if amt>=5:
            if sym=='MNQ1!':
                try: usd_eur_rate(d)
                except Exception: continue
            execute_buy(d,sym,x['price'],amt,'Raketen-Radar' if rocket else 'Automatik')
            if rocket: cooldown[sym]=time.time()
            invested+=amt

def trailing_exit(lots, price):
    """Persist the high-water mark per automatically managed lot.
    No fixed +7% profit-taking. Initial -4% stop remains active.
    Profit protection starts at +7%, with 3% peak drawdown;
    strong momentum above +12% receives 4% breathing room.
    """
    if not lots or not math.isfinite(float(price)) or price<=0:
        return None
    for lot in lots:
        entry=float(lot['entry'])
        if entry<=0: continue
        lot['peak_price']=max(entry,float(lot.get('peak_price') or entry),float(price))
    entry=sum(float(p['cost']) for p in lots)/sum(float(p['qty']) for p in lots)
    if price<=entry*.96: return 'Stop-Loss bei -4 %'
    armed=[p for p in lots if float(p.get('peak_price',0))>=float(p['entry'])*1.07]
    if not armed: return None
    # Use the highest *aggregate* portfolio entry, avoiding unrelated manual lots.
    peak=sum(float(p['peak_price'])*float(p['qty']) for p in lots)/sum(float(p['qty']) for p in lots)
    gap=.04 if peak>=entry*1.12 else .03
    if price<=peak*(1-gap):
        return f'Nachgezogene Gewinnsicherung: {gap*100:.0f} % unter Hoch'
    return None


def execute_buy(d,sym,price,amt,src='Manuell'):
    if not product_is_allowed(sym,d):
        raise ValueError('Kauf gesperrt: Hebelprodukt oder nicht eindeutig als ungehebelte Aktie/Spot-Krypto geprüft.')
    if not math.isfinite(float(price)) or float(price)<=0: raise ValueError('Ungültiger Kaufkurs.')
    amt=min(float(amt),d['cash'])
    if amt<=0:return
    contracts=4 if sym=='MNQ1!' else None
    d['positions'].append({'symbol':sym,'entry':price,'peak_price':price,'qty':amt/price,'cost':amt,'source':src,'auto_manage':src!='Manuell',**({'contracts':contracts} if contracts else {})});d['cash']-=amt
    desc=f'{src}: KAUF {sym} · {amt:.2f} € @ {price:.2f}'+(' · 4 MNQ-Kontrakte (Paper, 2 USD/Punkt/Kontrakt)' if sym=='MNQ1!' else '')
    d['history'].append({'time':time.strftime('%d.%m.%Y %H:%M'),'text':desc}); log_event(d,desc,'TRADE')

def execute_sell(d,sym,price,src='Manuell',fraction=1.0,reason=None,auto_only=False):
    if not math.isfinite(price) or price<=0: raise ValueError('Ungültiger Verkaufskurs.')
    if not math.isfinite(fraction) or not 0<fraction<=1: raise ValueError('Verkaufsanteil muss über 0 und höchstens 100 % sein.')
    lots=[p for p in d['positions'] if p['symbol']==sym and (not auto_only or p.get('auto_manage',p.get('source','Automatik')!='Manuell'))]
    if not lots: raise ValueError('Keine für diesen Verkauf freigegebene Position für '+sym)
    total_cost=sum(p['cost'] for p in lots)
    total_qty=sum(p['qty'] for p in lots)
    sold_qty=total_qty*fraction
    sold_cost=total_cost*fraction
    proceeds=sold_qty*price
    if sym=='MNQ1!':
        pnl=sum((price-float(p['entry']))*2*int(p.get('contracts',4))*usd_eur_rate(d) for p in lots)*fraction
        proceeds=sold_cost+pnl
    else:
        pnl=proceeds-sold_cost
    if fraction>=1-1e-10:
        d['positions']=[p for p in d['positions'] if p not in lots]
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
  elif path=='/api/live':self.sendj(live_view())
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
    if not product_is_allowed(symbol,d): raise ValueError('Produkt nicht freigegeben: Hebelprodukt oder nicht als ungehebelte Aktie/Spot-Krypto bestätigt.')
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
    d['auto']=in_auto_window();d['next_auto_check']=next_check_text(d)
   elif self.path=='/api/reset':
    key=d.get('key',''); oldevents=d.get('event_log',[]); d=copy.deepcopy(DEFAULT);d['key']=key;d['event_log']=oldevents[-250:];log_event(d,'Paper-Test zurückgesetzt; API-Konfiguration beibehalten.','SYSTEM')
   elif self.path=='/api/refresh':
    if not effective_key(d): raise ValueError('Twelve Data API-Key fehlt.')
    CACHE.clear();CACHE.extend(market(d));log_event(d,'Markt manuell aktualisiert.','SCAN')
    if not CACHE: raise ValueError('Keine Marktdaten erhalten.')
    if d.get('auto') and in_auto_window():
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
   elif self.path=='/api/management':
    b=self.body();sym=str(b.get('symbol','')).upper();enabled=b.get('enabled');lot_index=b.get('lot_index')
    if not isinstance(enabled,bool): raise ValueError('Ungültige Verwaltungseinstellung.')
    lots=[p for p in d['positions'] if p['symbol']==sym]
    if not lots: raise ValueError('Position nicht gefunden.')
    if lot_index is not None:
     if not isinstance(lot_index,int) or not 0<=lot_index<len(lots): raise ValueError('Ungültige Kaufposition.')
     lots=[lots[lot_index]]
    for p in lots:p['auto_manage']=enabled
    log_event(d,('Automatik freigegeben' if enabled else 'Selbstverwaltung aktiviert')+' für '+sym,'SYSTEM')
   elif self.path=='/api/buy':
    sym=self.body()['symbol'];x=next((x for x in CACHE if x.get('symbol')==sym and 'price' in x and quote_is_fresh(x)),None)
    if not x:
     with LIVE_LOCK:
      live=dict(LIVE_QUOTES.get(sym,{ }))
     if (product_is_allowed(sym,d) and live and
         0<=time.time()-float(live.get('seen',0))<=20 and
         math.isfinite(float(live.get('price',0))) and float(live['price'])>0):
      x=live
    if not x: raise ValueError('Kein ausreichend frischer Börsenkurs. Bitte später erneut prüfen.')
    # Manual buying intentionally does not depend on scanner score; instrument and quote checks remain mandatory.
    invested=sum(p['cost'] for p in d['positions']);amt=min(d['per_trade'],d['cash'],max(0,d['budget']-invested))
    if amt<1: raise ValueError('Nicht genügend freies Kapital oder Budget.')
    if not product_is_allowed(sym,d): raise ValueError('Kauf gesperrt: Hebelprodukt oder Produktart nicht verifiziert.')
    execute_buy(d,sym,x['price'],amt)
   elif self.path=='/api/sell':
    b=self.body();sym=b['symbol'];percent=float(b.get('percent',100));x=next((x for x in CACHE if x.get('symbol')==sym and 'price' in x and quote_is_fresh(x)),None);p=next((p for p in d['positions'] if p['symbol']==sym),None);
    # Bestehende Hebelpositionen bleiben zum Verkauf zugänglich.
    if not p: raise ValueError('Keine offene Position für '+sym)
    if not x:
     if not effective_key(d): raise ValueError('Kein API-Schlüssel für die Kursabfrage vorhanden.')
     fresh=quote_symbol(sym,effective_key(d))
     if not quote_is_fresh(fresh): raise ValueError('Kein ausreichend aktueller Börsenkurs verfügbar. Verkauf nicht ausgeführt.')
     x=fresh
     d.setdefault('scan_results',{})[sym]=fresh
     CACHE[:]=[q for q in CACHE if q.get('symbol')!=sym]+[fresh]
    execute_sell(d,sym,x['price'],fraction=percent/100)
   save(d);self.sendj(view(d))
  except Exception as e:
   self.sendj({'error':str(e),**view(d)})
 def log_message(self,*a):pass

if __name__=='__main__':
 port=int(os.environ.get('PORT','10000'))
 print(f'Trading Radar läuft auf Port {port}')
 threading.Thread(target=scheduler_loop,daemon=True).start()
 threading.Thread(target=alpaca_stream_loop,daemon=True).start()
 threading.Thread(target=live_paper_loop,daemon=True).start()
 HTTPServer(('0.0.0.0',port),H).serve_forever()
