import React from 'react';
import { ActionButton } from '@/types/ai-assistant';

interface ActionButtonsProps {
    actions: ActionButton[];
    onAction: (action: ActionButton) => void;
    isLoading?: boolean;
}

export default function ActionButtons({
    actions,
    onAction,
    isLoading = false
}: ActionButtonsProps) {
    const baseStyle = 'px-4 py-2 text-sm font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
    const buttonStyle = `${baseStyle} bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 dark:bg-primary-700 dark:hover:bg-primary-800`;

    const handleClick = (action: ActionButton) => {
        if (!isLoading) {
            // 如果需要确认，显示确认对话框
            if (action.metadata?.requiresConfirmation) {
                if (window.confirm('确定要执行此操作吗？')) {
                    onAction(action);
                }
            } else {
                onAction(action);
            }
        }
    };

    return (
        <div className="flex flex-wrap gap-2 p-4 border-t dark:border-gray-700">
            {actions.map((action) => (
                <button
                    key={action.id}
                    onClick={() => handleClick(action)}
                    disabled={isLoading}
                    className={buttonStyle}
                    title={action.description}
                >
                    {action.label}
                </button>
            ))}
        </div>
    );
}
