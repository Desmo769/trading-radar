import json, os, math, time, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT=Path(__file__).parent
STATE=ROOT/'state.json'
DEFAULT={"cash":100.0,"start":100.0,"budget":100.0,"per_trade":20.0,"positions":[],"history":[],"watch":["AAPL","MSFT","NVDA","AMZN","META","BTC/USD","ETH/USD"],"key":"","auto":False}

def load():
    if not STATE.exists(): STATE.write_text(json.dumps(DEFAULT,indent=2))
    d=json.loads(STATE.read_text());
    for k,v in DEFAULT.items(): d.setdefault(k,v)
    return d

def save(d): STATE.write_text(json.dumps(d,indent=2))

def td(path, key):
    url='https://api.twelvedata.com'+path+('&' if '?' in path else '?')+'apikey='+urllib.parse.quote(key)
    req=urllib.request.Request(url,headers={'User-Agent':'TradingRadar/1.0'})
    with urllib.request.urlopen(req,timeout=12) as r: return json.loads(r.read())

def market(d):
    out=[]
    if not d['key']: return out
    for sym in d['watch']:
        try:
            q=td('/time_series?symbol='+urllib.parse.quote(sym)+'&interval=1day&outputsize=30',d['key'])
            vals=q.get('values',[])
            closes=[float(x['close']) for x in vals][::-1]
            if len(closes)<15: continue
            p=closes[-1]; ma5=sum(closes[-5:])/5; ma15=sum(closes[-15:])/15
            mom=(p/closes[-6]-1)*100
            rets=[closes[i]/closes[i-1]-1 for i in range(1,len(closes))]
            vol=(sum((x-sum(rets)/len(rets))**2 for x in rets)/max(1,len(rets)-1))**.5*100
            score=50 + (12 if p>ma5 else -12)+(12 if ma5>ma15 else -12)+max(-16,min(16,mom*2))-min(12,vol*2)
            score=max(0,min(100,round(score)))
            risk='Niedrig' if vol<2 else ('Mittel' if vol<4 else 'Hoch')
            signal='KAUFEN' if score>=75 else ('BEOBACHTEN' if score>=55 else 'MEIDEN')
            out.append({'symbol':sym,'price':p,'score':score,'risk':risk,'signal':signal,'mom':round(mom,2),'vol':round(vol,2)})
        except Exception as e:
            out.append({'symbol':sym,'error':str(e)[:100]})
    return sorted(out,key=lambda x:x.get('score',-1),reverse=True)

def portfolio(d, quotes):
    qmap={x['symbol']:x for x in quotes if 'price' in x}
    val=d['cash']
    rows=[]
    for pos in d['positions']:
        p=qmap.get(pos['symbol'],{}).get('price',pos['entry'])
        cur=pos['qty']*p; pnl=cur-pos['cost']; val+=cur
        rows.append({**pos,'price':p,'value':cur,'pnl':pnl,'pnlpct':(p/pos['entry']-1)*100})
    return val,rows

