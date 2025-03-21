import React, { useState, useEffect } from 'react';
import { ThemeProvider } from 'styled-components';
import { MdEditor } from '../../../integrations/md-editor/src';
import { defaultTheme } from '../../../integrations/md-editor/src/theme';
import { useAutoSave } from './hooks';
import './style.css';

const Editor = ({ 
  initialContent = '', 
  onSave, 
  autoSaveInterval = 30000  // 30 seconds
}) => {
  const [content, setContent] = useState(initialContent);
  const [theme, setTheme] = useState(defaultTheme);

  // 自动保存功能
  useAutoSave(content, onSave, autoSaveInterval);

  // 内容变更处理
  const handleContentChange = (newContent) => {
    setContent(newContent);
  };

  // 主题切换
  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <div className="genflow-editor-container">
      <div className="editor-toolbar">
        <button onClick={toggleTheme}>
          切换主题
        </button>
        <button onClick={() => onSave(content)}>
          保存
        </button>
      </div>
      
      <ThemeProvider theme={theme}>
        <MdEditor
          value={content}
          onChange={handleContentChange}
          theme={theme}
        />
      </ThemeProvider>
    </div>
  );
};

export default Editor;