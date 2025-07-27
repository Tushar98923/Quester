// Comment ranking algorithm
function calculateCommentScore(comment) {
    const tickWeight = 3;
    const likeWeight = 1;
    const dislikeWeight = -1;
    const replyWeight = 0.5;

    return (
        comment.ticks * tickWeight +
        comment.likes * likeWeight +
        comment.dislikes * dislikeWeight +
        comment.replies.length * replyWeight
    );
}

// Sort comments by score
function sortComments(comments) {
    return comments.sort((a, b) => calculateCommentScore(b) - calculateCommentScore(a));
}

// Handle comment actions (like, dislike, tick)
async function handleCommentAction(commentId, action) {
    try {
        const response = await fetch(`/api/comment/${commentId}/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error('Failed to perform action');
        }

        const data = await response.json();
        updateCommentStats(commentId, data);
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to perform action', 'error');
    }
}

// Update comment statistics in the UI
function updateCommentStats(commentId, stats) {
    const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
    if (!commentElement) return;

    const statsContainer = commentElement.querySelector('.comment-stats');
    statsContainer.innerHTML = `
        <span class="stat">
            <i class="fas fa-check"></i> ${stats.ticks}
        </span>
        <span class="stat">
            <i class="fas fa-thumbs-up"></i> ${stats.likes}
        </span>
        <span class="stat">
            <i class="fas fa-thumbs-down"></i> ${stats.dislikes}
        </span>
        <span class="stat">
            <i class="fas fa-reply"></i> ${stats.replies}
        </span>
    `;
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Handle search functionality
const searchInput = document.querySelector('.search-input');
if (searchInput) {
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const query = e.target.value.trim();
            if (query.length >= 2) {
                window.location.href = `/search?q=${encodeURIComponent(query)}`;
            }
        }, 500);
    });
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', () => {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = e.target.dataset.tooltip;
            document.body.appendChild(tooltip);

            const rect = e.target.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
        });

        element.addEventListener('mouseleave', () => {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
}); 