// 主题管理
document.addEventListener('DOMContentLoaded', function () {
    // 创建主题切换按钮
    const themeToggle = document.createElement('button');
    themeToggle.className = 'btn btn-secondary';
    themeToggle.style.position = 'fixed';
    themeToggle.style.bottom = '20px';
    themeToggle.style.right = '20px';
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    document.body.appendChild(themeToggle);

    // 获取当前主题
    function getCurrentTheme() {
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        return savedTheme || (systemPrefersDark ? 'dark' : 'light');
    }

    // 应用主题
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        themeToggle.innerHTML = theme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    }

    // 切换主题
    function toggleTheme() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
    }

    // 初始化主题
    applyTheme(getCurrentTheme());
    themeToggle.addEventListener('click', toggleTheme);

    // 检查是否有token来显示/隐藏退出按钮
    if (localStorage.getItem('access_token')) {
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.style.display = 'block';
            // 退出登录
            logoutBtn.addEventListener('click', function (e) {
                e.preventDefault();
                localStorage.removeItem('access_token');
                window.location.href = '/';
            });
        }
    }

    // 为所有fetch请求添加Authorization头
    const originalFetch = window.fetch;
    window.fetch = function (url, options = {}) {
        const token = localStorage.getItem('access_token');
        if (token) {
            options.headers = options.headers || {};
            options.headers['Authorization'] = `Bearer ${token}`;
            options.credentials = 'include';
            options.mode = 'cors';
        }
        return originalFetch(url, options);
    };
}); 