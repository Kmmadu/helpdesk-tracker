class Knowledge {
    static async render() {
        try {
            const articles = await ApiClient.get('/knowledge');
            
            const container = document.getElementById('content-area');
            container.innerHTML = `
                <div style="margin-bottom:20px;">
                    <input type="text" id="searchKnowledge" placeholder="Search knowledge base..." style="width:100%;padding:10px;background:var(--bg-card);color:var(--text-primary);border:1px solid var(--border-color);border-radius:6px;">
                </div>
                <div class="kb-grid" id="knowledgeGrid"></div>
            `;
            
            document.getElementById('searchKnowledge').addEventListener('input', this.loadArticles);
            this.loadArticles(articles);
        } catch (error) {
            console.error('Error loading knowledge base:', error);
        }
    }

    static loadArticles(articles) {
        const search = document.getElementById('searchKnowledge').value.toLowerCase();
        const filtered = articles.filter(a => 
            a.title.toLowerCase().includes(search) || 
            a.problem.toLowerCase().includes(search)
        );
        
        const grid = document.getElementById('knowledgeGrid');
        grid.innerHTML = filtered.map(article => `
            <div class="kb-card">
                <h3>${article.title}</h3>
                <p><strong>Problem:</strong> ${article.problem.substring(0, 100)}${article.problem.length > 100 ? '...' : ''}</p>
                <p><strong>Solution:</strong> ${article.solution.substring(0, 100)}${article.solution.length > 100 ? '...' : ''}</p>
                <span class="category-tag">${article.category}</span>
                <div style="margin-top:8px;font-size:12px;color:var(--text-secondary);">
                    Created: ${new Date(article.created_date).toLocaleDateString()}
                </div>
            </div>
        `).join('');
    }
}