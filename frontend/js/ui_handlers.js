const DRUG_BRAND_MAP = {
    "Metformin": ["Metfogen-XR", "Glilcomet", "Glucopet-XR"],
    "Gliclazide": ["Diamicron-MR", "Diatica", "Glycinorm"],
    "Sitagliptin": ["Sita", "Sitavic", "Nsit"],
    "Pioglitazone": ["Pioz", "Glustin", "Actos"],
    "Atorvastatin": ["Atova", "Atovic", "Lipitor"],
    "Losartan": ["Losacar", "Zaart", "Repace"],
    "Amlodipine": ["Amlodac", "Amlong", "Amlopress"],
    "Bisoprolol": ["Bisovic", "Concor", "Monocor"],
    "Thyroxine": ["Euthyrox", "Thyronom", "TH (Levothyroxime)"],
    "Enalapril": ["Enam", "Envas", "Innovace"]
};

let currentUSD = 310.50;
let lastPrediction = null;
window.recordToDelete = null;

const SESSION_TIMEOUT = 24 * 60 * 60 * 1000;

function checkSession() {
    const loginTime = localStorage.getItem('hvtm_login_time');
    const isLoggedIn = localStorage.getItem('hvtm_auth');
    if (isLoggedIn === 'true' && loginTime) {
        const now = new Date().getTime();
        if (now - parseInt(loginTime) > SESSION_TIMEOUT) {
            logout();
        }
    }
}

// 100% Bulletproof Brand Loader
window.updateBrandOptions = function() {
    const genericSelect = document.getElementById('generic-select');
    const brandSelect = document.getElementById('brand-select');
    
    if (!genericSelect || !brandSelect) return;
    
    const generic = genericSelect.value;
    brandSelect.innerHTML = '<option value="">Select Brand...</option>';
    
    if (generic && DRUG_BRAND_MAP[generic]) {
        const brands = DRUG_BRAND_MAP[generic];
        for (let i = 0; i < brands.length; i++) {
            const opt = document.createElement('option');
            opt.value = brands[i];
            opt.innerHTML = brands[i];
            brandSelect.appendChild(opt);
        }
    }
};

function simulateUSD() {
    setInterval(() => {
        const change = (Math.random() * 0.1 - 0.05);
        currentUSD = parseFloat((currentUSD + change).toFixed(2));
        const usdDisp = document.getElementById('live-usd-display');
        if(usdDisp) usdDisp.innerText = currentUSD;
    }, 5000);
}

function toggleMobileMenu() {
    const nav = document.getElementById('nav-menu');
    nav.classList.toggle('hidden');
}

function updateUnifiedResults(data) {
    const resultCard = document.getElementById('results-card');
    resultCard.classList.remove('hidden');
    
    document.getElementById('order-qty').innerText = data.suggested_order_qty.toLocaleString();
    document.getElementById('demand-qty').innerText = data.predicted_demand.toLocaleString();
    document.getElementById('predict-date-range').innerText = data.prediction_period || "---";

    const exhaustionEl = document.getElementById('exhaustion-date-display');
    const riskBadge = document.getElementById('risk-badge');
    const currentStock = parseFloat(data.current_stock);
    const dailyDemand = data.predicted_demand / 30.0;

    if (currentStock <= 0) {
        exhaustionEl.innerText = "OUT OF STOCK";
        exhaustionEl.className = "text-xl font-black text-slate-400";
        riskBadge.innerText = "CRITICAL";
        riskBadge.className = "px-5 py-2 rounded-[25px] text-[10px] font-black bg-slate-800 text-white uppercase tracking-widest";
    } else {
        const daysRemaining = Math.floor(currentStock / dailyDemand);
        const exhDate = new Date();
        exhDate.setDate(exhDate.getDate() + daysRemaining);
        exhaustionEl.innerText = exhDate.toDateString();
        
        if (daysRemaining < 10) {
            riskBadge.innerText = "HIGH RISK";
            riskBadge.className = "px-5 py-2 rounded-[25px] text-[10px] font-black bg-slate-700 text-white uppercase tracking-widest";
            exhaustionEl.className = "text-xl font-black text-slate-700";
        } else {
            riskBadge.innerText = "OPTIMAL";
            riskBadge.className = "px-5 py-2 rounded-[25px] text-[10px] font-black bg-slate-200 text-slate-700 uppercase tracking-widest";
            exhaustionEl.className = "text-xl font-black text-slate-800";
        }
    }

    const learningBadge = document.getElementById('learning-badge');
    if (data.applied_learning_weight && data.applied_learning_weight !== "None") {
        learningBadge.classList.remove('hidden');
    } else {
        learningBadge.classList.add('hidden');
    }
}

function lockFutureMonths() {
    const yearSelect = document.getElementById('log-year');
    const monthSelect = document.getElementById('log-month');
    if (!yearSelect || !monthSelect) return;
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth() + 1;
    const selectedYear = parseInt(yearSelect.value);
    Array.from(monthSelect.options).forEach(option => {
        const optMonth = parseInt(option.value);
        if (selectedYear > currentYear) option.disabled = true;
        else if (selectedYear === currentYear && optMonth > currentMonth) option.disabled = true;
        else option.disabled = false;
    });
    if (monthSelect.options[monthSelect.selectedIndex].disabled) monthSelect.value = currentMonth;
}

