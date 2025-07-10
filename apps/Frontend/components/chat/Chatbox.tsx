import EmptyChatbox from "./EmptyChatbox";
import MessageGlobe from "./MessageGlobe";

interface ChatboxProps {
  messages: { text: string; isUser: boolean }[];
}

export default function Chatbox({ messages }: ChatboxProps) {
  return (
    <div className="flex flex-col space-y-4 px-4 py-6 overflow-y-auto w-full h-full">
      {messages.length === 0 ? (
        <EmptyChatbox />
      ) : (
        messages.map((msg, index) => (
          <MessageGlobe key={index} text={msg.text} isUser={msg.isUser} />
        ))
      )}
    </div>
  );
}