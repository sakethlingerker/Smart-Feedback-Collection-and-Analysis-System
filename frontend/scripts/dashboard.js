class EnhancedDashboard {
    constructor() {
        this.charts = {};
        this.wordcloudData = null;
        this.pendingDeleteId = null;
        this.autoRefreshInterval = null;
        
        this.initializeDashboard();
    }

    async initializeDashboard() {
        try {
            await this.initializeCharts();
            await this.loadDashboardData();
            await this.loadRecentFeedbacks();
            await this.loadWordCloud();
            
            this.startAutoRefresh();
            this.updateLastUpdated();
            
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.showError('Failed to initialize dashboard');
        }
    }

initializeCharts() {
    return new Promise((resolve) => {
        // 1. Sentiment Distribution (Doughnut)
        this.charts.sentiment = new Chart(
            document.getElementById('sentimentChart'),
            {
                type: 'doughnut',
                data: {
                    labels: ['Positive', 'Negative', 'Neutral'],
                    datasets: [{
                        data: [1, 1, 1],
                        backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { padding: 10, usePointStyle: true }
                        }
                    }
                }
            }
        );

        // 2. Rating Distribution (Bar)
        this.charts.rating = new Chart(
            document.getElementById('ratingChart'),
            {
                type: 'bar',
                data: {
                    labels: ['1★', '2★', '3★', '4★', '5★'],
                    datasets: [{
                        label: 'Ratings',
                        data: [0, 0, 0, 0, 0],
                        backgroundColor: '#667eea',
                        borderColor: '#5a6fd8',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: { beginAtZero: true, ticks: { stepSize: 1 } }
                    },
                    plugins: { legend: { display: false } }
                }
            }
        );

        // 3. Emotion Wheel (Polar Area)
        this.charts.emotionWheel = new Chart(
            document.getElementById('emotionChart'),
            {
                type: 'polarArea',
                data: {
                    labels: ['Joy', 'Trust', 'Fear', 'Surprise', 'Sadness', 'Anger'],
                    datasets: [{
                        data: [1, 1, 1, 1, 1, 1],
                        backgroundColor: [
                            '#fbbf24', '#10b981', '#8b5cf6', 
                            '#ec4899', '#3b82f6', '#ef4444'
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { position: 'right', labels: { font: { size: 10 } } }
                    }
                }
            }
        );

        // 4. Priority Action Matrix (Bubble)
        this.charts.priorityMatrix = new Chart(
            document.getElementById('priorityChart'),
            {
                type: 'bubble',
                data: {
                    datasets: [
                        {
                            label: 'Critical',
                            data: [],
                            backgroundColor: 'rgba(239, 68, 68, 0.7)',
                            borderColor: '#dc2626'
                        },
                        {
                            label: 'High',
                            data: [],
                            backgroundColor: 'rgba(245, 158, 11, 0.7)',
                            borderColor: '#d97706'
                        },
                        {
                            label: 'Medium',
                            data: [],
                            backgroundColor: 'rgba(59, 130, 246, 0.7)',
                            borderColor: '#2563eb'
                        },
                        {
                            label: 'Low',
                            data: [],
                            backgroundColor: 'rgba(16, 185, 129, 0.7)',
                            borderColor: '#059669'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        x: { 
                            title: { display: true, text: 'Impact' },
                            min: 0, max: 10
                        },
                        y: { 
                            title: { display: true, text: 'Frequency' },
                            min: 0, max: 10
                        }
                    }
                }
            }
        );

        // 5. Historical Trend Comparison (Line)
        this.charts.historicalTrend = new Chart(
            document.getElementById('trendChart'),
            {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [
                        {
                            label: 'Current Month',
                            data: [65, 72, 68, 75],
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Previous Month',
                            data: [58, 64, 62, 60],
                            borderColor: '#6b7280',
                            backgroundColor: 'rgba(107, 114, 128, 0.1)',
                            tension: 0.4,
                            fill: true,
                            borderDash: [5, 5]
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: { 
                            beginAtZero: true,
                            title: { display: true, text: 'Sentiment Score' }
                        }
                    }
                }
            }
        );

        // 6. Live Sentiment Meter (Doughnut as Gauge)
        this.charts.sentimentMeter = new Chart(
            document.getElementById('sentimentMeter'),
            {
                type: 'doughnut',
                data: {
                    labels: ['Positive', 'Neutral', 'Negative'],
                    datasets: [{
                        data: [70, 20, 10], // Current sentiment score
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                        borderWidth: 0,
                        circumference: 180,
                        rotation: -90
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    cutout: '70%',
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: false }
                    },
                    animation: { animateScale: true, animateRotate: true }
                }
            }
        );

        // 7. Topic-Sentiment Correlation (Bar)
        this.charts.topicSentiment = new Chart(
            document.getElementById('topicChart'),
            {
                type: 'bar',
                data: {
                    labels: ['Product', 'Support', 'Price', 'Features', 'UI/UX'],
                    datasets: [
                        {
                            label: 'Positive',
                            data: [65, 45, 30, 55, 70],
                            backgroundColor: '#10b981',
                            borderColor: '#059669',
                            borderWidth: 1
                        },
                        {
                            label: 'Negative',
                            data: [15, 35, 50, 25, 10],
                            backgroundColor: '#ef4444',
                            borderColor: '#dc2626',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        x: { stacked: true },
                        y: { 
                            stacked: true,
                            beginAtZero: true,
                            title: { display: true, text: 'Number of Mentions' }
                        }
                    }
                }
            }
        );

        // 8. Sentiment Intensity Gauge (Doughnut)
        this.charts.intensityGauge = new Chart(
            document.getElementById('intensityGauge'),
            {
                type: 'doughnut',
                data: {
                    labels: ['Strong Positive', 'Weak Positive', 'Neutral', 'Weak Negative', 'Strong Negative'],
                    datasets: [{
                        data: [25, 20, 30, 15, 10],
                        backgroundColor: [
                            '#059669', // Strong Positive
                            '#10b981', // Weak Positive
                            '#f59e0b', // Neutral
                            '#f97316', // Weak Negative
                            '#dc2626'  // Strong Negative
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { 
                            position: 'bottom',
                            labels: { font: { size: 10 }, padding: 8 }
                        }
                    }
                }
            }
        );

        resolve();
    });
}

updateCharts(data) {
    // 1. Update Sentiment Distribution
    this.charts.sentiment.data.datasets[0].data = [
        data.sentiment_distribution.positive || 0,
        data.sentiment_distribution.negative || 0,
        data.sentiment_distribution.neutral || 0
    ];
    this.charts.sentiment.update();

    // 2. Update Rating Distribution
    const ratingData = [0, 0, 0, 0, 0];
    Object.entries(data.rating_distribution).forEach(([rating, count]) => {
        const index = parseInt(rating) - 1;
        if (index >= 0 && index < 5) ratingData[index] = count;
    });
    this.charts.rating.data.datasets[0].data = ratingData;
    this.charts.rating.update();

    // 3. Update Emotion Wheel
    if (data.emotion_distribution) {
        const emotions = ['joy', 'trust', 'fear', 'surprise', 'sadness', 'anger'];
        const emotionData = emotions.map(emotion => data.emotion_distribution[emotion] || 0);
        this.charts.emotionWheel.data.datasets[0].data = emotionData;
        this.charts.emotionWheel.update();
    }

    // 4. Update Priority Action Matrix
    if (data.priority_matrix) {
        this.charts.priorityMatrix.data.datasets.forEach(dataset => dataset.data = []);
        
        data.priority_matrix.forEach(issue => {
            let datasetIndex;
            const priorityScore = (issue.impact + issue.frequency + issue.urgency) / 3;
            
            if (priorityScore >= 8) datasetIndex = 0;
            else if (priorityScore >= 6) datasetIndex = 1;
            else if (priorityScore >= 4) datasetIndex = 2;
            else datasetIndex = 3;
            
            this.charts.priorityMatrix.data.datasets[datasetIndex].data.push({
                x: issue.impact,
                y: issue.frequency,
                r: issue.urgency * 2,
                label: issue.name
            });
        });
        this.charts.priorityMatrix.update();
    }

    // 5. Update Historical Trend
    if (data.historical_trend) {
        this.charts.historicalTrend.data.labels = data.historical_trend.labels;
        this.charts.historicalTrend.data.datasets[0].data = data.historical_trend.current;
        this.charts.historicalTrend.data.datasets[1].data = data.historical_trend.previous;
        this.charts.historicalTrend.update();
    }

    // 6. Update Live Sentiment Meter
if (data.sentiment_meter) {
    const positivePercent = data.sentiment_meter.positive;
    document.getElementById('meterValue').textContent = `${positivePercent}%`;
    
    // Update color based on sentiment
    const meterValue = document.getElementById('meterValue');
    if (positivePercent >= 70) {
        meterValue.style.color = '#10b981';
    } else if (positivePercent >= 50) {
        meterValue.style.color = '#f59e0b';
    } else {
        meterValue.style.color = '#ef4444';
    }
}

    // 7. Update Topic-Sentiment Correlation
    if (data.topic_sentiment) {
        this.charts.topicSentiment.data.labels = data.topic_sentiment.topics;
        this.charts.topicSentiment.data.datasets[0].data = data.topic_sentiment.positive;
        this.charts.topicSentiment.data.datasets[1].data = data.topic_sentiment.negative;
        this.charts.topicSentiment.update();
    }

    // 8. Update Sentiment Intensity Gauge
    if (data.sentiment_intensity) {
        this.charts.intensityGauge.data.datasets[0].data = [
            data.sentiment_intensity.strong_positive,
            data.sentiment_intensity.weak_positive,
            data.sentiment_intensity.neutral,
            data.sentiment_intensity.weak_negative,
            data.sentiment_intensity.strong_negative
        ];
        this.charts.intensityGauge.update();
    }
}

async loadDashboardData() {
    try {
        const endpoints = [
            'http://localhost:5000/api/analytics',
            'http://localhost:5000/api/feedback/stats',
            'http://localhost:5000/api/analytics/emotion-distribution',
            'http://localhost:5000/api/analytics/priority-matrix',
            'http://localhost:5000/api/analytics/historical-trend',
            'http://localhost:5000/api/analytics/sentiment-meter',
            'http://localhost:5000/api/analytics/topic-sentiment',
            'http://localhost:5000/api/analytics/sentiment-intensity'
        ];

        const responses = await Promise.all(endpoints.map(url => fetch(url)));
        const data = await Promise.all(responses.map(response => response.json()));

        const combinedData = {
            ...data[0], // analytics
            ...data[1], // stats
            emotion_distribution: data[2],
            priority_matrix: data[3],
            historical_trend: data[4],
            sentiment_meter: data[5],
            topic_sentiment: data[6],
            sentiment_intensity: data[7]
        };

        this.updateCharts(combinedData);
        this.updateStats(data[1]);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        this.showError('Failed to load analytics data: ' + error.message);
    }
}


// Helper function for heatmap
getWeekNumber(date) {
    const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
    const pastDaysOfYear = (date - firstDayOfYear) / 86400000;
    return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
}

    updateStats(data) {
    console.log('Updating stats with:', data);
    
    document.getElementById('totalFeedbacks').textContent = data.total_feedbacks?.toLocaleString() || '0';
    document.getElementById('averageRating').textContent = data.average_rating?.toFixed(1) || '0.0';
    
    const positiveRate = data.sentiment_percentages?.positive || 0;
    document.getElementById('positiveRate').textContent = positiveRate.toFixed(1) + '%';
    
    // Update AI accuracy based on data quality
    const total = data.total_feedbacks || 0;
    const accuracy = total > 10 ? 'High' : total > 0 ? 'Medium' : 'N/A';
    document.getElementById('aiAccuracy').textContent = accuracy;
}

    async loadRecentFeedbacks() {
        try {
            const response = await fetch('http://localhost:5000/api/feedback?per_page=10');
            
            if (!response.ok) {
                throw new Error('Failed to fetch recent feedbacks');
            }

            const data = await response.json();
            this.displayFeedbacks(data.feedbacks);
            
        } catch (error) {
            console.error('Error loading feedbacks:', error);
            this.showError('Failed to load recent feedbacks');
        }
    }

    displayFeedbacks(feedbacks) {
        const container = document.getElementById('feedbackTable');
        
        if (!feedbacks || feedbacks.length === 0) {
            container.innerHTML = `
                <div class="no-data">
                    <div class="no-data-icon">📝</div>
                    <h3>No Feedbacks Yet</h3>
                    <p>No feedback has been submitted yet. Be the first to share your thoughts!</p>
                </div>
            `;
            return;
        }

        const feedbacksHTML = feedbacks.map(feedback => `
            <div class="feedback-item ${feedback.sentiment}" data-feedback-id="${feedback.id}">
                <div class="feedback-header">
                    <div class="feedback-meta">
                        <span class="feedback-name">${this.escapeHtml(feedback.name || 'Anonymous')}</span>
                        <span class="feedback-rating">${'★'.repeat(feedback.rating)}${'☆'.repeat(5 - feedback.rating)}</span>
                        <span class="feedback-sentiment ${feedback.sentiment}">${feedback.sentiment}</span>
                    </div>
                    <div class="feedback-actions">
                        <button onclick="openDeleteModal(${feedback.id})" class="delete-btn">Delete</button>
                    </div>
                </div>
                <div class="feedback-category">Category: ${this.escapeHtml(feedback.category)}</div>
                <div class="feedback-message">${this.escapeHtml(feedback.message)}</div>
                <div class="feedback-footer">
                    <div>
                        <span class="feedback-date">${new Date(feedback.created_at).toLocaleDateString()}</span>
                        <span class="feedback-method">${feedback.analysis_method}</span>
                    </div>
                    <div class="feedback-stats">
                        Polarity: ${feedback.polarity} • Subjectivity: ${feedback.subjectivity}
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = feedbacksHTML;
    }

    async loadWordCloud() {
        const loadingElement = document.getElementById('wordcloudLoading');
        const imageElement = document.getElementById('wordcloudImage');
        const topWordsElement = document.getElementById('topWords');
        
        try {
            loadingElement.style.display = 'block';
            imageElement.style.display = 'none';
            topWordsElement.innerHTML = '';

            const response = await fetch('http://localhost:5000/api/wordcloud');
            
            if (!response.ok) {
                throw new Error('Failed to generate wordcloud');
            }

            const data = await response.json();
            
            if (data.wordcloud) {
                imageElement.src = data.wordcloud;
                imageElement.style.display = 'block';
                loadingElement.style.display = 'none';
                
                // Display top words
                if (data.top_words && data.top_words.length > 0) {
                    const topWordsHTML = data.top_words.map(word => `
                        <div class="word-item">
                            <span class="word">${this.escapeHtml(word.word)}</span>
                            <span class="count">${word.count}</span>
                        </div>
                    `).join('');
                    
                    topWordsElement.innerHTML = topWordsHTML;
                }
            } else {
                throw new Error('No wordcloud data received');
            }
            
        } catch (error) {
            console.error('Error loading wordcloud:', error);
            loadingElement.innerHTML = `
                <div style="color: #ef4444;">
                    <p>❌ Failed to generate wordcloud</p>
                    <p style="font-size: 0.9rem; margin-top: 8px;">${error.message}</p>
                </div>
            `;
        }
    }

    startAutoRefresh() {
        // Refresh data every 30 seconds
        this.autoRefreshInterval = setInterval(() => {
            this.loadDashboardData();
            this.loadRecentFeedbacks();
            this.updateLastUpdated();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    updateLastUpdated() {
        const now = new Date();
        document.getElementById('lastUpdated').textContent = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    showError(message) {
        // You could implement a toast notification system here
        console.error('Dashboard Error:', message);
        
        // Simple alert for now
        const existingError = document.querySelector('.error-toast');
        if (existingError) {
            existingError.remove();
        }
        
        const errorToast = document.createElement('div');
        errorToast.className = 'error-toast';
        errorToast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1001;
            max-width: 300px;
        `;
        errorToast.textContent = message;
        
        document.body.appendChild(errorToast);
        
        setTimeout(() => {
            errorToast.remove();
        }, 5000);
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Global functions for HTML event handlers
function refreshDashboard() {
    if (window.dashboard) {
        console.log('Manual refresh triggered');
        
        const refreshBtn = document.querySelector('.btn-refresh');
        const originalHtml = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<span class="loading-spinner"></span> Refreshing...';
        refreshBtn.disabled = true;
        
        // Reload all data
        Promise.all([
            window.dashboard.loadDashboardData(),
            window.dashboard.loadRecentFeedbacks(),
            window.dashboard.loadWordCloud()
        ]).then(() => {
            window.dashboard.updateLastUpdated();
            refreshBtn.innerHTML = originalHtml;
            refreshBtn.disabled = false;
            console.log('Refresh completed');
        }).catch(error => {
            console.error('Refresh failed:', error);
            refreshBtn.innerHTML = originalHtml;
            refreshBtn.disabled = false;
        });
    }
}

function openDeleteModal(feedbackId) {
    window.dashboard.pendingDeleteId = feedbackId;
    document.getElementById('deleteModal').style.display = 'flex';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    window.dashboard.pendingDeleteId = null;
}

async function confirmDelete() {
    const feedbackId = window.dashboard.pendingDeleteId;
    
    if (!feedbackId) return;
    
    try {
        const response = await fetch(`http://localhost:5000/api/feedback/${feedbackId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            // Remove the feedback item from UI
            const feedbackElement = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
            if (feedbackElement) {
                feedbackElement.style.opacity = '0.5';
                setTimeout(() => {
                    feedbackElement.remove();
                    
                    // Reload data to update charts
                    window.dashboard.loadDashboardData();
                    window.dashboard.loadWordCloud();
                }, 300);
            }
            
            closeDeleteModal();
        } else {
            throw new Error('Failed to delete feedback');
        }
    } catch (error) {
        console.error('Error deleting feedback:', error);
        alert('Error deleting feedback: ' + error.message);
    }
}

function exportData() {
    // Simple export functionality - in a real app, this would generate a CSV or PDF
    alert('Export functionality would be implemented here. This could generate a CSV report or PDF summary.');
}
async function exportData() {
    try {
        console.log('Exporting data...');
        
        // Show export options
        const format = prompt('Choose export format:\n1. CSV (Excel)\n2. PDF Report\n3. JSON Data\n\nEnter 1, 2, or 3:');
        
        if (!format) return;
        
        let endpoint, filename, method = 'GET';
        
        switch(format) {
            case '1':
                endpoint = '/api/export/csv';
                filename = 'feedback_data.csv';
                break;
            case '2':
                endpoint = '/api/export/pdf';
                filename = 'feedback_report.pdf';
                break;
            case '3':
                endpoint = '/api/export/json';
                filename = 'feedback_data.json';
                break;
            default:
                alert('Invalid choice. Please enter 1, 2, or 3.');
                return;
        }
        
        // Show loading
        const exportBtn = document.querySelector('.btn-secondary');
        const originalText = exportBtn.innerHTML;
        exportBtn.innerHTML = '<span class="loading-spinner"></span> Generating...';
        exportBtn.disabled = true;
        
        // Fetch export data
        const response = await fetch(`http://localhost:5000${endpoint}`);
        
        if (!response.ok) {
            throw new Error(`Export failed: ${response.status}`);
        }
        
        // Handle different response types
        if (format === '2') {
            // PDF - download blob
            const blob = await response.blob();
            downloadFile(blob, filename, 'application/pdf');
        } else {
            // CSV or JSON - download text
            const data = await response.text();
            const mimeType = format === '1' ? 'text/csv' : 'application/json';
            downloadFile(data, filename, mimeType);
        }
        
        alert(`✅ ${filename} downloaded successfully!`);
        
    } catch (error) {
        console.error('Export error:', error);
        alert(`❌ Export failed: ${error.message}`);
    } finally {
        // Restore button
        const exportBtn = document.querySelector('.btn-secondary');
        exportBtn.innerHTML = originalText;
        exportBtn.disabled = false;
    }
}

function downloadFile(data, filename, mimeType) {
    const blob = data instanceof Blob ? data : new Blob([data], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}
// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new EnhancedDashboard();
    
    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        if (window.dashboard) {
            window.dashboard.stopAutoRefresh();
        }
    });
});