import React from 'react';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { Sidebar } from './components/Sidebar';
import { useTheme } from './hooks/useTheme';
import { useChat } from './hooks/useChat';

// Sample data for sidebar
const initialChats = [
  {
    id: '1',
    title: 'Website Development',
    preview: 'How do I create a responsive layout?',
    timestamp: new Date(),
  },
  {
    id: '2',
    title: 'React Hooks',
    preview: 'Can you explain useEffect?',
    timestamp: new Date(),
  },
];

function App() {
  const [activeChat, setActiveChat] = React.useState<string | null>('1');
  const { isDark, toggleTheme } = useTheme();
  const { messages, isLoading, error, sendMessage } = useChat();

  return (
    <div className="flex h-screen bg-white dark:bg-gray-900">
      <Sidebar
        chats={initialChats}
        activeChat={activeChat}
        onSelectChat={setActiveChat}
        onNewChat={() => {
          console.log('New chat');
        }}
        isDark={isDark}
        onToggleTheme={toggleTheme}
      />

      <main className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto">
          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500">
              <p className="text-red-700 dark:text-red-400">{error}</p>
            </div>
          )}
          
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="p-6">
              <div className="flex gap-2 items-center text-gray-500 dark:text-gray-400">
                <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-600 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-600 animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-600 animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          )}
        </div>

        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </main>
    </div>
  );
}

export default App;