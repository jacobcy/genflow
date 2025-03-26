'use client';

import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';

export default function NotFound() {
  const router = useRouter();

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-white dark:bg-gray-900 px-4 py-16 sm:px-6 sm:py-24 md:grid md:place-items-center lg:px-8">
      <div className="max-w-max mx-auto">
        <main className="sm:flex">
          <div className="relative sm:mr-10">
            <div className="absolute inset-0 bg-gradient-to-r from-primary-400 to-primary-600 shadow-lg transform skew-y-0 -rotate-6 rounded-3xl opacity-50 sm:opacity-80"></div>
            <p className="relative text-8xl font-extrabold text-white tracking-wide sm:text-9xl py-8 px-10">
              404
            </p>
          </div>

          <div className="mt-6 sm:mt-0 sm:ml-6 flex flex-col justify-center">
            <div>
              <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight sm:text-4xl">
                页面未找到
              </h1>
              <p className="mt-3 text-base text-gray-500 dark:text-gray-400 max-w-md">
                抱歉，您访问的页面不存在或已被移除。请检查您输入的URL是否正确，或尝试返回首页。
              </p>
            </div>
            <div className="mt-8 flex space-x-3">
              <Link href="/"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-900 transition-colors">
                返回首页
              </Link>
              <button
                onClick={() => router.back()}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-900 transition-colors">
                返回上一页
              </button>
            </div>
          </div>
        </main>

        <div className="mt-20 flex justify-center">
          <div className="relative w-full max-w-lg">
            <div className="absolute top-0 -left-4 w-72 h-72 bg-primary-300 dark:bg-primary-700 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
            <div className="absolute top-0 -right-4 w-72 h-72 bg-yellow-300 dark:bg-yellow-700 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
            <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 dark:bg-pink-700 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
            <div className="relative">
              <div className="p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg dark:shadow-xl">
                <h3 className="text-lg font-medium text-gray-800 dark:text-gray-200 mb-2">找不到您要找的内容？</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">您可以尝试以下方式：</p>
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li className="flex items-center">
                    <span className="mr-2 text-primary-500">•</span>
                    检查URL是否输入正确
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2 text-primary-500">•</span>
                    使用网站导航查找内容
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2 text-primary-500">•</span>
                    联系我们寻求帮助
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
