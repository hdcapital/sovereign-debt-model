"""Build reports/dashboard/latest.html (+ dated copy): a self-contained page with an
overview (quadrant chart, stage heatmap, transitions log, data issues) and one page per
core country with a card per indicator (current value, 1y/5y change, sparkline with the
threshold line, and the indicator's docstring). Inline CSS/JS and SVG only, no CDN, so
the file works offline as an email attachment."""

from __future__ import annotations

import json
import logging
from datetime import date

import numpy as np
import pandas as pd

from sdm.config import load_indicator_config, load_universe
from sdm.indicators import blocks  # noqa: F401
from sdm.indicators.applicability import indicator_applies
from sdm.indicators.compute import INDICATORS_PATH, LATEST_PATH, TRANSITIONS_PATH
from sdm.indicators.registry import REGISTRY
from sdm.paths import CATALOG, REPORTS

log = logging.getLogger(__name__)

OUT_DIR = REPORTS / "dashboard"
HISTORY_QUARTERS = 60
BLOCK_ORDER = ["trajectory", "captivity", "pressure"]
STAGE_NAMES = {
    0: "fuel",
    1: "trigger",
    2: "pricing",
    3: "choice",
    4: "fiscal dominance",
    5: "flight",
    6: "resolution",
}


def _clean(v: object) -> object:
    if v is None:
        return None
    if isinstance(v, str):
        try:
            v = float(v)
        except ValueError:
            return v
    if isinstance(v, (float, np.floating)):
        return None if np.isnan(v) else round(float(v), 4)
    if isinstance(v, (np.integer,)):
        return int(v)
    return v


def build_payload() -> dict:
    uni = load_universe()
    cfg = load_indicator_config()
    ind = pd.read_csv(INDICATORS_PATH, index_col=[0, 1], parse_dates=[1])
    latest = pd.read_csv(LATEST_PATH)
    latest["num"] = pd.to_numeric(latest["value"], errors="coerce")
    for col in ("chg_1y", "chg_5y", "stale_quarters"):
        latest[col] = pd.to_numeric(latest[col], errors="coerce")
    transitions = pd.read_csv(TRANSITIONS_PATH) if TRANSITIONS_PATH.exists() else pd.DataFrame()
    catalog = pd.read_csv(CATALOG) if CATALOG.exists() else pd.DataFrame()
    shown = [(n, m) for n, m in REGISTRY.items() if not m.helper]
    meta = {
        n: {
            "block": m.block,
            "units": m.units,
            "doc": m.doc,
            "threshold": cfg.thresholds.get(n, (None, None))[0],
            "direction": cfg.thresholds.get(n, (None, None))[1],
        }
        for n, m in shown
    }
    countries = {}
    for code in uni.core:
        if code not in ind.index.get_level_values(0):
            continue
        df = ind.loc[code].tail(HISTORY_QUARTERS)
        quarters = [q.strftime("%Y-%m-%d") for q in df.index]
        c = uni[code]
        series = {
            n: [_clean(v) for v in df[n].tolist()] for n, _ in shown if n in df and indicator_applies(n, c)
        }
        series["stage_estimate"] = [_clean(v) for v in df["stage_estimate"].tolist()]
        series["quadrant"] = [
            None if (isinstance(v, float) and np.isnan(v)) else v for v in df["quadrant"].tolist()
        ]
        lt = latest[latest["country"] == code].set_index("indicator")
        cards = {}
        for n, _ in shown:
            if n in lt.index:
                r = lt.loc[n]
                cards[n] = {
                    "value": _clean(r["value"]),
                    "quarter": r["quarter"] if isinstance(r["quarter"], str) else None,
                    "chg_1y": _clean(r["chg_1y"]),
                    "chg_5y": _clean(r["chg_5y"]),
                    "stale": _clean(r["stale_quarters"]),
                }
        countries[code] = {
            "name": c.name,
            "regime": c.monetary_regime,
            "gauge": c.pressure_gauge,
            "currency": c.currency,
            "quarters": quarters,
            "series": series,
            "cards": cards,
            "stage": _clean(lt.loc["stage_estimate", "num"]) if "stage_estimate" in lt.index else None,
            "quadrant": lt.loc["quadrant", "value"]
            if "quadrant" in lt.index and isinstance(lt.loc["quadrant", "value"], str)
            else None,
            "captivity": _clean(lt.loc["captivity_score", "value"])
            if "captivity_score" in lt.index
            else None,
            "fwd_rg": _clean(lt.loc["forward_r_minus_g_5y", "value"])
            if "forward_r_minus_g_5y" in lt.index
            else None,
        }
    issues = []
    core_latest = latest[latest["tier"] == "core"]
    for r in core_latest.itertuples(index=False):
        if r.indicator in meta and (
            pd.isna(r.value)
            or (r.stale_quarters is not None and not pd.isna(r.stale_quarters) and r.stale_quarters > 2)
        ):
            issues.append(
                {
                    "country": r.country,
                    "indicator": r.indicator,
                    "problem": "no data"
                    if pd.isna(r.value)
                    else f"stale by {int(r.stale_quarters)} quarters (last {r.quarter})",
                }
            )
    if len(catalog):
        bad = catalog[catalog["notes"].astype(str).str.contains("LAST ERROR")]
        for r in bad.itertuples(index=False):
            issues.append(
                {
                    "country": r.country,
                    "indicator": r.series_id,
                    "problem": str(r.notes).split("LAST ERROR:")[-1].strip()[:140],
                }
            )
    trans = transitions.sort_values("quarter", ascending=False).head(40) if len(transitions) else transitions
    trans = trans[trans["country"].isin(uni.core)] if len(trans) else trans
    return {
        "generated": date.today().isoformat(),
        "core": [c for c in uni.core if c in countries],
        "meta": meta,
        "blocks": BLOCK_ORDER,
        "countries": countries,
        "transitions": trans.to_dict("records") if len(trans) else [],
        "issues": issues,
        "quadrant_threshold": cfg.quadrant["captive"]["captivity_score_gt"],
        "stage_names": STAGE_NAMES,
    }


