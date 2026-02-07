// Configuration - REPLACE WITH YOUR ACTUAL GOOGLE SHEET ID
const GOOGLE_SHEET_ID = '1F9YWvXyWMAhTtlqp4hnu87dz1V2-ehQKJz-rCuYjjfg';
const SHEET_NAME = 'Jobs';

// Google Sheets JSON feed URL
const SHEET_URL = `https://docs.google.com/spreadsheets/d/${GOOGLE_SHEET_ID}/gviz/tq?tqx=out:json&sheet=${SHEET_NAME}`;

let jobsData = [];
let dataTable;

// Source colors
const sourceColors = {
    'CareerPower': 'primary',
    'AllGovtJobs': 'success',
    'AllGovtJobs-Filtered': 'info',
    'SarkariResult': 'warning',
    'Source5': 'secondary'
};

// Fetch data from Google Sheets
async function fetchJobs() {
    try {
        const response = await fetch(SHEET_URL);
        const text = await response.text();
        
        // Google Sheets returns JSONP, we need to extract the JSON
        const json = JSON.parse(text.substring(47).slice(0, -2));
        
        // Parse the data
        const rows = json.table.rows;
        jobsData = rows.map(row => {
            return {
                source: row.c[0]?.v || 'N/A',
                title: row.c[1]?.v || 'N/A',
                posts: row.c[2]?.v || 'N/A',
                qualification: row.c[3]?.v || 'N/A',
                lastDate: row.c[4]?.v || 'N/A',
                link: row.c[5]?.v || '',
                scrapedAt: row.c[6]?.v || ''
            };
        });
        
        console.log('Fetched jobs:', jobsData.length);
        return true;
    } catch (error) {
        console.error('Error fetching data:', error);
        alert('Error loading jobs data. Please check the Google Sheet ID and make sure the sheet is publicly accessible.');
        return false;
    }
}

// Initialize the page
async function init() {
    const success = await fetchJobs();
    
    if (!success || jobsData.length === 0) {
        document.getElementById('loading').innerHTML = '<p class="text-danger">Failed to load jobs. Please try again later.</p>';
        return;
    }
    
    // Hide loading, show table
    document.getElementById('loading').style.display = 'none';
    document.getElementById('table-container').style.display = 'block';
    
    // Update stats
    updateStats();
    
    // Populate filters
    populateFilters();
    
    // Render table
    renderTable();
    
    // Setup event listeners
    setupEventListeners();
}

// Update statistics
function updateStats() {
    document.getElementById('total-jobs').textContent = jobsData.length;
    
    // Get unique sources
    const uniqueSources = [...new Set(jobsData.map(job => job.source))];
    document.getElementById('total-sources').textContent = uniqueSources.length;
    
    // Get last update time
    if (jobsData.length > 0 && jobsData[0].scrapedAt) {
        const lastUpdate = new Date(jobsData[0].scrapedAt);
        const timeAgo = getTimeAgo(lastUpdate);
        document.getElementById('last-update').textContent = timeAgo;
        document.getElementById('footer-update').textContent = `Last updated: ${lastUpdate.toLocaleString()}`;
    }
}

// Get time ago string
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + 'y ago';
    
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + 'mo ago';
    
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + 'd ago';
    
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + 'h ago';
    
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + 'm ago';
    
    return 'Just now';
}

// Populate filter dropdowns
function populateFilters() {
    // Get unique sources
    const sources = [...new Set(jobsData.map(job => job.source))].sort();
    const sourceFilter = document.getElementById('source-filter');
    sources.forEach(source => {
        const option = document.createElement('option');
        option.value = source;
        option.textContent = source;
        sourceFilter.appendChild(option);
    });
    
    // Get unique qualifications
    const qualifications = [...new Set(jobsData.map(job => job.qualification))].sort();
    const qualFilter = document.getElementById('qualification-filter');
    qualifications.forEach(qual => {
        if (qual && qual !== 'N/A') {
            const option = document.createElement('option');
            option.value = qual;
            option.textContent = qual;
            qualFilter.appendChild(option);
        }
    });
}

// Render table with DataTables
function renderTable() {
    const tbody = document.getElementById('jobs-body');
    tbody.innerHTML = '';
    
    jobsData.forEach(job => {
        const row = document.createElement('tr');
        
        // Source badge
        const sourceColor = sourceColors[job.source] || 'secondary';
        const sourceBadge = `<span class="badge bg-${sourceColor} badge-source">${job.source}</span>`;
        
        // Link button
        const linkButton = job.link ? 
            `<a href="${job.link}" target="_blank" class="btn-link-custom">View</a>` : 
            '<span class="text-muted">N/A</span>';
        
        row.innerHTML = `
            <td>${sourceBadge}</td>
            <td><strong>${job.title}</strong></td>
            <td>${job.posts}</td>
            <td>${job.qualification}</td>
            <td>${job.lastDate}</td>
            <td>${linkButton}</td>
        `;
        
        tbody.appendChild(row);
    });
    
    // Initialize DataTables
    if (dataTable) {
        dataTable.destroy();
    }
    
    dataTable = $('#jobs-table').DataTable({
        pageLength: 25,
        order: [[4, 'desc']], // Sort by Last Date descending
        language: {
            search: "Search all columns:",
            lengthMenu: "Show _MENU_ jobs per page",
            info: "Showing _START_ to _END_ of _TOTAL_ jobs",
            infoFiltered: "(filtered from _MAX_ total jobs)"
        }
    });
}

// Setup event listeners for filters
function setupEventListeners() {
    // Source filter
    document.getElementById('source-filter').addEventListener('change', function() {
        const value = this.value;
        dataTable.column(0).search(value).draw();
    });
    
    // Qualification filter
    document.getElementById('qualification-filter').addEventListener('change', function() {
        const value = this.value;
        dataTable.column(3).search(value).draw();
    });
    
    // Search box (searches all columns)
    document.getElementById('search-box').addEventListener('keyup', function() {
        dataTable.search(this.value).draw();
    });
}

// Start the application
document.addEventListener('DOMContentLoaded', init);
```

---

## 4. requirements.txt
```
beautifulsoup4==4.12.3
requests==2.31.0
pandas==2.2.0
gspread==6.0.0
google-auth==2.27.0
