'use client'

import Link from 'next/link'
import { useState, useEffect, useRef } from 'react'
import { ThemeToggle } from '@/components/theme/ThemeToggle'
import { useAuth } from '@/lib/auth/AuthContext'

const navigation = [
    { name: '首页', href: '/' },
    { name: '功能', href: '#features' },
]

const userNavigation = [
    { name: '仪表盘', href: '/user/dashboard' },
]

const adminNavigation = [
    { name: '管理后台', href: '/admin/dashboard' },
]

export function Header() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
    const [isVisible, setIsVisible] = useState(true)
    const { isAuthenticated, user, logout, loading } = useAuth()
    const [isDropdownOpen, setIsDropdownOpen] = useState(false)
    const dropdownRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        let lastScrollY = window.scrollY
        let ticking = false

        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const currentScrollY = window.scrollY
                    const scrollingDown = currentScrollY > lastScrollY
                    const scrollDelta = Math.abs(currentScrollY - lastScrollY)

                    // 只有滚动距离超过 5px 时才触发状态更新
                    if (scrollDelta > 5) {
                        setIsVisible(!scrollingDown || currentScrollY < 10)
                        lastScrollY = currentScrollY
                    }

                    ticking = false
                })
                ticking = true
            }
        }

        window.addEventListener('scroll', handleScroll, { passive: true })
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    // 根据用户角色选择导航项
    const roleNavigation = user?.role === 'admin'
        ? adminNavigation
        : userNavigation;

    // 如果用户已登录，显示角色特定的导航项
    const navItems = isAuthenticated ? roleNavigation : navigation;

    const handleLogout = () => {
        logout()
        setIsDropdownOpen(false)
    }

    return (
        <header className={`fixed top-0 inset-x-0 z-50 transition-transform duration-300 ease-in-out ${isVisible ? 'translate-y-0' : '-translate-y-full'
            }`}>
            {/* 毛玻璃效果背景 */}
            <div className="absolute inset-0 bg-gradient-to-b from-white/80 to-gray-50/90 dark:from-gray-900/90 dark:to-gray-800/80 backdrop-blur-sm border-b border-gray-200/60 dark:border-gray-700/40"></div>

            {/* 内容区域 */}
            <div className="relative">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center justify-between">
                        {/* Logo */}
                        <div className="flex items-center">
                            <Link
                                href="/"
                                className="text-xl font-semibold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent"
                            >
                                GenFlow
                            </Link>
                        </div>

                        {/* 右侧菜单 */}
                        <div className="flex items-center gap-4">
                            {/* 暗色模式切换 */}
                            <ThemeToggle />

                            {/* 用户菜单 */}
                            {!loading && (
                                <>
                                    {isAuthenticated && user ? (
                                        <div className="relative" ref={dropdownRef}>
                                            <button
                                                type="button"
                                                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                                className="flex items-center gap-2 p-1.5 text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
                                            >
                                                <span className="relative flex h-8 w-8 shrink-0 overflow-hidden rounded-full">
                                                    <span className="flex h-full w-full items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
                                                        {user.email?.charAt(0).toUpperCase()}
                                                    </span>
                                                </span>
                                                <span className="hidden md:inline-block">{user.email}</span>
                                            </button>

                                            {/* 下拉菜单 */}
                                            {isDropdownOpen && (
                                                <div className="absolute right-0 mt-2 w-48 origin-top-right rounded-md bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-gray-200/60 dark:border-gray-700/40 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                                                    <div className="py-1">
                                                        <Link
                                                            href="/user/profile"
                                                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100/60 dark:hover:bg-gray-700/60"
                                                        >
                                                            个人信息
                                                        </Link>
                                                        <button
                                                            onClick={handleLogout}
                                                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100/60 dark:hover:bg-gray-700/60"
                                                        >
                                                            退出登录
                                                        </button>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-2">
                                            <Link
                                                href="/login"
                                                className="inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
                                            >
                                                登录
                                            </Link>
                                            <Link
                                                href="/register"
                                                className="inline-flex items-center justify-center px-4 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md shadow-sm transition-colors"
                                            >
                                                注册
                                            </Link>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </header>
    )
} 