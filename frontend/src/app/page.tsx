import type { Metadata } from 'next'
import { HeroSection } from '@/components/home/HeroSection'
import { FeatureSection } from '@/components/home/FeatureSection'
import { CTASection } from '@/components/home/CTASection'

export const metadata: Metadata = {
  title: 'GenFlow - 智能内容创作平台',
  description: '使用 GenFlow 进行智能内容创作，集成 AI 辅助写作、Markdown 编辑器和多平台发布功能。',
}

export default function Home() {
  return (
    <>
      <HeroSection />
      <FeatureSection />
      <CTASection />
    </>
  )
}
