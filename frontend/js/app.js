// ============================================
// AUTHENTICATION CHECK
// ============================================

// Check if user is authenticated
if (!localStorage.getItem('access_token')) {
    window.location.href = '/login.html';
}

// ============================================
// MAIN APP INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
    
    // Update user info in header
    const userInfo = document.querySelector('.user-info');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (user && userInfo) {
        // Update username
        const userNameSpan = userInfo.querySelector('.user-name');
        if (userNameSpan) {
            userNameSpan.textContent = user.full_name || user.username || 'User';
        }
        
        // Add logout button if not exists
        if (!document.getElementById('logoutBtn')) {
            const logoutBtn = document.createElement('button');
            logoutBtn.id = 'logoutBtn';
            logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> Logout';
            logoutBtn.style.cssText = `
                background: transparent;
                border: 1px solid var(--border-color);
                color: var(--text-secondary);
                padding: 6px 14px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 13px;
                transition: all 0.3s ease;
                font-family: 'Inter', sans-serif;
                margin-left: 12px;
            `;
            logoutBtn.onmouseover = function() {
                this.style.borderColor = 'var(--accent-red)';
                this.style.color = 'var(--accent-red)';
            };
            logoutBtn.onmouseout = function() {
                this.style.borderColor = 'var(--border-color)';
                this.style.color = 'var(--text-secondary)';
            };
            logoutBtn.onclick = function() {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                window.location.href = '/login.html';
            };
            userInfo.appendChild(logoutBtn);
        }
    }
    
    // Load dashboard by default
    Dashboard.render();
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active state
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            this.classList.add('active');
            
            // Update page title
            const page = this.dataset.page;
            const titles = {
                'dashboard': 'Dashboard',
                'tickets': 'Ticket Management',
                'knowledge': 'Knowledge Base',
                'new-ticket': 'Create New Ticket',
                'admin': 'Admin Settings'
            };
            document.getElementById('page-title').textContent = titles[page] || page;
            
            // Load appropriate content
            switch(page) {
                case 'dashboard':
                    Dashboard.render();
                    break;
                case 'tickets':
                    Tickets.render();
                    break;
                case 'knowledge':
                    Knowledge.render();
                    break;
                case 'new-ticket':
                    showNewTicketForm();
                    break;
                case 'admin':
                    showAdminPage();
                    break;
                default:
                    console.log('Unknown page:', page);
            }
        });
    });
    
    // Modal close
    document.querySelector('.close-modal').addEventListener('click', function() {
        document.getElementById('ticketModal').style.display = 'none';
    });
    
    window.addEventListener('click', function(e) {
        const modal = document.getElementById('ticketModal');
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// ============================================
// NEW TICKET FORM
// ============================================

function showNewTicketForm() {
    console.log('Showing new ticket form...');
    
    const container = document.getElementById('content-area');
    
    container.innerHTML = `
        <div style="max-width: 700px;margin:0 auto;padding:20px;">
            <h2 style="margin-bottom:20px;color:var(--accent-blue);">
                <i class="fas fa-plus-circle"></i> Create New Ticket
            </h2>
            <form id="newTicketForm" style="background:var(--bg-card);padding:30px;border-radius:12px;border:1px solid var(--border-color);">
                <div class="form-group">
                    <label>Title *</label>
                    <input type="text" id="ticketTitle" placeholder="Brief summary of the issue" required>
                </div>
                <div class="form-group">
                    <label>Description *</label>
                    <textarea id="ticketDescription" placeholder="Detailed description of the problem" required style="min-height:120px;"></textarea>
                </div>
                <div class="form-group">
                    <label>Category *</label>
                    <select id="ticketCategory" required>
                        <option value="">Select Category</option>
                        <option value="Network">🌐 Network</option>
                        <option value="Hardware">💻 Hardware</option>
                        <option value="Software">📱 Software</option>
                        <option value="Access">🔐 Access</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Priority *</label>
                    <select id="ticketPriority" required>
                        <option value="Low">🟢 Low</option>
                        <option value="Medium" selected>🟡 Medium</option>
                        <option value="High">🟠 High</option>
                        <option value="Critical">🔴 Critical</option>
                    </select>
                </div>
                <!-- ASSIGN TO FIELD - ADDED BACK -->
                <div class="form-group">
                    <label>Assign To</label>
                    <input type="text" id="assignTo" placeholder="Username or email (optional)">
                    <small style="color:var(--text-secondary);font-size:12px;">Leave blank to keep unassigned</small>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%;padding:12px;font-size:16px;">
                    <i class="fas fa-plus-circle"></i> Create Ticket
                </button>
            </form>
        </div>
    `;
    
    const form = document.getElementById('newTicketForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Form submitted');
            
            try {
                // Get the token
                const token = localStorage.getItem('access_token');
                if (!token) {
                    alert('❌ Not authenticated! Please login again.');
                    window.location.href = '/login.html';
                    return;
                }
                
                // Get assign to value
                const assignToValue = document.getElementById('assignTo').value.trim();
                
                // Prepare ticket data with assigned_to
                const ticket = {
                    title: document.getElementById('ticketTitle').value.trim(),
                    description: document.getElementById('ticketDescription').value.trim(),
                    category: document.getElementById('ticketCategory').value,
                    priority: document.getElementById('ticketPriority').value,
                    assigned_to: assignToValue || null
                };
                
                // Validate
                if (!ticket.title) {
                    alert('Please enter a ticket title');
                    document.getElementById('ticketTitle').focus();
                    return;
                }
                if (!ticket.description) {
                    alert('Please enter a ticket description');
                    document.getElementById('ticketDescription').focus();
                    return;
                }
                if (!ticket.category) {
                    alert('Please select a category');
                    document.getElementById('ticketCategory').focus();
                    return;
                }
                
                console.log('Creating ticket with data:', ticket);
                console.log('Using token:', token.substring(0, 20) + '...');
                
                // Use ApiClient to post
                const result = await ApiClient.post('/tickets', ticket);
                console.log('Ticket created:', result);
                
                alert('✅ Ticket created successfully!');
                form.reset();
                
                document.querySelector('[data-page="tickets"]').click();
            } catch (error) {
                console.error('Error creating ticket:', error);
                alert('❌ Error creating ticket: ' + error.message);
            }
        });
    } else {
        console.error('Form not found!');
    }
}

