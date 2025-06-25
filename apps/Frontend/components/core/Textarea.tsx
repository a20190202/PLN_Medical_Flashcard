import * as React from "react";
import { cn } from "../../lib/Utils";
import { Button } from "./Button";
import { SendHorizontal } from "lucide-react";

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  onSubmit?: () => void;
  buttonLabel?: string;
}

function Textarea({
  className,
  onSubmit,
  ...props
}: TextareaProps) {
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = React.useState(false);

  return (
    <div
      className={cn(
        "border-input placeholder:text-muted-foreground",
        "dark:bg-input/30 min-h-16 w-full rounded-md border bg-transparent px-4 py-4",
        "shadow-xs transition-[color,box-shadow]",
        "relative flex items-center gap-4",
        // Estados de focus y validación aplicados al contenedor
        isFocused && "border-ring ring-ring/50 ring-[3px]",
        className
      )}
      onClick={() => textareaRef.current?.focus()}
    >
      <textarea
        ref={textareaRef}
        className={cn(
          "flex-1 bg-transparent text-base outline-none resize-none",
          "placeholder:text-muted-foreground",
          "disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
          "border-none p-0"
        )}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        {...props}
      />
      <div className="flex items-center">
        <Button
          type="button"
          variant="outline"
          onClick={onSubmit}
          size="icon" className="size-12"
        >
          <SendHorizontal className="size-6"/>
        </Button>
      </div>
    </div>
  );
}

export { Textarea };
