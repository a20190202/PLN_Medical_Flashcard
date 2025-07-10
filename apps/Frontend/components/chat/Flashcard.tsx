"use client";

import { useState } from "react";
import { cn } from "../../lib/Utils";
import { Button } from "../core/Button";
import { RotateCcw } from "lucide-react";

interface FlashcardProps {
  question: string;
  answer: string;
}

export default function Flashcard({ question, answer }: FlashcardProps) {
  const [isFlipped, setIsFlipped] = useState(false);
  
  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  return (
    <div className="relative w-full min-h-[120px] perspective-1000">
      <div className={cn(
        "w-full h-full transition-transform duration-500 transform-style-preserve-3d",
        isFlipped && "rotate-y-180"
      )}>
        {/* Lado frontal - Pregunta */}
        <div className={cn(
          "absolute inset-0 w-full h-full backface-hidden",
          "border border-border rounded-lg p-4 bg-card shadow-sm",
          "flex flex-col justify-center"
        )}>
          <div className="flex justify-between items-start">
            <div className="flex-1 pr-2">
              <p className="text-sm font-medium text-foreground">{question}</p>
            </div>
            <div className="relative group">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleFlip}
                className="h-8 w-8 p-0 hover:bg-muted"
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
              {/* Tooltip */}
              <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block">
                <div className="bg-popover text-popover-foreground text-xs rounded px-2 py-1 shadow-md whitespace-nowrap">
                  Mostrar respuesta
                  <div className="absolute top-full right-2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-popover"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Lado trasero - Respuesta */}
        <div className={cn(
          "absolute inset-0 w-full h-full backface-hidden rotate-y-180",
          "border border-border rounded-lg p-4 bg-card shadow-sm",
          "flex flex-col justify-center"
        )}>
          <div className="flex justify-between items-start">
            <div className="flex-1 pr-2">
              <p className="text-sm text-muted-foreground">{answer}</p>
            </div>
            <div className="relative group">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleFlip}
                className="h-8 w-8 p-0 hover:bg-muted"
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
              {/* Tooltip */}
              <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block">
                <div className="bg-popover text-popover-foreground text-xs rounded px-2 py-1 shadow-md whitespace-nowrap">
                  Mostrar pregunta
                  <div className="absolute top-full right-2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-popover"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}