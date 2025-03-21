import { useEffect, useRef } from 'react';

export const useAutoSave = (content, onSave, interval) => {
  const savedContent = useRef(content);

  useEffect(() => {
    // 只在内容变化时保存
    if (content !== savedContent.current) {
      const timer = setTimeout(() => {
        onSave(content);
        savedContent.current = content;
      }, interval);

      return () => clearTimeout(timer);
    }
  }, [content, onSave, interval]);
};