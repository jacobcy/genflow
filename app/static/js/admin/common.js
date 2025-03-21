/**
 * 管理员通用功能
 */

// 初始化管理员页面通用功能
function initializeCommon() {
    // 检查认证状态
    checkAuthStatus();

    // 初始化主题
    initializeTheme();

    // 绑定登出按钮事件
    const logoutButton = document.getElementById('adminLogoutBtn');
    if (logoutButton) {
        logoutButton.addEventListener('click', handleAdminLogout);
    }

    // 绑定侧边栏切换按钮事件
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // 绑定主题切换按钮事件
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    // 初始化工具提示
    initializeTooltips();
}

// 初始化主题
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeToggleButton(savedTheme);
}

// 切换主题
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggleButton(newTheme);
}

// 更新主题切换按钮状态
function updateThemeToggleButton(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
                themeToggle.setAttribute('title', '切换到亮色模式');
            } else {
                icon.className = 'fas fa-moon';
                themeToggle.setAttribute('title', '切换到暗色模式');
            }
        }
    }
}

// 检查认证状态
function checkAuthStatus() {
    // 如果当前在登录页面，不需要检查认证状态
    if (window.location.pathname === '/admin/login') {
        return;
    }

    // 验证认证状态
    fetch('/api/auth/admin/verify', {
        method: 'GET',
        credentials: 'include'  // 包含 cookies
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('认证失败');
            }
            return response.json();
        })
        .catch(error => {
            console.error('认证检查失败:', error);
            redirectToLogin();
        });
}

// 重定向到登录页面
function redirectToLogin() {
    // 保存当前URL，登录后可以返回
    const currentPath = window.location.pathname;
    if (currentPath !== '/admin/login') {
        sessionStorage.setItem('adminRedirectUrl', currentPath);
    }

    // 跳转到登录页面
    window.location.href = '/admin/login';
}

// 切换侧边栏
function toggleSidebar() {
    const wrapper = document.getElementById('wrapper');
    if (wrapper) {
        wrapper.classList.toggle('toggled');

        // 保存侧边栏状态到本地存储
        const isToggled = wrapper.classList.contains('toggled');
        localStorage.setItem('sidebarToggled', isToggled);
    }
}

// 初始化工具提示
function initializeTooltips() {
    // 查找所有带有data-bs-toggle="tooltip"属性的元素
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));

    // 初始化Bootstrap工具提示
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 显示加载中状态
function showLoading(element, text = '加载中...') {
    if (element) {
        element.disabled = true;
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            ${text}
        `;
    }
}

// 恢复按钮状态
function resetButton(element, originalText) {
    if (element) {
        element.disabled = false;
        element.innerHTML = originalText;
    }
}

// 显示通知消息
function showNotification(message, type = 'success') {
    const container = document.createElement('div');
    container.className = `toast align-items-center text-white bg-${type} border-0`;
    container.setAttribute('role', 'alert');
    container.setAttribute('aria-live', 'assertive');
    container.setAttribute('aria-atomic', 'true');

    container.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    // 添加到通知容器
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        // 如果不存在通知容器，创建一个
        const newContainer = document.createElement('div');
        newContainer.id = 'toastContainer';
        newContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(newContainer);
        newContainer.appendChild(container);
    } else {
        toastContainer.appendChild(container);
    }

    // 初始化并显示通知
    const toast = new bootstrap.Toast(container);
    toast.show();

    // 监听隐藏事件，移除DOM元素
    container.addEventListener('hidden.bs.toast', function () {
        container.remove();
    });
}

// 格式化日期时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}

// 导出通用函数
export {
    initializeCommon,
    checkAuthStatus,
    redirectToLogin,
    toggleSidebar,
    showLoading,
    resetButton,
    showNotification,
    formatDateTime,
    toggleTheme
};

// 页面加载时初始化通用功能
document.addEventListener('DOMContentLoaded', initializeCommon); 