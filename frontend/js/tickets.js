class Tickets {
    static async render() {
        const container = document.getElementById('content-area');
        container.innerHTML = `
            <div class="ticket-controls">
                <select id="filterStatus">
                    <option value="">All Status</option>
                    <option value="Open">Open</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Resolved">Resolved</option>
                    <option value="Closed">Closed</option>
                </select>
                <select id="filterPriority">
                    <option value="">All Priority</option>
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Critical">Critical</option>
                </select>
                <select id="filterCategory">
                    <option value="">All Categories</option>
                    <option value="Network">Network</option>
                    <option value="Hardware">Hardware</option>
                    <option value="Software">Software</option>
                    <option value="Access">Access</option>
                </select>
                <input type="text" id="searchTickets" placeholder="Search tickets...">
            </div>
            <div id="ticketList" class="ticket-list"></div>
        `;

        // Add event listeners
        document.getElementById('filterStatus').addEventListener('change', this.loadTickets);
        document.getElementById('filterPriority').addEventListener('change', this.loadTickets);
        document.getElementById('filterCategory').addEventListener('change', this.loadTickets);
        document.getElementById('searchTickets').addEventListener('input', this.loadTickets);

        await this.loadTickets();
    }

    static async loadTickets() {
        try {
            const status = document.getElementById('filterStatus').value;
            const priority = document.getElementById('filterPriority').value;
            const category = document.getElementById('filterCategory').value;
            const search = document.getElementById('searchTickets').value;

            let url = '/tickets?';
            if (status) url += `status=${status}&`;
            if (priority) url += `priority=${priority}&`;
            if (category) url += `category=${category}&`;
            if (search) url += `search=${search}&`;

            const tickets = await ApiClient.get(url);
            const container = document.getElementById('ticketList');
            
            if (tickets.length === 0) {
                container.innerHTML = '<div style="text-align:center;color:var(--text-secondary);padding:40px;">No tickets found</div>';
                return;
            }

            container.innerHTML = tickets.map(ticket => `
                <div class="ticket-item priority-${ticket.priority.toLowerCase()}" onclick="Tickets.viewTicket(${ticket.id})">
                    <div class="ticket-info">
                        <h3>${ticket.title}</h3>
                        <div class="ticket-meta">
                            <span>#${ticket.id}</span>
                            <span>${ticket.category}</span>
                            <span>${ticket.reporter_name}</span>
                            ${ticket.assigned_to ? `<span>Assigned: ${ticket.assigned_to}</span>` : ''}
                            <span class="ticket-status status-${ticket.status.toLowerCase().replace(' ', '-')}">${ticket.status}</span>
                        </div>
                    </div>
                    <div style="font-size:12px;color:var(--text-secondary);">
                        ${new Date(ticket.created_at).toLocaleDateString()}
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading tickets:', error);
        }
    }

    static async viewTicket(id) {
        try {
            const ticket = await ApiClient.get(`/tickets/${id}`);
            const activities = await ApiClient.get(`/activities/ticket/${id}`);
            
            const modal = document.getElementById('ticketModal');
            const body = document.getElementById('modalBody');
            
            body.innerHTML = `
                <h2>${ticket.title}</h2>
                <div style="margin: 20px 0;">
                    <p><strong>ID:</strong> #${ticket.id}</p>
                    <p><strong>Status:</strong> <span class="ticket-status status-${ticket.status.toLowerCase().replace(' ', '-')}">${ticket.status}</span></p>
                    <p><strong>Priority:</strong> ${ticket.priority}</p>
                    <p><strong>Category:</strong> ${ticket.category}</p>
                    <p><strong>Reporter:</strong> ${ticket.reporter_name}</p>
                    <p><strong>Assigned To:</strong> ${ticket.assigned_to || 'Unassigned'}</p>
                    <p><strong>Description:</strong></p>
                    <p style="background:var(--bg-card);padding:12px;border-radius:6px;">${ticket.description}</p>
                    <p><strong>Created:</strong> ${new Date(ticket.created_at).toLocaleString()}</p>
                    ${ticket.updated_at ? `<p><strong>Updated:</strong> ${new Date(ticket.updated_at).toLocaleString()}</p>` : ''}
                </div>
                
                <div style="margin: 20px 0;">
                    <h3>Update Ticket</h3>
                    <select id="updateStatus" style="padding:8px;background:var(--bg-card);color:var(--text-primary);border:1px solid var(--border-color);border-radius:4px;">
                        <option value="Open" ${ticket.status === 'Open' ? 'selected' : ''}>Open</option>
                        <option value="In Progress" ${ticket.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                        <option value="Resolved" ${ticket.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
                        <option value="Closed" ${ticket.status === 'Closed' ? 'selected' : ''}>Closed</option>
                    </select>
                    <input type="text" id="updateAssignee" placeholder="Assign to..." value="${ticket.assigned_to || ''}" style="margin-left:10px;padding:8px;background:var(--bg-card);color:var(--text-primary);border:1px solid var(--border-color);border-radius:4px;">
                    <button class="btn btn-primary" onclick="Tickets.updateTicket(${ticket.id})">Update</button>
                    <button class="btn btn-danger" onclick="Tickets.deleteTicket(${ticket.id})" style="margin-left:10px;">Delete</button>
                </div>

                <div style="margin: 20px 0;">
                    <h3>Activity Timeline</h3>
                    <div class="timeline">
                        ${activities.map(activity => `
                            <div class="timeline-item">
                                <div class="time">${new Date(activity.timestamp).toLocaleString()}</div>
                                <div class="action">${activity.action}</div>
                                <div class="description">${activity.description}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                ${ticket.status === 'Open' || ticket.status === 'In Progress' ? `
                    <div style="margin: 20px 0;">
                        <h3>Resolve Ticket</h3>
                        <div class="form-group">
                            <label>Root Cause</label>
                            <input type="text" id="rootCause" placeholder="Enter root cause...">
                        </div>
                        <div class="form-group">
                            <label>Troubleshooting Steps</label>
                            <textarea id="troubleshootingSteps" placeholder="Describe troubleshooting steps..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>Resolution Summary</label>
                            <textarea id="resolutionSummary" placeholder="Summary of resolution..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>Prevention Notes</label>
                            <textarea id="preventionNotes" placeholder="Prevention notes..."></textarea>
                        </div>
                        <button class="btn btn-success" onclick="Tickets.resolveTicket(${ticket.id})">Resolve Ticket</button>
                        <button class="btn btn-primary" onclick="Tickets.createKnowledgeArticle(${ticket.id})" style="margin-left:10px;">Add to Knowledge Base</button>
                    </div>
                ` : ''}
            `;
            
            modal.style.display = 'block';
        } catch (error) {
            console.error('Error viewing ticket:', error);
        }
    }

    static async updateTicket(id) {
        try {
            const status = document.getElementById('updateStatus').value;
            const assigned_to = document.getElementById('updateAssignee').value;
            
            await ApiClient.put(`/tickets/${id}`, { status, assigned_to });
            alert('Ticket updated successfully!');
            document.getElementById('ticketModal').style.display = 'none';
            this.loadTickets();
        } catch (error) {
            console.error('Error updating ticket:', error);
            alert('Error updating ticket');
        }
    }

    static async deleteTicket(id) {
        if (!confirm('Are you sure you want to delete this ticket?')) return;
        
        try {
            await ApiClient.delete(`/tickets/${id}`);
            alert('Ticket deleted successfully!');
            document.getElementById('ticketModal').style.display = 'none';
            this.loadTickets();
        } catch (error) {
            console.error('Error deleting ticket:', error);
            alert('Error deleting ticket');
        }
    }

    static async resolveTicket(id) {
        try {
            const resolution = {
                ticket_id: id,
                root_cause: document.getElementById('rootCause').value,
                troubleshooting_steps: document.getElementById('troubleshootingSteps').value,
                resolution_summary: document.getElementById('resolutionSummary').value,
                prevention_notes: document.getElementById('preventionNotes').value
            };
            
            await ApiClient.post(`/tickets/${id}/resolve`, resolution);
            alert('Ticket resolved successfully!');
            document.getElementById('ticketModal').style.display = 'none';
            this.loadTickets();
        } catch (error) {
            console.error('Error resolving ticket:', error);
            alert('Error resolving ticket');
        }
    }

    static async createKnowledgeArticle(ticketId) {
        try {
            const ticket = await ApiClient.get(`/tickets/${ticketId}`);
            
            const article = {
                title: `KB-${ticketId}: ${ticket.title}`,
                problem: ticket.description,
                solution: document.getElementById('resolutionSummary').value || 'No solution provided',
                category: ticket.category,
                ticket_id: ticketId
            };
            
            await ApiClient.post('/knowledge', article);
            alert('Knowledge article created successfully!');
        } catch (error) {
            console.error('Error creating knowledge article:', error);
            alert('Error creating knowledge article');
        }
    }
}