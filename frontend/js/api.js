const API_URL = "http://127.0.0.1:8000";
window.inventoryLogs = []; 

function stayOnLogsTab() {
    const logsTabBtn = document.getElementById('nav-logs');
    if(logsTabBtn) {
        logsTabBtn.click(); // Force stay on Logs tab
    }
}

async function predictNow(event) {
    if (event) event.preventDefault();
    const brand = document.getElementById('brand-select').value;
    const stock = document.getElementById('stock-input').value;
    const btn = document.getElementById('predict-btn');

    if (!brand || !stock) {
        showToast("Please complete all fields first", "error");
        return;
    }

    btn.innerText = "ANALYZING...";
    btn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                brand_name: brand,
                current_stock: parseFloat(stock),
                usd_rate: currentUSD
            })
        });

        const data = await response.json();
        lastPrediction = data;

        document.getElementById('results-card').classList.remove('hidden');
        
        if (typeof updateUnifiedResults === 'function') {
            updateUnifiedResults(data);
        }

        showToast("AI Prediction Complete");

    } catch (error) {
        showToast("Connection Failed", "error");
    } finally {
        btn.innerText = "GENERATE FORECAST";
        btn.disabled = false;
    }
}

async function saveLogEntry(event) {
    if (event) event.preventDefault(); 
    
    const brand = document.getElementById('log-brand').value;
    const year = document.getElementById('log-year').value;
    const month = document.getElementById('log-month').value;
    const qty = document.getElementById('log-qty').value;
    
    const receivedQtyRaw = document.getElementById('log-received-qty').value;
    const receivedQty = receivedQtyRaw === "" ? 0.0 : parseFloat(receivedQtyRaw);

    const errorMsgEl = document.getElementById('modal-error-msg');
    if(errorMsgEl) errorMsgEl.classList.add('hidden'); 

    if(!brand || !qty) {
        if(errorMsgEl) {
            errorMsgEl.innerText = "Please fill in all required fields.";
            errorMsgEl.classList.remove('hidden');
        }
        return;
    }

    try {
        const response = await fetch(`${API_URL}/data/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                brand_name: brand,
                year: parseInt(year),
                month: parseInt(month),
                actual_issued_qty: parseFloat(qty),
                received_qty: receivedQty,
                usd_rate: currentUSD
            })
        });

        const res = await response.json();
        if(response.ok) {
            showToast("Consumption Logged Successfully");
            toggleModal('add-modal', false);
            await fetchLogs(); 
            stayOnLogsTab(); // Stay on inventory logs!
        } else {
            if(errorMsgEl) {
                errorMsgEl.innerText = res.detail || "Validation Error";
                errorMsgEl.classList.remove('hidden');
            } else {
                showToast(res.detail, "error");
            }
        }
    } catch (e) {
        if(errorMsgEl) {
            errorMsgEl.innerText = "Failed to connect to the server.";
            errorMsgEl.classList.remove('hidden');
        } else {
            showToast("Failed to Save Entry", "error");
        }
    }
}

async function executeDelete(event) {
    if (event) event.preventDefault();
    if(!window.recordToDelete) return;
    
    const { brandName, dateStr } = window.recordToDelete;
    closeDeleteModal(); 

    try {
        const response = await fetch(`${API_URL}/data/delete?brand_name=${encodeURIComponent(brandName)}&date=${encodeURIComponent(dateStr)}`, {
            method: 'DELETE'
        });

        if(response.ok) {
            showToast("Record Deleted Successfully");
            await fetchLogs();
            stayOnLogsTab(); // Stay on inventory logs!
        } else {
            showToast("Failed to delete record", "error");
        }
    } catch(e) {
        showToast("Connection Error", "error");
    }
}

async function saveEditedEntry(event) {
    if (event) event.preventDefault(); 
    
    const brand = document.getElementById('edit-brand').value;
    const dateStr = document.getElementById('edit-date').value; 
    
    const qtyRaw = document.getElementById('edit-issued-qty').value;
    const receivedQtyRaw = document.getElementById('edit-received-qty').value;
    
    const issuedQty = qtyRaw === "" ? 0.0 : parseFloat(qtyRaw);
    const receivedQty = receivedQtyRaw === "" ? 0.0 : parseFloat(receivedQtyRaw);

    const [year, month, day] = dateStr.split('-');

    try {
        const delResponse = await fetch(`${API_URL}/data/delete?brand_name=${encodeURIComponent(brand)}&date=${encodeURIComponent(dateStr)}`, {
            method: 'DELETE'
        });

        if(!delResponse.ok) throw new Error("Failed to clear old record");

        const addResponse = await fetch(`${API_URL}/data/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                brand_name: brand,
                year: parseInt(year),
                month: parseInt(month),
                actual_issued_qty: issuedQty,
                received_qty: receivedQty,
                usd_rate: currentUSD
            })
        });

        if(addResponse.ok) {
            showToast("Record Updated Successfully");
            toggleEditModal(false);
            await fetchLogs();
            stayOnLogsTab(); // Stay on inventory logs!
        } else {
            showToast("Failed to save edited data", "error");
        }
    } catch(e) {
        showToast("Update Error: " + e.message, "error");
    }
}

async function fetchLogs() {
    try {
        const response = await fetch(`${API_URL}/data/logs`);
        if (response.ok) {
            const data = await response.json();
            window.inventoryLogs = data; 
            if (typeof renderLogsTable === 'function') {
                renderLogsTable(data);
            }
            if (typeof updateBrandLock === 'function') {
                updateBrandLock(); 
            }
        }
    } catch (e) {
        console.error("Failed to fetch logs:", e);
    }
}

function showToast(msg, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-10 right-10 ${type === 'success' ? 'bg-gray-900' : 'bg-red-600'} text-white px-8 py-4 rounded-2xl shadow-2xl font-black text-[10px] uppercase tracking-widest animate-bounce z-[200]`;
    toast.innerText = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}