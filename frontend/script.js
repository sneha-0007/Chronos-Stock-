// script.js - separate file
// Handles UI interactions, mock data feed (Chronos-like), charting and dynamic updates

const bankSelect = document.getElementById('bankSelect');
const stockNameEl = document.getElementById('stockName');
const stockPriceEl = document.getElementById('stockPrice');
const stockChangeEl = document.getElementById('stockChange');
const predPriceEl = document.getElementById('predPrice');
const actPriceEl = document.getElementById('actPrice');
const confidenceEl = document.getElementById('confidence');
const simulateBtn = document.getElementById('simulate');
const refreshBtn = document.getElementById('refresh');
const timeBtns = document.querySelectorAll('.time-btn');

// Bank -> default stock mapping (for demo)
const bankStocks = {
  hdfc: {name: 'HDFC BANK', base: 1400},
  sbi: {name: 'STATE BANK OF INDIA', base: 560},
  icici: {name: 'ICICI BANK', base: 820},
  axis: {name: 'AXIS BANK', base: 720},
  kotak: {name: 'KOTAK MAHINDRA BANK', base: 1800}
};

let currentBank = bankSelect.value;
let timeframeHours = 6; // default

// helper: format number
function fmt(n){
  return '₹' + n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function fmtPct(n){
  const sign = n >= 0 ? '+' : '';
  return sign + n.toFixed(2) + '%';
}

// generate mock time series for 'hours' length
function generateSeries(hours, base){
  // sample per hour (if hours<=24) or per 3-hour bucket for long ranges
  const points = Math.min(Math.max(Math.round(hours), 1) * 4, 288); // cap points
  const data = [];
  let v = base;
  for(let i=0;i<points;i++){
    // small random walk with slight trend
    const noise = (Math.random() - 0.48) * (base * 0.004);
    const drift = (Math.sin(i/20) * base * 0.0008);
    v = Math.max(1, v + noise + drift);
    data.push(parseFloat(v.toFixed(2)));
  }
  return data;
}

// Create Chart
const ctx = document.getElementById('priceChart').getContext('2d');
const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Prediction',
        data: [],
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--accent-pred') || '#aae825',
        borderWidth: 2.5,
        tension: 0.28,
        pointRadius: 0,
        fill: false,
        segment: {borderDash: ctx => []}
      },
      {
        label: 'Actual',
        data: [],
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--accent-actual') || '#00d0ff',
        borderWidth: 2.5,
        tension: 0.22,
        pointRadius: 0,
        fill: false
      }
    ]
  },
  options: {
    responsive:true,
    maintainAspectRatio:false,
    plugins:{
      legend:{display:false},
      tooltip:{
        mode:'index',
        intersect:false,
        callbacks:{label: (ctx)=> ctx.dataset.label + ': ' + fmt(ctx.parsed.y)}
      }
    },
    scales:{
      x:{display:false},
      y:{
        grid:{color:'rgba(255,255,255,0.03)'},
        ticks:{callback: v => fmt(v)}
      }
    }
  }
});

// update UI with new bank
function updateBank(bankKey){
  currentBank = bankKey;
  const info = bankStocks[bankKey];
  stockNameEl.textContent = info.name;
  // bold already via style
  // simulate initial values
  performUpdate();
}

// update values and chart
function performUpdate(){
  const info = bankStocks[currentBank];
  // generate series for actual and predicted
  const base = info.base * (0.95 + Math.random()*0.1); // small variation
  const actual = generateSeries(timeframeHours, base);
  const predicted = actual.map((v,i)=> v * (1 + ((Math.random()-0.5)*0.01 + Math.sin(i/50)*0.002)));

  // labels: show points count as simple index
  const labels = actual.map((_,i)=> i+1);

  chart.data.labels = labels;
  chart.data.datasets[0].data = predicted;
  chart.data.datasets[1].data = actual;
  chart.update();

  const latestActual = actual[actual.length-1];
  const latestPred = predicted[predicted.length-1];
  stockPriceEl.textContent = fmt(latestActual);
  actPriceEl.textContent = fmt(latestActual);
  predPriceEl.textContent = fmt(latestPred);

  // change percent relative to previous point
  const prev = actual[Math.max(0, actual.length-2)];
  const changePct = ((latestActual - prev)/prev)*100;
  stockChangeEl.textContent = fmtPct(changePct);
  if(changePct >= 0){
    stockChangeEl.classList.remove('negative');
    stockChangeEl.classList.add('positive');
  } else {
    stockChangeEl.classList.remove('positive');
    stockChangeEl.classList.add('negative');
  }

  // confidence mock
  const conf = 50 + Math.round((Math.random()*40));
  confidenceEl.textContent = conf + '%';
}

// wire bank select
bankSelect.addEventListener('change', (e)=>{
  updateBank(e.target.value);
});

// time buttons
timeBtns.forEach(btn=> btn.addEventListener('click', (e)=>{
  timeBtns.forEach(b=> b.classList.remove('active'));
  e.currentTarget.classList.add('active');
  timeframeHours = parseInt(e.currentTarget.dataset.range, 10);
  performUpdate();
}));

// buttons
simulateBtn.addEventListener('click', ()=>performUpdate());
refreshBtn.addEventListener('click', ()=>performUpdate());

// init
updateBank(currentBank);

// subtle automatic updates to feel "live", not static constants
setInterval(()=>{
  // small random chance to update
  if(Math.random() > 0.55) performUpdate();
}, 9000);
