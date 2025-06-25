"use client";

import { Textarea } from "../core/Textarea";
import { useRef } from "react";

export default function Textbox() {
  const textareaRef = useRef(null);

  const handleInput = (e) => {
    const textarea = textareaRef.current;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 9 * 24) + "px"; // 24px ~ line-height
  };

  return (
    <div className="flex">
      <Textarea
        ref={textareaRef}
        placeholder="Type your message here."
        className="rounded-2xl bg-background shadow-lg resize-none"
        onInput={handleInput}
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
