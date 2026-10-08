import json, os, math, time, urllib.parse, urllib.request, copy, threading
from datetime import datetime
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT=Path(__file__).parent
STATE=ROOT/'state.json'
UNIVERSE=['AAPL','MSFT','NVDA','AMZN','META','GOOGL','AVGO','TSLA','AMD','NFLX','ORCL','CRM','ADBE','INTC','QCOM','TXN','MU','AMAT','LRCX','KLAC','PANW','CRWD','NOW','PLTR','UBER','ABNB','BKNG','JPM','BAC','GS','MS','V','MA','AXP','WMT','COST','HD','LOW','NKE','MCD','SBUX','KO','PEP','PG','JNJ','LLY','MRK','ABBV','UNH','XOM','CVX','CAT','GE','BA','RTX','DE','NEE','LIN','BTC/USD','ETH/USD','MNQ1!']
DEFAULT={"cash":100.0,"start":100.0,"budget":100.0,"per_trade":20.0,"positions":[],"history":[],"watch":UNIVERSE,"key":"","auto":False,"last_auto_check":"Noch nie","next_auto_check":"–","scan_index":0,"scan_results":{},"scanned_total":0,"version":"V6-MNQ","mnq_contracts":4,"event_log":[]}
def load():
    if not STATE.exists(): STATE.write_text(json.dumps(copy.deepcopy(DEFAULT),indent=2))
    d=json.loads(STATE.read_text())
    for k,v in DEFAULT.items(): d.setdefault(k,copy.deepcopy(v))
    # Neue Scanner-Werte aus Updates auch in bestehende state.json übernehmen.
    for sym in UNIVERSE:
        if sym not in d['watch']: d['watch'].append(sym)
    d['version']='V6-MNQ'; d['mnq_contracts']=4
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
        q=td('/time_series?symbol='+urllib.parse.quote(sym)+'&interval=15min&outputsize=30',key)
        vals=q.get('values',[])
    if not vals: return {'symbol':sym,'error':q.get('message','Keine Marktdaten erhalten')[:120]}
    closes=[float(x['close']) for x in vals][::-1]
    if len(closes)<15: return {'symbol':sym,'error':'Zu wenige Kursdaten'}
    p=closes[-1]; ma5=sum(closes[-5:])/5; ma15=sum(closes[-15:])/15
    mom=(p/closes[-6]-1)*100
    rets=[closes[i]/closes[i-1]-1 for i in range(1,len(closes))]
    vol=(sum((x-sum(rets)/len(rets))**2 for x in rets)/max(1,len(rets)-1))**.5*100
    score=50+(12 if p>ma5 else -12)+(12 if ma5>ma15 else -12)+max(-16,min(16,mom*2))-min(12,vol*2)
    score=max(0,min(100,round(score)))
    risk='Niedrig' if vol<2 else ('Mittel' if vol<4 else 'Hoch')
    signal='KAUFEN' if score>=75 else ('BEOBACHTEN' if score>=55 else 'MEIDEN')
    return add_momentum_labels({'symbol':sym,'price':p,'score':score,'risk':risk,'signal':signal,'mom':round(mom,2),'vol':round(vol,2),'seen':time.time()}, closes)


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
    universe=d.get('watch') or UNIVERSE
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
        try: results[sym]=quote_symbol(sym,key)
        except Exception as e: results[sym]={'symbol':sym,'error':str(e)[:120],'seen':time.time()}
    d['scan_index']=i%len(universe); d['scan_results']=results
    d['scanned_total']=len([x for x in results.values() if 'price' in x])
    # Keep recent successful candidates; held positions always stay visible.
    vals=list(results.values())
    good=[x for x in vals if 'price' in x]
    errs=[x for x in vals if 'error' in x and x.get('symbol') in symbols]
    return sorted(good,key=lambda x:x.get('score',-1),reverse=True)[:15]+errs

