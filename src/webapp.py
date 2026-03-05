"""Telegram Mini App – expense pie chart."""

import hashlib
import hmac
import json
from collections import defaultdict
from urllib.parse import parse_qsl

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from loguru import logger

from src.config import settings
from src.services.sheets import get_current_month_expenses

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Telegram initData validation
# ---------------------------------------------------------------------------


def validate_init_data(init_data: str) -> dict:
    """Validate Telegram WebApp initData using HMAC-SHA256."""
    if not settings.telegram_bot_token:
        raise ValueError("Bot token not configured")

    token = settings.telegram_bot_token.get_secret_value()
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise ValueError("Missing hash")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise ValueError("Invalid hash")

    if settings.allowed_chat_id and "user" in parsed:
        user_data = json.loads(parsed["user"])
        if user_data.get("id") != settings.allowed_chat_id:
            raise ValueError("Access denied")

    return parsed


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------


@app.get("/api/stats")
async def api_stats(initData: str = Query(...)):
    try:
        validate_init_data(initData)
    except ValueError as e:
        logger.warning(f"Mini App auth failed: {e}")
        raise HTTPException(status_code=403, detail=str(e))

    try:
        expenses = get_current_month_expenses()
    except Exception as e:
        logger.error(f"Failed to get expenses: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch expenses")

    category_totals: dict[str, float] = defaultdict(float)
    for exp in expenses:
        category = exp.get("category", "").strip()
        amount = exp.get("amount", 0)
        if category:
            category_totals[category] += amount

    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    total = sum(amount for _, amount in sorted_categories)

    return {
        "categories": [{"name": n, "amount": a} for n, a in sorted_categories],
        "total": total,
    }


# ---------------------------------------------------------------------------
# HTML page
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def stats_page():
    return STATS_HTML


STATS_HTML = """\
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>Расходы</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  background:var(--tg-theme-bg-color,#fff);
  color:var(--tg-theme-text-color,#000);
  padding:16px 16px 32px;
  -webkit-font-smoothing:antialiased;
}
.header{text-align:center;margin-bottom:20px}
.month{font-size:13px;color:var(--tg-theme-hint-color,#999);text-transform:uppercase;letter-spacing:.5px}
.total{font-size:34px;font-weight:700;margin-top:2px}
.chart-wrap{position:relative;max-width:280px;margin:0 auto 28px}
.legend{list-style:none;padding:0}
.legend-item{
  display:flex;align-items:center;
  padding:11px 0;
  border-bottom:1px solid var(--tg-theme-secondary-bg-color,#f0f0f0);
}
.legend-item:last-child{border-bottom:none}
.dot{width:10px;height:10px;border-radius:50%;margin-right:12px;flex-shrink:0}
.name{flex:1;font-size:15px}
.amount{font-weight:600;font-size:15px;margin-left:8px}
.pct{color:var(--tg-theme-hint-color,#999);font-size:13px;min-width:44px;text-align:right;margin-left:6px}
.loading,.error,.empty{text-align:center;padding:60px 20px;color:var(--tg-theme-hint-color,#999);font-size:15px}
.error{color:#e74c3c}
</style>
</head>
<body>
<div id="app"><div class="loading">Загрузка…</div></div>
<script>
const COLORS = [
  '#4C6EF5','#7950F2','#E64980','#FF6B6B','#FFA94D',
  '#FFD43B','#51CF66','#20C997','#22B8CF','#339AF0',
  '#845EF7','#F06595','#FF8787','#74C0FC','#B2F2BB',
];
const MONTHS = [
  'Январь','Февраль','Март','Апрель','Май','Июнь',
  'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь',
];

const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

function fmt(n){return Math.round(n).toLocaleString('ru-RU')}

async function load(){
  const app = document.getElementById('app');
  const initData = tg.initData;
  if(!initData){
    app.innerHTML='<div class="error">Откройте через Telegram</div>';
    return;
  }
  try{
    const r = await fetch('/api/stats?initData='+encodeURIComponent(initData));
    if(!r.ok){
      let detail = r.statusText;
      try{
        const err = await r.json();
        if(err && err.detail){
          detail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
        }
      }catch(_){}
      throw new Error(detail);
    }
    const data = await r.json();
    render(data);
  }catch(e){
    app.innerHTML='<div class="error">Ошибка загрузки: '+e.message+'</div>';
  }
}

function render(data){
  const app = document.getElementById('app');
  if(!data.categories||!data.categories.length){
    app.innerHTML='<div class="empty">Нет данных за текущий месяц</div>';
    return;
  }
  const now = new Date();
  const monthName = MONTHS[now.getMonth()];
  const total = data.total;
  const cats = data.categories;

  let html = '<div class="header">';
  html += '<div class="month">'+monthName+' '+now.getFullYear()+'</div>';
  html += '<div class="total">'+fmt(total)+'</div>';
  html += '</div>';
  html += '<div class="chart-wrap"><canvas id="chart"></canvas></div>';
  html += '<ul class="legend">';
  cats.forEach(function(c,i){
    const color = COLORS[i % COLORS.length];
    const pct = total > 0 ? (c.amount/total*100).toFixed(1) : '0.0';
    html += '<li class="legend-item">';
    html += '<span class="dot" style="background:'+color+'"></span>';
    html += '<span class="name">'+c.name+'</span>';
    html += '<span class="amount">'+fmt(c.amount)+'</span>';
    html += '<span class="pct">'+pct+'%</span>';
    html += '</li>';
  });
  html += '</ul>';
  app.innerHTML = html;

  const ctx = document.getElementById('chart').getContext('2d');
  new Chart(ctx,{
    type:'doughnut',
    data:{
      labels: cats.map(function(c){return c.name}),
      datasets:[{
        data: cats.map(function(c){return c.amount}),
        backgroundColor: cats.map(function(_,i){return COLORS[i%COLORS.length]}),
        borderWidth: 2,
        borderColor: getComputedStyle(document.body).getPropertyValue('--tg-theme-bg-color')||'#fff',
        hoverOffset: 6,
      }]
    },
    options:{
      cutout:'62%',
      responsive:true,
      plugins:{
        legend:{display:false},
        tooltip:{
          callbacks:{
            label:function(ctx){
              return ctx.label+': '+fmt(ctx.raw);
            }
          }
        }
      }
    }
  });
}

load();
</script>
</body>
</html>
"""
