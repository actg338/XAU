// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking on a link
    const navItems = document.querySelectorAll('.nav-links a');
    navItems.forEach(function(item) {
        item.addEventListener('click', function() {
            navLinks.classList.remove('active');
        });
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.style.backgroundColor = 'rgba(15, 15, 26, 0.98)';
            navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.backgroundColor = 'rgba(15, 15, 26, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });

    // Animate stats numbers
    animateStats();

    // Draw price chart
    drawPriceChart();

    // Contact form handling
    setupContactForm();
});

// Stats Animation
function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const target = entry.target;
                const endValue = parseFloat(target.getAttribute('data-target'));
                animateNumber(target, endValue);
                observer.unobserve(target);
            }
        });
    }, observerOptions);

    statNumbers.forEach(function(stat) {
        observer.observe(stat);
    });
}

function animateNumber(element, endValue) {
    const duration = 2000;
    const startValue = 0;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuad = 1 - (1 - progress) * (1 - progress);
        
        const currentValue = startValue + (endValue - startValue) * easeOutQuad;
        
        if (endValue >= 1000000) {
            element.textContent = Math.floor(currentValue).toLocaleString();
        } else if (endValue % 1 !== 0) {
            element.textContent = currentValue.toFixed(1);
        } else {
            element.textContent = Math.floor(currentValue);
        }
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

// Price Chart Drawing
function drawPriceChart() {
    const canvas = document.getElementById('priceChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    const container = canvas.parentElement;
    canvas.width = container.offsetWidth - 40;
    canvas.height = container.offsetHeight - 40;
    
    const width = canvas.width;
    const height = canvas.height;
    
    // Generate sample price data (simulating XAU/USD movement)
    const dataPoints = 50;
    const data = generatePriceData(dataPoints);
    
    // Draw chart background
    ctx.fillStyle = '#16213e';
    ctx.fillRect(0, 0, width, height);
    
    // Draw grid lines
    ctx.strokeStyle = 'rgba(212, 175, 55, 0.1)';
    ctx.lineWidth = 1;
    
    // Horizontal grid lines
    for (let i = 0; i <= 4; i++) {
        const y = (height / 4) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
    
    // Vertical grid lines
    for (let i = 0; i <= 6; i++) {
        const x = (width / 6) * i;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
    }
    
    // Calculate chart bounds
    const minPrice = Math.min(...data);
    const maxPrice = Math.max(...data);
    const priceRange = maxPrice - minPrice;
    const padding = priceRange * 0.1;
    
    // Draw price line
    const gradient = ctx.createLinearGradient(0, 0, width, 0);
    gradient.addColorStop(0, '#d4af37');
    gradient.addColorStop(0.5, '#f5e6a3');
    gradient.addColorStop(1, '#d4af37');
    
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    for (let i = 0; i < data.length; i++) {
        const x = (width / (data.length - 1)) * i;
        const normalizedPrice = (data[i] - minPrice + padding) / (priceRange + padding * 2);
        const y = height - (normalizedPrice * height);
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    
    ctx.stroke();
    
    // Draw area fill
    const areaGradient = ctx.createLinearGradient(0, 0, 0, height);
    areaGradient.addColorStop(0, 'rgba(212, 175, 55, 0.3)');
    areaGradient.addColorStop(1, 'rgba(212, 175, 55, 0)');
    
    ctx.lineTo(width, height);
    ctx.lineTo(0, height);
    ctx.closePath();
    ctx.fillStyle = areaGradient;
    ctx.fill();
    
    // Draw current price indicator
    const lastPrice = data[data.length - 1];
    const lastX = width;
    const lastNormalized = (lastPrice - minPrice + padding) / (priceRange + padding * 2);
    const lastY = height - (lastNormalized * height);
    
    ctx.beginPath();
    ctx.arc(lastX - 5, lastY, 6, 0, Math.PI * 2);
    ctx.fillStyle = '#d4af37';
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Draw price label
    ctx.fillStyle = '#d4af37';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'right';
    ctx.fillText('$' + lastPrice.toFixed(2), width - 15, lastY - 10);
    
    // Draw title
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'left';
    ctx.fillText('XAU/USD', 10, 25);
    
    // Draw time labels
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';
    const timeLabels = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'];
    for (let i = 0; i < timeLabels.length; i++) {
        const x = (width / 6) * i;
        ctx.fillText(timeLabels[i], x, height - 5);
    }
}

function generatePriceData(points) {
    const data = [];
    let price = 2000 + Math.random() * 100; // Start around $2000-2100
    
    for (let i = 0; i < points; i++) {
        // Add some randomness with a slight upward trend
        const change = (Math.random() - 0.48) * 5;
        price += change;
        
        // Keep price in reasonable range
        if (price < 1950) price = 1950 + Math.random() * 10;
        if (price > 2150) price = 2150 - Math.random() * 10;
        
        data.push(price);
    }
    
    return data;
}

// Contact Form Setup
function setupContactForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(form);
        const data = {};
        formData.forEach(function(value, key) {
            data[key] = value;
        });
        
        // Validate form
        if (!data.name || !data.email || !data.message) {
            showNotification('请填写所有必填字段', 'error');
            return;
        }
        
        // Simple email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) {
            showNotification('请输入有效的邮箱地址', 'error');
            return;
        }
        
        // Simulate form submission
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.textContent = '发送中...';
        submitBtn.disabled = true;
        
        setTimeout(function() {
            showNotification('消息已发送成功！我们会尽快与您联系。', 'success');
            form.reset();
            submitBtn.textContent = '发送消息';
            submitBtn.disabled = false;
        }, 1500);
    });
}

// Notification System
function showNotification(message, type) {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification notification-' + type;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = 
        'position: fixed; ' +
        'bottom: 20px; ' +
        'right: 20px; ' +
        'padding: 15px 25px; ' +
        'border-radius: 8px; ' +
        'font-size: 14px; ' +
        'z-index: 10000; ' +
        'animation: slideIn 0.3s ease; ' +
        (type === 'success' 
            ? 'background: linear-gradient(135deg, #d4af37, #f5e6a3); color: #1a1a2e;'
            : 'background: #ff4757; color: white;');
    
    // Add animation keyframes
    if (!document.querySelector('#notificationStyles')) {
        const style = document.createElement('style');
        style.id = 'notificationStyles';
        style.textContent = 
            '@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }' +
            '@keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }';
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(function() {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 3000);
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            const offsetTop = targetElement.offsetTop - 80; // Account for fixed navbar
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Resize handler for chart
window.addEventListener('resize', function() {
    // Debounce resize events
    clearTimeout(window.resizeTimer);
    window.resizeTimer = setTimeout(function() {
        drawPriceChart();
    }, 250);
});