def portfolio(d, quotes):
    qmap={x['symbol']:x for x in quotes if 'price' in x}
    val=d['cash']; rows=[]
    for pos in d['positions']:
        p=qmap.get(pos['symbol'],{}).get('price',pos['entry'])
        cur=pos['qty']*p; pnl=cur-pos['cost']; val+=cur
        pct=(p/pos['entry']-1)*100
        q=qmap.get(pos['symbol'],{})
        score=q.get('score')
        if pct<=-4: decision,reason='VERKAUFEN',f'Stop-Loss erreicht ({pct:+.2f} %)'
        elif pct>=7: decision,reason='VERKAUFEN',f'Gewinnziel erreicht ({pct:+.2f} %)'
        elif score is not None and score<45: decision,reason='VERKAUFEN',f'Score {score} unter 45'
        elif score is None: decision,reason='HALTEN','Noch keine aktuelle Scanner-Pruefung'
        else: decision,reason='HALTEN',f'Score {score}, Ergebnis {pct:+.2f} %'
        seen=q.get('seen')
        checked=datetime.fromtimestamp(seen,ZoneInfo('Europe/Berlin')).strftime('%d.%m. %H:%M') if seen else '–'
        rows.append({**pos,'price':p,'value':cur,'pnl':pnl,'pnlpct':pct,'score':score,'decision':decision,'reason':reason,'checked':checked})
    return val,rows