function updateBrandLock() {
    const yearSelect = document.getElementById('log-year');
    const monthSelect = document.getElementById('log-month');
    const brandSelect = document.getElementById('log-brand');
    if (!yearSelect || !monthSelect || !brandSelect) return;
    const selectedYear = yearSelect.value;
    const selectedMonth = monthSelect.value;
    if (selectedYear === "2026" && selectedMonth === "1") {
        Array.from(brandSelect.options).forEach(option => {
            if (option.value !== "") {
                option.disabled = true;
                option.text = `${option.value} (Locked)`;
            }
        });
        brandSelect.value = "";
        return;
    }
    const targetDate = `${selectedYear}-${selectedMonth.padStart(2, '0')}-01`;
    const existingBrands = (window.inventoryLogs || []).filter(log => log.Date === targetDate).map(log => log.Brand_Name);
    Array.from(brandSelect.options).forEach(option => {
        if (option.value === "") return;
        if (existingBrands.includes(option.value)) {
            option.disabled = true;
            option.text = `${option.value} (Added)`;
            if (option.selected) brandSelect.value = ""; 
        } else {
            option.disabled = false;
            option.text = option.value;
        }
    });
}

function toggleModal(id, show) {
    const modal = document.getElementById(id);
    if(show) {
        modal.classList.remove('hidden');
        populateLogBrands();
        document.getElementById('log-qty').value = '';
        const receivedQtyInput = document.getElementById('log-received-qty');
        if(receivedQtyInput) receivedQtyInput.value = '';
        const errorMsg = document.getElementById('modal-error-msg');
        if(errorMsg) { errorMsg.classList.add('hidden'); errorMsg.innerText = ''; }
        lockFutureMonths();
        updateBrandLock(); 
    } else {
        modal.classList.add('hidden');
    }
}

function populateLogBrands() {
    const logBrand = document.getElementById('log-brand');
    logBrand.innerHTML = '<option value="">Select Brand...</option>';
    Object.values(DRUG_BRAND_MAP).flat().forEach(brand => logBrand.add(new Option(brand, brand)));
}

function renderLogsTable(entries) {
    const tbody = document.getElementById('logs-body');
    if(!tbody) return;
    tbody.innerHTML = '';
    const limitDate = new Date('2026-02-01');
    const filteredEntries = entries.filter(entry => new Date(entry.Date) >= limitDate);
    filteredEntries.forEach((entry) => {
        const dateStr = entry.Date || 'N/A';
        const brandName = entry.Brand_Name || 'N/A';
        const issuedQty = entry.Issued_Qty || 0;
        const receivedQty = entry.Received_Qty || 0;
        tbody.innerHTML += `
            <tr class="hover:bg-slate-100 transition-colors group">
                <td class="px-10 py-6 text-slate-500 font-bold">${dateStr}</td>
                <td class="px-10 py-6 font-black text-slate-800">
                    ${brandName}
                    <span class="block text-[9px] text-slate-400 font-bold uppercase mt-1">Received: ${receivedQty.toLocaleString()}</span>
                </td>
                <td class="px-10 py-6 text-center font-black text-lg text-slate-700">${issuedQty.toLocaleString()}</td>
                <td class="px-10 py-6 text-right space-x-2">
                    <button onclick="openEditModal('${brandName}', '${dateStr}', ${issuedQty}, ${receivedQty})" class="text-slate-500 font-black text-[10px] uppercase px-4 py-2 rounded-[25px] hover:bg-slate-200 transition-colors">Edit</button>
                    <button onclick="openDeleteModal('${brandName}', '${dateStr}')" class="text-red-500 font-black text-[10px] uppercase px-4 py-2 rounded-[25px] hover:bg-red-50 transition-colors">Delete</button>
                </td>
            </tr>`;
    });
    if(window.lucide) lucide.createIcons();
}

function openDeleteModal(brandName, dateStr) {
    window.recordToDelete = { brandName, dateStr };
    const delName = document.getElementById('del-brand-name');
    if(delName) delName.innerText = `${brandName} (${dateStr})`;
    document.getElementById('delete-modal').classList.remove('hidden');
}

function closeDeleteModal() {
    window.recordToDelete = null;
    document.getElementById('delete-modal').classList.add('hidden');
}

function openEditModal(brandName, dateStr, issuedQty, receivedQty) {
    const info = document.getElementById('edit-record-info');
    if(info) info.innerText = `${brandName} | ${dateStr}`;
    document.getElementById('edit-brand').value = brandName;
    document.getElementById('edit-date').value = dateStr;
    document.getElementById('edit-issued-qty').value = issuedQty;
    document.getElementById('edit-received-qty').value = receivedQty;
    document.getElementById('edit-modal').classList.remove('hidden');
}

function toggleEditModal(show) {
    const modal = document.getElementById('edit-modal');
    if(show) modal.classList.remove('hidden');
    else modal.classList.add('hidden');
}

window.addEventListener('load', () => {
    checkSession();
    simulateUSD();
    if (typeof fetchLogs === 'function') fetchLogs();
});