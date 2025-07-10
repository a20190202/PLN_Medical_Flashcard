import Chatbox from "../components/chat/Chatbox";
import Sidebar from "../components/sidebar/Sidebar";
import Textbox from "../components/textbox/Textbox";

// Tipos para los mensajes
interface QAPair {
  question: string;
  answer: string;
}

interface BaseMessage {
  id: string;
  timestamp: Date;
}

interface UserMessageData extends BaseMessage {
  type: 'user';
  content: string;
}

interface ModelMessageData extends BaseMessage {
  type: 'model';
  mainAnswer: string;
  flashcards: QAPair[];
}

type Message = UserMessageData | ModelMessageData;

export default function Home() {
  // Array vacío para mostrar EmptyChatbox
  const emptyMessages: Message[] = [];

  // Array hardcodeado para probar el contenido
  const testMessages: Message[] = [
    {
      id: "1",
      type: "user",
      content: "¿Qué es la hipertensión arterial y cuáles son sus principales causas?",
      timestamp: new Date('2024-07-10T10:30:00')
    },
    {
      id: "2",
      type: "model", 
      mainAnswer: "La hipertensión arterial es una condición médica crónica caracterizada por el aumento sostenido de la presión arterial por encima de los valores normales (≥140/90 mmHg). Es conocida como 'el asesino silencioso' porque frecuentemente no presenta síntomas evidentes.",
      flashcards: [
        {
          question: "¿Cuáles son los valores normales de presión arterial?",
          answer: "Presión arterial normal: <120/80 mmHg. Presión arterial elevada: 120-129/<80 mmHg. Hipertensión estadio 1: 130-139/80-89 mmHg."
        },
        {
          question: "¿Cuáles son las principales causas de hipertensión?",
          answer: "Factores de riesgo incluyen: edad avanzada, obesidad, sedentarismo, consumo excesivo de sal, estrés, tabaquismo, consumo de alcohol, antecedentes familiares y enfermedades como diabetes."
        },
        {
          question: "¿Por qué se llama 'el asesino silencioso'?",
          answer: "Porque la hipertensión generalmente no presenta síntomas evidentes, pero puede causar daño grave a órganos vitales como corazón, riñones, cerebro y vasos sanguíneos sin que la persona se dé cuenta."
        }
      ],
      timestamp: new Date('2024-07-10T10:31:15')
    },
    {
      id: "3",
      type: "user",
      content: "¿Cuáles son los síntomas cuando la hipertensión es severa?",
      timestamp: new Date('2024-07-10T10:35:00')
    },
    {
      id: "4",
      type: "model",
      mainAnswer: "Cuando la hipertensión es severa (crisis hipertensiva), pueden aparecer síntomas como dolor de cabeza intenso, visión borrosa, dolor en el pecho, dificultad para respirar, mareos, sangrado nasal y confusión. Estos síntomas requieren atención médica inmediata.",
      flashcards: [
        {
          question: "¿Qué es una crisis hipertensiva?",
          answer: "Es cuando la presión arterial supera los 180/120 mmHg, representando una emergencia médica que puede causar daño agudo a órganos vitales."
        },
        {
          question: "¿Cuándo debo buscar atención médica urgente?",
          answer: "Busca atención inmediata si experimentas: dolor de cabeza severo, dolor en el pecho, dificultad para respirar, cambios en la visión, o confusión junto con presión arterial elevada."
        }
      ],
      timestamp: new Date('2024-07-10T10:36:30')
    }
  ];

  // Cambia entre emptyMessages y testMessages para probar
  const currentMessages = testMessages; // Cambia a emptyMessages para ver EmptyChatbox

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <div className="flex flex-row p-6 space-x-6 w-full">
        <Sidebar />
        <div className="flex flex-col space-y-6 flex-1 min-h-0">
          <Chatbox messages={currentMessages} />
          <div className="flex-shrink-0">
            <Textbox />
          </div>
        </div>
      </div>
    </div>
  );
}

// pt-18
