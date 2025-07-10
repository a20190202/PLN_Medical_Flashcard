import { useEffect, useRef } from "react";
import EmptyChatbox from "./EmptyChatbox";
import UserMessage from "./UserMessage";
import ModelMessage from "./ModelMessage";

interface QAPair {
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
}

export default function Chatbox({ messages }: ChatboxProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-200px)] rounded-2xl border bg-card">
      {messages.length > 0 ? (
        <div
          ref={containerRef}
          className="flex flex-col-reverse overflow-y-auto px-6 py-4 space-y-reverse space-y-4 h-full w-full"
        >
          {[...messages].reverse().map((message) => (
            <div key={message.id}>
              {message.type === "user" && (
                <UserMessage
                  content={message.content}
                  timestamp={message.timestamp}
                />
              )}
              {message.type === "model" && (
                <ModelMessage
                  mainAnswer={message.mainAnswer}
                  flashcards={message.flashcards}
                  timestamp={message.timestamp}
                />
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <EmptyChatbox />
        </div>
      )}
    </div>
  );
}
