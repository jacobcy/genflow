/**
 * 编辑器主脚本
 * 整合基础编辑功能、AI 功能和文章管理
 */

class Editor {
    constructor(selector, options = {}) {
        this.element = typeof selector === 'string' ? document.querySelector(selector) : selector;
        if (!this.element) throw new Error('Editor element not found');

        this.options = {
            autofocus: true,
            placeholder: '开始写作...',
            onChange: null,
            autosaveInterval: 30000, // 30秒
            ...options
        };

        this.isContentChanged = false;
        this.lastSavedContent = '';
        this.autosaveTimer = null;

        this.initialize();
    }

    initialize() {
        // 初始化编辑器 UI
        this.setupUI();

        // 加载已有内容
        this.loadExistingContent();

        // 绑定事件
        this.bindEvents();

        // 初始化 AI 功能
        this.initializeAIFeatures();

        // 设置自动保存
        this.setupAutosave();

        // 设置图片上传
        this.setupImageUpload();
    }

    setupUI() {
        // 设置编辑器基础 UI
        this.element.contentEditable = true;
        this.element.classList.add('editor-content');

        if (this.options.placeholder) {
            this.element.setAttribute('data-placeholder', this.options.placeholder);
        }

        if (this.options.autofocus) {
            this.element.focus();
        }
    }

    // 加载已有内容
    async loadExistingContent() {
        const articleId = new URLSearchParams(window.location.search).get('article_id');
        if (!articleId) return;

        try {
            const response = await fetch(`/api/articles/${articleId}`);
            if (!response.ok) throw new Error('加载失败');

            const article = await response.json();
            this.setContent(article.content || '');
            this.lastSavedContent = this.getContent();

            // 设置其他字段
            document.getElementById('articleTitle').value = article.title || '';
            document.getElementById('articleSummary').value = article.summary || '';
            document.getElementById('articleTags').value = article.tags || '';

            if (article.cover_image) {
                this.setCoverImage(article.cover_image);
            }
        } catch (error) {
            console.error('加载文章失败:', error);
            this.showToast('加载文章失败', 'error');
        }
    }

    // 绑定事件
    bindEvents() {
        this.element.addEventListener('input', () => {
            this.isContentChanged = true;
            if (this.options.onChange) {
                this.options.onChange();
            }
        });

        // 离开页面提示
        window.addEventListener('beforeunload', e => {
            if (this.isContentChanged) {
                e.preventDefault();
                e.returnValue = '您有未保存的更改，确定要离开吗？';
            }
        });
    }

    // 获取内容
    getContent() {
        return this.element.innerHTML;
    }

    // 设置内容
    setContent(content) {
        this.element.innerHTML = content;
    }

    // 设置封面图片
    setCoverImage(url) {
        const preview = document.createElement('img');
        preview.src = url;
        preview.className = 'img-thumbnail mt-2';
        preview.alt = '封面图片';

        const coverInput = document.getElementById('articleCover');
        if (coverInput) {
            const existingPreview = coverInput.nextElementSibling;
            if (existingPreview && existingPreview.tagName === 'IMG') {
                existingPreview.remove();
            }
            coverInput.parentNode.appendChild(preview);
        }
    }

    // 保存文章
    async save(publish = false, isAutosave = false) {
        const title = document.getElementById('articleTitle').value;
        const content = this.getContent();
        const summary = document.getElementById('articleSummary').value;
        const tags = document.getElementById('articleTags').value;

        // 基本验证
        if (!isAutosave && !title.trim()) {
            this.showToast('请输入文章标题', 'warning');
            return;
        }

        try {
            const articleId = new URLSearchParams(window.location.search).get('article_id');
            const endpoint = articleId ? `/api/articles/${articleId}` : '/api/articles';
            const method = articleId ? 'PUT' : 'POST';

            const response = await fetch(endpoint, {
                method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title,
                    content,
                    summary,
                    tags,
                    published: publish
                })
            });

            if (!response.ok) {
                throw new Error('保存失败');
            }

            const data = await response.json();
            this.lastSavedContent = content;
            this.isContentChanged = false;

            if (!isAutosave) {
                const message = publish ? '文章已发布' : '草稿已保存';
                this.showToast(message, 'success');

                if (!articleId && data.id) {
                    window.location.href = `/user/edit/${data.id}`;
                }
            }
        } catch (error) {
            console.error('保存文章失败:', error);
            if (!isAutosave) {
                this.showToast('保存失败，请重试', 'error');
            }
        }
    }

    // 显示提示消息
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.appendChild(toast);
        document.body.appendChild(container);

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            container.remove();
        });
    }

    // 事件监听
    on(event, callback) {
        this.element.addEventListener(event, callback);
    }

    // 检查内容是否改变
    hasChanges() {
        return this.isContentChanged;
    }

    // 设置自动保存
    setupAutosave() {
        this.on('change', () => {
            clearTimeout(this.autosaveTimer);
            this.autosaveTimer = setTimeout(() => {
                if (this.hasChanges()) {
                    this.save(false, true);
                }
            }, this.options.autosaveInterval);
        });
    }

    // 设置图片上传
    setupImageUpload() {
        const coverInput = document.getElementById('articleCover');
        if (!coverInput) return;

        coverInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            try {
                const formData = new FormData();
                formData.append('image', file);

                const response = await fetch('/api/upload/image', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('上传失败');
                }

                const data = await response.json();
                if (data.url) {
                    this.setCoverImage(data.url);
                }
            } catch (error) {
                console.error('图片上传失败:', error);
                this.showToast('图片上传失败，请重试', 'error');
            }
        });
    }

    // 初始化 AI 功能
    initializeAIFeatures() {
        // AI 相关功能将在 ai-features.js 中实现
    }
}

// 初始化编辑器实例
document.addEventListener('DOMContentLoaded', () => {
    window.editor = new Editor('#editor');
});

// 导出编辑器类和全局函数
window.Editor = Editor;
window.saveArticle = function (publish = false) {
    if (window.editor) {
        window.editor.save(publish);
    }
}; 