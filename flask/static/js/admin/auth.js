/**
 * 管理员认证功能
 */

// 初始化登录页面
function initializeLogin() {
    const loginForm = document.getElementById('adminLoginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            e.preventDefault();
            handleAdminLogin();
        });
    }
}

// 处理管理员登录
function handleAdminLogin() {
    const email = document.getElementById('adminEmail').value;
    const password = document.getElementById('adminPassword').value;
    const errorMessageContainer = document.getElementById('adminErrorMessage');
    const loginButton = document.querySelector('#loginButton');
    const btnText = loginButton.querySelector('.btn-text');
    const loadingText = loginButton.querySelector('.loading-text');

    // 显示加载状态
    loginButton.disabled = true;
    btnText.style.display = 'none';
    loadingText.style.display = 'inline-block';
    errorMessageContainer.style.display = 'none';

    fetch('/api/auth/admin/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email,
            password: password
        }),
        credentials: 'include'  // 允许发送和接收 cookies
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.message || err.error || '登录失败');
                });
            }
            return response.json();
        })
        .then(data => {
            // 显示成功消息
            errorMessageContainer.className = 'admin-alert admin-alert-success mt-3';
            errorMessageContainer.textContent = '登录成功，正在跳转...';
            errorMessageContainer.style.display = 'block';

            // 跳转到管理员仪表盘
            setTimeout(() => {
                window.location.href = '/admin/dashboard';
            }, 1000);
        })
        .catch(error => {
            console.error('登录失败:', error);
            errorMessageContainer.className = 'admin-alert admin-alert-error mt-3';
            errorMessageContainer.textContent = `登录失败: ${error.message}`;
            errorMessageContainer.style.display = 'block';
        })
        .finally(() => {
            // 恢复按钮状态
            loginButton.disabled = false;
            btnText.style.display = 'inline-block';
            loadingText.style.display = 'none';
        });
}

// 检查管理员认证状态
function checkAdminAuth() {
    return fetch('/api/auth/admin/verify', {
        method: 'GET',
        credentials: 'include'  // 允许发送和接收 cookies
    })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/admin';
                    throw new Error('认证已过期，请重新登录');
                }
                return response.json().then(err => {
                    throw new Error(err.error || err.message || '认证失败');
                });
            }
            return response.json();
        });
}

// 管理员登出
function handleAdminLogout() {
    fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
    })
        .then(() => {
            window.location.href = '/admin';
        })
        .catch(error => {
            console.error('登出失败:', error);
            window.location.href = '/admin';
        });
}

// 导出函数供其他模块使用
export {
    checkAdminAuth,
    handleAdminLogout
};

// 页面加载时初始化登录功能
document.addEventListener('DOMContentLoaded', initializeLogin); 