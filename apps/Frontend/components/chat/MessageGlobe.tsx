interface MessageGlobeProps {
  text: string;
  isUser: boolean;
}

export default function MessageGlobe({ text, isUser }: MessageGlobeProps) {
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} w-full`}>
      <div
        className={`max-w-[70%] px-4 py-2 rounded-xl shadow-md ${
          isUser ? "bg-primary text-white" : "bg-white text-black"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
