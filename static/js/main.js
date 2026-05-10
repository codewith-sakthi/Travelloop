// main.js - Traveloop
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-msg');
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(msg => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateX(100%)';
                msg.style.transition = 'all 0.3s ease';
                setTimeout(() => msg.remove(), 300);
            });
        }, 5000);
    }
});
