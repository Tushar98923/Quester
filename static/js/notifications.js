// Function to mark a notification as viewed
function markNotificationAsViewed(notificationId) {
    fetch(`/api/notifications/${notificationId}/view`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the notification's visual state
            const notification = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notification) {
                notification.classList.remove('unviewed');
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Set up Intersection Observer for notifications
document.addEventListener('DOMContentLoaded', function() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const notificationId = entry.target.dataset.notificationId;
                markNotificationAsViewed(notificationId);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.5
    });

    // Observe all unviewed notifications
    document.querySelectorAll('.notification-item.unviewed').forEach(notification => {
        observer.observe(notification);
    });
});

// Handle filter changes
document.querySelectorAll('.notification-filter').forEach(filter => {
    filter.addEventListener('click', function(e) {
        e.preventDefault();
        const filterType = this.dataset.filter;
        window.location.href = `/notifications?filter_type=${filterType}`;
    });
}); 