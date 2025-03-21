// 用户仪表盘页面脚本
document.addEventListener('DOMContentLoaded', function () {
    // 初始化用户仪表盘
    initializeDashboard();
});

function initializeDashboard() {
    // 绑定退出登录事件
    const logoutButton = document.querySelector('button[onclick="handleLogout()"]');
    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
    }
}

// 处理退出登录
async function handleLogout() {
    if (confirm('确定要退出登录吗？')) {
        try {
            // 调用退出登录接口
            const response = await fetch('/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // 清除 JWT token
                localStorage.removeItem('jwt_token');
                // 跳转到首页
                window.location.href = '/';
            } else {
                throw new Error('退出登录失败');
            }
        } catch (error) {
            console.error('退出登录错误:', error);
            alert('退出登录失败，请重试');
        }
    }
}

// 删除文章
function deleteArticle(articleId) {
    if (confirm('确定要删除这篇文章吗？此操作不可恢复。')) {
        fetch(`/api/articles/${articleId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
            }
        })
            .then(response => {
                if (response.ok) {
                    // 刷新页面
                    window.location.reload();
                } else {
                    throw new Error('删除文章失败');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('删除文章失败，请稍后重试');
            });
    }
} 