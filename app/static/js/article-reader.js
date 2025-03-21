// 文章页面脚本
document.addEventListener('DOMContentLoaded', function () {
    // 初始化文章页面
    initializeArticlePage();
});

function initializeArticlePage() {
    // 处理代码块高亮
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
    });

    // 处理图片点击放大
    document.querySelectorAll('.article-content img').forEach(img => {
        img.addEventListener('click', function () {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-body">
                            <img src="${this.src}" class="img-fluid">
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();
            modal.addEventListener('hidden.bs.modal', function () {
                modal.remove();
            });
        });
        img.style.cursor = 'pointer';
    });

    // 添加目录导航（如果文章有标题）
    const headings = document.querySelectorAll('.article-content h2, .article-content h3');
    if (headings.length > 0) {
        const toc = document.createElement('div');
        toc.className = 'article-toc';
        toc.innerHTML = '<h4>目录</h4><nav class="toc-nav"></nav>';

        const tocNav = toc.querySelector('.toc-nav');
        headings.forEach((heading, index) => {
            const id = `heading-${index}`;
            heading.id = id;
            const link = document.createElement('a');
            link.href = `#${id}`;
            link.textContent = heading.textContent;
            link.className = heading.tagName === 'H2' ? 'toc-h2' : 'toc-h3';
            tocNav.appendChild(link);
        });

        document.querySelector('.article-content').insertAdjacentElement('beforebegin', toc);
    }
} 