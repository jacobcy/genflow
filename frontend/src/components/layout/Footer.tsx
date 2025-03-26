export function Footer() {
    return (
        <footer className="mt-auto pt-8 relative z-10">
            {/* 毛玻璃效果背景 */}
            <div className="absolute inset-0 bg-gradient-to-t from-gray-50/95 to-white/80 dark:from-gray-900/90 dark:to-gray-800/80 backdrop-blur-sm border-t border-gray-200/60 dark:border-gray-700/40"></div>

            {/* 内容区域 */}
            <div className="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        © {new Date().getFullYear()} GenFlow. All rights reserved.
                    </p>
                    <div className="flex items-center space-x-4">
                        <a
                            href="#"
                            className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                        >
                            隐私政策
                        </a>
                        <a
                            href="#"
                            className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                        >
                            使用条款
                        </a>
                        <a
                            href="#"
                            className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
                        >
                            联系我们
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    )
}
