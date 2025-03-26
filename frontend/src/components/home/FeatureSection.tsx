'use client'

import { motion } from 'framer-motion'

const features = [
    {
        icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7h6V5a3 3 0 0 0-3-3Z" />
                <path d="M19 9h2a2 2 0 0 1 2 2v1a2 2 0 0 1-2 2h-2" />
                <path d="M5 9H3a2 2 0 0 0-2 2v1a2 2 0 0 0 2 2h2" />
                <path d="M12 19c-2.8 0-5-2.2-5-5v-3h10v3c0 2.8-2.2 5-5 5Z" />
            </svg>
        ),
        title: 'AI 辅助写作',
        description: '集成多种 AI 模型，提供智能写作建议、自动润色和内容优化，让创作更加高效。'
    },
    {
        icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3Z" />
            </svg>
        ),
        title: 'Markdown 编辑器',
        description: '支持实时预览的 Markdown 编辑器，内置多种主题和快捷键，让写作体验更加流畅。'
    },
    {
        icon: (
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3m9 9a9 9 0 0 1-9-9m9 9c1.66 0 3-4.03 3-9s-1.34-9-3-9m0 18c-1.66 0-3-4.03-3-9s1.34-9 3-9m-9 9a9 9 0 0 1 9-9" />
            </svg>
        ),
        title: '多平台发布',
        description: '一键发布到主流内容平台，支持自定义发布规则和内容格式，让分发更加便捷。'
    }
]

export function FeatureSection() {
    return (
        <section id="features" className="relative w-full overflow-hidden bg-white dark:bg-gray-900">
            <div className="max-w-[85rem] px-4 py-8 sm:px-6 lg:px-8 mx-auto">
                {/* 标题 */}
                <motion.div
                    className="max-w-2xl mx-auto text-center mb-16"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
                >
                    <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl dark:text-white">
                        专注于<span className="text-primary-600">创作体验</span>
                    </h2>
                    <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
                        简单易用的工具，让你的创作更加高效
                    </p>
                </motion.div>

                {/* 特性列表 */}
                <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            className="relative group"
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.6, delay: index * 0.1, ease: [0.23, 1, 0.32, 1] }}
                        >
                            <div className="relative z-10 p-8 bg-gray-50 border border-gray-200 rounded-2xl transition-all duration-200 dark:bg-gray-800 dark:border-gray-700 hover:shadow-lg dark:hover:shadow-gray-800/50">
                                <div className="inline-flex items-center justify-center w-10 h-10 mb-6 bg-primary-100 rounded-lg text-primary-600 dark:bg-primary-900/30 dark:text-primary-400">
                                    {feature.icon}
                                </div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-3 dark:text-white">
                                    {feature.title}
                                </h3>
                                <p className="text-gray-600 dark:text-gray-400">
                                    {feature.description}
                                </p>
                            </div>
                            {/* 装饰性背景 */}
                            <div className="absolute -inset-px bg-gradient-to-r from-primary-500/0 via-primary-500/10 to-primary-500/0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* 装饰性背景元素 */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gray-200 dark:via-gray-700 to-transparent" />
            <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gray-200 dark:via-gray-700 to-transparent" />
        </section>
    )
}
