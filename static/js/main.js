class SmartFeedbackSystem {
    constructor() {
        this.currentRating = 0;
        this.isSubmitting = false;
        this.initializeEventListeners();
        this.setupRealTimeValidation();
    }

    initializeEventListeners() {
        // Star rating with enhanced touch support
        this.setupStarRating();
        
        // Form submission
        document.getElementById('feedbackForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitFeedback();
        });

        // Character count for message
        document.getElementById('message').addEventListener('input', (e) => {
            this.updateCharacterCount(e.target.value);
        });
    }

    setupStarRating() {
        const stars = document.querySelectorAll('.star');
        const ratingText = document.getElementById('ratingText');
        
        const ratingLabels = {
            0: 'Select a rating',
            1: 'Poor - Very dissatisfied',
            2: 'Fair - Needs improvement', 
            3: 'Good - Meets expectations',
            4: 'Very Good - Exceeds expectations',
            5: 'Excellent - Outstanding experience'
        };

        stars.forEach(star => {
            // Click events
            star.addEventListener('click', (e) => {
                this.setRating(parseInt(e.target.getAttribute('data-value')));
            });

            // Touch events for mobile
            star.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.setRating(parseInt(e.target.getAttribute('data-value')));
            }, { passive: false });

            // Hover effects for desktop
            star.addEventListener('mouseenter', (e) => {
                if (!this.isSubmitting) {
                    this.highlightStars(parseInt(e.target.getAttribute('data-value')));
                }
            });
        });

        // Reset hover effects when leaving rating area
        document.querySelector('.rating-stars').addEventListener('mouseleave', () => {
            if (!this.isSubmitting) {
                this.resetStarHighlight();
            }
        });

        // Update rating text based on current rating
        this.updateRatingText = (rating) => {
            ratingText.textContent = ratingLabels[rating] || ratingLabels[0];
            ratingText.style.color = rating > 0 ? '#1f2937' : '#6b7280';
        };

        // Initialize
        this.updateRatingText(0);
    }

    setRating(rating) {
        if (this.isSubmitting) return;
        
        this.currentRating = rating;
        document.getElementById('rating').value = rating;
        
        // Update star display
        document.querySelectorAll('.star').forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });

        this.updateRatingText(rating);
    }

    highlightStars(hoverRating) {
        document.querySelectorAll('.star').forEach((star, index) => {
            if (index < hoverRating) {
                star.style.color = '#ffd700';
            } else {
                star.style.color = '#e5e7eb';
            }
        });
    }

    resetStarHighlight() {
        document.querySelectorAll('.star').forEach((star, index) => {
            if (index < this.currentRating) {
                star.style.color = '#ffd700';
            } else {
                star.style.color = '#e5e7eb';
            }
        });
    }

    setupRealTimeValidation() {
        const messageInput = document.getElementById('message');
        
        messageInput.addEventListener('input', (e) => {
            this.validateMessage(e.target.value);
        });

        messageInput.addEventListener('blur', (e) => {
            this.validateMessage(e.target.value, true);
        });
    }

    validateMessage(message, showErrors = false) {
        const minLength = 10;
        const maxLength = 1000;
        const messageElement = document.getElementById('message');
        let isValid = true;
        
        if (message.length > 0 && message.length < minLength) {
            if (showErrors) {
                this.showFieldError('message', `Message must be at least ${minLength} characters`);
            }
            messageElement.style.borderColor = '#ef4444';
            isValid = false;
        } else if (message.length > maxLength) {
            if (showErrors) {
                this.showFieldError('message', `Message must not exceed ${maxLength} characters`);
            }
            messageElement.style.borderColor = '#ef4444';
            isValid = false;
        } else {
            this.clearFieldError('message');
            messageElement.style.borderColor = '#e5e7eb';
        }
        
        return isValid;
    }

    updateCharacterCount(message) {
        const charCount = document.getElementById('charCount');
        const maxLength = 1000;
        
        charCount.textContent = message.length;
        
        if (message.length > maxLength * 0.9) {
            charCount.style.color = '#ef4444';
        } else if (message.length > maxLength * 0.75) {
            charCount.style.color = '#f59e0b';
        } else {
            charCount.style.color = '#6b7280';
        }
    }

    showFieldError(fieldName, message) {
        let errorElement = document.getElementById(`${fieldName}Error`);
        
        if (!errorElement) {
            const field = document.getElementById(fieldName);
            errorElement = document.createElement('div');
            errorElement.id = `${fieldName}Error`;
            errorElement.className = 'field-error';
            errorElement.style.cssText = `
                color: #ef4444;
                font-size: 12px;
                margin-top: 4px;
                display: flex;
                align-items: center;
                gap: 4px;
            `;
            errorElement.innerHTML = `⚠️ ${message}`;
            field.parentNode.appendChild(errorElement);
        } else {
            errorElement.innerHTML = `⚠️ ${message}`;
        }
    }

    clearFieldError(fieldName) {
        const errorElement = document.getElementById(`${fieldName}Error`);
        if (errorElement) {
            errorElement.remove();
        }
    }

    validateForm(formData) {
        const rating = formData.get('rating');
        const message = formData.get('message');
        const category = formData.get('category');
        let isValid = true;

        // Validate rating
        if (!rating || rating === '0') {
            this.showMessage('Please provide a rating', 'error');
            isValid = false;
        }

        // Validate message
        if (!message.trim()) {
            this.showMessage('Please provide feedback message', 'error');
            isValid = false;
        } else if (message.trim().length < 10) {
            this.showMessage('Feedback message should be at least 10 characters long', 'error');
            isValid = false;
        } else if (message.trim().length > 1000) {
            this.showMessage('Feedback message should not exceed 1000 characters', 'error');
            isValid = false;
        }

        // Validate category
        if (!category) {
            this.showMessage('Please select a category', 'error');
            isValid = false;
        }

        return isValid;
    }

    async submitFeedback() {
        if (this.isSubmitting) return;
        
        const form = document.getElementById('feedbackForm');
        const formData = new FormData(form);
        const submitBtn = document.getElementById('submitBtn');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoading = submitBtn.querySelector('.btn-loading');
        
        if (!this.validateForm(formData)) {
            return;
        }

        this.isSubmitting = true;
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'flex';

        const feedbackData = {
            name: formData.get('name') || undefined,
            email: formData.get('email') || undefined,
            category: formData.get('category'),
            rating: parseInt(formData.get('rating')),
            message: formData.get('message').trim(),
            timestamp: new Date().toISOString()
        };

        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(feedbackData)
            });

            const result = await response.json();

            if (response.ok) {
                const sentimentBadge = `<span class="sentiment-badge ${result.sentiment}">${result.sentiment}</span>`;
                this.showMessage(
                    `Feedback submitted successfully! Sentiment: ${result.sentiment} (Polarity: ${result.polarity})`, 
                    'success'
                );
                
                // Reset form
                form.reset();
                this.currentRating = 0;
                this.resetStarHighlight();
                this.updateRatingText(0);
                this.updateCharacterCount('');
                
                // Show analysis method info
                setTimeout(() => {
                    this.showMessage(
                        ` Analysis performed using: ${result.analysis_method}`, 
                        'info'
                    );
                }, 3000);

            } else {
                throw new Error(result.error || 'Failed to submit feedback');
            }
        } catch (error) {
            console.error('Submission error:', error);
            this.showMessage(`Error: ${error.message}`, 'error');
        } finally {
            this.isSubmitting = false;
            submitBtn.disabled = false;
            btnText.style.display = 'flex';
            btnLoading.style.display = 'none';
        }
    }

    showMessage(message, type) {
        const messageDiv = document.getElementById('responseMessage');
        messageDiv.innerHTML = message;
        messageDiv.className = `response-message ${type}`;
        messageDiv.style.display = 'block';

        // Auto-hide after appropriate time
        const hideTime = type === 'success' ? 8000 : 
                        type === 'info' ? 5000 : 6000;
        
        setTimeout(() => {
            if (messageDiv.style.display === 'block') {
                messageDiv.style.display = 'none';
            }
        }, hideTime);
    }
    getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (window.authManager && window.authManager.token) {
        headers['Authorization'] = `Bearer ${window.authManager.token}`;
    }
    
    return headers;
}

