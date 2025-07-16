import { useEffect, useRef } from "react";
import EmptyChatbox from "./EmptyChatbox";
import UserMessage from "./UserMessage";
import ModelMessage from "./ModelMessage";
import TypingLoader from "./TypingLoader";

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

interface ChatboxProps {
  messages: Message[];
  isLoading?: boolean; // Nueva prop para estado de carga
}

export default function Chatbox({ messages, isLoading = false }: ChatboxProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll al final cuando hay nuevos mensajes o está cargando
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-200px)] rounded-2xl border bg-card">
      {messages.length > 0 || isLoading ? (
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id}>
              {message.type === 'user' && (
                <UserMessage content={message.content} timestamp={message.timestamp} />
              )}
              {message.type === 'model' && (
                <ModelMessage 
                  mainAnswer={message.mainAnswer} 
                  flashcards={message.flashcards}
                  timestamp={message.timestamp}
                />
              )}
            </div>
          ))}
          
          {/* Mostrar loader cuando está cargando */}
          {isLoading && <TypingLoader />}
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <EmptyChatbox />
        </div>
      )}
    </div>
  );
}
