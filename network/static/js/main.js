document.addEventListener('DOMContentLoaded', () => {
    // Post creation form AJAX
    const createPostForm = document.querySelector('.create-post form');
    if (createPostForm) {
        createPostForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch('', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const newPostHtml = `
                        <div class="glass-card post">
                            <div class="post-header">
                                <a href="/profile/${data.post.author}" class="post-author">${data.post.author}</a>
                                <span class="post-date">${data.post.created_at}</span>
                            </div>
                            <div class="post-content">${escapeHtml(data.post.content)}</div>
                            ${data.post.image_url ? `<div class="post-image"><img src="${data.post.image_url}" alt="Post image"></div>` : ''}
                            <div class="post-actions">
                                <button class="action-btn like-btn" data-post="${data.post.id}">
                                    <span class="heart-icon">🤍</span>
                                    <span class="like-count">${data.post.likes_count}</span>
                                </button>
                                <span class="action-btn comment-count">💬 ${data.post.comments_count} Comments</span>
                            </div>
                            <div class="comments-section">
                                <form action="/post/${data.post.id}/comment" method="POST" class="comment-form">
                                    <input type="text" name="content" class="form-control" placeholder="Add a comment..." required>
                                    <button type="submit" class="btn btn-primary">Reply</button>
                                </form>
                                <div class="comments-list"></div>
                            </div>
                        </div>
                    `;
                    
                    const postsList = document.querySelector('.posts-list');
                    const emptyState = postsList.querySelector('.empty-state');
                    if (emptyState) emptyState.remove();
                    
                    postsList.insertAdjacentHTML('afterbegin', newPostHtml);
                    
                    this.reset();
                    showToast('Post created!');
                    
                    attachLikeListener(postsList.querySelector('.like-btn'));
                    attachCommentListener(postsList.querySelector('.comment-form'));
                } else {
                    showToast(data.error || 'Failed to create post');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Unable to create post.');
            });
        });
    }

    document.querySelectorAll('.like-btn').forEach(btn => {
        attachLikeListener(btn);
    });

    document.querySelectorAll('.comment-form').forEach(form => {
        attachCommentListener(form);
    });

    document.querySelectorAll('.follow-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const username = this.dataset.user;

            fetch(`/api/follow/${username}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showToast(data.error);
                    return;
                }

                const followersCountSpan = document.getElementById('followers-count');
                if (followersCountSpan) {
                    followersCountSpan.textContent = data.followers_count;
                }

                if (data.following) {
                    this.textContent = 'Unfollow';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-outline');
                    showToast('Now following ' + username + '!');
                } else {
                    this.textContent = 'Follow';
                    this.classList.remove('btn-outline');
                    this.classList.add('btn-primary');
                    showToast('Unfollowed ' + username + '.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Unable to update follow status.');
            });
        });
    });
});

function attachLikeListener(btn) {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        const postId = this.dataset.post;
        const heart = this.querySelector('.heart-icon');
        const countSpan = this.querySelector('.like-count');

        fetch(`/api/like/${postId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.liked) {
                this.classList.add('liked');
                heart.textContent = '❤️';
                showToast('Liked the post!');
            } else {
                this.classList.remove('liked');
                heart.textContent = '🤍';
                showToast('Like removed.');
            }

            if (countSpan) {
                countSpan.textContent = data.like_count;
            }

            this.classList.add('bounce');
            setTimeout(() => this.classList.remove('bounce'), 300);
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Unable to update like.');
        });
    });
}

function attachCommentListener(form) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const postId = this.action.split('/').slice(-2)[0];
        const contentInput = this.querySelector('input[name="content"]');
        
        const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const commentHtml = `
                    <div class="comment">
                        <div class="comment-author">${data.comment.author}</div>
                        <div class="comment-content">${escapeHtml(data.comment.content)}</div>
                    </div>
                `;
                
                const commentsList = form.parentElement.querySelector('.comments-list');
                commentsList.insertAdjacentHTML('beforeend', commentHtml);
                
                const commentCount = form.parentElement.parentElement.querySelector('.comment-count');
                if (commentCount) {
                    const count = parseInt(commentCount.textContent.match(/\d+/)[0]) + 1;
                    commentCount.textContent = `💬 ${count} Comments`;
                }
                
                contentInput.value = '';
                showToast('Comment added!');
            } else {
                showToast(data.error || 'Failed to add comment');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Unable to add comment.');
        });
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', () => {
    let toast = document.querySelector('.toast-message');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast-message';
        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.classList.add('visible');
    clearTimeout(toast.timeoutId);
    toast.timeoutId = setTimeout(() => {
        toast.classList.remove('visible');
    }, 2200);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
