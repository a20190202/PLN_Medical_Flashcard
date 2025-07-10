import MessageGlobe from "./MessageGlobe";
import Flashcard from "./Flashcard";

interface QAPair {
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
      <div className="space-y-4">
        <p className="text-lg font-medium">{mainAnswer}</p>
        
        {flashcards.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-muted-foreground">Flashcards:</h4>
            <div className="grid gap-2">
              {flashcards.map((pair, index) => (
                <Flashcard 
                  key={index}
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