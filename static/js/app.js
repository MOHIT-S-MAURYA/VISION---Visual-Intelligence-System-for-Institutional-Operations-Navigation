// Global JavaScript for AI Attendance System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.classList.remove('show');
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 150);
            }
        }, 5000);
    });
});

// Utility Functions
const AppUtils = {
    // Show loading overlay
    showLoading: function() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'loadingOverlay';
        overlay.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="mt-2">
                    <strong>Processing...</strong>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    },
    
    // Hide loading overlay
    hideLoading: function() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.remove();
        }
    },
    
    // Show notification
    showNotification: function(type, title, message, container = 'body') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show slide-up`;
        notification.innerHTML = `
            <strong>${title}</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        if (container === 'body') {
            // Create notification container if it doesn't exist
            let notificationContainer = document.getElementById('notificationContainer');
            if (!notificationContainer) {
                notificationContainer = document.createElement('div');
                notificationContainer.id = 'notificationContainer';
                notificationContainer.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 1050;
                    max-width: 350px;
                `;
                document.body.appendChild(notificationContainer);
            }
            notificationContainer.appendChild(notification);
        } else {
            const targetContainer = document.querySelector(container);
            if (targetContainer) {
                targetContainer.insertBefore(notification, targetContainer.firstChild);
            }
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 150);
            }
        }, 5000);
    },
    
    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },
    
    // Format time
    formatTime: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Validate file type
    isValidImageFile: function(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        return validTypes.includes(file.type);
    },
    
    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // API call wrapper
    apiCall: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }
};

// File Upload Handler
class FileUploadHandler {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.options = {
            maxFiles: 10,
            maxFileSize: 10 * 1024 * 1024, // 10MB
            allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'],
            previewContainer: null,
            ...options
        };
        
        this.init();
    }
    
    init() {
        // Add drag and drop functionality
        if (this.input.parentElement) {
            this.input.parentElement.classList.add('file-upload-area');
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                this.input.parentElement.addEventListener(eventName, this.preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                this.input.parentElement.addEventListener(eventName, () => {
                    this.input.parentElement.classList.add('dragover');
                }, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                this.input.parentElement.addEventListener(eventName, () => {
                    this.input.parentElement.classList.remove('dragover');
                }, false);
            });
            
            this.input.parentElement.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                this.handleFiles(files);
            }, false);
        }
        
        // Handle file input change
        this.input.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    handleFiles(files) {
        const validFiles = Array.from(files).filter(file => this.validateFile(file));
        
        if (this.options.previewContainer && validFiles.length > 0) {
            this.showPreview(validFiles);
        }
    }
    
    validateFile(file) {
        // Check file type
        if (!this.options.allowedTypes.includes(file.type)) {
            AppUtils.showNotification('danger', 'Invalid File Type', 
                `${file.name} is not a supported image format.`);
            return false;
        }
        
        // Check file size
        if (file.size > this.options.maxFileSize) {
            AppUtils.showNotification('danger', 'File Too Large', 
                `${file.name} is larger than ${AppUtils.formatFileSize(this.options.maxFileSize)}.`);
            return false;
        }
        
        return true;
    }
    
    showPreview(files) {
        const container = document.querySelector(this.options.previewContainer);
        if (!container) return;
        
        container.innerHTML = '';
        container.style.display = 'block';
        
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.createElement('div');
                preview.className = 'position-relative d-inline-block me-2 mb-2';
                preview.innerHTML = `
                    <img src="${e.target.result}" class="img-thumbnail" 
                         style="width: 100px; height: 100px; object-fit: cover;">
                    <div class="position-absolute top-0 start-100 translate-middle">
                        <span class="badge bg-secondary">${AppUtils.formatFileSize(file.size)}</span>
                    </div>
                `;
                container.appendChild(preview);
            };
            reader.readAsDataURL(file);
        });
    }
}

// Navigation Helper
class NavigationHelper {
    static setActiveNav(path = window.location.pathname) {
        // Remove active class from all nav links
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to current page
        const activeLink = document.querySelector(`.navbar-nav .nav-link[href="${path}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }
}

// Initialize navigation
NavigationHelper.setActiveNav();

// Global error handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    AppUtils.showNotification('danger', 'Error', 'An unexpected error occurred. Please try again.');
});
