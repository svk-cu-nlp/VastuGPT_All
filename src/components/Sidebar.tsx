import React from 'react';
import { MessageSquare, Plus, Settings } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface Chat {
  id: string;
  title: string;
  preview: string;
  timestamp: Date;
}

interface SidebarProps {
  chats: Chat[];
  activeChat: string | null;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  isDark: boolean;
  onToggleTheme: () => void;
}

export function Sidebar({ 
  chats, 
  activeChat, 
  onSelectChat, 
  onNewChat,
  isDark,
  onToggleTheme 
}: SidebarProps) {
  return (
    <div className="w-80 flex flex-col h-full border-r bg-gray-50 dark:bg-gray-900 dark:border-gray-800">
      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-4 py-3 text-sm font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {chats.map((chat) => (
          <button
            key={chat.id}
            onClick={() => onSelectChat(chat.id)}
            className={`w-full flex flex-col gap-1 p-4 text-left hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${
              activeChat === chat.id ? 'bg-gray-100 dark:bg-gray-800' : ''
            }`}
          >
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              <span className="font-medium text-sm truncate dark:text-gray-200">{chat.title}</span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{chat.preview}</p>
          </button>
        ))}
      </div>

      <div className="p-4 border-t dark:border-gray-800 flex items-center justify-between">
        <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
          <Settings className="w-4 h-4" />
          Settings
        </button>
        <ThemeToggle isDark={isDark} onToggle={onToggleTheme} />
      </div>
    </div>
  );
}