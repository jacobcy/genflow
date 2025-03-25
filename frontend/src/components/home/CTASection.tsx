'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'

export function CTASection() {
    return (
        <section className="relative w-full overflow-hidden bg-white dark:bg-gray-900">
            <div className="max-w-[85rem] px-4 py-16 sm:px-6 lg:px-8 lg:py-20 mx-auto">
                <motion.div
                    className="relative z-10 max-w-2xl mx-auto text-center"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, ease: [0.23, 1, 0.32, 1] }}
                >
                    <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white mb-6">
                        准备好开始创作了吗？
                    </h2>
                    <Link
                        href="/editor"
                        className="group inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-semibold text-white bg-primary-600 hover:bg-primary-500 rounded-lg transition-all duration-200 dark:bg-primary-600 dark:hover:bg-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
                    >
                        <span>开始创作</span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3Z" />
                        </svg>
                    </Link>
                </motion.div>
            </div>

            {/* 装饰性背景元素 */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gray-200 dark:via-gray-700 to-transparent" />
        </section>
    )
} 