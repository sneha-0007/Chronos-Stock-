/**
 * script.js  –  Chronos Stock (fully fixed)
 *
 * Fixes:
 *  - candleSeries.setVisible() removed (not in lightweight-charts v4)
 *    → series are destroyed and re-created when chart type changes
 *  - All buttons wired up
 *  - Time range filter working
 *  - Live prices from backend
 */

const bankSelect      = document.getElementById('bankSelect');
const chartTypeSelect = document.getElementById('chartType');
const indicatorSelect = document.getElementById('indicator');
const stockNameEl     = document.getElementById('stockName');
const stockPriceEl    = document.getElementById('stockPrice');
const stockChangeEl   = document.getElementById('stockChange');
const predPriceEl     = document.getElementById('predPrice');
const actPriceEl      = document.getElementById('actPrice');
const confidenceEl    = document.getElementById('confidence');

// ── Lightweight Charts setup ──────────────────────────────────────────────────
const chart = LightweightCharts.createChart(
    document.getElementById('priceChart'),
    {
        layout:    { background: { color: '#071226' }, textColor: '#DDD' },
        grid:      { vertLines: { color: '#1a2233' }, horzLines: { color: '#1a2233' } },
        crosshair: { mode: 1 },
        timeScale: { timeVisible: true, secondsVisible: false },
        rightPriceScale: { borderColor: '#1a2233' },
    }
);

// Active series references (null = not currently on chart)
let candleSeries    = null;
let lineSeries      = null;
let volumeSeries    = null;
let indicatorSeries = null;

// ── State ─────────────────────────────────────────────────────────────────────
let allData          = [];
let activeRangeHours = 6;
let lastSlice        = [];

// ── Helpers ───────────────────────────────────────────────────────────────────
const BANK_NAMES = {
    hdfc:  'HDFC Bank',
    sbi:   'State Bank of India',
    icici: 'ICICI Bank',
    axis:  'Axis Bank',
    kotak: 'Kotak Mahindra Bank',
};

function symbolFromBank(b) {
    return { hdfc:'HDFCBANK.NS', sbi:'SBIN.NS', icici:'ICICIBANK.NS', axis:'AXISBANK.NS', kotak:'KOTAKBANK.NS' }[b];
}

function formatINR(n) {
    return '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function filterByRange(data, hours) {
    if (!data.length) return data;
    const cutoff = data[data.length - 1].time - hours * 3600;
    return data.filter(d => d.time >= cutoff);
}

function removeSeries(s) {
    if (s) { try { chart.removeSeries(s); } catch(e) {} }
    return null;
}

// ── Chart rendering ───────────────────────────────────────────────────────────
function renderChart(data) {
    if (!data.length) return;
    lastSlice = data;

    const type = chartTypeSelect.value;

    // Remove all price series first
    candleSeries    = removeSeries(candleSeries);
    lineSeries      = removeSeries(lineSeries);
    volumeSeries    = removeSeries(volumeSeries);
    indicatorSeries = removeSeries(indicatorSeries);

    // Always add volume
    volumeSeries = chart.addHistogramSeries({
        priceFormat:  { type: 'volume' },
        priceScaleId: '',
        color:        '#26a69a',
    });
    volumeSeries.setData(data.map(d => ({
        time:  d.time,
        value: d.volume,
        color: d.close > d.open ? '#26a69a' : '#ef5350',
    })));

    // Add candle OR line depending on selection
    if (type === 'candle') {
        candleSeries = chart.addCandlestickSeries();
        candleSeries.setData(data.map(d => ({
            time: d.time, open: d.open, high: d.high, low: d.low, close: d.close,
        })));
    } else {
        lineSeries = chart.addLineSeries({ color: '#00d0ff', lineWidth: 2 });
        lineSeries.setData(data.map(d => ({ time: d.time, value: d.close })));
    }

    renderIndicator(data);
}

