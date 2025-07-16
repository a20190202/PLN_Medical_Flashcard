"use client";

import { useState } from "react";
import { Plus, Trash2, X, Check } from "lucide-react";
import { Button } from "../core/Button";
import { LogoHorizontal } from "../core/LogoHorizontal";

interface Chat {
  id: string;
  title: string;
  createdAt: Date;
}

interface SidebarProps {
  onChatSelect?: (chatId: string) => void;
  onNewChat?: (newChatId?: string) => void;
  activeChatId?: string;
  chats: Chat[];
  onChatsChange: (chats: Chat[]) => void;
}

export default function Sidebar({ onChatSelect, onNewChat, activeChatId, chats, onChatsChange }: SidebarProps) {
  const [chatToDelete, setChatToDelete] = useState<string | null>(null);

  const handleNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: `Nuevo chat ${chats.length + 1}`,
      createdAt: new Date()
    };
    
    const updatedChats = [newChat, ...chats];
    onChatsChange(updatedChats);
    onNewChat?.(newChat.id);
  };

  const handleDeleteClick = (chatId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    setChatToDelete(chatId);
  };

  const confirmDelete = () => {
    if (!chatToDelete) return;
    
    const updatedChats = chats.filter(chat => chat.id !== chatToDelete);
    onChatsChange(updatedChats);
    
    // Si el chat eliminado era el activo, seleccionar otro o crear uno nuevo
    if (chatToDelete === activeChatId) {
      if (updatedChats.length > 0) {
        onChatSelect?.(updatedChats[0].id);
      } else {
        onNewChat?.();
      }
    }
    
    setChatToDelete(null);
  };

  const cancelDelete = () => {
    setChatToDelete(null);
  };

  const handleChatSelect = (chatId: string) => {
    // Cancelar eliminación si está activa
    if (chatToDelete) {
      setChatToDelete(null);
      return;
    }
    onChatSelect?.(chatId);
  };

  return (
    <div className="flex flex-col justify-between bg-sidebar shadow-lg px-6 py-6 w-[350px] rounded-2xl h-full">
      <div className="flex flex-col gap-2">
        {/* Botón New Chat */}
        <Button 
          onClick={handleNewChat}
          className="w-full flex justify-start items-center gap-3 px-3 py-2 bg-white/10 border/10 hover:bg-sidebar-accent hover:text-white text-white" 
          variant="outline"
        >
          <Plus className="size-5" />
          <span>New Chat</span>
        </Button>

        {/* Lista de chats */}
        <div className="flex flex-col gap-1 mt-4 max-h-[calc(100vh-300px)] overflow-y-auto">
          {chats.map((chat) => (
            <div key={chat.id} className="relative">
              <div 
                className={`group flex items-center justify-between w-full px-3 py-2 rounded-md transition-colors cursor-pointer ${
                  activeChatId === chat.id 
                    ? 'bg-sidebar-accent text-white' 
                    : 'hover:bg-white/10 text-white/80 hover:text-white'
                } ${chatToDelete === chat.id ? 'opacity-50' : ''}`}
                onClick={() => handleChatSelect(chat.id)}
              >
                <span className="flex-1 text-sm truncate text-left">
                  {chat.title}
                </span>
                
                {chatToDelete !== chat.id && (
                  <Button
                    onClick={(e) => handleDeleteClick(chat.id, e)}
                    className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0 hover:bg-red-500/20 hover:text-red-400 transition-all"
                    variant="ghost"
                    size="sm"
                  >
                    <Trash2 className="size-4" />
                  </Button>
                )}
              </div>

              {/* Modal de confirmación */}
              {chatToDelete === chat.id && (
                <div className="absolute top-0 left-0 right-0 bg-red-900/90 backdrop-blur-sm rounded-md p-3 z-10 border border-red-500/30">
                  <div className="text-xs text-white mb-2 text-center">
                    Are you sure to delete {chat.title.length > 20 ? chat.title.substring(0, 20) + '...' : chat.title}?
                  </div>
                  <div className="flex justify-center gap-2">
                    <Button
                      onClick={confirmDelete}
                      size="sm"
                      className="h-6 px-2 bg-red-600 hover:bg-red-700 text-white text-xs"
                    >
                      <Check className="size-3 mr-1" />
                      Yes
                    </Button>
                    <Button
                      onClick={cancelDelete}
                      size="sm"
                      variant="outline"
                      className="h-6 px-2 bg-gray-700 border-white/30 text-white hover:bg-white/10 text-xs"
                    >
                      <X className="size-3 mr-1" />
                      No
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Mensaje cuando no hay chats */}
        {chats.length === 0 && (
          <div className="text-white/60 text-sm text-center py-8">
            No hay chats disponibles.
            <br />
            Crea uno nuevo para comenzar.
          </div>
        )}
      </div>

      <LogoHorizontal />
    </div>
  );
}
