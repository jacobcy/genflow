/**
 * 管理员设置功能
 */

// 初始化设置页面
function initializeSettings() {
    // 绑定数据库设置表单提交事件
    const dbSettingsForm = document.getElementById('dbSettingsForm');
    if (dbSettingsForm) {
        dbSettingsForm.addEventListener('submit', function (e) {
            e.preventDefault();
            updateDatabaseSettings();
        });
    }

    // 绑定系统设置表单提交事件
    const systemSettingsForm = document.getElementById('systemSettingsForm');
    if (systemSettingsForm) {
        systemSettingsForm.addEventListener('submit', function (e) {
            e.preventDefault();
            updateSystemSettings();
        });
    }

    // 加载当前设置
    loadCurrentSettings();
}

// 加载当前设置
function loadCurrentSettings() {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        showError('认证失败：请重新登录');
        return;
    }

    fetch('/api/admin/settings', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    localStorage.removeItem('jwt_token');
                    throw new Error('认证已过期，请重新登录');
                }
                return response.json().then(err => {
                    throw new Error(err.error || err.message || '获取设置失败');
                });
            }
            return response.json();
        })
        .then(data => {
            // 填充数据库设置
            if (data.database) {
                document.getElementById('dbPath').value = data.database.path || '';
                document.getElementById('dbBackupPath').value = data.database.backup_path || '';
            }

            // 填充系统设置
            if (data.system) {
                document.getElementById('siteName').value = data.system.site_name || '';
                document.getElementById('siteDescription').value = data.system.site_description || '';
                document.getElementById('allowRegistration').checked = data.system.allow_registration || false;
            }
        })
        .catch(error => {
            console.error('加载设置失败:', error);
            showError(error.message);
        });
}

// 更新数据库设置
function updateDatabaseSettings() {
    const dbPath = document.getElementById('dbPath').value;
    const dbBackupPath = document.getElementById('dbBackupPath').value;
    const messageContainer = document.getElementById('dbSettingsMessage');

    // 显示加载状态
    const submitButton = document.querySelector('#dbSettingsForm button[type="submit"]');
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 保存中...';

    const token = localStorage.getItem('jwt_token');

    fetch('/api/admin/settings/database', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            path: dbPath,
            backup_path: dbBackupPath
        })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.message || err.error || '更新数据库设置失败');
                });
            }
            return response.json();
        })
        .then(data => {
            messageContainer.innerHTML = `
            <div class="alert alert-success mt-3">
                数据库设置更新成功!
            </div>
        `;

            // 3秒后清除成功消息
            setTimeout(() => {
                messageContainer.innerHTML = '';
            }, 3000);
        })
        .catch(error => {
            console.error('更新数据库设置失败:', error);
            messageContainer.innerHTML = `
            <div class="alert alert-danger mt-3">
                更新失败: ${error.message}
            </div>
        `;
        })
        .finally(() => {
            // 恢复按钮状态
            submitButton.disabled = false;
            submitButton.innerHTML = '保存设置';
        });
}

// 更新系统设置
function updateSystemSettings() {
    const siteName = document.getElementById('siteName').value;
    const siteDescription = document.getElementById('siteDescription').value;
    const allowRegistration = document.getElementById('allowRegistration').checked;
    const messageContainer = document.getElementById('systemSettingsMessage');

    // 显示加载状态
    const submitButton = document.querySelector('#systemSettingsForm button[type="submit"]');
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 保存中...';

    const token = localStorage.getItem('jwt_token');

    fetch('/api/admin/settings/system', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            site_name: siteName,
            site_description: siteDescription,
            allow_registration: allowRegistration
        })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.message || err.error || '更新系统设置失败');
                });
            }
            return response.json();
        })
        .then(data => {
            messageContainer.innerHTML = `
            <div class="alert alert-success mt-3">
                系统设置更新成功!
            </div>
        `;

            // 3秒后清除成功消息
            setTimeout(() => {
                messageContainer.innerHTML = '';
            }, 3000);
        })
        .catch(error => {
            console.error('更新系统设置失败:', error);
            messageContainer.innerHTML = `
            <div class="alert alert-danger mt-3">
                更新失败: ${error.message}
            </div>
        `;
        })
        .finally(() => {
            // 恢复按钮状态
            submitButton.disabled = false;
            submitButton.innerHTML = '保存设置';
        });
}

// 显示错误消息
function showError(message) {
    const containers = [
        document.getElementById('dbSettingsMessage'),
        document.getElementById('systemSettingsMessage')
    ];

    containers.forEach(container => {
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger mt-3">
                    ${message}
                </div>
            `;
        }
    });
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', initializeSettings); 