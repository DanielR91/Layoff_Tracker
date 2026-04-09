// State Management
let layoffData = [];
let filteredData = [];
let trendChart = null;

const state = {
    period: 1, // Default to 1 Month (30 days) as requested
    search: '',
    industry: 'all',
    sortBy: 'date',
    visibleCount: 20 // Pagination
};

// Initialize Dashboard
async function init() {
    try {
        // Use global LAYOFF_DATA (loaded from layoffs.js) instead of fetch to avoid CORS
        layoffData = window.LAYOFF_DATA || [];
        
        // Merge similar company names logic
        layoffData = mergeDuplicates(layoffData);
        
        if (layoffData.length === 0) {
            console.warn('No layoff data found. Ensure src/data/layoffs.js is loaded.');
        }

        // Render Last Updated timestamp
        if (window.LAST_UPDATED) {
            document.getElementById('lastUpdated').textContent = `| UPDATED: ${window.LAST_UPDATED}`;
        }

        applyFilters();
        initEventListeners();
        renderMap();
        console.log('Dashboard initialized with', layoffData.length, 'entries');
    } catch (error) {
        console.error('Failed to load data:', error);
    }
}

function mergeDuplicates(data) {
    const merged = {};
    data.forEach(item => {
        const normName = item.company.toLowerCase().replace(/ llc| inc\.| inc| corp\.| corp/g, '').trim();
        const key = `${normName}_${item.date}`;
        
        if (!merged[key] || item.layoffs > merged[key].layoffs) {
            merged[key] = item;
        }
    });
    return Object.values(merged);
}

// Event Listeners
function initEventListeners() {
    // Search
    document.getElementById('companySearch').addEventListener('input', (e) => {
        state.search = e.target.value.toLowerCase();
        applyFilters();
    });

    // Period Toggles
    document.querySelectorAll('#periodToggle button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#periodToggle button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.period = parseInt(btn.dataset.period);
            applyFilters();
        });
    });

    // Industry Filter
    const industrySelect = document.getElementById('industryFilter');
    const industries = [...new Set(layoffData.map(d => d.industry))];
    industries.forEach(ind => {
        const opt = document.createElement('option');
        opt.value = ind;
        opt.textContent = ind;
        industrySelect.appendChild(opt);
    });

    industrySelect.addEventListener('change', (e) => {
        state.industry = e.target.value;
        applyFilters();
    });

    // Sort By
    document.getElementById('sortBy').addEventListener('change', (e) => {
        state.sortBy = e.target.value;
        applyFilters();
    });
}

// Filtering Logic
function applyFilters() {
    const now = new Date();
    const cutoff = new Date();
    
    // logic for period
    if (state.period === 1) cutoff.setMonth(now.getMonth() - 1);
    else if (state.period === 3) cutoff.setMonth(now.getMonth() - 3);
    else if (state.period === 6) cutoff.setMonth(now.getMonth() - 6);
    else if (state.period === 9) cutoff.setMonth(now.getMonth() - 9);
    else if (state.period === 12) cutoff.setMonth(now.getMonth() - 12);
    else if (state.period === 24) cutoff.setMonth(now.getMonth() - 24);

    const baseFiltered = layoffData.filter(item => {
        const itemDate = new Date(item.date);
        const matchesDate = itemDate >= cutoff;
        const matchesSearch = item.company.toLowerCase().includes(state.search);
        const matchesIndustry = state.industry === 'all' || item.industry === state.industry;
        return matchesDate && matchesSearch && matchesIndustry;
    });

    // Split into Confirmed (layoffs > 0) and news (layoffs <= 0 or null)
    const confirmedItems = baseFiltered.filter(d => d.layoffs && Number(d.layoffs) > 0);
    const newsItems = baseFiltered.filter(d => !d.layoffs || Number(d.layoffs) <= 0);

    // Sort Confirmed
    confirmedItems.sort((a, b) => {
        if (state.sortBy === 'date') return new Date(b.date) - new Date(a.date);
        if (state.sortBy === 'amount') return b.layoffs - a.layoffs;
        return 0;
    });

    // Sort News (always by date)
    newsItems.sort((a, b) => new Date(b.date) - new Date(a.date));

    state.visibleCount = 20; // Reset pagination
    
    renderStats(confirmedItems);
    renderTable(confirmedItems);
    renderNewsFeed(newsItems);
    updateChart(confirmedItems);
}

function renderStats(data) {
    const total = data.reduce((sum, item) => sum + item.layoffs, 0);
    const uniqueCompanies = new Set(data.map(d => d.company)).size;
    const largest = data.length > 0 ? Math.max(...data.map(d => d.layoffs)) : 0;
    
    // Find most affected industry
    const indCount = {};
    data.forEach(d => indCount[d.industry] = (indCount[d.industry] || 0) + d.layoffs);
    const topIndustry = Object.entries(indCount).sort((a,b) => b[1]-a[1])[0]?.[0] || 'N/A';

    const container = document.getElementById('statsContainer');
    container.innerHTML = `
        <div class="stat-card glass">
            <span>Total Layoffs</span>
            <h2 class="glow-cyan">${total.toLocaleString()}</h2>
            <p class="trend up">Last ${state.period} Months</p>
        </div>
        <div class="stat-card glass">
            <span>Companies Affected</span>
            <h2>${uniqueCompanies}</h2>
            <p class="trend">Active Reporting</p>
        </div>
        <div class="stat-card glass">
            <span>Largest Single Cut</span>
            <h2 class="glow-pink">${largest.toLocaleString()}</h2>
            <p class="trend">Peak Event</p>
        </div>
        <div class="stat-card glass">
            <span>Most Impacted Sector</span>
            <h2>${topIndustry}</h2>
            <p class="trend">By Volume</p>
        </div>
    `;
}

