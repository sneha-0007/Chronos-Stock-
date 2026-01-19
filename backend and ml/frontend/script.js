
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

// Bank -> NSE symbol mapping (for Fyers API: NSE:HDFCBANK-EQ)
const bankStocks = {
  hdfc: {name: 'HDFC BANK', symbol: 'HDFCBANK', base: 1400},
  sbi: {name: 'STATE BANK OF INDIA', symbol: 'SBIN', base: 560},
  icici: {name: 'ICICI BANK', symbol: 'ICICIBANK', base: 820},
  axis: {name: 'AXIS BANK', symbol: 'AXISBANK', base: 720},
  kotak: {name: 'KOTAK MAHINDRA BANK', symbol: 'KOTAKBANK', base: 1800}
};

let currentBank = bankSelect.value;
let timeframeHours = 6; // default
let isLoading = false;

// Format helpers
function fmt(n) {
  return '₹' + n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function fmtPct(n) {
  const sign = n >= 0 ? '+' : '';
  return sign + n.toFixed(2) + '%';
}

// Generate mock historical series (for chart actual prices)
function generateSeries(hours, base) {
  const points = Math.min(Math.max(Math.round(hours), 1) * 4, 288);
  const data = [];
  let v = base;
  for (let i = 0; i < points; i++) {
    const noise = (Math.random() - 0.5) * 0.8 * base * 0.004;
    const drift = Math.sin(i / 20) * base * 0.0008;
    v = Math.max(1, v + noise + drift);
    data.push(parseFloat(v.toFixed(2)));
  }
  return data;
}

// Fetch real prediction from backend
async function fetchPrediction(symbol) {
  try {
    const response = await fetch(`http://localhost:5000/predict?symbol=${symbol}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (e) {
    console.error('Prediction API failed:', e);
    return { action: 'HOLD', predicted_price: 0, error: e.message };
  }
}

// Update UI with new bank/symbol
async function updateBank(bankKey) {
  currentBank = bankKey;
  const info = bankStocks[bankKey];
  stockNameEl.textContent = info.name;
  await performUpdate();
}

// Main update: Fetch prediction + update chart/UI
async function performUpdate() {
  if (isLoading) return;
  isLoading = true;

  const info = bankStocks[currentBank];
  
  // Fetch real QuantAgent prediction
  const predData = await fetchPrediction(info.symbol);
  const latestPred = predData.predicted_price || info.base * 1.01;
  const action = predData.action || 'HOLD';
  
  // Generate mock actual series for chart (simulates historical data)
  const base = info.base * (0.95 + Math.random() * 0.1);
  const actual = generateSeries(timeframeHours, base);
  const latestActual = actual[actual.length - 1];
  
  // Predicted series: slight trend from actual toward prediction
  const predicted = actual.map((v, i) => {
    const progress = i / actual.length;
    return v + (latestPred - v) * progress * 0.3;
  });

  // Update chart
  const labels = actual.map((_, i) => i + 1);
  chart.data.labels = labels;
  chart.data.datasets[0].data = predicted; // Prediction line
  chart.data.datasets[1].data = actual;    // Actual line
  chart.update('none');

  // Update prices
  stockPriceEl.textContent = fmt(latestActual);
  predPriceEl.textContent = fmt(latestPred);
  actPriceEl.textContent = fmt(latestActual);

  // Change %
  const prev = actual[Math.max(0, actual.length - 2)];
  const changePct = prev ? ((latestActual - prev) / prev) * 100 : 0;
  stockChangeEl.textContent = fmtPct(changePct);
  stockChangeEl.className = `change ${changePct >= 0 ? 'positive' : 'negative'}`;

  // Confidence based on action
  let conf = 50;
  if (action === 'BUY') conf = 75;
  else if (action === 'SELL') conf = 68;
  confidenceEl.textContent = `${conf}%`;

  // Log action (add action display to HTML if desired)
  console.log(`[${info.symbol}] Action: ${action}, Pred: ₹${latestPred}, Error: ${predData.error || 'none'}`);

  isLoading = false;
}

// Chart.js setup
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
        fill: false
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
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: (ctx) => `${ctx.dataset.label}: ${fmt(ctx.parsed.y)}`
        }
      }
    },
    scales: {
      x: { display: false },
      y: {
        grid: { color: 'rgba(255,255,255,0.03)' },
        ticks: { callback: v => fmt(v) }
      }
    }
  }
});

// Event listeners
bankSelect.addEventListener('change', (e) => {
  updateBank(e.target.value);
});

timeBtns.forEach(btn => btn.addEventListener('click', (e) => {
  timeBtns.forEach(b => b.classList.remove('active'));
  e.currentTarget.classList.add('active');
  timeframeHours = parseInt(e.currentTarget.dataset.range, 10);
  performUpdate();
}));

simulateBtn.addEventListener('click', () => performUpdate());
refreshBtn.addEventListener('click', () => performUpdate());

// Auto-refresh for live feel
setInterval(() => {
  if (Math.random() > 0.55) performUpdate();
}, 9000);

// Init
updateBank(currentBank);