// Modify the existing submitFeedback method
async submitFeedback() {
    if (this.isSubmitting) return;
    
    const form = document.getElementById('feedbackForm');
    const formData = new FormData(form);
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    
    if (!this.validateForm(formData)) {
        return;
    }

    this.isSubmitting = true;
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'flex';

    const feedbackData = {
        name: formData.get('name') || undefined,
        email: formData.get('email') || undefined,
        category: formData.get('category'),
        rating: parseInt(formData.get('rating')),
        message: formData.get('message').trim(),
        timestamp: new Date().toISOString()
    };

    try {
        // Use enhanced headers that include auth token if available
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: this.getAuthHeaders(), // Updated line
            body: JSON.stringify(feedbackData)
        });

        const result = await response.json();

        if (response.ok) {
            let successMessage = `Feedback submitted successfully! Sentiment: ${result.sentiment} (Polarity: ${result.polarity})`;
            
            // Add user context to message
            if (window.authManager && window.authManager.isLoggedIn()) {
                successMessage += ' - Saved to your account';
            } else {
                successMessage += ' - Submitted anonymously';
            }
            
            this.showMessage(successMessage, 'success');
            
            // Reset form
            form.reset();
            this.currentRating = 0;
            this.resetStarHighlight();
            this.updateRatingText(0);
            this.updateCharacterCount('');
            
            // Show analysis method info
            setTimeout(() => {
                this.showMessage(
                    `Analysis performed using: ${result.analysis_method}`, 
                    'info'
                );
            }, 3000);

        } else {
            throw new Error(result.error || 'Failed to submit feedback');
        }
    } catch (error) {
        console.error('Submission error:', error);
        this.showMessage(`Error: ${error.message}`, 'error');
    } finally {
        this.isSubmitting = false;
        submitBtn.disabled = false;
        btnText.style.display = 'flex';
        btnLoading.style.display = 'none';
    }
}

// Add this method to update UI based on auth state
updateAuthUI() {
    if (window.authManager) {
        window.authManager.updateUI();
    }
}
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add touch device class for specific styling
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        document.body.classList.add('touch-device');
    }

    // Initialize feedback system
    window.feedbackSystem = new SmartFeedbackSystem();
    
    // Add loading state to page
    document.body.classList.add('loaded');
});