class AuthManager {
    constructor() {
        this.token = localStorage.getItem('authToken');
        this.user = JSON.parse(localStorage.getItem('userData') || 'null');
        console.log('AuthManager initialized', { 
            hasToken: !!this.token, 
            hasUser: !!this.user,
            user: this.user 
        });
        this.init();
    }

    init() {
        console.log('Updating UI with auth state:', this.isLoggedIn() ? 'Logged in' : 'Guest');
        this.updateUI();
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.id === 'logoutBtn' || e.target.closest('#logoutBtn')) {
                this.logout();
            }
        });
    }

    async login(email, password) {
        try {
            console.log('Attempting login for:', email);
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email, password })
            });
            const data = await response.json();
            
            if (response.ok) {
                console.log('Login successful:', data.user);
                this.token = data.token;
                this.user = data.user;
                localStorage.setItem('authToken', this.token);
                localStorage.setItem('userData', JSON.stringify(this.user));
                this.updateUI();
                return { success: true, user: this.user };
            } else {
                console.error('Login failed:', data.error);
                throw new Error(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: error.message };
        }
    }

    async register(email, password) {
        try {
            console.log('Attempting registration for:', email);
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email, password })
            });
            const data = await response.json();
            
            if (response.ok) {
                console.log('Registration successful:', data.user);
                this.token = data.token;
                this.user = data.user;
                localStorage.setItem('authToken', this.token);
                localStorage.setItem('userData', JSON.stringify(this.user));
                this.updateUI();
                return { success: true, user: this.user };
            } else {
                console.error('Registration failed:', data.error);
                throw new Error(data.error || 'Registration failed');
            }
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, error: error.message };
        }
    }

    logout() {
        console.log('Logging out user');
        this.token = null;
        this.user = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        this.updateUI();
        window.location.href = 'index.html';
    }

    isLoggedIn() { 
        return !!this.token && !!this.user;
    }
    
    isAdmin() { 
        return this.isLoggedIn() && this.user.role === 'admin';
    }

    getAuthHeaders() {
        const headers = {'Content-Type': 'application/json'};
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    updateUI() {
        console.log('=== UPDATING UI ===');
        const isLoggedIn = this.isLoggedIn();
        const isAdmin = this.isAdmin();
        
        console.log('Auth State:', { isLoggedIn, isAdmin, user: this.user });

        // Update body classes for CSS-based visibility
        document.body.classList.remove('guest', 'authenticated', 'admin');
        
        if (isLoggedIn) {
            document.body.classList.add('authenticated');
            if (isAdmin) {
                document.body.classList.add('admin');
            }
        } else {
            document.body.classList.add('guest');
        }

        // Update user info
        const userEmail = document.getElementById('userEmail');
        const userRole = document.getElementById('userRole');
        
        if (userEmail) {
            userEmail.textContent = this.user ? this.user.email : 'User';
        }
        if (userRole) {
            userRole.textContent = this.user ? this.user.role : 'Role';
        }

        console.log('Body classes:', document.body.className);
        console.log('=== UI UPDATE COMPLETE ===');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing AuthManager...');
    window.authManager = new AuthManager();
});