// ============================================
// ADMIN SETTINGS PAGE
// ============================================

function showAdminPage() {
    console.log('Loading admin page...');
    
    const container = document.getElementById('content-area');
    
    container.innerHTML = `
        <div class="settings-container" style="max-width: 800px;margin:0 auto;padding:20px;">
            <div class="settings-card" style="background:var(--bg-card);border-radius:12px;padding:25px;margin-bottom:20px;border:1px solid var(--border-color);">
                <h3 style="margin-bottom:15px;color:var(--accent-blue);">📧 Email Configuration</h3>
                <p style="color:var(--text-secondary);margin-bottom:20px;font-size:14px;">
                    Configure email settings for automatic ticket creation from emails.
                </p>
                
                <div class="setting-group" style="margin-bottom:15px;">
                    <label style="display:block;margin-bottom:5px;color:var(--text-secondary);font-size:14px;font-weight:500;">Email Host</label>
                    <input type="text" id="emailHost" placeholder="imap.gmail.com" value="imap.gmail.com" style="width:100%;padding:10px;background:var(--bg-primary);border:1px solid var(--border-color);border-radius:6px;color:var(--text-primary);font-size:14px;">
                    <small style="color:var(--text-secondary);font-size:12px;">e.g., imap.gmail.com, outlook.office365.com</small>
                </div>
                
                <div class="setting-group" style="margin-bottom:15px;">
                    <label style="display:block;margin-bottom:5px;color:var(--text-secondary);font-size:14px;font-weight:500;">Email Username</label>
                    <input type="email" id="emailUsername" placeholder="support@yourcompany.com" style="width:100%;padding:10px;background:var(--bg-primary);border:1px solid var(--border-color);border-radius:6px;color:var(--text-primary);font-size:14px;">
                </div>
                
                <div class="setting-group" style="margin-bottom:15px;">
                    <label style="display:block;margin-bottom:5px;color:var(--text-secondary);font-size:14px;font-weight:500;">Email Password</label>
                    <input type="password" id="emailPassword" placeholder="Your app password" style="width:100%;padding:10px;background:var(--bg-primary);border:1px solid var(--border-color);border-radius:6px;color:var(--text-primary);font-size:14px;font-family:monospace;">
                    <small style="color:var(--text-secondary);font-size:12px;">
                        For Gmail, use an <a href="https://myaccount.google.com/apppasswords" target="_blank" style="color:var(--accent-blue);">App Password</a>
                    </small>
                </div>
                
                <div class="setting-group" style="margin-bottom:15px;">
                    <label style="display:block;margin-bottom:5px;color:var(--text-secondary);font-size:14px;font-weight:500;">Email Port</label>
                    <input type="number" id="emailPort" placeholder="993" value="993" style="width:100%;padding:10px;background:var(--bg-primary);border:1px solid var(--border-color);border-radius:6px;color:var(--text-primary);font-size:14px;">
                    <small style="color:var(--text-secondary);font-size:12px;">Default: 993 (IMAP SSL)</small>
                </div>
                
                <div class="setting-group" style="margin-bottom:15px;">
                    <label style="display:block;margin-bottom:5px;color:var(--text-secondary);font-size:14px;font-weight:500;">Check Interval (minutes)</label>
                    <input type="number" id="checkInterval" placeholder="5" value="5" style="width:100%;padding:10px;background:var(--bg-primary);border:1px solid var(--border-color);border-radius:6px;color:var(--text-primary);font-size:14px;">
                    <small style="color:var(--text-secondary);font-size:12px;">How often to check for new emails</small>
                </div>
                
                <div class="setting-group" style="margin-bottom:15px;">
                    <label style="display:block;margin-bottom:5px;color:var(--text-secondary);font-size:14px;font-weight:500;">Auto-Ticket Enabled</label>
                    <select id="autoEnabled" style="width:100%;padding:10px;background:var(--bg-primary);border:1px solid var(--border-color);border-radius:6px;color:var(--text-primary);font-size:14px;">
                        <option value="true">✅ Enabled</option>
                        <option value="false">❌ Disabled</option>
                    </select>
                </div>
                
                <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:20px;">
                    <button class="btn btn-primary" onclick="window.saveSettings()" style="padding:10px 20px;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;background:var(--accent-blue);color:white;">
                        <i class="fas fa-save"></i> Save Settings
                    </button>
                    <button class="btn" onclick="window.testConnection()" style="padding:10px 20px;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;background:var(--accent-yellow);color:var(--bg-primary);">
                        <i class="fas fa-vial"></i> Test Connection
                    </button>
                    <button class="btn" onclick="window.loadSettings()" style="padding:10px 20px;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;background:var(--text-secondary);color:var(--bg-primary);">
                        <i class="fas fa-sync"></i> Load Settings
                    </button>
                </div>
                
                <div id="statusMessage" style="padding:12px;border-radius:6px;margin-top:15px;display:none;"></div>
            </div>
            
            <div class="settings-card" style="background:var(--bg-card);border-radius:12px;padding:25px;border:1px solid var(--border-color);">
                <h3 style="margin-bottom:15px;color:var(--accent-blue);">📊 Email Processing Statistics</h3>
                <div id="emailStats">
                    <p style="color:var(--text-secondary);">Loading stats...</p>
                </div>
            </div>
        </div>
    `;
    
    // Load settings and stats
    loadSettings();
    loadEmailStats();
    
    // Refresh stats every 30 seconds
    if (window.statsInterval) {
        clearInterval(window.statsInterval);
    }
    window.statsInterval = setInterval(loadEmailStats, 30000);
}

