import Chatbox from "../components/chat/Chatbox";
import Sidebar from "../components/sidebar/Sidebar";
import Textbox from "../components/textbox/Textbox";

export default function Home() {
  return (
    <div className="flex container bg-background min-h-[100dvh] max-h-fit max-w-full overflow-auto">
      <div className="flex flex-row px-6 py-6 space-x-6 w-full">
        <Sidebar />
        <div className="flex flex-col space-y-6 w-full rounded-2xl">
          <Chatbox />
          <Textbox />
        </div>
      </div>
    </div>
  );
}

// pt-18
