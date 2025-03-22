// AI 功能模块
const AIFeatures = {
    // AI 助手状态
    state: {
        isProcessing: false,
        context: []
    },

    // 初始化 AI 功能
    init() {
        this.bindEvents();
    },

    // 绑定事件
    bindEvents() {
        const aiInput = document.querySelector('#aiInput');
        const aiSubmit = document.querySelector('#aiSubmit');

        if (aiInput && aiSubmit) {
            aiSubmit.addEventListener('click', () => this.handleAIRequest(aiInput.value));
            aiInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleAIRequest(aiInput.value);
                }
            });
        }
    },

    // 处理 AI 请求
    async handleAIRequest(prompt) {
        if (this.state.isProcessing || !prompt.trim()) return;

        try {
            this.state.isProcessing = true;
            this.updateUIState('processing');

            const response = await this.sendAIRequest(prompt);
            this.handleAIResponse(response);

        } catch (error) {
            console.error('AI 请求失败:', error);
            this.showError('AI 服务暂时不可用，请稍后重试');
        } finally {
            this.state.isProcessing = false;
            this.updateUIState('idle');
        }
    },

    // 发送 AI 请求到服务器
    async sendAIRequest(prompt) {
        const response = await fetch('/api/ai/assist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt,
                context: this.state.context
            })
        });

        if (!response.ok) {
            throw new Error('AI 服务响应错误');
        }

        return response.json();
    },

    // 处理 AI 响应
    handleAIResponse(response) {
        // 更新上下文
        this.state.context.push({
            role: 'user',
            content: response.prompt
        }, {
            role: 'assistant',
            content: response.response
        });

        // 显示响应
        this.displayAIResponse(response);

        // 清空输入
        const aiInput = document.querySelector('#aiInput');
        if (aiInput) {
            aiInput.value = '';
        }
    },

    // 显示 AI 响应
    displayAIResponse(response) {
        const aiContent = document.querySelector('#aiContent');
        if (!aiContent) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = 'ai-message';
        messageDiv.innerHTML = `
            <div class="ai-message-content">
                ${marked.parse(response.response)}
            </div>
            <div class="ai-message-actions">
                <button class="btn btn-sm btn-outline-primary" onclick="AIFeatures.applyToEditor(this)">
                    应用到编辑器
                </button>
            </div>
        `;

        aiContent.appendChild(messageDiv);
        aiContent.scrollTop = aiContent.scrollHeight;
    },

    // 将 AI 响应应用到编辑器
    applyToEditor(button) {
        const content = button.parentElement.previousElementSibling.textContent;
        if (window.editor) {
            window.editor.insertContent(content);
        }
    },

    // 更新 UI 状态
    updateUIState(state) {
        const aiSubmit = document.querySelector('#aiSubmit');
        if (!aiSubmit) return;

        if (state === 'processing') {
            aiSubmit.disabled = true;
            aiSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        } else {
            aiSubmit.disabled = false;
            aiSubmit.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
    },

    // 显示错误信息
    showError(message) {
        const aiContent = document.querySelector('#aiContent');
        if (!aiContent) return;

        const errorDiv = document.createElement('div');
        errorDiv.className = 'ai-message error';
        errorDiv.textContent = message;
        aiContent.appendChild(errorDiv);
        aiContent.scrollTop = aiContent.scrollHeight;
    }
};

// 初始化 AI 功能
document.addEventListener('DOMContentLoaded', () => {
    AIFeatures.init();
});