// ============================================
// ADMIN SETTINGS FUNCTIONS
// ============================================

async function loadSettings() {
    const statusDiv = document.getElementById('statusMessage');
    if (statusDiv) {
        statusDiv.style.display = 'block';
        statusDiv.style.background = 'rgba(74, 158, 255, 0.1)';
        statusDiv.style.border = '1px solid var(--accent-blue)';
        statusDiv.style.color = 'var(--accent-blue)';
        statusDiv.textContent = 'Loading settings...';
    }
    
    try {
        const response = await fetch('http://localhost:8000/api/settings');
        if (!response.ok) throw new Error('Failed to load settings');
        const data = await response.json();
        
        const hostInput = document.getElementById('emailHost');
        const usernameInput = document.getElementById('emailUsername');
        const passwordInput = document.getElementById('emailPassword');
        const portInput = document.getElementById('emailPort');
        const intervalInput = document.getElementById('checkInterval');
        const autoInput = document.getElementById('autoEnabled');
        
        if (hostInput) hostInput.value = data.EMAIL_HOST || 'imap.gmail.com';
        if (usernameInput) usernameInput.value = data.EMAIL_USERNAME || '';
        if (passwordInput) passwordInput.value = data.EMAIL_PASSWORD || '';
        if (portInput) portInput.value = data.EMAIL_PORT || '993';
        if (intervalInput) intervalInput.value = data.EMAIL_CHECK_INTERVAL || '5';
        if (autoInput) autoInput.value = data.EMAIL_AUTO_TICKET_ENABLED || 'true';
        
        showAdminStatus('success', '✅ Settings loaded successfully!');
    } catch (error) {
        showAdminStatus('error', '❌ Failed to load settings: ' + error.message);
    }
}

