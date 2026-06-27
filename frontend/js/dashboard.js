class Dashboard {
    static async render() {
        try {
            const stats = await ApiClient.get('/dashboard/stats');
            
            const container = document.getElementById('content-area');
            container.innerHTML = `
                <div class="dashboard-stats">
                    <div class="stat-card">
                        <div class="label">Total Tickets</div>
                        <div class="value blue">${stats.total_tickets}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Open</div>
                        <div class="value yellow">${stats.open_tickets}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">In Progress</div>
                        <div class="value blue">${stats.in_progress_tickets}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Resolved</div>
                        <div class="value green">${stats.resolved_tickets}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Critical</div>
                        <div class="value red">${stats.critical_tickets}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Most Common Category</div>
                        <div class="value" style="font-size:24px;">${stats.most_common_category || 'N/A'}</div>
                    </div>
                </div>
                <div style="margin-top:30px;">
                    <h2>Recent Tickets</h2>
                    <div id="recentTickets"></div>
                </div>
            `;
            
            // Load recent tickets
            const tickets = await ApiClient.get('/tickets?limit=5');
            const recentContainer = document.getElementById('recentTickets');
            recentContainer.innerHTML = tickets.map(ticket => `
                <div class="ticket-item priority-${ticket.priority.toLowerCase()}">
                    <div class="ticket-info">
                        <h3>${ticket.title}</h3>
                        <div class="ticket-meta">
                            <span>#${ticket.id}</span>
                            <span>${ticket.category}</span>
                            <span>${ticket.reporter_name}</span>
                            <span class="ticket-status status-${ticket.status.toLowerCase().replace(' ', '-')}">${ticket.status}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }
}