function renderTable(data) {
    const tbody = document.getElementById('layoffBody');
    const displayData = data.slice(0, state.visibleCount);
    
    tbody.innerHTML = displayData.map(item => `
        <tr>
            <td>
                <div style="font-weight: 600">${item.company}</div>
                <div style="font-size: 0.7rem; color: var(--text-secondary)">${item.industry}</div>
            </td>
            <td>${new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</td>
            <td>
                <div style="display: flex; align-items: center; gap: 6px">
                    <i data-lucide="trending-down" style="width: 14px; color: var(--accent-pink)"></i>
                    <span class="badge" style="color: var(--accent-pink)">${item.layoffs.toLocaleString()}</span>
                </div>
            </td>
            <td><a href="${item.source}" target="_blank" class="source-link">Source</a></td>
        </tr>
    `).join('');
    
    lucide.createIcons();
    // ... rest of button logic

    // Handle Load More Button
    let loadMoreBtn = document.getElementById('loadMoreBtn');
    if (!loadMoreBtn) {
        loadMoreBtn = document.createElement('button');
        loadMoreBtn.id = 'loadMoreBtn';
        loadMoreBtn.className = 'glass load-more-btn';
        document.getElementById('confirmedSection').appendChild(loadMoreBtn);
        loadMoreBtn.addEventListener('click', () => {
            state.visibleCount += 50;
            renderTable(data);
        });
    }
    
    if (state.visibleCount >= data.length) {
        loadMoreBtn.style.display = 'none';
    } else {
        loadMoreBtn.style.display = 'block';
        loadMoreBtn.textContent = `Load More (${data.length - state.visibleCount} remaining)`;
    }
}

function renderNewsFeed(data) {
    const feed = document.getElementById('newsFeed');
    if (data.length === 0) {
        feed.innerHTML = '<div class="news-item" style="text-align: center; color: var(--text-secondary)">No recent rumors found.</div>';
        return;
    }

    // Only show top 10 news items for density
    feed.innerHTML = data.slice(0, 10).map(item => `
        <div class="news-item">
            <div class="news-meta">
                <div style="display: flex; align-items: center; gap: 4px">
                    <i data-lucide="newspaper" style="width: 12px"></i>
                    <span class="news-tag">${item.industry}</span>
                </div>
                <span>${new Date(item.date).toLocaleDateString()}</span>
            </div>
            <h4>${item.company} layoffs reported</h4>
            <div class="news-meta">
                <a href="${item.source}" target="_blank" class="source-link">Read Full Article</a>
            </div>
        </div>
    `).join('');

    lucide.createIcons();
}

function updateChart(data) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    // Aggregate by month
    const dataByMonth = {};
    data.forEach(d => {
        const month = d.date.substring(0, 7); // YYYY-MM
        dataByMonth[month] = (dataByMonth[month] || 0) + d.layoffs;
    });

    const labels = Object.keys(dataByMonth).sort();
    const values = labels.map(l => dataByMonth[l]);

    if (trendChart) trendChart.destroy();
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Layoffs per Month',
                data: values,
                borderColor: '#00f2ff',
                backgroundColor: 'rgba(0, 242, 255, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 3,
                pointBackgroundColor: '#00f2ff',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, border: { display: false } },
                x: { grid: { display: false }, border: { display: false } }
            }
        }
    });
}

function renderMap() {
    // Simple mock SVG map representation
    const container = document.getElementById('mapContainer');
    container.innerHTML = `
        <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; position: relative">
            <svg viewBox="0 0 800 400" width="100%" height="100%" style="opacity: 0.3">
                <path fill="currentColor" d="M150,150 Q200,100 250,150 T350,150 T450,150 T550,150 T650,150" stroke="var(--accent-cyan)" stroke-width="1" fill="none"/>
                <!-- Simplistic world shape -->
                <rect x="100" y="100" width="100" height="60" rx="10" fill="rgba(255,255,255,0.05)"/>
                <rect x="300" y="80" width="150" height="100" rx="10" fill="rgba(255,255,255,0.05)"/>
                <rect x="550" y="120" width="120" height="80" rx="10" fill="rgba(255,255,255,0.05)"/>
            </svg>
            <div style="position: absolute; top: 120px; left: 140px; text-align: center">
                <div class="glow-pink" style="font-size: 1.5rem; font-weight: 700">NA</div>
                <div style="font-size: 0.7rem">High Impact</div>
            </div>
            <div style="position: absolute; top: 100px; left: 360px; text-align: center">
                <div class="glow-cyan" style="font-size: 1.5rem; font-weight: 700">EU</div>
                <div style="font-size: 0.7rem">Moderate</div>
            </div>
             <div style="position: absolute; top: 140px; left: 580px; text-align: center">
                <div class="glow-cyan" style="font-size: 1.5rem; font-weight: 700">ASIA</div>
                <div style="font-size: 0.7rem">Expanding</div>
            </div>
        </div>
    `;
}

// Start app
init();
