import { cn } from "../../lib/Utils";
import { ReactNode } from "react";

interface MessageGlobeProps {
  type: 'user' | 'model';
  timestamp: Date;
  children: ReactNode;
}

export default function MessageGlobe({ type, timestamp, children }: MessageGlobeProps) {
  const isUser = type === 'user';
  
  return (
    <div className={cn(
      "flex w-full mb-4",
      isUser ? "justify-end" : "justify-start"
    )}>
      <div className={cn(
        "max-w-[70%] rounded-2xl px-4 py-3 shadow-sm",
        isUser 
          ? "bg-primary text-primary-foreground ml-12" 
          : "bg-muted mr-12"
      )}>
        <div className="space-y-2">
          {children}
          <div className={cn(
            "text-xs opacity-70 mt-2",
            isUser ? "text-right" : "text-left"
          )}>
            {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </div>
  );
}