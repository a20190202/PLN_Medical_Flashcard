import { ChevronDown, Dot, Plus, PlusSquare } from "lucide-react";
import { Button } from "../core/Button";
import { LogoHorizontal } from "../core/LogoHorizontal";

export default function Sidebar() {
  return (
    <div className="flex flex-col justify-between bg-sidebar shadow-lg px-6 py-6 w-[350px] rounded-2xl">
      <div className="flex flex-col gap-2">
        <Button className="w-full flex justify-between px-3 bg-white/10 border/10 hover:bg-sidebar-accent hover:text-white text-white" variant="outline" size="icon">
          <Plus className="size-6" />
          <span className="ml-2">New Chat</span>
        </Button>

        <Button className="w-full flex justify-between px-3 bg-white/10 border/10 hover:bg-sidebar-accent hover:text-white text-white" variant="outline" size="icon">
          <ChevronDown className="size-6" />
          <span className="ml-2">Recent chats</span>
        </Button>
        <Button className="w-full flex justify-between px-3 bg-white/10 border/10 hover:bg-sidebar-accent hover:text-white text-white" variant="outline" size="icon">
          <Dot className="size-6" />
          <span className="ml-2">Chat 1</span>
        </Button>
        <Button className="w-full flex justify-between px-3 bg-white/10 border/10 hover:bg-sidebar-accent hover:text-white text-white" variant="outline" size="icon">
          <Dot className="size-6" />
          <span className="ml-2">Chat 2</span>
        </Button>
      </div>
      <LogoHorizontal />
    </div>
  );
}
