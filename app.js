let jobsData = [];
let dataTable;
let lastUpdateTime = null;

// GitHub Configuration - UPDATE THESE!
const GITHUB_USERNAME = 'TheCracker007';  // Your GitHub username
const GITHUB_REPO = 'TabbedAIOPlus';      // Your repository name
const GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN_HERE'; // Add your token here OR use repository secret

// Source colors
const sourceColors = {
    'CareerPower': 'primary',
    'AllGovtJobs': 'success',
    'AllGovtJobs-Filtered': 'info',
    'SarkariResult': 'warning'
};

// Show alert notification
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    const alertId = 'alert-' + Date.now();
    
    const icons = {
        'success': '✅',
        'danger': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show alert-custom" role="alert">
            <strong>${icons[type] || 'ℹ️'}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            const bsAlert = bootstrap.Alert.getInstance(alert);
            if (bsAlert) bsAlert.close();
        }
    }, 5000);
}

// Check if data needs refresh (older than 4 hours)
function needsRefresh() {
    if (!lastUpdateTime) return false;
    
    const now = new Date();
    const diff = (now - lastUpdateTime) / 1000 / 60 / 60; // hours
    
    return diff >= 4; // If data is 4+ hours old
}

// Update refresh button info
function updateRefreshInfo() {
    const infoDiv = document.getElementById('refresh-info');
    
    if (!lastUpdateTime) {
        infoDiv.textContent = '';
        return;
    }
    
    const hours = Math.floor((new Date() - lastUpdateTime) / 1000 / 60 / 60);
    
    if (hours >= 4) {
        infoDiv.innerHTML = '<span style="color: #ff9800;">⚠️ Data is ' + hours + 'h old</span>';
    } else {
        infoDiv.textContent = 'Updated ' + hours + 'h ago';
    }
}

// Smart refresh function
async function smartRefresh() {
    const btn = document.getElementById('refresh-btn');
    const btnText = document.getElementById('refresh-text');
    const btnIcon = btn.querySelector('i');
    
    // Check if refresh is needed
    if (!needsRefresh() && lastUpdateTime) {
        const hours = Math.floor((new Date() - lastUpdateTime) / 1000 / 60 / 60);
        showAlert(`Data was updated ${hours} hour(s) ago. Refresh is only needed after 4+ hours.`, 'info');
        return;
    }
    
    // Disable button
    btn.disabled = true;
    btn.classList.add('spinning');
    
    // Show progress modal
    const modal = new bootstrap.Modal(document.getElementById('progressModal'));
    modal.show();
    
    try {
        // Step 1: Trigger workflow
        updateProgress(10, 'Triggering GitHub Actions workflow...');
        
        const response = await fetch(`https://api.github.com/repos/${GITHUB_USERNAME}/${GITHUB_REPO}/actions/workflows/scrape.yml/dispatches`, {
            method: 'POST',
            headers: {
                'Accept': 'application/vnd.github+json',
                'Authorization': `Bearer ${GITHUB_TOKEN}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ref: 'main'
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to trigger workflow');
        }
        
        updateProgress(30, 'Workflow triggered! Waiting for scraper to start...');
        
        // Step 2: Wait for workflow to start
        await sleep(5000);
        updateProgress(50, 'Scraping job websites...');
        
        // Step 3: Wait for scraping to complete (estimated 60 seconds)
        await sleep(30000);
        updateProgress(70, 'Almost done... Saving data...');
        
        await sleep(20000);
        updateProgress(85, 'Committing changes to repository...');
        
        // Step 4: Wait for commit
        await sleep(10000);
        updateProgress(95, 'Refreshing page data...');
        
        // Step 5: Reload page data
        await sleep(5000);
        const newData = await fetchJobs();
        
        if (newData && newData.jobs.length > 0) {
            updateProgress(100, 'Success! Jobs updated.');
            
            // Hide modal after short delay
            setTimeout(() => {
                modal.hide();
                
                // Refresh the page to show new data
                location.reload();
            }, 1000);
            
            showAlert(`Successfully refreshed! Found ${newData.totalJobs} jobs.`, 'success');
        } else {
            throw new Error('No data received');
        }
        
    } catch (error) {
        console.error('Refresh error:', error);
        modal.hide();
        showAlert('Refresh failed. Please try again or check GitHub Actions manually.', 'danger');
        
        // Re-enable button
        btn.disabled = false;
        btn.classList.remove('spinning');
    }
}

// Helper function to update progress
function updateProgress(percent, message) {
    document.getElementById('progress-bar').style.width = percent + '%';
    document.getElementById('progress-message').textContent = message;
}

// Helper sleep function
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Fetch data from jobs.json
async function fetchJobs() {
    try {
        // Add timestamp to prevent caching
        const timestamp = new Date().getTime();
        const response = await fetch(`jobs.json?t=${timestamp}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        jobsData = data.jobs;
        
        // Store last update time
        if (data.lastUpdated) {
            lastUpdateTime = new Date(data.lastUpdated);
            updateRefreshInfo();
        }
        
        console.log('Fetched jobs:', jobsData.length);
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}

// Initialize the page
async function init() {
    const data = await fetchJobs();
    
    if (!data || jobsData.length === 0) {
        document.getElementById('loading').innerHTML = '<p class="text-danger">Failed to load jobs. Please try again later.</p>';
        return;
    }
    
    // Hide loading, show table
    document.getElementById('loading').style.display = 'none';
    document.getElementById('table-container').style.display = 'block';
    
    // Update stats
    updateStats(data);
    
    // Populate filters
    populateFilters();
    
    // Render table
    renderTable();
    
    // Setup event listeners
    setupEventListeners();
    
    // Update refresh info periodically
    setInterval(updateRefreshInfo, 60000); // Every minute
}

// Update statistics
function updateStats(data) {
    document.getElementById('total-jobs').textContent = data.totalJobs;
    
    // Get unique sources
    const uniqueSources = [...new Set(jobsData.map(job => job.source))];
    document.getElementById('total-sources').textContent = uniqueSources.length;
    
    // Get last update time
    if (data.lastUpdated) {
        const lastUpdate = new Date(data.lastUpdated);
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
