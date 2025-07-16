import MessageGlobe from "./MessageGlobe";

export default function TypingLoader() {
  return (
    <MessageGlobe type="model" timestamp={new Date()}>
      <div className="flex items-center space-x-2">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
        <span className="text-sm text-muted-foreground">Loading...</span>
      </div>
    </MessageGlobe>
  );
}