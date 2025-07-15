
"use client";
import { useState } from "react";
import { RotateCcw } from "lucide-react";

interface FlashcardProps {
  title?: string;
  question: string;
  answer: string;
}

export default function Flashcard({ title, question, answer }: FlashcardProps) {
  const [isFlipped, setIsFlipped] = useState(false);
  
  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  // Función para agregar las clases de transformación 3D necesarias
  const cn = (...classes: (string | boolean | undefined)[]) => {
    return classes.filter(Boolean).join(' ');
  };

  return (
    <div className="relative w-full" style={{ perspective: '1000px' }}>
      <div 
        className="w-full transition-transform duration-500 relative"
        style={{
          transformStyle: 'preserve-3d',
          transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
          minHeight: '120px'
        }}
      >
        {/* Elemento fantasma para mantener la altura correcta */}
        <div className="invisible pointer-events-none" aria-hidden="true">
          <div className="w-full border border-gray-200 rounded-lg p-4 bg-white shadow-sm flex flex-col justify-between min-h-[120px]">
            <div className="flex-1 pb-12">
              {title && (
                <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                  {title}{isFlipped ? " - Answer" : ""}
                </div>
              )}
              <div className="text-sm leading-relaxed">
                {isFlipped ? answer : question}
              </div>
            </div>
          </div>
        </div>

        {/* Lado frontal - Pregunta */}
        <div 
          className={cn(
            "w-full border border-gray-200 rounded-lg p-4 bg-white shadow-sm",
            "flex flex-col justify-between min-h-[120px]"
          )}
          style={{
            backfaceVisibility: 'hidden',
            transform: 'rotateY(0deg)',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          <div className="flex-1 pb-12">
            {title && (
              <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                {title}
              </div>
            )}
            <p className="text-sm font-medium text-gray-800 leading-relaxed">
              {question}
            </p>
          </div>
          
          <div className="absolute bottom-3 right-3">
            <div className="relative group">
              <button
                onClick={handleFlip}
                className="h-8 w-8 p-0 hover:bg-gray-100 bg-white shadow-sm rounded border border-gray-200 flex items-center justify-center transition-colors"
              >
                <RotateCcw className="h-3 w-3 text-gray-600" />
              </button>
              {/* Tooltip */}
              <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block z-50">
                <div className="bg-gray-800 text-white text-xs rounded px-2 py-1 shadow-md whitespace-nowrap">
                  Show answer
                  <div className="absolute top-full right-2 w-0 h-0 border-l-2 border-r-2 border-t-2 border-transparent border-t-gray-800"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Lado trasero - Respuesta */}
        <div 
          className={cn(
            "w-full border border-gray-200 rounded-lg p-4 bg-white shadow-sm",
            "flex flex-col justify-between min-h-[120px]"
          )}
          style={{
            backfaceVisibility: 'hidden',
            transform: 'rotateY(180deg)',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          <div className="flex-1 pb-12">
            {title && (
              <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                {title} - Answer
              </div>
            )}
            <div className="text-sm text-gray-700 leading-relaxed">
              {answer}
            </div>
          </div>
          
          <div className="absolute bottom-3 right-3">
            <div className="relative group">
              <button
                onClick={handleFlip}
                className="h-8 w-8 p-0 hover:bg-gray-100 bg-white shadow-sm rounded border border-gray-200 flex items-center justify-center transition-colors"
              >
                <RotateCcw className="h-3 w-3 text-gray-600" />
              </button>
              {/* Tooltip */}
              <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block z-50">
                <div className="bg-gray-800 text-white text-xs rounded px-2 py-1 shadow-md whitespace-nowrap">
                  Show question
                  <div className="absolute top-full right-2 w-0 h-0 border-l-2 border-r-2 border-t-2 border-transparent border-t-gray-800"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}