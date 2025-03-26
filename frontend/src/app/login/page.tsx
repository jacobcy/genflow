import type { Metadata } from 'next'
import LoginForm from './LoginForm'

export const metadata: Metadata = {
  title: 'GenFlow - 登录',
  description: '登录 GenFlow 智能内容创作平台',
}

export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-900">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
            登录 GenFlow
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            智能内容创作平台
          </p>
        </div>

        <LoginForm />
      </div>
    </div>
  )
}
