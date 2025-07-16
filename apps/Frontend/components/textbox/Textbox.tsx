"use client";

import { Textarea } from "../core/Textarea";
import { useRef, useState } from "react";

interface TextboxProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function Textbox({ onSend, disabled = false }: TextboxProps) {
  const textareaRef = useRef(null);
  const [input, setInput] = useState("");

  const handleInput = (e) => {
    const textarea = textareaRef.current;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 9 * 24) + "px"; // 24px ~ line-height
    setInput(e.target.value);
  };

  const handleSubmit = () => {
    if (!input.trim()) return;
    onSend(input.trim());
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  return (
    <div className="flex">
          <Textarea
            ref={textareaRef}
            value={input}
            placeholder={disabled ? "Generating answer..." : "Type your message here."}
            disabled={disabled}
            className="w-full resize-none border-0 focus:ring-0 bg-transparent placeholder-muted-foreground disabled:opacity-50"
            onInput={handleInput}
            onSubmit={handleSubmit}
            style={{
              width: "100%",
              resize: "none",
              lineHeight: "1.5",
              fontSize: "16px",
              boxSizing: "border-box",
              minHeight: "1.5em",
              maxHeight: "13.5em", // 9 líneas x 1.5em
            }}
            rows={1}
          />
        </div>
  );
}
