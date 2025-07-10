"use client";

import { useState } from "react";
import Chatbox from "../components/chat/Chatbox";
import Sidebar from "../components/sidebar/Sidebar";
import Textbox from "../components/textbox/Textbox";

export default function Home() {
  const [messages, setMessages] = useState<{ text: string; isUser: boolean }[]>([]);

  const handleSend = async (message: string) => {
    // Add user message immediately
    setMessages((prev) => [...prev, { text: message, isUser: true }]);

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
          text: data.preguntas || "Sorry, I didn't understand that.",
          isUser: false,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          text: "Error: Unable to fetch response from the server.",
          isUser: false,
        },
      ]);
    }
  };

  return (
    <div className="flex container bg-background min-h-[100dvh] max-h-fit max-w-full overflow-auto">
      <div className="flex flex-row px-6 py-6 space-x-6 w-full">
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
