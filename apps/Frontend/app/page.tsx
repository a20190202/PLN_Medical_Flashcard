"use client";

import { useState } from "react";
import Chatbox from "../components/chat/Chatbox";
import Sidebar from "../components/sidebar/Sidebar";
import Textbox from "../components/textbox/Textbox";

export default function Home() {
  const [messages, setMessages] = useState([] as { text: string; isUser: boolean }[]);

  const handleSend = (message: string) => {
    setMessages((prev) => [
      ...prev,
      { text: message, isUser: true },
      {
        text: getBotResponse(message),
        isUser: false,
      },
    ]);
  };

  const getBotResponse = (input: string): string => {
    // Hardcoded logic
    if (input.toLowerCase().includes("risk")) {
      return "Hypertension risk factors include obesity, high salt intake, and sedentary lifestyle.";
    }
    if (input.toLowerCase().includes("complication")) {
      return "Complications of hypertension include heart disease, stroke, and kidney failure.";
    }
    return "Hypertension is a chronic condition where blood pressure is elevated. Ask me more!";
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