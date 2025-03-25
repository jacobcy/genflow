/**
 * 管理员仪表盘功能
 */

// 初始化仪表盘
function initializeDashboard() {
    // 加载用户列表
    loadUserList();

    // 添加用户表单提交处理
    const addUserForm = document.getElementById('addUserForm');
    if (addUserForm) {
        addUserForm.addEventListener('submit', function (e) {
            e.preventDefault();
            addNewUser();
        });
    }
}

// 加载用户列表
function loadUserList() {
    console.log('正在加载用户列表...');

    const tableBody = document.getElementById('userTableBody');
    if (!tableBody) return;

    // 显示加载状态
    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center">
                <div class="admin-loading"></div>
                <span>正在加载用户数据...</span>
            </td>
        </tr>
    `;

    fetch('/api/auth/admin/users', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'  // 包含 cookies
    })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    // 认证失败或无权限，重定向到登录页面
                    window.location.href = '/admin/login';
                    throw new Error('认证已过期或无权限，请重新登录');
                }
                return response.json().then(err => {
                    throw new Error(err.error || err.message || '获取用户列表失败');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('获取到的用户列表:', data);
            if (!data.users || !Array.isArray(data.users)) {
                throw new Error('无效的用户数据');
            }
            renderUserTable(data.users);
        })
        .catch(error => {
            console.error('获取用户列表失败:', error);
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-danger">
                            ${error.message}
                        </td>
                    </tr>
                `;
            }
        });
}

// 渲染用户表格
function renderUserTable(users) {
    const tableBody = document.getElementById('userTableBody');

    if (!users || users.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">暂无用户数据</td>
            </tr>
        `;
        return;
    }

    const rows = users.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td><span class="badge ${user.role === 'admin' ? 'bg-danger' : 'bg-secondary'}">${user.role}</span></td>
            <td>${new Date(user.created_at).toLocaleString()}</td>
            <td>
                ${user.role !== 'admin' ? `
                    <button class="admin-btn admin-btn-danger" onclick="deleteUser(${user.id})">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                ` : ''}
            </td>
        </tr>
    `).join('');

    tableBody.innerHTML = rows;
}

// 添加新用户
function addNewUser() {
    const username = document.getElementById('newUsername').value;
    const email = document.getElementById('newEmail').value;
    const password = document.getElementById('newPassword').value;
    const messageContainer = document.getElementById('addUserMessage');

    // 显示加载状态
    const addButton = document.querySelector('#addUserForm button[type="submit"]');
    addButton.disabled = true;
    addButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';

    fetch('/api/auth/admin/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',  // 包含 cookies
        body: JSON.stringify({
            username: username,
            email: email,
            password: password,
            role: 'user'  // 默认创建普通用户
        })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.message || err.error || '添加用户失败');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('添加用户成功:', data);

            // 显示成功消息
            messageContainer.innerHTML = `
            <div class="admin-alert admin-alert-success">
                用户 ${username} 添加成功!
            </div>
        `;

            // 清空表单
            document.getElementById('newUsername').value = '';
            document.getElementById('newEmail').value = '';
            document.getElementById('newPassword').value = '';

            // 重新加载用户列表
            loadUserList();

            // 3秒后清除成功消息
            setTimeout(() => {
                messageContainer.innerHTML = '';
            }, 3000);
        })
        .catch(error => {
            console.error('添加用户失败:', error);

            // 显示错误消息
            messageContainer.innerHTML = `
            <div class="admin-alert admin-alert-error">
                添加失败: ${error.message}
            </div>
        `;
        })
        .finally(() => {
            // 恢复按钮状态
            addButton.disabled = false;
            addButton.innerHTML = '<i class="fas fa-plus"></i> 添加';
        });
}

// 删除用户
function deleteUser(userId) {
    if (!confirm(`确定要删除ID为 ${userId} 的用户吗？此操作不可恢复!`)) {
        return;
    }

    fetch(`/api/auth/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'  // 包含 cookies
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.message || err.error || '删除用户失败');
                });
            }
            return response.json();
        })
        .then(() => {
            // 重新加载用户列表
            loadUserList();
        })
        .catch(error => {
            console.error('删除用户失败:', error);
            alert(`删除失败: ${error.message}`);
        });
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', initializeDashboard); 