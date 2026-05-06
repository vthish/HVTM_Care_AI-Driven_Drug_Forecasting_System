function switchTab(tabId) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.add('hidden'));

    const activeTab = document.getElementById(`tab-${tabId}`);
    if (activeTab) {
        activeTab.classList.remove('hidden');
        activeTab.classList.add('animate-fade-in');
    }

    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    const currentBtn = document.getElementById(`nav-${tabId}`);
    if (currentBtn) {
        currentBtn.classList.add('active');
    }

    const titles = {
        'predict': 'AI Predictor',
        'analytics': 'Shortage Analysis',
        'logs': 'Inventory Logs',
        'finance': 'Financial Insights'
    };
    
    const titleEl = document.getElementById('header-title');
    if (titleEl && titles[tabId]) {
        titleEl.innerText = titles[tabId];
    }

    lucide.createIcons();
}

window.onload = function() {
    lucide.createIcons();
};