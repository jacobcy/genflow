import React from 'react';
import Editor from '../Editor';

const ArticleEditor = ({ article, onSave }) => {
  const handleSave = async (content) => {
    try {
      // 这里可以调用后端 API 保存文章
      await onSave({
        ...article,
        content
      });
    } catch (error) {
      console.error('保存失败:', error);
      // 这里可以添加错误提示
    }
  };

  return (
    <div style={{ height: '100vh' }}>
      <Editor
        initialContent={article?.content || ''}
        onSave={handleSave}
        autoSaveInterval={30000} // 30秒自动保存
      />
    </div>
  );
};

export default ArticleEditor;