// 在页面加载时获取文章列表
document.addEventListener('DOMContentLoaded', function () {
    // 检查是否已登录
    if (!localStorage.getItem('access_token')) {
        window.location.href = '/';
        return;
    }

    // 加载所有文章
    loadArticles();

    // 为Tab切换添加事件监听
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (event) {
            const targetId = event.target.getAttribute('data-bs-target').substring(1);
            if (targetId === 'all-articles') {
                loadArticles();
            } else if (targetId === 'drafts') {
                loadDrafts();
            } else if (targetId === 'published') {
                loadPublished();
            }
        });
    });
});

// 加载所有文章
function loadArticles() {
    const tableBody = document.getElementById('allArticlesBody');
    tableBody.innerHTML = '<tr><td colspan="5" class="text-center py-3"><i class="fas fa-spinner fa-spin me-2"></i>加载中...</td></tr>';

    fetch('/api/articles', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('加载文章失败');
            }
            return response.json();
        })
        .then(articles => {
            if (articles.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" class="text-center py-3">暂无文章，点击右上角"新建文章"开始创作吧！</td></tr>';
                return;
            }

            // 排序：最新的先显示
            articles.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

            // 渲染文章列表
            tableBody.innerHTML = articles.map(article => `
                <tr>
                    <td>${article.title}</td>
                    <td>
                        <span class="badge ${getStatusBadgeClass(article.status)}">
                            ${getStatusText(article.status)}
                        </span>
                    </td>
                    <td>${formatDate(article.created_at)}</td>
                    <td>${formatDate(article.updated_at)}</td>
                    <td>
                        <a href="/editor?id=${article.id}" class="btn btn-sm btn-outline-primary me-1">编辑</a>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteArticle(${article.id})">删除</button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => {
            console.error('获取文章列表失败:', error);
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-3">加载失败: ${error.message}</td></tr>`;
        });
}

// 加载草稿
function loadDrafts() {
    const tableBody = document.getElementById('draftsBody');
    tableBody.innerHTML = '<tr><td colspan="4" class="text-center py-3"><i class="fas fa-spinner fa-spin me-2"></i>加载中...</td></tr>';

    fetch('/api/articles', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('加载草稿失败');
            }
            return response.json();
        })
        .then(articles => {
            // 过滤出草稿
            const drafts = articles.filter(article => article.status === 'draft');

            if (drafts.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="4" class="text-center py-3">暂无草稿</td></tr>';
                return;
            }

            // 排序：最新的先显示
            drafts.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

            // 渲染草稿列表
            tableBody.innerHTML = drafts.map(draft => `
                <tr>
                    <td>${draft.title}</td>
                    <td>${formatDate(draft.created_at)}</td>
                    <td>${formatDate(draft.updated_at)}</td>
                    <td>
                        <a href="/editor?id=${draft.id}" class="btn btn-sm btn-outline-primary me-1">编辑</a>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteArticle(${draft.id})">删除</button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => {
            console.error('获取草稿列表失败:', error);
            tableBody.innerHTML = `<tr><td colspan="4" class="text-center text-danger py-3">加载失败: ${error.message}</td></tr>`;
        });
}

// 加载已发布文章
function loadPublished() {
    const tableBody = document.getElementById('publishedBody');
    tableBody.innerHTML = '<tr><td colspan="4" class="text-center py-3"><i class="fas fa-spinner fa-spin me-2"></i>加载中...</td></tr>';

    fetch('/api/articles', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('加载已发布文章失败');
            }
            return response.json();
        })
        .then(articles => {
            // 过滤出已发布文章
            const published = articles.filter(article => article.status === 'published');

            if (published.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="4" class="text-center py-3">暂无已发布文章</td></tr>';
                return;
            }

            // 排序：最新发布的先显示
            published.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

            // 渲染已发布文章列表
            tableBody.innerHTML = published.map(article => `
                <tr>
                    <td>${article.title}</td>
                    <td>${formatDate(article.updated_at)}</td>
                    <td>未指定</td>
                    <td>
                        <a href="/editor?id=${article.id}" class="btn btn-sm btn-outline-primary me-1">查看</a>
                        <button class="btn btn-sm btn-outline-secondary" onclick="republishArticle(${article.id})">重新发布</button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => {
            console.error('获取已发布文章列表失败:', error);
            tableBody.innerHTML = `<tr><td colspan="4" class="text-center text-danger py-3">加载失败: ${error.message}</td></tr>`;
        });
}

// 删除文章
function deleteArticle(articleId) {
    if (!confirm('确定要删除这篇文章吗？此操作不可恢复！')) {
        return;
    }

    // TODO: 实现删除文章的API调用
    alert('删除文章功能即将上线，敬请期待！');

    // 重新加载文章列表
    loadArticles();
}

// 重新发布文章
function republishArticle(articleId) {
    // TODO: 实现重新发布文章的API调用
    alert('重新发布功能即将上线，敬请期待！');
}

// 获取状态对应的样式类
function getStatusBadgeClass(status) {
    switch (status) {
        case 'draft': return 'bg-secondary';
        case 'published': return 'bg-success';
        case 'deleted': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

// 获取状态对应的文本
function getStatusText(status) {
    switch (status) {
        case 'draft': return '草稿';
        case 'published': return '已发布';
        case 'deleted': return '已删除';
        default: return status;
    }
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
} 