/**
 * 编辑器主脚本
 * 整合基础编辑功能、AI 功能和文章管理
 */

// 编辑器全局状态
let editor = null;
let isContentChanged = false;
let lastSavedContent = '';

// 初始化编辑器
document.addEventListener('DOMContentLoaded', function () {
    initializeEditor();
});

/**
 * 编辑器初始化
 */
function initializeEditor() {
    // 初始化编辑器实例
    editor = new Editor('#editor', {
        autofocus: true,
        placeholder: '开始写作...',
        onChange: () => {
            isContentChanged = true;
            updatePreview();
        }
    });

    // 加载已有内容
    loadExistingContent();

    // 绑定事件处理
    bindEditorEvents();

    // 初始化 AI 功能
    initializeAIFeatures();
}

/**
 * 加载已有内容
 */
function loadExistingContent() {
    const articleId = new URLSearchParams(window.location.search).get('article_id');
    if (articleId) {
        fetch(`/api/articles/${articleId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.article) {
                    editor.setContent(data.article.content);
                    document.getElementById('articleTitle').value = data.article.title;
                    document.getElementById('articleSummary').value = data.article.summary || '';
                    document.getElementById('articleTags').value = data.article.tags || '';

                    // 显示已有封面图
                    if (data.article.cover_image) {
                        const img = document.createElement('img');
                        img.src = data.article.cover_image;
                        img.className = 'img-thumbnail mt-2';
                        img.alt = '封面图片';
                        document.getElementById('articleCover').parentNode.appendChild(img);
                    }

                    lastSavedContent = editor.getContent();
                    updatePreview();
                }
            })
            .catch(console.error);
    }
}

/**
 * 绑定编辑器事件
 */
function bindEditorEvents() {
    // 保存草稿
    document.querySelector('button[onclick="saveArticle(false)"]')
        .addEventListener('click', () => saveArticle(false));

    // 发布文章
    document.querySelector('button[onclick="saveArticle(true)"]')
        .addEventListener('click', () => saveArticle(true));

    // 封面图片预览
    document.getElementById('articleCover').addEventListener('change', handleCoverImagePreview);

    // 离开页面提示
    window.addEventListener('beforeunload', e => {
        if (isContentChanged) {
            e.preventDefault();
            e.returnValue = '您有未保存的更改，确定要离开吗？';
        }
    });
}

/**
 * 处理封面图片预览
 */
function handleCoverImagePreview(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = document.querySelector('.img-thumbnail');
            if (img) {
                img.src = e.target.result;
            } else {
                const newImg = document.createElement('img');
                newImg.src = e.target.result;
                newImg.className = 'img-thumbnail mt-2';
                newImg.alt = '封面图片';
                document.getElementById('articleCover').parentNode.appendChild(newImg);
            }
        }
        reader.readAsDataURL(file);
    }
}

/**
 * 保存或发布文章
 */
function saveArticle(isPublished = false) {
    const articleId = new URLSearchParams(window.location.search).get('article_id');
    const title = document.getElementById('articleTitle').value;
    const content = editor.getContent();
    const summary = document.getElementById('articleSummary').value;
    const tags = document.getElementById('articleTags').value;

    if (!title) {
        alert('请输入文章标题');
        return;
    }

    if (!content) {
        alert('请输入文章内容');
        return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    formData.append('summary', summary);
    formData.append('tags', tags);
    formData.append('published', isPublished);

    const coverFile = document.getElementById('articleCover').files[0];
    if (coverFile) {
        formData.append('cover_image', coverFile);
    }

    const url = articleId ? `/api/articles/${articleId}` : '/api/articles';
    const method = articleId ? 'PUT' : 'POST';

    // 显示保存中状态
    const saveBtn = document.querySelector(`button[onclick="saveArticle(${isPublished})"]`);
    const originalText = saveBtn.textContent;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>保存中...';

    fetch(url, {
        method: method,
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        },
        body: formData
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('保存文章失败');
        })
        .then(data => {
            alert(isPublished ? '文章已发布' : '草稿已保存');
            lastSavedContent = content;
            isContentChanged = false;

            // 如果是新建文章，保存后跳转到编辑页
            if (!articleId && data.id) {
                window.location.href = `/user/edit?article_id=${data.id}`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('保存失败，请稍后重试');
        })
        .finally(() => {
            saveBtn.disabled = false;
            saveBtn.textContent = originalText;
        });
}

/**
 * 实时预览更新
 */
function updatePreview() {
    const previewContainer = document.getElementById('preview');
    if (previewContainer) {
        const content = editor.getContent();
        previewContainer.innerHTML = content || '<p class="text-muted">预览区域</p>';
    }
}

/**
 * AI 功能初始化
 */
function initializeAIFeatures() {
    // AI 写作助手按钮
    const aiToolbar = document.createElement('div');
    aiToolbar.className = 'ai-toolbar';
    aiToolbar.innerHTML = `
        <div class="btn-group">
            <button class="btn btn-outline-primary btn-sm" onclick="aiComplete()">
                <i class="fas fa-magic me-1"></i>AI 补全
            </button>
            <button class="btn btn-outline-primary btn-sm" onclick="aiPolish()">
                <i class="fas fa-feather me-1"></i>优化文本
            </button>
            <button class="btn btn-outline-primary btn-sm" onclick="aiSuggest()">
                <i class="fas fa-lightbulb me-1"></i>写作建议
            </button>
        </div>
    `;
    editor.wrapper.insertBefore(aiToolbar, editor.wrapper.firstChild);
}

/**
 * AI 文本补全
 */
function aiComplete() {
    const selection = editor.getSelection();
    if (!selection) {
        alert('请先选择需要补全的文本');
        return;
    }

    fetch('/api/ai/complete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        },
        body: JSON.stringify({ text: selection })
    })
        .then(response => response.json())
        .then(data => {
            if (data.completion) {
                editor.replaceSelection(data.completion);
            }
        })
        .catch(error => {
            console.error('AI 补全失败:', error);
            alert('AI 补全失败，请稍后重试');
        });
}

/**
 * AI 文本优化
 */
function aiPolish() {
    const selection = editor.getSelection();
    if (!selection) {
        alert('请先选择需要优化的文本');
        return;
    }

    fetch('/api/ai/polish', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        },
        body: JSON.stringify({ text: selection })
    })
        .then(response => response.json())
        .then(data => {
            if (data.polished) {
                editor.replaceSelection(data.polished);
            }
        })
        .catch(error => {
            console.error('文本优化失败:', error);
            alert('文本优化失败，请稍后重试');
        });
}

/**
 * AI 写作建议
 */
function aiSuggest() {
    const content = editor.getContent();
    if (!content) {
        alert('请先输入一些内容');
        return;
    }

    fetch('/api/ai/suggest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
        },
        body: JSON.stringify({ text: content })
    })
        .then(response => response.json())
        .then(data => {
            if (data.suggestions) {
                // 显示建议对话框
                const modal = new bootstrap.Modal(document.getElementById('aiSuggestionsModal'));
                document.getElementById('aiSuggestionsList').innerHTML = data.suggestions
                    .map(s => `<li class="list-group-item">${s}</li>`)
                    .join('');
                modal.show();
            }
        })
        .catch(error => {
            console.error('获取写作建议失败:', error);
            alert('获取写作建议失败，请稍后重试');
        });
} 