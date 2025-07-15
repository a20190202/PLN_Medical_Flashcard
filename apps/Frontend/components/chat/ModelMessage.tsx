import MessageGlobe from "./MessageGlobe";
import Flashcard from "./Flashcard";

interface QAPair {
  title: string;
  question: string;
  answer: string;
}

interface ModelMessageProps {
  mainAnswer: string;
  flashcards: QAPair[];
  timestamp: Date;
}

export default function ModelMessage({ mainAnswer, flashcards, timestamp }: ModelMessageProps) {
  return (
    <MessageGlobe type="model" timestamp={timestamp}>
      <div className="space-y-4 w-full">
        {/* Respuesta principal */}
        <div className="prose prose-sm max-w-none">
          <p className="text-base leading-relaxed text-foreground mb-0">
            {mainAnswer}
          </p>
        </div>
        
        {/* Flashcards */}
        {flashcards.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="h-px bg-border flex-1"></div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2">
                Flashcards ({flashcards.length})
              </h4>
              <div className="h-px bg-border flex-1"></div>
            </div>
            
            <div className="grid gap-3">
              {flashcards.map((pair, index) => (
                <Flashcard 
                  key={index}
                  title={pair.title}
                  question={pair.question}
                  answer={pair.answer}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </MessageGlobe>
  );
}