// 初始化变量
let gradioPort = 6060;  // 默认端口

// 获取端口配置
async function getPortConfig() {
    try {
        const response = await fetch('/api/config/ports', {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.status === 'success') {
            gradioPort = data.data.gradio;
            console.log('Port configuration loaded:', data.data);
        }
    } catch (error) {
        console.error('Error loading port configuration:', error);
        // 使用默认端口配置
        console.log('Using default port configuration');
    }
}

// 登录处理函数
async function handleLogin(event) {
    if (event) {
        event.preventDefault();
    }

    console.log('handleLogin function called'); // 调试日志

    const email = document.getElementById('email')?.value;
    const password = document.getElementById('password')?.value;
    const loginButton = document.getElementById('loginButton');
    const errorMessageDiv = document.getElementById('errorMessage');

    console.log('Elements found:', { // 调试日志
        email: !!email,
        password: !!password,
        loginButton: !!loginButton,
        errorMessageDiv: !!errorMessageDiv
    });

    if (!email || !password || !loginButton || !errorMessageDiv) {
        console.error('Required elements not found');
        return;
    }

    console.log('Sending login request to /api/auth/login');

    // 禁用登录按钮防止重复提交
    loginButton.disabled = true;
    loginButton.innerHTML = '<div class="d-flex align-items-center justify-content-center"><span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>登录中...</div>';

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
            credentials: 'include'
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || errorData.message || '登录失败');
        }

        const data = await response.json();
        console.log('Login response data:', data);

        // 清除错误信息和错误样式
        errorMessageDiv.innerHTML = '';
        document.getElementById('email')?.classList.remove('is-invalid');
        document.getElementById('password')?.classList.remove('is-invalid');

        // 保存token
        document.cookie = `access_token_cookie=${data.access_token}; Path=/; SameSite=Lax; ${location.protocol === 'https:' ? 'Secure' : ''}`;
        localStorage.setItem('access_token', data.access_token);

        // 跳转到用户仪表盘
        console.log('User logged in, redirecting to user dashboard');
        window.location.href = '/user/dashboard';

    } catch (error) {
        console.error('Login error:', error);

        // 错误信息美化
        let errorMessage = error.message;
        if (errorMessage.includes('邮箱格式不正确')) {
            errorMessage = '请输入有效的邮箱地址';
        } else if (errorMessage.includes('邮箱或密码错误')) {
            errorMessage = '账号或密码不正确，请重试';
        } else if (errorMessage.includes('缺少必填字段')) {
            errorMessage = '请填写所有必填信息';
        }

        errorMessageDiv.innerHTML = `
            <div class="alert alert-danger">
                <div class="d-flex align-items-center">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    <span>${errorMessage}</span>
                </div>
            </div>
        `;

        // 添加错误样式
        if (errorMessage.includes('邮箱')) {
            document.getElementById('email')?.classList.add('is-invalid');
        }
        if (errorMessage.includes('密码')) {
            document.getElementById('password')?.classList.add('is-invalid');
        }
    } finally {
        // 恢复登录按钮状态
        loginButton.disabled = false;
        loginButton.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>登录';
    }
}

// 文档加载后设置事件监听
document.addEventListener('DOMContentLoaded', async function () {
    console.log('DOMContentLoaded event fired'); // 调试日志

    // 加载端口配置
    await getPortConfig();

    // 清除错误提示的函数
    const clearError = () => {
        const errorMessage = document.getElementById('errorMessage');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');

        if (errorMessage) errorMessage.innerHTML = '';
        if (emailInput) emailInput.classList.remove('is-invalid');
        if (passwordInput) passwordInput.classList.remove('is-invalid');
    };

    // 获取所有需要的元素
    const loginForm = document.getElementById('loginForm');
    const loginButton = document.getElementById('loginButton');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    console.log('Form elements found:', { // 调试日志
        loginForm: !!loginForm,
        loginButton: !!loginButton,
        emailInput: !!emailInput,
        passwordInput: !!passwordInput
    });

    // 为表单添加提交事件监听器
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
        console.log('Added submit event listener to form');
    }

    // 为登录按钮添加点击事件监听器
    if (loginButton) {
        loginButton.addEventListener('click', handleLogin);
        console.log('Added click event listener to login button');
    }

    // 为输入框添加事件监听器
    if (emailInput) {
        emailInput.addEventListener('input', clearError);
        console.log('Added input event listener to email field');
    }
    if (passwordInput) {
        passwordInput.addEventListener('input', clearError);
        console.log('Added input event listener to password field');
    }
}); 