CSS = """
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;--axis:#c3c2b7;--border:rgba(11,11,11,.10);--s1:#2a78d6;--s2:#eb6834;--good:#0ca30c;--warn:#fab219;--serious:#ec835a;--critical:#d03b3b;--tip:#fff}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;--border:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--tip:#242423}}
:root[data-theme=dark]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;--border:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--tip:#242423}
*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
header{padding:16px 16px 8px}h1{font-size:20px;margin:0 0 4px;font-weight:600}h2{font-size:16px;margin:24px 0 8px;font-weight:600}h3{font-size:14px;margin:0 0 4px;font-weight:600}
.sub{color:var(--ink2);font-size:13px}nav{display:flex;flex-wrap:wrap;gap:6px;padding:8px 16px;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--page);z-index:2}
nav a{padding:5px 10px;border-radius:6px;color:var(--ink2);text-decoration:none;border:1px solid transparent}nav a.on{color:var(--ink);border-color:var(--border);background:var(--surface)}
main{padding:0 16px 48px;max-width:1280px;margin:0 auto}.page{display:none}.page.on{display:block}
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin:0 0 12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}.grid .card{margin:0}
.val{font-size:26px;font-weight:600;letter-spacing:-.01em}.unit{font-size:12px;color:var(--muted);margin-left:4px}.chg{font-size:12px;color:var(--ink2);margin:2px 0 6px}.chg b{font-weight:600;color:var(--ink)}
.doc{font-size:12.5px;color:var(--ink2);margin-top:8px}svg{display:block;width:100%;height:auto;overflow:visible}
.ax{stroke:var(--axis);stroke-width:1}.gr{stroke:var(--grid);stroke-width:1}.ln{fill:none;stroke:var(--s1);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}.th{stroke:var(--s2);stroke-width:1.5}
text{fill:var(--ink2);font-size:11px}.lab{fill:var(--ink);font-size:12px;font-weight:600}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--grid);vertical-align:top}th{color:var(--muted);font-weight:500}td.n{font-variant-numeric:tabular-nums;text-align:right}
.heat td{padding:0}.cell{width:18px;height:18px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:600;color:#0b0b0b;border:1px solid var(--surface)}
.st0,.st1{background:var(--good);color:#fff}.st2,.st3{background:var(--warn)}.st4{background:var(--serious)}.st5,.st6{background:var(--critical);color:#fff}.stn{background:var(--grid);color:var(--muted)}
.tag{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;border:1px solid var(--border);color:var(--ink2);margin-right:4px}
#tip{position:fixed;pointer-events:none;background:var(--tip);border:1px solid var(--border);border-radius:6px;padding:4px 8px;font-size:12px;display:none;box-shadow:0 2px 8px rgba(0,0,0,.12);z-index:5}
.legend{font-size:12px;color:var(--ink2);margin:6px 0}.legend span{display:inline-block;width:10px;height:10px;border-radius:2px;margin:0 4px 0 10px;vertical-align:middle}
.stale{color:var(--critical);font-size:11px}.btn{background:none;border:1px solid var(--border);border-radius:6px;color:var(--ink2);padding:4px 8px;cursor:pointer;font-size:12px}
@media (max-width:600px){.val{font-size:22px}}
"""

