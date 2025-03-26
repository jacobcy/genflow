'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'

export function HeroSection() {
    return (
        <section className="relative w-full overflow-hidden bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20 md:pt-24 lg:pt-32 pb-20">
            {/* 背景装饰 */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-1/4 -left-1/4 w-1/2 h-1/2 bg-gradient-to-br from-primary-500/20 to-transparent rounded-full blur-3xl" />
                <div className="absolute -bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-gradient-to-tl from-primary-500/20 to-transparent rounded-full blur-3xl" />
            </div>

            <div className="relative max-w-[85rem] mx-auto px-4 sm:px-6 lg:px-8">
                {/* 标题 */}
                <motion.div
                    className="max-w-3xl mx-auto text-center"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
                >
                    <span className="inline-flex items-center gap-2 px-3 py-1 text-sm font-medium text-primary-700 bg-primary-100/80 rounded-full dark:bg-primary-900/30 dark:text-primary-300 mb-6">
                        <span className="flex w-2 h-2 bg-primary-600 rounded-full animate-pulse"></span>
                        内部创作平台
                    </span>
                    <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl dark:text-white mb-8">
                        <span className="inline-block">智能创作，</span>{' '}
                        <span className="inline-block bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-primary-400">
                            从这里开始
                        </span>
                    </h1>
                    <p className="text-lg leading-relaxed text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
                        GenFlow 是一个现代化的内容创作平台，集成了 AI 辅助写作、Markdown 编辑器和多平台发布功能，让创作变得更加轻松高效。
                    </p>
                </motion.div>

                {/* 按钮组 */}
                <motion.div
                    className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-8"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2, ease: [0.23, 1, 0.32, 1] }}
                >
                    <Link
                        href="/editor"
                        className="group inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-semibold text-white bg-primary-600 hover:bg-primary-500 rounded-lg transition-all duration-200 dark:bg-primary-600 dark:hover:bg-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                    >
                        <span>开始创作</span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3Z" />
                        </svg>
                    </Link>
                    <Link
                        href="#features"
                        className="group inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-semibold text-gray-700 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg transition-all duration-200 dark:bg-gray-800 dark:hover:bg-gray-700 dark:border-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-200 focus:ring-offset-2 dark:focus:ring-gray-700 dark:focus:ring-offset-gray-900"
                    >
                        <span>了解更多</span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="m9 18 6-6-6-6" />
                        </svg>
                    </Link>
                </motion.div>
            </div>
        </section>
    )
}
