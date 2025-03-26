/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    output: 'standalone',
    trailingSlash: true,
    poweredByHeader: false,
    webpack: (config, { isServer }) => {
        // 强制解析node_modules中的依赖
        config.resolve.fallback = {
            ...config.resolve.fallback,
            fs: false,
            net: false,
            tls: false,
            dns: false,
        };

        // 为 Preline 添加TypeScript处理
        config.module.rules.push({
            test: /\.ts$/,
            include: /node_modules\/preline/,
            use: [
                {
                    loader: 'ts-loader',
                    options: {
                        transpileOnly: true,
                        compilerOptions: {
                            module: 'esnext',
                        },
                    },
                },
            ],
        });

        // 优化chunk加载
        if (!isServer) {
            config.optimization.splitChunks = {
                chunks: 'all',
                cacheGroups: {
                    default: false,
                    vendors: false,
                    commons: {
                        name: 'commons',
                        chunks: 'all',
                        minChunks: 2,
                    },
                    // 为react相关库创建单独的chunk
                    react: {
                        name: 'react',
                        chunks: 'all',
                        test: /[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/,
                        priority: 20,
                    },
                },
            };
        }

        return config;
    },
    // 忽略构建错误，允许应用继续启动
    typescript: {
        ignoreBuildErrors: true,
    },
    eslint: {
        ignoreDuringBuilds: true,
    },
};

module.exports = nextConfig;
