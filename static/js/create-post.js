document.addEventListener('DOMContentLoaded', function() {
    // Initialize TinyMCE
    tinymce.init({
        selector: '#post-content',
        plugins: 'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table code help wordcount',
        toolbar: 'undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help',
        height: 400,
        skin: document.documentElement.getAttribute('data-theme') === 'dark' ? 'oxide-dark' : 'oxide',
        content_css: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'default'
    });

    const createPostBtn = document.getElementById('create-post-btn');
    const createPostModal = document.getElementById('create-post-modal');
    const modalBackdrop = document.getElementById('modal-backdrop');
    const closeModalBtn = document.getElementById('close-modal');
    const postForm = document.getElementById('post-form');
    let isModalOpen = false;

    function openModal() {
        createPostModal.style.display = 'block';
        modalBackdrop.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Trigger animations
        setTimeout(() => {
            modalBackdrop.style.opacity = '1';
            createPostModal.style.opacity = '1';
            createPostModal.style.transform = 'translate(-50%, -50%) scale(1)';
        }, 10);
        
        isModalOpen = true;
    }

    function closeModal() {
        modalBackdrop.style.opacity = '0';
        createPostModal.style.opacity = '0';
        createPostModal.style.transform = 'translate(-50%, -50%) scale(0.8)';
        
        setTimeout(() => {
            createPostModal.style.display = 'none';
            modalBackdrop.style.display = 'none';
            document.body.style.overflow = 'auto';
        }, 300);
        
        isModalOpen = false;
    }

    // Event Listeners
    createPostBtn.addEventListener('click', openModal);
    closeModalBtn.addEventListener('click', closeModal);
    modalBackdrop.addEventListener('click', (e) => {
        if (e.target === modalBackdrop) {
            closeModal();
        }
    });

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isModalOpen) {
            closeModal();
        }
    });

    // Handle form submission
    postForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(postForm);
        formData.set('content', tinymce.get('post-content').getContent());

        try {
            const response = await fetch('/post/new', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                closeModal();
                window.location.href = `/post/${result.post_id}`;
            } else {
                throw new Error('Failed to create post');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to create post. Please try again.');
        }
    });

    // Handle tag input
    const tagInput = document.getElementById('tag-input');
    const tagContainer = document.getElementById('tag-container');
    const tags = new Set();

    tagInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            const tag = tagInput.value.trim().toLowerCase();
            
            if (tag && !tags.has(tag)) {
                tags.add(tag);
                const tagElement = document.createElement('span');
                tagElement.className = 'tag';
                tagElement.innerHTML = `
                    ${tag}
                    <button type="button" class="remove-tag" aria-label="Remove tag">×</button>
                `;
                tagContainer.appendChild(tagElement);
                
                // Add hidden input for form submission
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'tags';
                hiddenInput.value = tag;
                postForm.appendChild(hiddenInput);
            }
            
            tagInput.value = '';
        }
    });

    // Handle tag removal
    tagContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-tag')) {
            const tagElement = e.target.parentElement;
            const tag = tagElement.textContent.trim().slice(0, -1);
            tags.delete(tag);
            tagElement.remove();
            
            // Remove hidden input
            const hiddenInputs = postForm.querySelectorAll('input[name="tags"]');
            hiddenInputs.forEach(input => {
                if (input.value === tag) {
                    input.remove();
                }
            });
        }
    });
}); 