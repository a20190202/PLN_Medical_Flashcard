import { cn } from "../../lib/Utils";
import { ReactNode } from "react";

interface MessageGlobeProps {
  type: 'user' | 'model';
  timestamp?: Date; // Hacer timestamp opcional
  children: ReactNode;
  hideTimestamp?: boolean; // Opción para ocultar timestamp
}

export default function MessageGlobe({ type, timestamp, children, hideTimestamp = false }: MessageGlobeProps) {
  const isUser = type === 'user';
  
  return (
    <div className="w-full mb-4">
      <div className={cn(
        "rounded-2xl px-4 py-3 shadow-sm",
        isUser 
          ? "max-w-[50%] bg-primary text-primary-foreground ml-auto"
          : "max-w-[70%] bg-muted mr-auto"
      )}>
        <div className="space-y-2">
          {children}
          {!hideTimestamp && timestamp && (
            <div className={cn(
              "text-xs opacity-70 mt-2",
              isUser ? "text-right" : "text-left"
            )}>
              {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
