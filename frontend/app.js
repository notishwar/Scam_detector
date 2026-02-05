// ============== STATE MANAGEMENT ==============
const state = {
    sessionId: null,
    apiKey: sessionStorage.getItem('llm_api_key') || '',
    llmUrl: sessionStorage.getItem('llm_url') || 'https://openrouter.ai/api/v1/chat/completions',
    llmModel: sessionStorage.getItem('llm_model') || 'meta-llama/llama-3.1-8b-instruct',
    backendUrl: 'https://honeypot-backend-production-8bc9.up.railway.app',
    persona: 'elderly',
    inboxItems: [],
    currentInboxIndex: 0,
    intel: {
        upi_ids: [],
        bank_accounts: [],
        phone_numbers: [],
        urls: [],
        crypto_wallets: [],
        emails: [],
        ip_addresses: []
    }
};

// ============== DOM ELEMENTS ==============
const elements = {
    apiKeyInput: document.getElementById('llm-api-key'),
    llmBaseUrlInput: document.getElementById('llm-base-url'),
    llmModelInput: document.getElementById('llm-model'),
    backendUrlInput: document.getElementById('backend-url'),
    personaSelect: document.getElementById('persona-select'),
    connectionStatus: document.getElementById('connection-status'),
    apiStatus: document.getElementById('api-status'),
    scammerInput: document.getElementById('scammer-input'),
    analyzeBtn: document.getElementById('analyze-btn'),
    messagesArea: document.getElementById('messages-area'),
    inboxList: document.getElementById('inbox-list'),
    fraudBadge: document.getElementById('fraud-badge'),
    fraudPercent: document.getElementById('fraud-percent'),
    intelUpi: document.getElementById('intel-upi'),
    intelBank: document.getElementById('intel-bank'),
    intelPhone: document.getElementById('intel-phone'),
    intelUrl: document.getElementById('intel-url'),
    intelCrypto: document.getElementById('intel-crypto'),
    intelEmail: document.getElementById('intel-email'),
    intelIp: document.getElementById('intel-ip'),
    themeToggle: document.getElementById('theme-toggle'),
    clearActivityBtn: document.getElementById('clear-activity-btn'),
    sidebar: document.getElementById('sidebar'),
    intelPanel: document.querySelector('.intel-panel'),
    searchInput: document.getElementById('search-input')
};

// ============== INITIALIZATION ==============
function init() {
    state.sessionId = 'sess_' + generateId();

    // Load saved values
    if (elements.apiKeyInput) elements.apiKeyInput.value = state.apiKey;
    if (elements.llmBaseUrlInput) elements.llmBaseUrlInput.value = state.llmUrl;
    if (elements.llmModelInput) elements.llmModelInput.value = state.llmModel;
    if (elements.backendUrlInput) elements.backendUrlInput.value = state.backendUrl;

    // Check connection
    updateConnectionStatus();

    // Event listeners
    setupEventListeners();

    // DON'T load demo inbox - it should be empty initially
    // Inbox will populate as conversations happen
}

function setupEventListeners() {
    // Settings
    elements.apiKeyInput?.addEventListener('change', (e) => {
        state.apiKey = e.target.value;
        sessionStorage.setItem('llm_api_key', state.apiKey);
        updateConnectionStatus();
    });

    elements.llmBaseUrlInput?.addEventListener('change', (e) => {
        state.llmUrl = e.target.value;
        sessionStorage.setItem('llm_url', state.llmUrl);
    });

    elements.llmModelInput?.addEventListener('change', (e) => {
        state.llmModel = e.target.value;
        sessionStorage.setItem('llm_model', state.llmModel);
    });

    elements.backendUrlInput?.addEventListener('change', (e) => {
        state.backendUrl = e.target.value;
    });

    elements.personaSelect?.addEventListener('change', (e) => {
        state.persona = e.target.value;
    });

    // Actions
    elements.analyzeBtn?.addEventListener('click', handleAnalyze);
    elements.themeToggle?.addEventListener('click', toggleTheme);
    elements.clearActivityBtn?.addEventListener('click', clearActivity);

    // Search functionality
    elements.searchInput?.addEventListener('input', handleSearch);

    // Mobile nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            const view = e.currentTarget.dataset.view;
            switchMobileView(view, e.currentTarget);
        });
    });

    // Enter to send
    elements.scammerInput?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleAnalyze();
        }
    });
}

