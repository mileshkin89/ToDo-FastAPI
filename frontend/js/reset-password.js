// Getting the token from the URL parameters
function getTokenFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('token');
}

// Validating passwords on the client
function validatePasswords() {
    const newPassword = document.getElementById('newPassword').value;
    const repeatPassword = document.getElementById('repeatPassword').value;
    const newPasswordError = document.getElementById('newPasswordError');
    const repeatPasswordError = document.getElementById('repeatPasswordError');
    
    let isValid = true;
    
    // Clearing previous errors
    newPasswordError.textContent = '';
    repeatPasswordError.textContent = '';
    
    // Minimum Length Check
    if (newPassword.length < 5) {
        newPasswordError.textContent = 'The password must contain at least 5 characters';
        isValid = false;
    }
    
    // Checking password matches
    if (newPassword !== repeatPassword) {
        repeatPasswordError.textContent = 'The passwords don\'t match';
        isValid = false;
    }
    
    return isValid;
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    const successDiv = document.getElementById('successMessage');
    successDiv.style.display = 'none';
}

// Show success message
function showSuccess(message) {
    const successDiv = document.getElementById('successMessage');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.style.display = 'none';
}

// Hide all messages
function hideMessages() {
    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('successMessage').style.display = 'none';
}

// Setting the boot state
function setLoading(isLoading) {
    const submitButton = document.getElementById('submitButton');
    const buttonText = submitButton.querySelector('.button-text');
    const buttonLoader = submitButton.querySelector('.button-loader');
    
    if (isLoading) {
        submitButton.disabled = true;
        buttonText.style.display = 'none';
        buttonLoader.style.display = 'flex';
    } else {
        submitButton.disabled = false;
        buttonText.style.display = 'inline';
        buttonLoader.style.display = 'none';
    }
}

// Submitting a form
async function handleSubmit(event) {
    event.preventDefault();
    
    hideMessages();
    
    if (!validatePasswords()) {
        return;
    }
    
    const token = getTokenFromURL();
    if (!token) {
        showError('The password reset token was not found in the URL. Please use the link in the email.');
        return;
    }
    
    const newPassword = document.getElementById('newPassword').value;
    const repeatPassword = document.getElementById('repeatPassword').value;
    
    setLoading(true);
    
    try {
        // Get the base API URL from the current host
        const apiBaseUrl = window.location.origin;
        const response = await fetch(`${apiBaseUrl}/api/v1/auth/reset_password/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                token: token,
                new_password: newPassword,
                repeat_new_password: repeatPassword
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            // Handling validation errors
            if (response.status === 422) {
                const errors = data.detail || [];
                if (Array.isArray(errors)) {
                    const errorMessages = errors.map(err => {
                        const field = err.loc ? err.loc.join('.') : '';
                        return `${field}: ${err.msg}`;
                    }).join('\n');
                    showError(errorMessages || 'Data validation error');
                } else {
                    showError(data.detail || 'Data validation error');
                }
            } else {
                showError(data.detail || 'Password reset error');
            }
            setLoading(false);
            return;
        }
        
        showSuccess(data.message || 'Password changed successfully!');
        
        document.getElementById('resetPasswordForm').reset();
        
        setTimeout(() => {
            window.location.href = '/';
        }, 3000);
        
    } catch (error) {
        console.error('Error sending request:', error);
        showError('Failed to connect to the server. Please check your internet connection.');
        setLoading(false);
    }
}

// Initialization on page load
document.addEventListener('DOMContentLoaded', function() {
    const token = getTokenFromURL();
    
    if (!token) {
        showError('The password reset token was not found in the URL. Please use the link in the email.');
        document.getElementById('resetPasswordForm').style.display = 'none';
        return;
    }
    
    // Setting the token in a hidden field
    document.getElementById('resetToken').value = token;
    
    // Form submission handler
    document.getElementById('resetPasswordForm').addEventListener('submit', handleSubmit);
    
    // Real-time validation
    document.getElementById('repeatPassword').addEventListener('blur', validatePasswords);
    document.getElementById('newPassword').addEventListener('input', function() {
        const repeatPassword = document.getElementById('repeatPassword').value;
        if (repeatPassword) {
            validatePasswords();
        }
    });
});
