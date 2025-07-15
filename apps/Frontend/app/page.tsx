"use client";

import { useState } from "react";
import Chatbox from "../components/chat/Chatbox";
import Sidebar from "../components/sidebar/Sidebar";
import Textbox from "../components/textbox/Textbox";

// Tipos para los mensajes
interface QAPair {
  title: string;
  question: string;
  answer: string;
}

interface BaseMessage {
  id: string;
  timestamp: Date;
}

interface UserMessageData extends BaseMessage {
  type: "user";
  content: string;
}

interface ModelMessageData extends BaseMessage {
  type: "model";
  mainAnswer: string;
  flashcards: QAPair[];
}

type Message = UserMessageData | ModelMessageData;

interface Chat {
  id: string;
  title: string;
  createdAt: Date;
}

export default function Home() {
  // Estado para los chats
  const [chats, setChats] = useState<Chat[]>([
    { id: "1", title: "New chat 1", createdAt: new Date() },
  ]);

  // Estado para los mensajes de cada chat
  const [chatMessages, setChatMessages] = useState<Record<string, Message[]>>({
    "1": [], // Mensajes del chat de hipertensión
    "2": [], // Mensajes del chat de diabetes
  });

  const [activeChatId, setActiveChatId] = useState<string | undefined>("1");

  // Obtener mensajes del chat activo
  const currentMessages = activeChatId ? chatMessages[activeChatId] || [] : [];

  const handleSend = async (message: string) => {
    if (!activeChatId) return;

    const userMessage: UserMessageData = {
      id: crypto.randomUUID(),
      type: "user",
      content: message,
      timestamp: new Date(),
    };

    // Variable para rastrear si es el primer mensaje
    const isFirstMessage =
      !chatMessages[activeChatId] || chatMessages[activeChatId].length === 0;

    // Agregar mensaje del usuario al chat actual
    setChatMessages((prev) => ({
      ...prev,
      [activeChatId]: [...(prev[activeChatId] || []), userMessage],
    }));

    // Actualizar título si es el primer mensaje
    if (isFirstMessage) {
      setChats((prevChats) =>
        prevChats.map((chat) =>
          chat.id === activeChatId
            ? {
                ...chat,
                title:
                  message.substring(0, 50) + (message.length > 50 ? "..." : ""),
              }
            : chat
        )
      );
    }
    
    let modelMessage: ModelMessageData 

    try {
      const response = await fetch("http://localhost:8000/generar_preguntas", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ texto: message }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from bot");
      }

      const data = await response.json();

      modelMessage = {
        id: crypto.randomUUID(),
        timestamp: new Date(),
        type: 'model',
        mainAnswer: data.flashcards ? `Generated ${data.flashcards.length} flashcards` : "Sorry, I didn't understand that.",
        flashcards: data.flashcards || [],
      };
    } catch (error) {
      modelMessage = {
          id: (Date.now() + 1).toString(),
          type: "model",
          mainAnswer: `Error: Unable to fetch response from the server. Code: "${error instanceof Error ? error.message : "Unknown error"}"`,
          flashcards: [],
          timestamp: new Date(),
        };
    } finally {
      setChatMessages((prev) => ({
        ...prev,
        [activeChatId]: [...(prev[activeChatId] || []), modelMessage],
      }));
    }
  };

  const handleChatSelect = (chatId: string) => {
    setActiveChatId(chatId);
  };

  const handleNewChat = (newChatId?: string) => {
    if (newChatId) {
      // Nuevo chat creado desde el sidebar
      setActiveChatId(newChatId);
      setChatMessages((prev) => ({
        ...prev,
        [newChatId]: [],
      }));
    } else {
      // Limpiar chat actual
      setActiveChatId(undefined);
    }
  };

  const handleChatsChange = (updatedChats: Chat[]) => {
    setChats(updatedChats);
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <div className="flex flex-row p-6 space-x-6 w-full">
        <Sidebar
          onChatSelect={handleChatSelect}
          onNewChat={handleNewChat}
          activeChatId={activeChatId}
          chats={chats}
          onChatsChange={handleChatsChange}
        />
        <div className="flex flex-col space-y-6 w-full rounded-2xl h-[calc(100dvh-3rem)]">
          <div className="flex-grow overflow-hidden">
            <Chatbox messages={currentMessages} />
          </div>
          <Textbox onSend={handleSend} />
        </div>
      </div>
    </div>
  );
}