HTML=r"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trading Radar</title><style>
body{font-family:system-ui;background:#07111f;color:#eaf1ff;margin:0}header{padding:18px 5%;background:#0c1b2d;position:sticky;top:0}.wrap{max-width:1100px;margin:auto;padding:22px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}.card{background:#102238;border:1px solid #203b5b;border-radius:16px;padding:16px;margin-bottom:14px}.big{font-size:28px;font-weight:800}.green{color:#42df91}.red{color:#ff6677}.yellow{color:#ffd15c}button,input{font:inherit;border-radius:10px;padding:10px;border:1px solid #34506d}button{background:#19b873;color:white;font-weight:700;cursor:pointer}.danger{background:#c53e50}.muted{color:#9db0c7}.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.trade{display:grid;grid-template-columns:1.2fr .8fr .8fr .8fr .8fr;gap:8px;padding:10px 0;border-top:1px solid #233c58}#status{margin-top:10px;font-weight:700}@media(max-width:700px){.trade{grid-template-columns:1fr 1fr}.hideM{display:none}}
.price-up{color:#22c55e;font-weight:700}.price-down{color:#ef4444;font-weight:700}.price-flat{color:inherit;font-weight:700}</style></head><body><header><b>⚡ Trading Radar V6-MNQ</b> <span class="muted">Paper-Trading · kein Echtgeld</span></header><div class="wrap">
<div class="grid"><div class="card">Virtuelles Depot<div id="value" class="big">–</div><span id="pnl"></span></div><div class="card">Freies Kapital<div id="cash" class="big">–</div></div><div class="card">Offene Trades<div id="count" class="big">–</div></div><div class="card">Automatik<div id="auto" class="big">AUS</div></div></div>
<div class="card"><h3>Einstellungen</h3><div class="row"><input id="key" type="password" placeholder="Twelve Data API-Key"><button onclick="setKey()">API-Key speichern</button><label>Budget € <input id="budget" type="number" value="100" style="width:75px"></label><label>pro Trade € <input id="per" type="number" value="20" style="width:70px"></label><button onclick="settings()">Speichern</button><button onclick="toggleAuto()">Automatik AN/AUS</button><button class="danger" onclick="resetAll()">Test zurücksetzen</button></div><p class="muted">Die App handelt nur virtuell. Tipp: Hinterlege TWELVE_DATA_API_KEY später einmal bei Render; dann bleibt der Schlüssel bei Updates erhalten. Trades werden zusätzlich in diesem Browser gesichert und nach einem Deploy automatisch wiederhergestellt.</p><div id="status" class="muted">Bereit.</div><p class="muted">Automatik-Zeitfenster: Mo–Fr 14:30–22:00 Uhr (Deutschland), Prüfung höchstens alle 15 Minuten. Auf dem kostenlosen Render-Tarif kann der Dienst bei Inaktivität schlafen; solange diese Seite geöffnet ist, stößt sie die Prüfung regelmäßig an.</p><div class="row"><span>Letzte automatische Prüfung: <b id="lastcheck">–</b></span><span>Nächste Prüfung: <b id="nextcheck">–</b></span></div></div>
<div class="card"><h3>Virtuelles Kapital verwalten</h3>
<p class="muted">Ein- und Auszahlungen ändern nur dein freies virtuelles Kapital. Offene Trades bleiben bestehen. Das Handelsbudget wird separat eingestellt.</p>
<div class="row"><label>Betrag € <input id="capitalAmount" type="number" min="0.01" step="0.01" value="100" style="width:115px"></label>
<button onclick="changeCapital('deposit')">+ Einzahlen</button>
<button onclick="changeCapital('withdraw')">− Entnehmen</button></div>
<p class="muted">Startkapital für die Gewinnberechnung anpassen, ohne offene Trades zu schließen:</p>
<div class="row"><label>Neues Startkapital € <input id="newStart" type="number" min="0" step="0.01" value="100" style="width:115px"></label>
<button onclick="changeCapital('start')">Startkapital ändern</button></div></div>
<div class="card"><h3>Markt-Scanner · Top-Chancen</h3><p class="muted">Rotierender Scanner: pro Prüfung wird ein neuer Teil der Beobachtungsliste analysiert, um das API-Limit einzuhalten. Bereits geprüfte Kandidaten bleiben im Ranking. MNQ wird im Paper-Trading mit <b>4 Kontrakten</b> geführt. Frühwarnstufen: DIP → FRÜHSIGNAL → 🚀 AUSBRUCH AUS DEM KELLER.</p><div id="scaninfo" class="muted"></div><div id="radar">API-Key eintragen und „Markt aktualisieren“ drücken.</div><br><button id="refreshBtn" onclick="refreshMarket()">Markt aktualisieren</button></div>
<div class="card"><h3>Meine virtuellen Trades</h3><p class="muted">Automatische Verkaufsregeln: Gewinnmitnahme ab +7 % · Stop-Loss ab −4 % · Verkauf bei Score unter 45.</p><div id="positions"></div></div>
<div class="card"><h3>Protokoll</h3><button onclick="exportBackup()">Sicherung herunterladen</button><p class="muted">Bitte Sicherung vor jedem Update herunterladen. Render Free speichert Daten nicht dauerhaft.</p><div id="history" class="muted"></div><hr><div id="events" class="muted"></div></div>
</div><script>
let S={};
async function api(path,opt){
  let r=await fetch(path,opt);
  let data=await r.json();
  if(data.error) throw new Error(data.error);
  return data;
}
function euro(x){return Number(x).toLocaleString('de-DE',{style:'currency',currency:'EUR'})}
function msg(t,bad=false){status.textContent=t;status.className=bad?'red':'green'}
function backupState(s){try{localStorage.setItem('tradingRadarBackupV6',JSON.stringify({cash:s.cash,start:s.start,budget:s.budget,per_trade:s.per_trade,positions:s.positions,history:s.history,auto:s.auto,event_log:s.event_log,scan_results:s.scan_results,scan_index:s.scan_index}))}catch(e){}}
async function load(){try{S=await api('/api/state');let raw=localStorage.getItem('tradingRadarBackupV6');if(raw&&S.positions.length===0&&S.history.length===0){let b=JSON.parse(raw);if((b.positions&&b.positions.length)||(b.history&&b.history.length)){S=await api('/api/restore',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({backup:b})})}}render(S);backupState(S)}catch(e){msg('Fehler: '+e.message,true)}}
function render(s){
 backupState(s);
 value.textContent=euro(s.value);let pp=s.value-s.start;pnl.textContent=(pp>=0?'+':'')+euro(pp)+' seit Start';pnl.className=pp>=0?'green':'red';cash.textContent=euro(s.cash);count.textContent=s.positions.length;auto.textContent=s.auto?'AN':'AUS';auto.className='big '+(s.auto?'green':'red');budget.value=s.budget;per.value=s.per_trade;document.getElementById('newStart').value=s.start;lastcheck.textContent=s.last_auto_check||'Noch nie';nextcheck.textContent=s.next_auto_check||'–';
 scaninfo.textContent='Analysierte Werte im aktuellen Scan-Speicher: '+(s.scanned_total||0)+' / '+(s.watch?.length||0)+' · API-Key: '+(s.api_key_source||'–');
 radar.innerHTML=s.market?.length?s.market.map(x=>x.error?`<div class=trade><b>${x.symbol}</b><span class=red>Fehler</span><span>${x.error}</span></div>`:`<div class=trade><b>${x.symbol}</b><span>${euro(x.price)}</span><span class=${x.score>=75?'green':x.score>=55?'yellow':'red'}>${x.score}/100</span><span>${x.risk}</span><span><b>${x.signal}</b>${x.stage?`<br><small>${x.stage}</small>`:''} ${x.signal==='KAUFEN'?`<button onclick="buy('${x.symbol}')">virtuell kaufen</button>`:''}</span></div>`).join(''):'Noch keine Marktdaten.';
 positions.innerHTML=s.position_rows.length?s.position_rows.map(x=>`<div class=trade><b>${x.symbol}${x.contracts?` · ${x.contracts} Kontrakte`:''}</b><span>${euro(x.value)}</span><span class=${x.pnl>=0?'green':'red'}>${x.pnl>=0?'+':''}${euro(x.pnl)} (${x.pnlpct.toFixed(2)}%)</span><span>Einstieg ${euro(x.entry)} → aktuell <b class=${x.price>x.entry?'green':x.price<x.entry?'red':''}>${euro(x.price)}</b></span><span><b class=${x.decision==='VERKAUFEN'?'red':'green'}>${x.decision}</b><br><small>${x.reason}</small><br><small>Score ${x.score??'–'}/100 · geprüft ${x.checked||'–'}</small><br><button class=danger onclick="sell('${x.symbol}')">verkaufen</button></span></div>`).join(''):'Keine offenen virtuellen Trades.';
 document.getElementById('history').innerHTML=(s.history||[]).slice().reverse().slice(0,40).map(x=>`<div>${x.time} · ${x.text}</div>`).join('')||'Noch keine Trades.'; document.getElementById('events').innerHTML=(s.event_log||[]).slice().reverse().slice(0,40).map(x=>`<div>${x.time} · ${x.kind} · ${x.text}</div>`).join('')||'Noch keine Systemereignisse.';
}
function exportBackup(){const a=document.createElement('a');const data={...S,key:undefined,market:undefined,position_rows:undefined};const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});a.href=URL.createObjectURL(blob);a.download='trading-radar-sicherung-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
async function refreshMarket(){
 let b=document.getElementById('refreshBtn'); b.disabled=true; b.textContent='Aktualisiere …'; msg('Marktdaten werden geladen …');
 try{S=await api('/api/refresh',{method:'POST'});render(S);msg(S.auto?'Markt aktualisiert – Automatik wurde geprüft.':'Markt aktualisiert.')}
 catch(e){msg('Fehler beim Aktualisieren: '+e.message,true)}
 finally{b.disabled=false;b.textContent='Markt aktualisieren'}
}
async function buy(s){try{render(await api('/api/buy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:s})}));msg(s+' virtuell gekauft.')}catch(e){msg('Fehler: '+e.message,true)}}
async function sell(s){try{render(await api('/api/sell',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:s})}));msg(s+' virtuell verkauft.')}catch(e){msg('Fehler: '+e.message,true)}}
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
async function autoTick(){try{S=await api('/api/auto-check',{method:'POST'});render(S)}catch(e){console.log(e)}}
load();setInterval(autoTick,60000);
</script></body></html>"""

CACHE=[]

AUTO_INTERVAL=15*60
AUTO_LOCK=threading.Lock()

def berlin_now():
    return datetime.now(ZoneInfo('Europe/Berlin'))

def in_auto_window(now=None):
    now=now or berlin_now()
    mins=now.hour*60+now.minute
    return now.weekday()<5 and (14*60+30)<=mins<=(22*60)

def auto_due(d, now_ts=None):
    now_ts=now_ts or time.time()
    return now_ts-float(d.get('_last_auto_ts',0) or 0)>=AUTO_INTERVAL

def next_check_text(d):
    if not d.get('auto'): return 'Automatik AUS'
    now=berlin_now()
    if not in_auto_window(now): return 'Im nächsten Handelszeitfenster'
    last=float(d.get('_last_auto_ts',0) or 0)
    if not last: return 'Jetzt'
    remain=max(0,int(AUTO_INTERVAL-(time.time()-last)))
    return 'Jetzt' if remain<=0 else f'in ca. {max(1,(remain+59)//60)} Min.'

def run_auto_check(force=False):
    global CACHE
    with AUTO_LOCK:
        d=load()
        if not d.get('auto') or not effective_key(d): return d
        if not force and (not in_auto_window() or not auto_due(d)): 
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
    val,rows=portfolio(d,CACHE)
    return {**d,'key':'***' if effective_key(d) else '', 'value':val,'position_rows':rows,'market':CACHE,'api_key_source':'Render' if os.environ.get('TWELVE_DATA_API_KEY') else ('App' if d.get('key') else 'Fehlt')}

def auto_step(d):
    global CACHE
    if not d['auto'] or not CACHE: return
    q={x['symbol']:x for x in CACHE if 'price' in x}
    for p in list(d['positions']):
        x=q.get(p['symbol'])
        if not x: continue
        ch=x['price']/p['entry']-1
        if x['score']<45 or ch<=-.04 or ch>=.07:
            execute_sell(d,p['symbol'],x['price'],'Automatik')
    invested=sum(p['cost'] for p in d['positions'])
    for x in CACHE:
        # Wichtig: dieselbe Grenze wie das sichtbare KAUFEN-Signal.
        if x.get('score',0)>=75 and x.get('risk')!='Hoch' and not any(p['symbol']==x['symbol'] for p in d['positions']):
            amt=min(d['per_trade'],d['cash'],max(0,d['budget']-invested))
            if amt>=5:
                execute_buy(d,x['symbol'],x['price'],amt,'Automatik')
                invested+=amt

def execute_buy(d,sym,price,amt,src='Manuell'):
    amt=min(float(amt),d['cash'])
    if amt<=0:return
    contracts=4 if sym=='MNQ1!' else None
    d['positions'].append({'symbol':sym,'entry':price,'qty':amt/price,'cost':amt,**({'contracts':contracts} if contracts else {})});d['cash']-=amt
    desc=f'{src}: KAUF {sym} · {amt:.2f} € @ {price:.2f}'+(' · 4 MNQ-Kontrakte (Paper)' if sym=='MNQ1!' else '')
    d['history'].append({'time':time.strftime('%d.%m.%Y %H:%M'),'text':desc}); log_event(d,desc,'TRADE')

def execute_sell(d,sym,price,src='Manuell'):
    for p in list(d['positions']):
        if p['symbol']==sym:
            val=p['qty']*price;pnl=val-p['cost'];d['cash']+=val;d['positions'].remove(p)
            pct=(price/p['entry']-1)*100
            desc=f'{src}: VERKAUF {sym} @ {price:.2f} · Ergebnis {pnl:+.2f} € ({pct:+.2f} %)'; d['history'].append({'time':time.strftime('%d.%m.%Y %H:%M'),'text':desc}); log_event(d,desc,'TRADE')
            break

class H(BaseHTTPRequestHandler):
 def sendj(self,o,status=200):
  b=json.dumps(o).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',len(b));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  path=urllib.parse.urlparse(self.path).path.rstrip('/') or '/'
  if path in ('/','/index.html'):
   b=HTML.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',len(b));self.end_headers();self.wfile.write(b)
  elif path=='/api/state':self.sendj(view(load()))
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
    save(d);d=run_auto_check(False)
   elif self.path=='/api/restore':
    b=self.body(); backup=b.get('backup',{})
    for k in ('cash','start','budget','per_trade','positions','history','auto','event_log','scan_results','scan_index'):
     if k in backup: d[k]=backup[k]
    d['history'].append({'time':time.strftime('%d.%m.%Y %H:%M'),'text':'Browser-Sicherung nach Update wiederhergestellt.'})
   elif self.path=='/api/buy':
    sym=self.body()['symbol'];x=next((x for x in CACHE if x.get('symbol')==sym and 'price' in x),None)
    if x:
     invested=sum(p['cost'] for p in d['positions']);amt=min(d['per_trade'],d['cash'],max(0,d['budget']-invested));execute_buy(d,sym,x['price'],amt)
   elif self.path=='/api/sell':
    sym=self.body()['symbol'];x=next((x for x in CACHE if x.get('symbol')==sym and 'price' in x),None);p=next((p for p in d['positions'] if p['symbol']==sym),None);execute_sell(d,sym,x['price'] if x else p['entry']) if p else None
   save(d);self.sendj(view(d))
  except Exception as e:
   self.sendj({'error':str(e),**view(d)})
 def log_message(self,*a):pass

if __name__=='__main__':
 port=int(os.environ.get('PORT','10000'))
 print(f'Trading Radar läuft auf Port {port}')
 threading.Thread(target=scheduler_loop,daemon=True).start()
 HTTPServer(('0.0.0.0',port),H).serve_forever()