JS = r"""
const D = window.__DATA__;
const fmt = (v, d=2) => (v===null||v===undefined||Number.isNaN(v)) ? "–" : (Math.abs(v)>=1000? v.toLocaleString(undefined,{maximumFractionDigits:0}) : v.toFixed(d));
const sgn = v => (v===null||v===undefined) ? "–" : (v>0?"+":"")+fmt(v);
const stCls = s => (s===null||s===undefined) ? "stn" : "st"+Math.round(s);
const tip = document.getElementById("tip");
function showTip(e, html){ tip.innerHTML = html; tip.style.display="block"; tip.style.left=(e.clientX+12)+"px"; tip.style.top=(e.clientY+12)+"px"; }
function hideTip(){ tip.style.display="none"; }

function sparkline(quarters, vals, thr, dir, units){
  const W=300,H=90,P={l:36,r:8,t:8,b:18};
  const pts = vals.map((v,i)=>[i,v]).filter(p=>p[1]!==null);
  if(pts.length<2) return '<svg viewBox="0 0 300 90"><text x="150" y="50" text-anchor="middle">no history</text></svg>';
  let lo=Math.min(...pts.map(p=>p[1])), hi=Math.max(...pts.map(p=>p[1]));
  if(thr!==null){ lo=Math.min(lo,thr); hi=Math.max(hi,thr); }
  if(hi===lo){hi+=1;lo-=1;} const pad=(hi-lo)*0.08; lo-=pad; hi+=pad;
  const x=i=>P.l+(i/(vals.length-1))*(W-P.l-P.r), y=v=>P.t+(1-(v-lo)/(hi-lo))*(H-P.t-P.b);
  let d="", prev=null;
  vals.forEach((v,i)=>{ if(v===null){prev=null;return;} d+=(prev===null?"M":"L")+x(i).toFixed(1)+" "+y(v).toFixed(1)+" "; prev=v; });
  const yt=[lo+pad, (hi+lo)/2, hi-pad];
  let s=`<svg viewBox="0 0 ${W} ${H}" data-n="${vals.length}">`;
  yt.forEach(t=>{ s+=`<line class="gr" x1="${P.l}" x2="${W-P.r}" y1="${y(t)}" y2="${y(t)}"/><text x="${P.l-4}" y="${y(t)+4}" text-anchor="end">${fmt(t,1)}</text>`; });
  if(thr!==null) s+=`<line class="th" x1="${P.l}" x2="${W-P.r}" y1="${y(thr)}" y2="${y(thr)}"/>`;
  s+=`<path class="ln" d="${d}"/>`;
  const last=pts[pts.length-1]; s+=`<circle cx="${x(last[0])}" cy="${y(last[1])}" r="4" fill="var(--s1)" stroke="var(--surface)" stroke-width="2"/>`;
  s+=`<text x="${P.l}" y="${H-4}">${quarters[0].slice(0,4)}</text><text x="${W-P.r}" y="${H-4}" text-anchor="end">${quarters[quarters.length-1].slice(0,7)}</text>`;
  s+=`<rect x="${P.l}" y="0" width="${W-P.l-P.r}" height="${H}" fill="transparent" class="hit"/></svg>`;
  return s;
}
function attachHover(svg, quarters, vals, units){
  const hit=svg.querySelector(".hit"); if(!hit) return;
  hit.addEventListener("mousemove", e=>{ const r=svg.getBoundingClientRect(); const f=(e.clientX-r.left)/r.width; const i=Math.max(0,Math.min(vals.length-1,Math.round((f*300-36)/(300-44)*(vals.length-1))));
    showTip(e, `<b>${quarters[i].slice(0,7)}</b> ${fmt(vals[i])} ${units}`); });
  hit.addEventListener("mouseleave", hideTip);
}
function cardHTML(code, name){
  const c=D.countries[code], m=D.meta[name], k=c.cards[name]||{};
  const stale = (k.stale!==null && k.stale!==undefined && k.stale>2) ? `<span class="stale">stale: last ${k.quarter}</span>` : (k.quarter? `<span class="sub">${k.quarter.slice(0,7)}</span>`:"");
  return `<div class="card" data-ind="${name}"><h3>${name.replace(/_/g," ")}</h3>
  <div><span class="val">${fmt(k.value)}</span><span class="unit">${m.units}</span></div>
  <div class="chg">1y <b>${sgn(k.chg_1y)}</b> · 5y <b>${sgn(k.chg_5y)}</b> · ${stale}${m.threshold!==null?` · threshold ${m.direction} ${fmt(m.threshold,1)}`:""}</div>
  <div class="spark">${sparkline(c.quarters, c.series[name]||[], m.threshold, m.direction, m.units)}</div>
  <div class="doc">${m.doc}</div></div>`;
}
function countryPage(code){
  const c=D.countries[code];
  let h=`<h2>${c.name} <span class="tag">${c.regime.replace(/_/g," ")}</span><span class="tag">gauge: ${c.gauge}</span><span class="tag">stage ${c.stage===null?"–":Math.round(c.stage)+" · "+D.stage_names[Math.round(c.stage)]}</span><span class="tag">${c.quadrant?c.quadrant.replace(/_/g," "):"quadrant n/a"}</span></h2>`;
  D.blocks.forEach(b=>{ const names=Object.keys(D.meta).filter(n=>D.meta[n].block===b && c.series[n]); if(!names.length) return;
    h+=`<h2 style="font-size:14px;color:var(--ink2)">${b}</h2><div class="grid">`+names.map(n=>cardHTML(code,n)).join("")+`</div>`; });
  return h;
}
function quadrantChart(){
  const W=560,H=380,P={l:48,r:16,t:16,b:36}; const xs=v=>P.l+(v/100)*(W-P.l-P.r);
  const ys=D.core.map(c=>D.countries[c].fwd_rg).filter(v=>v!==null); let lo=Math.min(-3,...ys), hi=Math.max(3,...ys); const pad=(hi-lo)*.1; lo-=pad; hi+=pad;
  const y=v=>P.t+(1-(v-lo)/(hi-lo))*(H-P.t-P.b);
  let s=`<svg viewBox="0 0 ${W} ${H}">`;
  s+=`<rect x="${P.l}" y="${P.t}" width="${W-P.l-P.r}" height="${H-P.t-P.b}" fill="var(--surface)"/>`;
  [0,25,50,75,100].forEach(t=>s+=`<line class="gr" x1="${xs(t)}" x2="${xs(t)}" y1="${P.t}" y2="${H-P.b}"/><text x="${xs(t)}" y="${H-P.b+14}" text-anchor="middle">${t}</text>`);
  for(let t=Math.ceil(lo);t<=hi;t+=1){ if(t%1===0 && Math.abs(t)<=20) s+=`<line class="gr" x1="${P.l}" x2="${W-P.r}" y1="${y(t)}" y2="${y(t)}"/><text x="${P.l-6}" y="${y(t)+4}" text-anchor="end">${t}</text>`; }
  s+=`<line class="th" x1="${xs(D.quadrant_threshold)}" x2="${xs(D.quadrant_threshold)}" y1="${P.t}" y2="${H-P.b}"/><line class="th" x1="${P.l}" x2="${W-P.r}" y1="${y(0)}" y2="${y(0)}"/>`;
  s+=`<text x="${P.l+6}" y="${P.t+14}" class="lab">unsustainable · free</text><text x="${W-P.r-6}" y="${P.t+14}" text-anchor="end" class="lab">unsustainable · captive</text>`;
  s+=`<text x="${P.l+6}" y="${H-P.b-6}" class="lab">sustainable · free</text><text x="${W-P.r-6}" y="${H-P.b-6}" text-anchor="end" class="lab">sustainable · captive</text>`;
  D.core.forEach(code=>{ const c=D.countries[code]; if(c.captivity===null||c.fwd_rg===null) return; const cx=xs(c.captivity), cy=y(c.fwd_rg);
    s+=`<g class="pt" data-c="${code}"><circle cx="${cx}" cy="${cy}" r="9" fill="var(--${['good','good','warn','warn','serious','critical','critical'][Math.round(c.stage||0)]})" stroke="var(--surface)" stroke-width="2"/><text x="${cx}" y="${cy+4}" text-anchor="middle" style="fill:#0b0b0b;font-size:10px;font-weight:600">${code}</text><circle cx="${cx}" cy="${cy}" r="16" fill="transparent" class="hitpt"/></g>`; });
  s+=`<text x="${(P.l+W-P.r)/2}" y="${H-4}" text-anchor="middle">captivity score (0–100) →</text>`;
  s+=`<text transform="translate(12 ${(P.t+H-P.b)/2}) rotate(-90)" text-anchor="middle">forward r − g, 5y (pp) →</text></svg>`;
  return s;
}
function heatmap(){
  const q=D.countries[D.core[0]].quarters.slice(-40); let h=`<table class="heat"><tr><th></th>`;
  q.forEach((x,i)=>h+=`<th style="padding:0 1px;font-size:9px">${i%8===0?x.slice(0,4):""}</th>`); h+=`</tr>`;
  D.core.forEach(code=>{ const c=D.countries[code]; const st=c.series.stage_estimate.slice(-40); const qs=c.quarters.slice(-40);
    h+=`<tr><th style="padding:2px 8px 2px 0">${code}</th>`+st.map((s,i)=>`<td><div class="cell ${stCls(s)}" data-c="${code}" data-q="${qs[i]}" data-s="${s===null?'–':Math.round(s)}">${s===null?"":Math.round(s)}</div></td>`).join("")+`</tr>`; });
  return h+`</table><div class="legend"><span style="background:var(--good)"></span>0–1 fuel/trigger<span style="background:var(--warn)"></span>2–3 pricing/choice<span style="background:var(--serious)"></span>4 fiscal dominance<span style="background:var(--critical)"></span>5–6 flight/resolution<span style="background:var(--grid)"></span>undetermined</div>`;
}
function overview(){
  let h=`<h2>Where every core market sits</h2><div class="card">${quadrantChart()}<div class="legend">Point colour is the stage estimate; x is captivity, y is forward r − g over five years. Lines are the quadrant thresholds.</div></div>`;
  h+=`<h2>Snapshot</h2><div class="card"><table><tr><th>market</th><th>regime</th><th>quadrant</th><th>stage</th><th class="n">debt/GDP</th><th class="n">primary bal.</th><th class="n">r eff.</th><th class="n">fwd r−g 5y</th><th class="n">captivity</th><th class="n">gauge 12m</th></tr>`;
  D.core.forEach(code=>{ const c=D.countries[code], k=c.cards; const g = c.gauge==="spread" ? (k.spread_to_anchor_bp? fmt(k.spread_to_anchor_bp.value,0)+" bp":"–") : (k.fx_vs_usd_12m&&k.fx_vs_usd_12m.value!==null? fmt(k.fx_vs_usd_12m.value,1)+"% vs USD" : (k.fx_broad_reer_12m? fmt(k.fx_broad_reer_12m.value,1)+"% REER":"–"));
    h+=`<tr><td><a href="#${code}">${c.name}</a></td><td>${c.regime.replace(/_/g," ")}</td><td>${c.quadrant?c.quadrant.replace(/_/g," "):"–"}</td><td><span class="cell ${stCls(c.stage)}" style="display:inline-flex">${c.stage===null?"":Math.round(c.stage)}</span></td><td class="n">${fmt(k.debt_gdp&&k.debt_gdp.value,1)}</td><td class="n">${fmt(k.primary_balance_gdp&&k.primary_balance_gdp.value,1)}</td><td class="n">${fmt(k.r_effective&&k.r_effective.value)}</td><td class="n">${fmt(c.fwd_rg)}</td><td class="n">${fmt(c.captivity,0)}</td><td class="n">${g}</td></tr>`; });
  h+=`</table></div>`;
  h+=`<h2>Stage heatmap, last ten years</h2><div class="card" style="overflow-x:auto">${heatmap()}</div>`;
  h+=`<h2>Transitions</h2><div class="card">`+(D.transitions.length?`<table><tr><th>quarter</th><th>market</th><th>kind</th><th>from</th><th>to</th></tr>`+D.transitions.map(t=>`<tr><td>${String(t.quarter).slice(0,7)}</td><td>${t.country}</td><td>${t.kind}</td><td>${t.from}</td><td>${t.to}</td></tr>`).join("")+`</table>`:"<span class='sub'>none</span>")+`</div>`;
  h+=`<h2>Data issues</h2><div class="card">`+(D.issues.length?`<table><tr><th>market</th><th>series</th><th>problem</th></tr>`+D.issues.map(i=>`<tr><td>${i.country}</td><td>${i.indicator}</td><td>${i.problem}</td></tr>`).join("")+`</table>`:"<span class='sub'>none</span>")+`</div>`;
  return h;
}
function render(){
  const main=document.getElementById("main"); const nav=document.getElementById("nav");
  const pages=[["overview","Overview"]].concat(D.core.map(c=>[c,c]));
  nav.innerHTML=pages.map(p=>`<a href="#${p[0]}" data-p="${p[0]}">${p[1]}</a>`).join("")+`<button class="btn" id="theme">theme</button>`;
  main.innerHTML=`<section class="page" id="p-overview">${overview()}</section>`+D.core.map(c=>`<section class="page" id="p-${c}">${countryPage(c)}</section>`).join("");
  document.querySelectorAll(".card[data-ind]").forEach(card=>{ const code=card.closest("section").id.slice(2), n=card.dataset.ind; const svg=card.querySelector("svg"); const c=D.countries[code]; attachHover(svg, c.quarters, c.series[n]||[], D.meta[n].units); });
  document.querySelectorAll(".cell[data-q]").forEach(el=>{ el.addEventListener("mousemove",e=>showTip(e,`<b>${el.dataset.c}</b> ${el.dataset.q.slice(0,7)}: stage ${el.dataset.s}`)); el.addEventListener("mouseleave",hideTip); });
  document.querySelectorAll(".pt").forEach(el=>{ const c=D.countries[el.dataset.c]; el.addEventListener("mousemove",e=>showTip(e,`<b>${c.name}</b><br>captivity ${fmt(c.captivity,0)} · fwd r−g ${fmt(c.fwd_rg)} pp<br>stage ${c.stage===null?"–":Math.round(c.stage)} · ${c.quadrant||"–"}`)); el.addEventListener("mouseleave",hideTip); el.addEventListener("click",()=>location.hash=el.dataset.c); });
  document.getElementById("theme").addEventListener("click",()=>{ const r=document.documentElement; r.dataset.theme = r.dataset.theme==="dark"?"light":"dark"; });
  route();
}
function route(){ const p=(location.hash||"#overview").slice(1); document.querySelectorAll(".page").forEach(s=>s.classList.toggle("on", s.id==="p-"+p)); document.querySelectorAll("nav a").forEach(a=>a.classList.toggle("on", a.dataset.p===p)); window.scrollTo(0,0); }
window.addEventListener("hashchange", route); render();
"""


def render_html(payload: dict) -> str:
    data = json.dumps(payload, default=_clean, separators=(",", ":")).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sovereign Debt Monitor</title>
<meta name="description" content="Quarterly sovereign debt sustainability dashboard: quadrant, stages, indicators per market.">
<style>{CSS}</style></head>
<body><header><h1>Sovereign Debt Monitor</h1><div class="sub">Generated {payload["generated"]} · quarterly indicators for the core markets · see docs/MODEL.md for the framework</div></header>
<nav id="nav"></nav><main id="main"></main><div id="tip"></div>
<script>window.__DATA__ = {data};</script>
<script>{JS}</script>
</body></html>
"""


def build_dashboard() -> tuple[object, object]:
    payload = build_payload()
    html = render_html(payload)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    latest = OUT_DIR / "latest.html"
    dated = OUT_DIR / f"dashboard-{payload['generated']}.html"
    latest.write_text(html, encoding="utf-8")
    dated.write_text(html, encoding="utf-8")
    log.info("dashboard: %s (%d KB)", latest, len(html) // 1024)
    return latest, dated
