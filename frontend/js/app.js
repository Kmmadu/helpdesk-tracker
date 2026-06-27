// App initialization
document.addEventListener('DOMContentLoaded', function() {
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
                'new-ticket': 'Create New Ticket'
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
                    this.showNewTicketForm();
                    break;
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

// New Ticket Form
function showNewTicketForm() {
    const container = document.getElementById('content-area');
    container.innerHTML = `
        <div style="max-width: 600px;margin:0 auto;">
            <h2>Create New Ticket</h2>
            <form id="newTicketForm">
                <div class="form-group">
                    <label>Title*</label>
                    <input type="text" id="ticketTitle" required>
                </div>
                <div class="form-group">
                    <label>Description*</label>
                    <textarea id="ticketDescription" required></textarea>
                </div>
                <div class="form-group">
                    <label>Category*</label>
                    <select id="ticketCategory" required>
                        <option value="Network">Network</option>
                        <option value="Hardware">Hardware</option>
                        <option value="Software">Software</option>
                        <option value="Access">Access</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Priority*</label>
                    <select id="ticketPriority" required>
                        <option value="Low">Low</option>
                        <option value="Medium" selected>Medium</option>
                        <option value="High">High</option>
                        <option value="Critical">Critical</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Reporter Name*</label>
                    <input type="text" id="reporterName" required>
                </div>
                <div class="form-group">
                    <label>Assign To</label>
                    <input type="text" id="assignTo" placeholder="Optional">
                </div>
                <button type="submit" class="btn btn-primary">Create Ticket</button>
            </form>
        </div>
    `;
    
    document.getElementById('newTicketForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        try {
            const ticket = {
                title: document.getElementById('ticketTitle').value,
                description: document.getElementById('ticketDescription').value,
                category: document.getElementById('ticketCategory').value,
                priority: document.getElementById('ticketPriority').value,
                reporter_name: document.getElementById('reporterName').value,
                assigned_to: document.getElementById('assignTo').value || null
            };
            
            await ApiClient.post('/tickets', ticket);
            alert('Ticket created successfully!');
            this.reset();
        } catch (error) {
            console.error('Error creating ticket:', error);
            alert('Error creating ticket');
        }
    });
}