HTML=r'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trading Radar</title><style>
body{font-family:system-ui;background:#07111f;color:#eaf1ff;margin:0}header{padding:18px 5%;background:#0c1b2d;position:sticky;top:0}.wrap{max-width:1100px;margin:auto;padding:22px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}.card{background:#102238;border:1px solid #203b5b;border-radius:16px;padding:16px;margin-bottom:14px}.big{font-size:28px;font-weight:800}.green{color:#42df91}.red{color:#ff6677}.yellow{color:#ffd15c}button,input{font:inherit;border-radius:10px;padding:10px;border:1px solid #34506d}button{background:#19b873;color:white;font-weight:700;cursor:pointer}.danger{background:#c53e50}.muted{color:#9db0c7}.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.trade{display:grid;grid-template-columns:1.2fr .8fr .8fr .8fr .8fr;gap:8px;padding:10px 0;border-top:1px solid #233c58}@media(max-width:700px){.trade{grid-template-columns:1fr 1fr}.hideM{display:none}}
</style></head><body><header><b>⚡ Trading Radar</b> <span class="muted">Paper-Trading · kein Echtgeld</span></header><div class="wrap">
<div class="grid"><div class="card">Virtuelles Depot<div id="value" class="big">–</div><span id="pnl"></span></div><div class="card">Freies Kapital<div id="cash" class="big">–</div></div><div class="card">Offene Trades<div id="count" class="big">–</div></div><div class="card">Automatik<div id="auto" class="big">AUS</div></div></div>
<div class="card"><h3>Einstellungen</h3><div class="row"><input id="key" type="password" placeholder="Twelve Data API-Key"><button onclick="setKey()">API-Key speichern</button><label>Budget € <input id="budget" type="number" value="100" style="width:75px"></label><label>pro Trade € <input id="per" type="number" value="20" style="width:70px"></label><button onclick="settings()">Speichern</button><button onclick="toggleAuto()">Automatik AN/AUS</button><button class="danger" onclick="resetAll()">Test zurücksetzen</button></div><p class="muted">Die App handelt nur virtuell. Der API-Key liefert Marktdaten; er hat keinen Zugriff auf Bank oder Broker.</p></div>
<div class="card"><h3>Beste Chancen jetzt</h3><div id="radar">API-Key eintragen und „Markt aktualisieren“ drücken.</div><br><button onclick="refresh()">Markt aktualisieren</button></div>
<div class="card"><h3>Meine virtuellen Trades</h3><div id="positions"></div></div>
<div class="card"><h3>Protokoll</h3><div id="history" class="muted"></div></div>
</div><script>
let S={}; async function api(path,opt){let r=await fetch(path,opt);return r.json()}
function euro(x){return Number(x).toLocaleString('de-DE',{style:'currency',currency:'EUR'})}
async function load(){S=await api('/api/state'); render(S)}
function render(s){value.textContent=euro(s.value); let pp=s.value-s.start;pnl.textContent=(pp>=0?'+':'')+euro(pp)+' seit Start';pnl.className=pp>=0?'green':'red';cash.textContent=euro(s.cash);count.textContent=s.positions.length;auto.textContent=s.auto?'AN':'AUS';auto.className='big '+(s.auto?'green':'red');budget.value=s.budget;per.value=s.per_trade;
radar.innerHTML=s.market?.length?s.market.map(x=>x.error?`<div class=trade><b>${x.symbol}</b><span class=red>Fehler</span><span>${x.error}</span></div>`:`<div class=trade><b>${x.symbol}</b><span>${euro(x.price)}</span><span class=${x.score>=75?'green':x.score>=55?'yellow':'red'}>${x.score}/100</span><span>${x.risk}</span><span><b>${x.signal}</b> ${x.signal==='KAUFEN'?`<button onclick="buy('${x.symbol}')">virtuell kaufen</button>`:''}</span></div>`).join(''):'Noch keine Marktdaten.';
positions.innerHTML=s.position_rows.length?s.position_rows.map(x=>`<div class=trade><b>${x.symbol}</b><span>${euro(x.value)}</span><span class=${x.pnl>=0?'green':'red'}>${x.pnl>=0?'+':''}${euro(x.pnl)} (${x.pnlpct.toFixed(2)}%)</span><span>Einstieg ${euro(x.entry)}</span><span><button class=danger onclick="sell('${x.symbol}')">verkaufen</button></span></div>`).join(''):'Keine offenen virtuellen Trades.';
history.innerHTML=s.history.slice().reverse().slice(0,20).map(x=>`<div>${x.time} · ${x.text}</div>`).join('')||'Noch keine Trades.'}
async function refresh(){render(await api('/api/refresh',{method:'POST'}))} async function buy(s){render(await api('/api/buy',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:s})}))} async function sell(s){render(await api('/api/sell',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({symbol:s})}))}
async function setKey(){render(await api('/api/key',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:key.value})}));key.value=''} async function settings(){render(await api('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({budget:+budget.value,per_trade:+per.value})}))} async function toggleAuto(){render(await api('/api/auto',{method:'POST'}))} async function resetAll(){if(confirm('Paper-Depot wirklich auf 100 € zurücksetzen?'))render(await api('/api/reset',{method:'POST'}))} load();</script></body></html>'''

CACHE=[]
def view(d, refresh=False):
    global CACHE
    if refresh: CACHE=market(d)
    val,rows=portfolio(d,CACHE)
    return {**d,'key':'***' if d['key'] else '', 'value':val,'position_rows':rows,'market':CACHE}

def auto_step(d):
    global CACHE
    if not d['auto'] or not CACHE: return
    q={x['symbol']:x for x in CACHE if 'price' in x}
    # sell if score deteriorates or -4% / +7%
    for p in list(d['positions']):
        x=q.get(p['symbol']);
        if not x: continue
        ch=x['price']/p['entry']-1
        if x['score']<45 or ch<=-.04 or ch>=.07: execute_sell(d,p['symbol'],x['price'],'Automatik')
    invested=sum(p['cost'] for p in d['positions'])
    for x in CACHE:
        if x.get('score',0)>=82 and x['risk']!='Hoch' and not any(p['symbol']==x['symbol'] for p in d['positions']):
            amt=min(d['per_trade'],d['cash'],max(0,d['budget']-invested))
            if amt>=5: execute_buy(d,x['symbol'],x['price'],amt,'Automatik'); invested+=amt

def execute_buy(d,sym,price,amt,src='Manuell'):
    amt=min(float(amt),d['cash']);
    if amt<=0:return
    d['positions'].append({'symbol':sym,'entry':price,'qty':amt/price,'cost':amt});d['cash']-=amt
    d['history'].append({'time':time.strftime('%d.%m.%Y %H:%M'),'text':f'{src}: {sym} virtuell für {amt:.2f} € gekauft @ {price:.2f}'})
def execute_sell(d,sym,price,src='Manuell'):
    for p in list(d['positions']):
        if p['symbol']==sym:
            val=p['qty']*price; pnl=val-p['cost'];d['cash']+=val;d['positions'].remove(p);d['history'].append({'time':time.strftime('%d.%m.%Y %H:%M'),'text':f'{src}: {sym} virtuell verkauft · Ergebnis {pnl:+.2f} €'});break

class H(BaseHTTPRequestHandler):
 def sendj(self,o):
  b=json.dumps(o).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',len(b));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  if self.path=='/':
   b=HTML.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',len(b));self.end_headers();self.wfile.write(b)
  elif self.path=='/api/state':self.sendj(view(load()))
  else:self.send_error(404)
 def body(self):
  n=int(self.headers.get('Content-Length',0));return json.loads(self.rfile.read(n) or b'{}')
 def do_POST(self):
  d=load()
  try:
   if self.path=='/api/key': d['key']=self.body().get('key','').strip()
   elif self.path=='/api/settings':
    b=self.body();d['budget']=max(0,float(b['budget']));d['per_trade']=max(1,float(b['per_trade']))
   elif self.path=='/api/auto':d['auto']=not d['auto']
   elif self.path=='/api/reset':
    key=d['key']; d={**DEFAULT,'key':key}
   elif self.path=='/api/refresh':
    CACHE.clear(); CACHE.extend(market(d));auto_step(d)
   elif self.path=='/api/buy':
    sym=self.body()['symbol'];x=next((x for x in CACHE if x.get('symbol')==sym and 'price'in x),None)
    if x:
     invested=sum(p['cost'] for p in d['positions']);amt=min(d['per_trade'],d['cash'],max(0,d['budget']-invested));execute_buy(d,sym,x['price'],amt)
   elif self.path=='/api/sell':
    sym=self.body()['symbol'];x=next((x for x in CACHE if x.get('symbol')==sym and 'price'in x),None);p=next((p for p in d['positions'] if p['symbol']==sym),None);execute_sell(d,sym,x['price'] if x else p['entry']) if p else None
   save(d);self.sendj(view(d))
  except Exception as e:self.sendj({'error':str(e),**view(d)})
 def log_message(self,*a):pass

if __name__=='__main__':
 port=int(os.environ.get('PORT','10000'))
 print(f'Trading Radar läuft auf Port {port}')
 HTTPServer(('0.0.0.0',port),H).serve_forever()
