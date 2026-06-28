// App initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
    
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
                    showNewTicketForm();
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

// New Ticket Form - This function creates the form
function showNewTicketForm() {
    console.log('Showing new ticket form...');
    
    const container = document.getElementById('content-area');
    
    // Clear container and add form
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
                <div class="form-group">
                    <label>Reporter Name *</label>
                    <input type="text" id="reporterName" placeholder="Your full name" required>
                </div>
                <div class="form-group">
                    <label>Assign To</label>
                    <input type="text" id="assignTo" placeholder="Technician name (optional)">
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%;padding:12px;font-size:16px;">
                    <i class="fas fa-plus-circle"></i> Create Ticket
                </button>
            </form>
        </div>
    `;
    
    // Attach form submit handler
    const form = document.getElementById('newTicketForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Form submitted');
            
            try {
                const ticket = {
                    title: document.getElementById('ticketTitle').value.trim(),
                    description: document.getElementById('ticketDescription').value.trim(),
                    category: document.getElementById('ticketCategory').value,
                    priority: document.getElementById('ticketPriority').value,
                    reporter_name: document.getElementById('reporterName').value.trim(),
                    assigned_to: document.getElementById('assignTo').value.trim() || null
                };
                
                // Validate required fields
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
                if (!ticket.reporter_name) {
                    alert('Please enter your name');
                    document.getElementById('reporterName').focus();
                    return;
                }
                
                console.log('Creating ticket:', ticket);
                
                const result = await ApiClient.post('/tickets', ticket);
                console.log('Ticket created:', result);
                
                alert('✅ Ticket created successfully!');
                form.reset();
                
                // Redirect to tickets view after creation
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

// Make function available globally
window.showNewTicketForm = showNewTicketForm;