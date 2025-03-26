'use client'

import { ThemeProvider as NextThemesProvider } from 'next-themes'
import { ReactNode } from 'react'

// 使用正确的类型定义
type DataAttribute = `data-${string}`;
type Attribute = DataAttribute | 'class';

interface ThemeProviderProps {
    children: ReactNode;
    /** List of all available theme names */
    themes?: string[];
    /** Forced theme name for the current page */
    forcedTheme?: string;
    /** Whether to switch between dark and light themes based on prefers-color-scheme */
    enableSystem?: boolean;
    /** Disable all CSS transitions when switching themes */
    disableTransitionOnChange?: boolean;
    /** Whether to indicate to browsers which color scheme is used (dark or light) for built-in UI */
    enableColorScheme?: boolean;
    /** Key used to store theme setting in localStorage */
    storageKey?: string;
    /** Default theme name */
    defaultTheme?: string;
    /** HTML attribute modified based on the active theme */
    attribute?: Attribute | Attribute[];
}

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
    return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
