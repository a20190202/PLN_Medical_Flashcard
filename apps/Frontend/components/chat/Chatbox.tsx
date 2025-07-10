import { useEffect, useRef } from "react";
import EmptyChatbox from "./EmptyChatbox";
import MessageGlobe from "./MessageGlobe";

interface ChatboxProps {
  messages: { text: string; isUser: boolean }[];
}

export default function Chatbox({ messages }: ChatboxProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div
      ref={containerRef}
      className="w-full h-full overflow-y-auto px-4 py-6"
      style={{ display: "flex", flexDirection: "column-reverse" }}
    >
      {messages.length === 0 ? (
        <EmptyChatbox />
      ) : (
        [...messages]
          .reverse()
          .map((msg, index) => (
            <MessageGlobe key={index} text={msg.text} isUser={msg.isUser} />
          ))
      )}
    </div>
  );
}