async function saveSettings() {
    const settings = {
        EMAIL_HOST: document.getElementById('emailHost').value.trim(),
        EMAIL_USERNAME: document.getElementById('emailUsername').value.trim(),
        EMAIL_PASSWORD: document.getElementById('emailPassword').value.trim(),
        EMAIL_PORT: document.getElementById('emailPort').value.trim(),
        EMAIL_CHECK_INTERVAL: document.getElementById('checkInterval').value.trim(),
        EMAIL_AUTO_TICKET_ENABLED: document.getElementById('autoEnabled').value
    };
    
    if (!settings.EMAIL_USERNAME) {
        showAdminStatus('error', '❌ Please enter an email username');
        return;
    }
    
    showAdminStatus('info', 'Saving settings...');
    try {
        const response = await fetch('http://localhost:8000/api/settings/email', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        if (!response.ok) throw new Error('Failed to save settings');
        const data = await response.json();
        
        showAdminStatus('success', '✅ ' + data.message);
        loadEmailStats();
    } catch (error) {
        showAdminStatus('error', '❌ Failed to save settings: ' + error.message);
    }
}

async function testConnection() {
    showAdminStatus('info', 'Testing email connection...');
    try {
        const response = await fetch('http://localhost:8000/api/settings/email/test');
        if (!response.ok) throw new Error('Connection test failed');
        const data = await response.json();
        
        if (data.status === 'success') {
            showAdminStatus('success', '✅ ' + data.message);
        } else {
            showAdminStatus('error', '❌ ' + data.message);
        }
    } catch (error) {
        showAdminStatus('error', '❌ Connection test failed: ' + error.message);
    }
}

async function loadEmailStats() {
    try {
        const response = await fetch('http://localhost:8000/api/email/stats');
        if (!response.ok) throw new Error('Failed to load stats');
        const data = await response.json();
        
        const statsDiv = document.getElementById('emailStats');
        if (!statsDiv) return;
        
        statsDiv.innerHTML = `
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:15px;margin-top:10px;">
                <div style="background:var(--bg-primary);padding:15px;border-radius:8px;text-align:center;">
                    <div style="color:var(--text-secondary);font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">📧 Total Processed</div>
                    <div style="font-size:24px;font-weight:700;color:var(--accent-blue);margin-top:5px;">${data.total_processed || 0}</div>
                </div>
                <div style="background:var(--bg-primary);padding:15px;border-radius:8px;text-align:center;">
                    <div style="color:var(--text-secondary);font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">📅 Today</div>
                    <div style="font-size:24px;font-weight:700;color:var(--accent-green);margin-top:5px;">${data.today || 0}</div>
                </div>
                <div style="background:var(--bg-primary);padding:15px;border-radius:8px;text-align:center;">
                    <div style="color:var(--text-secondary);font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">❌ Failed</div>
                    <div style="font-size:24px;font-weight:700;color:var(--accent-red);margin-top:5px;">${data.failed || 0}</div>
                </div>
                <div style="background:var(--bg-primary);padding:15px;border-radius:8px;text-align:center;">
                    <div style="color:var(--text-secondary);font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">📊 Success Rate</div>
                    <div style="font-size:24px;font-weight:700;color:var(--accent-yellow);margin-top:5px;">${data.success_rate || 0}%</div>
                </div>
            </div>
            ${data.last_processed ? `<p style="color:var(--text-secondary);font-size:12px;margin-top:10px;">🕐 Last processed: ${new Date(data.last_processed).toLocaleString()}</p>` : ''}
        `;
    } catch (error) {
        const statsDiv = document.getElementById('emailStats');
        if (statsDiv) {
            statsDiv.innerHTML = '<p style="color:var(--text-secondary);">Failed to load stats</p>';
        }
    }
}

function showAdminStatus(type, message) {
    const statusDiv = document.getElementById('statusMessage');
    if (!statusDiv) return;
    
    statusDiv.style.display = 'block';
    statusDiv.style.background = type === 'success' ? 'rgba(74, 222, 128, 0.1)' : 
                                type === 'error' ? 'rgba(248, 113, 113, 0.1)' : 
                                'rgba(74, 158, 255, 0.1)';
    statusDiv.style.border = `1px solid ${type === 'success' ? 'var(--accent-green)' : 
                                          type === 'error' ? 'var(--accent-red)' : 
                                          'var(--accent-blue)'}`;
    statusDiv.style.color = type === 'success' ? 'var(--accent-green)' : 
                            type === 'error' ? 'var(--accent-red)' : 
                            'var(--accent-blue)';
    statusDiv.textContent = message;
    
    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}

// ============================================
// MAKE FUNCTIONS GLOBALLY AVAILABLE
// ============================================

window.showNewTicketForm = showNewTicketForm;
window.showAdminPage = showAdminPage;
window.loadSettings = loadSettings;
window.saveSettings = saveSettings;
window.testConnection = testConnection;
window.loadEmailStats = loadEmailStats;