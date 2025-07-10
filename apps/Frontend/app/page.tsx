"use client";

import { useState } from "react";
import Chatbox from "../components/chat/Chatbox";
import Sidebar from "../components/sidebar/Sidebar";
import Textbox from "../components/textbox/Textbox";

// Tipos para los mensajes
interface QAPair {
  question: string;
  answer: string;
}

interface BaseMessage {
  id: string;
  timestamp: Date;
}

interface UserMessageData extends BaseMessage {
  type: 'user';
  content: string;
}

interface ModelMessageData extends BaseMessage {
  type: 'model';
  mainAnswer: string;
  flashcards: QAPair[];
}

type Message = UserMessageData | ModelMessageData;

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSend = async (message: string) => {
    // Add user message immediately
    setMessages((prev) => [...prev, {
      id: crypto.randomUUID(),
      timestamp: new Date(),
      type: 'user',
      content: message,
    }]);

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

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          timestamp: new Date(),
          type: 'model',
          mainAnswer: data.preguntas || "Sorry, I didn't understand that.",
          flashcards: [],
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          timestamp: new Date(),
          type: 'model',
          mainAnswer: "Error: Unable to fetch response from the server.",
          flashcards: [],
        },
      ]);
    }
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <div className="flex flex-row p-6 space-x-6 w-full">
        <Sidebar />
        <div className="flex flex-col space-y-6 w-full rounded-2xl h-[calc(100dvh-3rem)]">
          <div className="flex-grow overflow-hidden">
            <Chatbox messages={messages} />
          </div>
          <Textbox onSend={handleSend} />
        </div>
      </div>
    </div>
  );
}
