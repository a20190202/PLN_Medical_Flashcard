import MessageGlobe from "./MessageGlobe";

interface UserMessageProps {
  content: string;
  timestamp: Date;
}

export default function UserMessage({ content, timestamp }: UserMessageProps) {
  return (
    <MessageGlobe type="user" timestamp={timestamp}>
      <p className="text-base">{content}</p>
    </MessageGlobe>
  );
}