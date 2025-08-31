// Global variables
let currentUser = null;

// Show login form
function showLoginForm() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('auth-overlay').style.display = 'flex';
}

// Show signup form
function showSignupForm() {
    document.getElementById('signup-form').style.display = 'block';
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('auth-overlay').style.display = 'flex';
}

// Close authentication forms
function closeAuthForms() {
    document.getElementById('auth-overlay').style.display = 'none';
}

// Switch between login and signup
function switchToSignup() {
    showSignupForm();
}

function switchToLogin() {
    showLoginForm();
}

// Handle login form submission
function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    if (!email || !password) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    loginUser(email, password);
}

// Handle signup form submission
function handleSignup(event) {
    event.preventDefault();
    
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm-password').value;
    
    if (!name || !email || !password || !confirmPassword) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showNotification('Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 6) {
        showNotification('Password must be at least 6 characters long', 'error');
        return;
    }
    
    signupUser(name, email, password);
}

// Login user
async function loginUser(email, password) {
    showNotification('Logging in...', 'info');
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        if (data.status === 'ok' && data.user) {
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            updateUIForLoggedInUser(data.user);
            closeAuthForms();
            showNotification('Login successful!', 'success');
        } else {
            showNotification(data.message || 'Invalid credentials', 'error');
        }
    } catch (err) {
        showNotification('Login failed. Please try again.', 'error');
    }
}

// Signup user
async function signupUser(name, email, password) {
    showNotification('Creating account...', 'info');
    let avatarUrl = 'https://images.unsplash.com/photo-1677442136019-21780ecad995?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=100&q=80';
    const profilePictureInput = document.getElementById('profile-picture');
    if (profilePictureInput && profilePictureInput.files && profilePictureInput.files[0]) {
        avatarUrl = profilePictureInput.files[0];
    }
    try {
        const response = await fetch('/api/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password, avatar: avatarUrl })
        });
        const data = await response.json();
        if (data.status === 'ok' && data.user) {
            showNotification(data.message || 'Verification email sent. Please check your inbox.', 'success');
            closeAuthForms();
        } else {
            showNotification(data.message || 'Signup failed', 'error');
        }
    } catch (err) {
        showNotification('Signup failed. Please try again.', 'error');
    }
}

// Complete signup process
function completeSignup(name, email, avatarUrl) {
    // Create user object
    const user = {
        name: name,
        email: email,
        avatar: avatarUrl
    };
    
    // Store user data
    currentUser = user;
    localStorage.setItem('currentUser', JSON.stringify(user));
    
    // Update UI
    updateUIForLoggedInUser(user);
    closeAuthForms();
    
    // Reset form
    document.getElementById('signup-form').reset();
    document.getElementById('profile-preview-img').src = 'https://images.unsplash.com/photo-1677442136019-21780ecad995?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=100&q=80';
    
    showNotification('Account created successfully!', 'success');
}

// Preview profile picture
function previewProfilePicture(event) {
    const file = event.target.files[0];
    if (file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showNotification('Please select an image file', 'error');
            return;
        }
        
        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showNotification('Image size should be less than 5MB', 'error');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('profile-preview-img').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

// Logout user
function logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    updateUIForGuestUser();
    showNotification('Logged out successfully', 'info');
}

// Check authentication status on page load
function checkAuthStatus() {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        updateUIForLoggedInUser(currentUser);
    } else {
        updateUIForGuestUser();
    }
}

// Update UI for logged in user
function updateUIForLoggedInUser(user) {
    document.getElementById('guest-interface').style.display = 'none';
    document.getElementById('user-interface').style.display = 'flex';
    
    document.getElementById('user-name').textContent = user.name;
    document.getElementById('user-avatar').src = user.avatar;
}

// Update UI for guest user
function updateUIForGuestUser() {
    document.getElementById('guest-interface').style.display = 'flex';
    document.getElementById('user-interface').style.display = 'none';
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add account removal functionality
async function removeAccount() {
    if (!currentUser || !currentUser.email) {
        alert('No user logged in.');
        return;
    }
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        return;
    }
    try {
        const response = await fetch('/api/remove_account', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: currentUser.email })
        });
        const data = await response.json();
        if (data.status === 'ok') {
            alert('Account removed successfully.');
            logout();
            closeProfileModal();
        } else {
            alert(data.message || 'Account removal failed');
        }
    } catch (err) {
        alert('Account removal failed. Please try again.');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    
    // Close auth modal when clicking outside
    document.getElementById('auth-overlay').addEventListener('click', function(e) {
        if (e.target === this) {
            closeAuthForms();
        }
    });
    
    // Close auth modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAuthForms();
        }
    });
});
