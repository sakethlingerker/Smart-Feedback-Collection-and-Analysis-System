class EnhancedDashboard {
    constructor() {
        if (window.dashboardInstance) {
            console.log('Dashboard instance already exists, returning existing instance');
            return window.dashboardInstance;
        }
        
        this.charts = {};
        this.initialized = false;
        this.pendingDeleteId = null;
        this.autoRefreshInterval = null;
        window.dashboardInstance = this;
        this.init();
    }

    async init() {
        if (this.initialized) {
            console.log('Dashboard already initialized');
            return;
        }

        console.log('Dashboard: Starting initialization...');
        
        // Wait for auth manager
        if (!window.authManager) {
            setTimeout(() => this.init(), 100);
            return;
        }

        // Check authentication
        if (!await this.checkAuth()) {
            return;
        }

        try {
            await this.initializeCharts();
            await this.loadDashboardData();
            await this.loadRecentFeedbacks();
            await this.loadWordCloud();
            
            this.startAutoRefresh();
            this.updateLastUpdated();
            this.initialized = true;
            
            console.log('Dashboard: Initialization completed successfully');
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.showError('Failed to initialize dashboard');
        }
    }

    async checkAuth() {
        console.log("Dashboard: Checking authentication...");

        if (!window.authManager.isLoggedIn()) {
            console.log("Dashboard: User not logged in");
            this.showAccessDenied("Please login to access the dashboard");
            setTimeout(() => {
                window.location.href = "login.html";
            }, 3000);
            return false;
        }

        if (!window.authManager.isAdmin()) {
            console.log("Dashboard: User is not admin");
            this.showAccessDenied("Admin access required for dashboard");
            setTimeout(() => {
                window.location.href = "index.html";
            }, 3000);
            return false;
        }

        console.log("Dashboard: Authentication successful - user is admin");
        return true;
    }

    showAccessDenied(message) {
        console.log("Dashboard: Showing access denied -", message);
        document.body.innerHTML = `
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: 'Inter', sans-serif;
                color: white;
            ">
                <div style="text-align: center; padding: 40px; background: rgba(255,255,255,0.1); border-radius: 12px; backdrop-filter: blur(10px);">
                    <h2 style="font-size: 2rem; margin-bottom: 20px;">🔒 Access Denied</h2>
                    <p style="font-size: 1.2rem; margin-bottom: 30px;">${message}</p>
                    <a href="login.html" style="
                        background: white; 
                        color: #667eea; 
                        padding: 12px 24px; 
                        border-radius: 8px; 
                        text-decoration: none;
                        font-weight: 600;
                        display: inline-block;
                    ">Login Here</a>
                </div>
            </div>
        `;
    }

    initializeCharts() {
        return new Promise((resolve) => {
            // Destroy existing charts first
            if (this.charts.sentiment) {
                this.charts.sentiment.destroy();
            }
            if (this.charts.rating) {
                this.charts.rating.destroy();
            }
            if (this.charts.emotionWheel) {
                this.charts.emotionWheel.destroy();
            }
            if (this.charts.priorityMatrix) {
                this.charts.priorityMatrix.destroy();
            }
            if (this.charts.historicalTrend) {
                this.charts.historicalTrend.destroy();
            }
            if (this.charts.sentimentMeter) {
                this.charts.sentimentMeter.destroy();
            }
            if (this.charts.topicSentiment) {
                this.charts.topicSentiment.destroy();
            }
            if (this.charts.intensityGauge) {
                this.charts.intensityGauge.destroy();
            }

            // Reset charts object
            this.charts = {};

            console.log('Initializing charts...');

            // 1. Sentiment Distribution (Doughnut)
            const sentimentCtx = document.getElementById('sentimentChart');
            if (sentimentCtx) {
                this.charts.sentiment = new Chart(sentimentCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Positive', 'Negative', 'Neutral'],
                        datasets: [{
                            data: [0, 0, 0],
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
                });
            }

            // 2. Rating Distribution (Bar)
            const ratingCtx = document.getElementById('ratingChart');
            if (ratingCtx) {
                this.charts.rating = new Chart(ratingCtx, {
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
                });
            }

            // 3. Emotion Wheel (Polar Area)
            const emotionCtx = document.getElementById('emotionChart');
            if (emotionCtx) {
                this.charts.emotionWheel = new Chart(emotionCtx, {
                    type: 'polarArea',
                    data: {
                        labels: ['Joy', 'Trust', 'Fear', 'Surprise', 'Sadness', 'Anger'],
                        datasets: [{
                            data: [0, 0, 0, 0, 0, 0],
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
                });
            }

            // 4. Priority Action Matrix (Bubble)
            const priorityCtx = document.getElementById('priorityChart');
            if (priorityCtx) {
                this.charts.priorityMatrix = new Chart(priorityCtx, {
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
                });
            }

            // 5. Historical Trend Comparison (Line)
            const trendCtx = document.getElementById('trendChart');
            if (trendCtx) {
                this.charts.historicalTrend = new Chart(trendCtx, {
                    type: 'line',
                    data: {
                        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                        datasets: [
                            {
                                label: 'Current Month',
                                data: [0, 0, 0, 0],
                                borderColor: '#3b82f6',
                                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                tension: 0.4,
                                fill: true
                            },
                            {
                                label: 'Previous Month',
                                data: [0, 0, 0, 0],
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
                });
            }

            // 6. Live Sentiment Meter (Doughnut as Gauge)
            const meterCtx = document.getElementById('sentimentMeter');
            if (meterCtx) {
                this.charts.sentimentMeter = new Chart(meterCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Positive', 'Neutral', 'Negative'],
                        datasets: [{
                            data: [0, 0, 0],
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
            });
        }

        // 7. Topic-Sentiment Correlation (Bar)
        const topicCtx = document.getElementById('topicChart');
        if (topicCtx) {
            this.charts.topicSentiment = new Chart(topicCtx, {
                type: 'bar',
                data: {
                    labels: ['Product', 'Support', 'Price', 'Features', 'UI/UX'],
                    datasets: [
                        {
                            label: 'Positive',
                            data: [0, 0, 0, 0, 0],
                            backgroundColor: '#10b981',
                            borderColor: '#059669',
                            borderWidth: 1
                        },
                        {
                            label: 'Negative',
                            data: [0, 0, 0, 0, 0],
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
            });
        }

        // 8. Sentiment Intensity Gauge (Doughnut)
        const intensityCtx = document.getElementById('intensityGauge');
        if (intensityCtx) {
            this.charts.intensityGauge = new Chart(intensityCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Strong Positive', 'Weak Positive', 'Neutral', 'Weak Negative', 'Strong Negative'],
                    datasets: [{
                        data: [0, 0, 0, 0, 0],
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
            });
        }

        console.log('Charts initialized successfully');
        resolve();
    });
}

    updateCharts(data) {
        if (!data) {
            console.warn("No data provided to update charts");
            return;
        }

        // 1. Update Sentiment Distribution
        if (data.sentiment_distribution) {
            this.charts.sentiment.data.datasets[0].data = [
                data.sentiment_distribution.positive || 0,
                data.sentiment_distribution.negative || 0,
                data.sentiment_distribution.neutral || 0,
            ];
            this.charts.sentiment.update();
        }

        // 2. Update Rating Distribution
        if (data.rating_distribution) {
            const ratingData = [0, 0, 0, 0, 0];
            Object.entries(data.rating_distribution).forEach(([rating, count]) => {
                const index = parseInt(rating) - 1;
                if (index >= 0 && index < 5) ratingData[index] = count;
            });
            this.charts.rating.data.datasets[0].data = ratingData;
            this.charts.rating.update();
        }

        // 3. Update Emotion Wheel
        if (data.emotion_distribution) {
            const emotions = ["joy", "trust", "fear", "surprise", "sadness", "anger"];
            const emotionData = emotions.map(
                (emotion) => data.emotion_distribution[emotion] || 0
            );
            this.charts.emotionWheel.data.datasets[0].data = emotionData;
            this.charts.emotionWheel.update();
        }

        // 4. Update Priority Action Matrix
        if (data.priority_matrix && Array.isArray(data.priority_matrix)) {
            this.charts.priorityMatrix.data.datasets.forEach(
                (dataset) => (dataset.data = [])
            );

            data.priority_matrix.forEach((issue) => {
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
                    label: issue.name,
                });
            });
            this.charts.priorityMatrix.update();
        }

        // 5. Update Historical Trend
        if (data.historical_trend) {
            this.charts.historicalTrend.data.labels = data.historical_trend.labels || ["Week 1", "Week 2", "Week 3", "Week 4"];
            this.charts.historicalTrend.data.datasets[0].data = data.historical_trend.current || [0, 0, 0, 0];
            this.charts.historicalTrend.data.datasets[1].data = data.historical_trend.previous || [0, 0, 0, 0];
            this.charts.historicalTrend.update();
        }

        // 6. Update Live Sentiment Meter
        if (data.sentiment_meter) {
            const positivePercent = data.sentiment_meter.positive || 0;
            const neutralPercent = data.sentiment_meter.neutral || 0;
            const negativePercent = data.sentiment_meter.negative || 0;

            this.charts.sentimentMeter.data.datasets[0].data = [
                positivePercent,
                neutralPercent,
                negativePercent,
            ];
            this.charts.sentimentMeter.update();

            document.getElementById("meterValue").textContent = `${positivePercent}%`;

            // Update color based on sentiment
            const meterValue = document.getElementById("meterValue");
            if (positivePercent >= 70) {
                meterValue.style.color = "#10b981";
            } else if (positivePercent >= 50) {
                meterValue.style.color = "#f59e0b";
            } else {
                meterValue.style.color = "#ef4444";
            }
        }

        // 7. Update Topic-Sentiment Correlation
        if (data.topic_sentiment) {
            this.charts.topicSentiment.data.labels = data.topic_sentiment.topics || [
                "Product",
                "Support",
                "Price",
                "Features",
                "UI/UX",
            ];
            this.charts.topicSentiment.data.datasets[0].data = data.topic_sentiment.positive || [0, 0, 0, 0, 0];
            this.charts.topicSentiment.data.datasets[1].data = data.topic_sentiment.negative || [0, 0, 0, 0, 0];
            this.charts.topicSentiment.update();
        }

        // 8. Update Sentiment Intensity Gauge
        if (data.sentiment_intensity) {
            this.charts.intensityGauge.data.datasets[0].data = [
                data.sentiment_intensity.strong_positive || 0,
                data.sentiment_intensity.weak_positive || 0,
                data.sentiment_intensity.neutral || 0,
                data.sentiment_intensity.weak_negative || 0,
                data.sentiment_intensity.strong_negative || 0,
            ];
            this.charts.intensityGauge.update();
        }
    }

    async loadDashboardData() {
        try {
            const endpoints = [
                "http://localhost:5000/api/analytics",
                "http://localhost:5000/api/feedback/stats",
                "http://localhost:5000/api/analytics/emotion-distribution",
                "http://localhost:5000/api/analytics/priority-matrix",
                "http://localhost:5000/api/analytics/historical-trend",
                "http://localhost:5000/api/analytics/sentiment-meter",
                "http://localhost:5000/api/analytics/topic-sentiment",
                "http://localhost:5000/api/analytics/sentiment-intensity",
            ];

            const responses = await Promise.all(
                endpoints.map((url) =>
                    fetch(url, {
                        headers: window.authManager.getAuthHeaders(),
                    })
                )
            );

            // Check for auth errors
            for (const response of responses) {
                if (response.status === 401 || response.status === 403) {
                    window.location.href = "login.html";
                    return;
                }
            }

            const data = await Promise.all(
                responses.map((response) => response.json())
            );

            const combinedData = {
                ...data[0], // analytics
                ...data[1], // stats
                emotion_distribution: data[2],
                priority_matrix: data[3],
                historical_trend: data[4],
                sentiment_meter: data[5],
                topic_sentiment: data[6],
                sentiment_intensity: data[7],
            };

            this.updateCharts(combinedData);
            this.updateStats(data[1]);
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.showError("Failed to load analytics data: " + error.message);
        }
    }

    updateStats(data) {
        console.log("Updating stats with:", data);

        document.getElementById("totalFeedbacks").textContent = data.total_feedbacks?.toLocaleString() || "0";
        document.getElementById("averageRating").textContent = data.average_rating?.toFixed(1) || "0.0";

        const positiveRate = data.sentiment_percentages?.positive || 0;
        document.getElementById("positiveRate").textContent = positiveRate.toFixed(1) + "%";

        // Update AI accuracy based on data quality
        const total = data.total_feedbacks || 0;
        const accuracy = total > 10 ? "High" : total > 0 ? "Medium" : "N/A";
        document.getElementById("aiAccuracy").textContent = accuracy;
    }

    async loadRecentFeedbacks() {
        try {
            const response = await fetch("api/feedback?per_page=10");

            if (!response.ok) {
                throw new Error("Failed to fetch recent feedbacks");
            }

            const data = await response.json();
            this.displayFeedbacks(data.feedbacks);
        } catch (error) {
            console.error("Error loading feedbacks:", error);
            this.showError("Failed to load recent feedbacks");
        }
    }

    displayFeedbacks(feedbacks) {
        const container = document.getElementById("feedbackTable");

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

        const feedbacksHTML = feedbacks.map((feedback) => `
            <div class="feedback-item ${feedback.sentiment}" data-feedback-id="${feedback.id}">
                <div class="feedback-header">
                    <div class="feedback-meta">
                        <span class="feedback-name">${this.escapeHtml(feedback.name || "Anonymous")}</span>
                        <span class="feedback-rating">${"★".repeat(feedback.rating)}${"☆".repeat(5 - feedback.rating)}</span>
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
        `).join("");

        container.innerHTML = feedbacksHTML;
    }

    async loadWordCloud() {
        const loadingElement = document.getElementById('wordcloudLoading');
        const imageElement = document.getElementById('wordcloudImage');
        const topWordsElement = document.getElementById('topWords');
        
        try {
            if (loadingElement) loadingElement.style.display = 'block';
            if (imageElement) imageElement.style.display = 'none';
            if (topWordsElement) topWordsElement.innerHTML = '';

            const response = await fetch('/api/wordcloud', {
                headers: window.authManager.getAuthHeaders()
            });
            
            if (response.status === 401 || response.status === 403) {
                console.warn('WordCloud: Unauthorized access');
                if (loadingElement) {
                    loadingElement.innerHTML = `
                        <div style="color: #f59e0b;">
                            <p>⚠️ WordCloud requires admin privileges</p>
                        </div>
                    `;
                }
                return;
            }

            if (!response.ok) {
                throw new Error(`Failed to generate wordcloud: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.wordcloud && imageElement) {
                imageElement.src = data.wordcloud;
                imageElement.style.display = 'block';
                if (loadingElement) loadingElement.style.display = 'none';
                
                // Display top words
                if (data.top_words && data.top_words.length > 0 && topWordsElement) {
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
            if (loadingElement) {
                loadingElement.innerHTML = `
                    <div style="color: #ef4444;">
                        <p>❌ Failed to generate wordcloud</p>
                        <p style="font-size: 0.9rem; margin-top: 8px;">${error.message}</p>
                    </div>
                `;
            }
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
        document.getElementById("lastUpdated").textContent = now.toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        });
    }

    // EXPORT FUNCTIONALITY
    async exportData() {
        try {
            console.log("Exporting data...");

            // Simple format selection
            const format = confirm("Export data as CSV? Click OK for CSV, Cancel for JSON");
            const endpoint = format ? "/api/export/csv" : "/api/export/json";
            const filename = format ? "feedback_export.csv" : "feedback_export.json";
            
            console.log(`Exporting as ${format ? 'CSV' : 'JSON'}...`);
            
            const response = await fetch(`${endpoint}`, {
                headers: window.authManager.getAuthHeaders()
            });

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Export feature is not available on the server.');
                }
                throw new Error(`Server returned ${response.status}`);
            }

            const data = await response.text();
            this.downloadFile(data, filename, format ? 'text/csv' : 'application/json');
            
            this.showToast(`✅ ${filename} downloaded successfully!`, 'success');
            
        } catch (error) {
            console.error("Export error:", error);
            this.showToast(`❌ Export failed: ${error.message}`, 'error');
        }
    }

    downloadFile(data, filename, mimeType) {
        const blob = new Blob([data], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }

    showToast(message, type = 'info') {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.export-toast');
        existingToasts.forEach(toast => toast.remove());
        
        const toast = document.createElement('div');
        toast.className = `export-toast ${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            max-width: 300px;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    openDeleteModal(feedbackId) {
        this.pendingDeleteId = feedbackId;
        document.getElementById("deleteModal").style.display = "flex";
    }

    closeDeleteModal() {
        document.getElementById("deleteModal").style.display = "none";
        this.pendingDeleteId = null;
    }

    async confirmDelete() {
        const feedbackId = this.pendingDeleteId;

        if (!feedbackId) return;

        try {
            const response = await fetch(`/api/feedback/${feedbackId}`, {
                method: "DELETE",
                headers: window.authManager.getAuthHeaders()
            });

            if (response.ok) {
                // Remove the feedback item from UI
                const feedbackElement = document.querySelector(`[data-feedback-id="${feedbackId}"]`);
                if (feedbackElement) {
                    feedbackElement.style.opacity = "0.5";
                    setTimeout(() => {
                        feedbackElement.remove();

                        // Reload data to update charts
                        this.loadDashboardData();
                        this.loadWordCloud();
                    }, 300);
                }

                this.closeDeleteModal();
            } else {
                throw new Error("Failed to delete feedback");
            }
        } catch (error) {
            console.error("Error deleting feedback:", error);
            alert("Error deleting feedback: " + error.message);
        }
    }

    showError(message) {
        console.error("Dashboard Error:", message);
        
        const existingError = document.querySelector(".error-toast");
        if (existingError) {
            existingError.remove();
        }

        const errorToast = document.createElement("div");
        errorToast.className = "error-toast";
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
        console.log("Manual refresh triggered");

        const refreshBtn = document.querySelector(".btn-refresh");
        const originalHtml = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<span class="loading-spinner"></span> Refreshing...';
        refreshBtn.disabled = true;

        // Reload all data
        Promise.all([
            window.dashboard.loadDashboardData(),
            window.dashboard.loadRecentFeedbacks(),
            window.dashboard.loadWordCloud(),
        ])
            .then(() => {
                window.dashboard.updateLastUpdated();
                refreshBtn.innerHTML = originalHtml;
                refreshBtn.disabled = false;
                console.log("Refresh completed");
            })
            .catch((error) => {
                console.error("Refresh failed:", error);
                refreshBtn.innerHTML = originalHtml;
                refreshBtn.disabled = false;
            });
    }
}

function exportData() {
    if (window.dashboard) {
        window.dashboard.exportData();
    } else {
        alert('Dashboard not initialized yet. Please wait...');
    }
}

function openDeleteModal(feedbackId) {
    if (window.dashboard) {
        window.dashboard.openDeleteModal(feedbackId);
    }
}

function closeDeleteModal() {
    if (window.dashboard) {
        window.dashboard.closeDeleteModal();
    }
}

function confirmDelete() {
    if (window.dashboard) {
        window.dashboard.confirmDelete();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    window.dashboard = new EnhancedDashboard();

    // Clean up on page unload
    window.addEventListener("beforeunload", () => {
        if (window.dashboard) {
            window.dashboard.stopAutoRefresh();
        }
    });
});