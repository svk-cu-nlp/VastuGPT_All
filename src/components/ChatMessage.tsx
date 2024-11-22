import React from 'react';
import { Bot, User } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 p-6 ${
      isUser 
        ? 'bg-white dark:bg-gray-900' 
        : 'bg-gray-50 dark:bg-gray-800'
    }`}>
      <div className="flex-shrink-0">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-blue-100 dark:bg-blue-900' 
            : 'bg-emerald-100 dark:bg-emerald-900'
        }`}>
          {isUser ? (
            <User className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          ) : (
            <Bot className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          )}
        </div>
      </div>
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm text-gray-900 dark:text-gray-100">
            {isUser ? 'You' : 'Assistant'}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
        <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{message.content}</p>
      </div>
    </div>
  );
}