function renderIndicator(data) {
    indicatorSeries = removeSeries(indicatorSeries);
    const ind = indicatorSelect.value;
    if (ind === 'sma') {
        indicatorSeries = chart.addLineSeries({ color: '#aae825', lineWidth: 2 });
        indicatorSeries.setData(data.filter(d => d.sma && !isNaN(d.sma)).map(d => ({ time: d.time, value: d.sma })));
    } else if (ind === 'rsi') {
        indicatorSeries = chart.addLineSeries({ color: '#ffaa00', lineWidth: 2 });
        indicatorSeries.setData(data.filter(d => d.rsi && !isNaN(d.rsi)).map(d => ({ time: d.time, value: d.rsi })));
    }
}

// ── Data fetching ─────────────────────────────────────────────────────────────
async function loadChart() {
    const symbol = symbolFromBank(bankSelect.value);
    stockNameEl.textContent  = BANK_NAMES[bankSelect.value] || 'Bank';
    stockPriceEl.textContent = 'Loading…';
    stockChangeEl.textContent = '';

    try {
        const res  = await fetch(`http://127.0.0.1:5000/chart?symbol=${symbol}&interval=5m`);
        const json = await res.json();

        if (!json.data) {
            stockPriceEl.textContent = 'Error';
            console.error('Backend error:', json.error);
            return;
        }

        allData = json.data.map(d => ({
            time:   new Date(d.time).getTime() / 1000,
            open:   +d.open, high: +d.high, low: +d.low, close: +d.close,
            volume: +d.volume, sma: +d.SMA, rsi: +d.RSI,
        }));

        const slice = filterByRange(allData, activeRangeHours);
        renderChart(slice);

        // Update price display
        const latest    = json.latest_price;
        const predicted = json.predicted_price;
        const prev      = allData.length > 1 ? allData[allData.length - 2].close : latest;
        const changePct = ((latest - prev) / prev * 100).toFixed(2);
        const isPos     = changePct >= 0;

        stockPriceEl.textContent  = formatINR(latest);
        stockChangeEl.textContent = (isPos ? '+' : '') + changePct + '%';
        stockChangeEl.className   = 'change ' + (isPos ? 'positive' : 'negative');

        predPriceEl.textContent  = formatINR(predicted);
        actPriceEl.textContent   = formatINR(latest);
        confidenceEl.textContent = json.confidence + '%';

    } catch (err) {
        console.error('Fetch failed:', err);
        stockPriceEl.textContent = 'Offline';
    }
}

// ── Event listeners ───────────────────────────────────────────────────────────
bankSelect.addEventListener('change', loadChart);

chartTypeSelect.addEventListener('change', () => {
    if (lastSlice.length) renderChart(lastSlice);
});

indicatorSelect.addEventListener('change', () => {
    if (lastSlice.length) renderIndicator(lastSlice);
});

document.querySelectorAll('.time-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeRangeHours = +btn.dataset.range;
        renderChart(filterByRange(allData, activeRangeHours));
    });
});

document.getElementById('simulate').addEventListener('click', async () => {
    const btn    = document.getElementById('simulate');
    const symbol = symbolFromBank(bankSelect.value);
    btn.textContent = 'Analyzing…';
    btn.disabled    = true;

    try {
        const res  = await fetch('http://127.0.0.1:5000/analyze', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ symbol, interval: '5m' }),
        });
        const json = await res.json();
        if (json.error) {
            alert('Analysis error: ' + json.error);
        } else {
            alert('📊 QuantAgent Decision\n\n' + (json.decision || 'No decision returned') +
                '\n\n--- Indicator ---\n' + (json.indicator_report || '') +
                '\n\n--- Pattern ---\n'   + (json.pattern_report   || '') +
                '\n\n--- Trend ---\n'     + (json.trend_report     || ''));
        }
    } catch (err) {
        alert('Could not reach backend: ' + err.message);
    } finally {
        btn.textContent = 'Simulate update';
        btn.disabled    = false;
    }
});

document.getElementById('refresh').addEventListener('click', loadChart);

// ── Initial load ──────────────────────────────────────────────────────────────
loadChart();