// ============== CONNECTION STATUS ==============
function updateConnectionStatus() {
    const isConnected = state.apiKey && state.apiKey.length > 10;

    if (elements.connectionStatus) {
        if (isConnected) {
            elements.connectionStatus.classList.add('connected');
            elements.connectionStatus.querySelector('span:last-child').textContent = 'Connected';
        } else {
            elements.connectionStatus.classList.remove('connected');
            elements.connectionStatus.querySelector('span:last-child').textContent = 'Disconnected';
        }
    }

    if (elements.apiStatus) {
        elements.apiStatus.textContent = isConnected ? 'Connected' : 'Not Connected';
        elements.apiStatus.style.background = isConnected
            ? 'rgba(16, 185, 129, 0.2)'
            : 'rgba(239, 68, 68, 0.2)';
        elements.apiStatus.style.color = isConnected
            ? 'var(--success)'
            : 'var(--danger)';
    }
}

// ============== MESSAGE HANDLING ==============
async function handleAnalyze() {
    const message = elements.scammerInput.value.trim();
    if (!message) return;

    if (!state.apiKey) {
        alert('Please enter your API Key in the settings first!');
        return;
    }

    // Add scammer message to UI
    addMessage('scammer', message);
    elements.scammerInput.value = '';

    // Disable button
    elements.analyzeBtn.disabled = true;
    elements.analyzeBtn.textContent = 'Analyzing...';

    try {
        const response = await fetch(`${state.backendUrl}/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-LLM-API-KEY': state.apiKey
            },
            body: JSON.stringify({
                session_id: state.sessionId,
                message: message,
                persona: state.persona,
                llm_url: state.llmUrl || undefined,
                llm_model: state.llmModel || undefined
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        // Add agent reply
        addMessage('agent', data.reply);

        // Update risk indicator
        updateRiskIndicator(data.scam_confidence);

        // Update intel
        mergeIntel(data.extracted_intel);

        // Add to inbox
        addInboxItem(message, data.scam_confidence);

    } catch (error) {
        console.error('Error:', error);
        addMessage('agent', `⚠️ Error: ${error.message}`);
    } finally {
        elements.analyzeBtn.disabled = false;
        elements.analyzeBtn.textContent = 'Analyze & Reply';
    }
}

function addMessage(type, text, tags = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'scammer' ? '🚨' : '🤖';

    const content = document.createElement('div');
    content.className = 'message-content';

    const header = document.createElement('div');
    header.className = 'message-header';
    header.innerHTML = `
        <span class="message-sender">${type === 'scammer' ? 'Scammer' : 'Agent (Elderly)'}</span>
        <span class="message-time">${formatTime(new Date())}</span>
    `;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;

    content.appendChild(header);
    content.appendChild(bubble);

    if (tags.length > 0) {
        const tagsDiv = document.createElement('div');
        tagsDiv.className = 'risk-tags';
        tags.forEach(tag => {
            const tagSpan = document.createElement('span');
            tagSpan.className = `risk-tag ${tag.toLowerCase()}`;
            tagSpan.textContent = tag;
            tagsDiv.appendChild(tagSpan);
        });
        content.appendChild(tagsDiv);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    elements.messagesArea.appendChild(messageDiv);
    elements.messagesArea.scrollTop = elements.messagesArea.scrollHeight;
}

// ============== RISK INDICATOR ==============
function updateRiskIndicator(confidence) {
    if (elements.fraudPercent) {
        elements.fraudPercent.textContent = `Fraud Risk: ${Math.round(confidence)}%`;
    }

    if (elements.fraudBadge) {
        if (confidence > 70) {
            elements.fraudBadge.textContent = 'HIGH';
            elements.fraudBadge.style.background = 'rgba(239, 68, 68, 0.2)';
            elements.fraudBadge.style.color = 'var(--danger)';
        } else if (confidence > 40) {
            elements.fraudBadge.textContent = 'MEDIUM';
            elements.fraudBadge.style.background = 'rgba(245, 158, 11, 0.2)';
            elements.fraudBadge.style.color = 'var(--warning)';
        } else {
            elements.fraudBadge.textContent = 'LOW';
            elements.fraudBadge.style.background = 'rgba(16, 185, 129, 0.2)';
            elements.fraudBadge.style.color = 'var(--success)';
        }
    }
}

// ============== INTEL MANAGEMENT ==============
function mergeIntel(newIntel) {
    // Merge new intel with existing
    Object.keys(newIntel).forEach(key => {
        if (Array.isArray(newIntel[key])) {
            newIntel[key].forEach(item => {
                if (!state.intel[key].includes(item)) {
                    state.intel[key].push(item);
                }
            });
        }
    });

    // Update display
    renderIntel();
}

function renderIntel() {
    renderIntelSection(elements.intelUpi, state.intel.upi_ids);
    renderIntelSection(elements.intelBank, state.intel.bank_accounts);
    renderIntelSection(elements.intelPhone, state.intel.phone_numbers);
    renderIntelSection(elements.intelUrl, state.intel.urls);
    renderIntelSection(elements.intelCrypto, state.intel.crypto_wallets);
    renderIntelSection(elements.intelEmail, state.intel.emails);
    renderIntelSection(elements.intelIp, state.intel.ip_addresses);
}

function renderIntelSection(container, items) {
    if (!container) return;
    container.innerHTML = '';
    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'code-item';
        div.textContent = `"${item}"`;
        container.appendChild(div);
    });
}

// ============== INBOX MANAGEMENT ==============
function addInboxItem(preview, confidence, title = 'Scam Attempt', icon = '🚨', time = null) {
    const item = document.createElement('div');
    item.className = 'inbox-item';
    item.dataset.title = title.toLowerCase();
    item.dataset.preview = preview.toLowerCase();

    const confidenceLevel = confidence > 70 ? 'high' : confidence > 40 ? 'medium' : 'low';

    item.innerHTML = `
        <div class="inbox-icon">${icon}</div>
        <div class="inbox-content">
            <div class="inbox-header">
                <span class="inbox-title">${title}</span>
                <span class="inbox-time">${time || formatTime(new Date())}</span>
            </div>
            <div class="inbox-preview">${preview.substring(0, 50)}...</div>
            <div class="inbox-footer">
                <span class="confidence-tag ${confidenceLevel}">${confidenceLevel.toUpperCase()}</span>
            </div>
        </div>
    `;

    state.inboxItems.push({ title, preview, confidence, icon, time, element: item });
    elements.inboxList.prepend(item);
}

// ============== SEARCH FUNCTIONALITY ==============
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase().trim();

    const inboxItems = elements.inboxList.querySelectorAll('.inbox-item');

    inboxItems.forEach(item => {
        const title = item.dataset.title || '';
        const preview = item.dataset.preview || '';

        const matches = title.includes(searchTerm) || preview.includes(searchTerm);

        if (matches || searchTerm === '') {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });

    // Show message if no results
    const visibleItems = Array.from(inboxItems).filter(item => item.style.display !== 'none');

    let noResultsMsg = elements.inboxList.querySelector('.no-results-message');

    if (visibleItems.length === 0 && searchTerm !== '') {
        if (!noResultsMsg) {
            noResultsMsg = document.createElement('div');
            noResultsMsg.className = 'no-results-message';
            noResultsMsg.style.cssText = 'padding: 20px; text-align: center; color: var(--text-muted); font-size: 0.85rem;';
            noResultsMsg.textContent = 'No conversations found';
            elements.inboxList.appendChild(noResultsMsg);
        }
    } else if (noResultsMsg) {
        noResultsMsg.remove();
    }
}

// ============== UTILITIES ==============
function generateId() {
    return Math.random().toString(36).substring(2, 11);
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
}

function toggleTheme() {
    document.body.classList.toggle('light-theme');

    // Switch icons
    const moonIcon = document.querySelector('.moon-icon');
    const sunIcon = document.querySelector('.sun-icon');

    if (document.body.classList.contains('light-theme')) {
        // Light mode - show sun icon
        moonIcon.style.display = 'none';
        sunIcon.style.display = 'block';
    } else {
        // Dark mode - show moon icon
        moonIcon.style.display = 'block';
        sunIcon.style.display = 'none';
    }
}

function clearActivity() {
    if (confirm('⚠️ Clear all conversation history, inbox items, and extracted intelligence?\n\nThis action cannot be undone.')) {
        // Clear messages
        elements.messagesArea.innerHTML = '';

        // Clear inbox
        elements.inboxList.innerHTML = '';
        state.inboxItems = [];

        // Clear intel
        state.intel = { upi_ids: [], bank_accounts: [], phone_numbers: [], urls: [], crypto_wallets: [], emails: [], ip_addresses: [] };
        renderIntel();

        // Clear search
        if (elements.searchInput) {
            elements.searchInput.value = '';
        }

        // Reset risk indicators
        if (elements.fraudBadge) {
            elements.fraudBadge.textContent = 'LOW';
            elements.fraudBadge.style.background = 'rgba(16, 185, 129, 0.2)';
            elements.fraudBadge.style.color = 'var(--success)';
        }

        if (elements.fraudPercent) {
            elements.fraudPercent.textContent = 'Fraud Risk: 0%';
        }

        console.log('✅ All activity cleared');
    }
}

function switchMobileView(view, activeItem) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    if (activeItem) {
        activeItem.classList.add('active');
    }

    elements.sidebar.classList.toggle('active', view === 'inbox');
    elements.intelPanel.classList.toggle('active', view === 'intel');

    if (view === 'chat') {
        elements.sidebar.classList.remove('active');
        elements.intelPanel.classList.remove('active');
    }
}

// ============== START ==============
document.addEventListener('DOMContentLoaded', init);

