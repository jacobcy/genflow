'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/AuthContext';
import { createArticle, updateArticle } from '@/lib/api/articles';
import { toast } from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';

interface ArticleFormData {
  title: string;
  content: string;
  summary: string;
  tags: string[];
  coverImage?: string;
}

interface ArticleEditorProps {
  article?: any; // 编辑模式下传入的文章数据
}

export default function ArticleEditor({ article }: ArticleEditorProps) {
  const { user } = useAuth();
  const router = useRouter();

  const [formData, setFormData] = useState<ArticleFormData>({
    title: '',
    content: '',
    summary: '',
    tags: [],
    coverImage: '',
  });
  const [newTag, setNewTag] = useState('');
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [isPreviewMode, setIsPreviewMode] = useState(false);

  // 如果是编辑模式，加载现有文章数据
  useEffect(() => {
    if (article) {
      setFormData({
        title: article.title || '',
        content: article.content || '',
        summary: article.summary || '',
        tags: article.tags || [],
        coverImage: article.cover_image || article.coverImage || '',
      });
    }
  }, [article]);

  // 切换预览模式
  const togglePreview = () => {
    setIsPreviewMode(!isPreviewMode);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData((prev) => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()],
      }));
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData((prev) => ({
      ...prev,
      tags: prev.tags.filter((tag) => tag !== tagToRemove),
    }));
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData((prev) => ({
          ...prev,
          coverImage: reader.result as string,
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const validateForm = (): boolean => {
    if (!formData.title.trim()) {
      toast.error('请输入文章标题');
      return false;
    }
    if (!formData.content.trim()) {
      toast.error('请输入文章内容');
      return false;
    }
    return true;
  };

  const saveAsDraft = async () => {
    if (!validateForm()) return;

    setSaving(true);
    try {
      if (article) {
        // 更新现有文章
        await updateArticle(article.id, {
          ...formData,
          status: 'draft',
        });
        toast.success('草稿已保存');
      } else {
        // 创建新文章
        const newArticle = await createArticle({
          ...formData,
          status: 'draft',
        });
        router.push(`/user/articles/${newArticle.id}`);
        toast.success('草稿已保存');
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      toast.error('保存失败: ' + errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const publishArticle = async () => {
    if (!validateForm()) return;

    setPublishing(true);
    try {
      if (article) {
        // 更新并发布现有文章
        await updateArticle(article.id, {
          ...formData,
          status: 'published',
        });
        toast.success('文章已发布');
        router.push('/user/articles/published');
      } else {
        // 创建并发布新文章
        await createArticle({
          ...formData,
          status: 'published',
        });
        toast.success('文章已发布');
        router.push('/user/articles/published');
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      toast.error('发布失败: ' + errorMessage);
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="w-full" id="article-editor">
      {/* 中间文章编辑区域（画布） */}
      <div className="w-full">
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg border border-gray-200/60 dark:border-gray-700/40 shadow-sm">
          {!isPreviewMode ? (
            <>
              <div className="px-6 py-4">
                <input
                  type="text"
                  name="title"
                  id="title"
                  className="block w-full border-0 bg-transparent focus:ring-0 focus:border-primary-500 dark:text-white text-2xl font-medium placeholder-gray-400"
                  placeholder="文章标题"
                  value={formData.title}
                  onChange={handleInputChange}
                />
              </div>
              <div className="px-6 py-5">
                <div className="space-y-8">
                  {/* 正文区域 */}
                  <div>
                    <textarea
                      name="content"
                      id="content"
                      className="block w-full border-0 bg-transparent focus:ring-0 text-base dark:text-white placeholder-gray-400 min-h-[300px] resize-none"
                      placeholder="在这里编写文章内容..."
                      value={formData.content}
                      onChange={(e) => {
                        handleInputChange(e);
                        // 自动调整高度
                        e.target.style.height = 'auto';
                        e.target.style.height = e.target.scrollHeight + 'px';
                      }}
                      style={{ height: 'auto', minHeight: '300px' }}
                    />
                  </div>

                  {/* 分割线 */}
                  <div className="border-t border-gray-200/60 dark:border-gray-700/40"></div>

                  {/* 摘要区域 */}
                  <div>
                    <label htmlFor="summary" className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                      文章摘要
                    </label>
                    <div className="relative">
                      <textarea
                        name="summary"
                        id="summary"
                        className="block w-full rounded-lg border border-gray-200/60 dark:border-gray-700/40 bg-white/50 dark:bg-gray-800/50 px-4 py-3 focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 text-sm text-gray-600 dark:text-gray-300 placeholder-gray-400 leading-relaxed min-h-[80px] resize-none transition-colors"
                        placeholder="用简洁的语言描述文章的主要内容..."
                        value={formData.summary}
                        onChange={(e) => {
                          handleInputChange(e);
                          // 自动调整高度
                          e.target.style.height = 'auto';
                          e.target.style.height = e.target.scrollHeight + 'px';
                        }}
                        style={{ height: 'auto', minHeight: '80px' }}
                      />
                    </div>
                  </div>

                  {/* 标签区域 */}
                  <div>
                    <label htmlFor="tags" className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                      文章标签
                    </label>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {formData.tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center px-3 py-1 rounded-lg text-sm font-medium bg-primary-50 text-primary-700 dark:bg-primary-900/50 dark:text-primary-300 border border-primary-100/60 dark:border-primary-700/40 transition-colors"
                        >
                          {tag}
                          <button
                            type="button"
                            className="ml-1.5 inline-flex items-center justify-center h-4 w-4 rounded-full hover:bg-primary-100 dark:hover:bg-primary-800/60 focus:outline-none transition-colors"
                            onClick={() => handleRemoveTag(tag)}
                          >
                            <span className="sr-only">删除标签</span>
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleAddTag();
                          }
                        }}
                        placeholder="输入标签"
                        className="flex-1 rounded-lg border border-gray-200/60 dark:border-gray-700/40 bg-white/50 dark:bg-gray-800/50 px-4 py-2 text-sm text-gray-600 dark:text-gray-300 placeholder-gray-400 focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-colors"
                      />
                      <button
                        type="button"
                        onClick={handleAddTag}
                        className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900 transition-colors shadow-sm"
                      >
                        添加
                      </button>
                    </div>
                  </div>

                  {/* 封面图片区域 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                      封面图片
                    </label>
                    <div className="mt-1 relative group">
                      {formData.coverImage ? (
                        <div className="relative rounded-lg overflow-hidden bg-gray-50 dark:bg-gray-800/50 border border-gray-200/60 dark:border-gray-700/40 backdrop-blur-sm transition-colors">
                          <img
                            src={formData.coverImage}
                            alt="Cover"
                            className="w-full max-h-[240px] object-cover"
                          />
                          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <button
                              type="button"
                              onClick={() => setFormData((prev) => ({ ...prev, coverImage: '' }))}
                              className="p-2 rounded-lg bg-red-500/90 text-white hover:bg-red-600/90 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900 backdrop-blur-sm transition-colors"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </div>
                        </div>
                      ) : (
                        <label
                          htmlFor="cover-image"
                          className="flex flex-col items-center justify-center w-full h-[240px] rounded-lg border-2 border-dashed border-gray-200/60 dark:border-gray-700/40 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm cursor-pointer hover:bg-gray-50/80 dark:hover:bg-gray-750/50 transition-colors"
                        >
                          <div className="flex flex-col items-center justify-center pt-5 pb-6 px-4 text-center">
                            <svg className="w-12 h-12 text-gray-400 dark:text-gray-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <p className="mb-2 text-sm text-gray-600 dark:text-gray-400">
                              <span className="font-medium text-primary-600 dark:text-primary-500 hover:text-primary-700 dark:hover:text-primary-400">点击上传</span>
                              {" "}或拖放图片
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              支持 PNG、JPG、GIF 格式，最大 10MB
                            </p>
                          </div>
                          <input
                            id="cover-image"
                            name="cover-image"
                            type="file"
                            className="hidden"
                            accept="image/*"
                            onChange={handleImageUpload}
                          />
                        </label>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="px-6 py-4 prose dark:prose-invert max-w-none">
              <h1>{formData.title}</h1>
              <ReactMarkdown>{formData.content}</ReactMarkdown>
            </div>
          )}
        </div>
      </div>

      {/* 隐藏的按钮供父组件调用 */}
      <button
        data-action="save-draft"
        onClick={saveAsDraft}
        className="hidden"
      />
      <button
        data-action="publish"
        onClick={publishArticle}
        className="hidden"
      />
      <button
        data-action="toggle-preview"
        onClick={togglePreview}
        className="hidden"
      />
    </div>
  );
}
