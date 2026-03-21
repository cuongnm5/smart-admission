import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User } from "lucide-react";
import type { StudentProfile } from "@/lib/admissionEngine";

interface ChatProfileInputProps {
  onComplete: (profile: StudentProfile) => void;
}

interface Message {
  role: "bot" | "user";
  text: string;
}

const STEPS = [
  { key: "name", question: "Hey! I'm your AI admission advisor. 👋 What's your name?", placeholder: "Your name" },
  { key: "major", question: "Great to meet you, {name}! What's your dream major?", placeholder: "e.g. Computer Science, Business, Biology" },
  { key: "gpa", question: "What's your current GPA? (on a 4.0 scale)", placeholder: "e.g. 3.8" },
  { key: "sat", question: "What's your SAT score? (out of 1600)", placeholder: "e.g. 1350" },
  { key: "ielts", question: "And your IELTS score? (out of 9.0) If not applicable, type 'N/A'.", placeholder: "e.g. 7.5 or N/A" },
  { key: "activities", question: "Tell me about your extracurricular activities. List them separated by commas.", placeholder: "e.g. Debate Club, Robotics, Volunteering" },
  { key: "awards", question: "Any awards or honors? List them separated by commas (or 'none').", placeholder: "e.g. Science Olympiad Gold, Dean's List" },
  { key: "leadership", question: "How many leadership positions do you hold? (e.g. club president, team captain)", placeholder: "e.g. 2" },
  { key: "extras", question: "Two quick yes/no questions:\n1. Do you have community service experience?\n2. Do you have research experience?\n\nAnswer like: yes, no", placeholder: "e.g. yes, no" },
];

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="w-2 h-2 rounded-full bg-accent animate-typing-dot"
          style={{ animationDelay: `${i * 0.2}s` }}
        />
      ))}
    </div>
  );
}

export default function ChatProfileInput({ onComplete }: ChatProfileInputProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [step, setStep] = useState(0);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(true);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const addBotMessage = useCallback((text: string) => {
    setTyping(true);
    setTimeout(() => {
      setMessages((prev) => [...prev, { role: "bot", text }]);
      setTyping(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }, 800);
  }, []);

  useEffect(() => {
    addBotMessage(STEPS[0].question);
  }, [addBotMessage]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const handleSend = () => {
    if (!input.trim() || typing) return;
    const userText = input.trim();
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setInput("");

    const newAnswers = { ...answers, [STEPS[step].key]: userText };
    setAnswers(newAnswers);

    const nextStep = step + 1;
    if (nextStep < STEPS.length) {
      setStep(nextStep);
      let question = STEPS[nextStep].question;
      if (question.includes("{name}")) {
        question = question.replace("{name}", newAnswers.name || "");
      }
      addBotMessage(question);
    } else {
      // Parse and build profile
      addBotMessage(`Thanks ${newAnswers.name}! 🎯 I have everything I need. Let me analyze your profile against 500+ universities...`);
      setTimeout(() => {
        const extras = (newAnswers.extras || "no, no").split(",").map((s) => s.trim().toLowerCase());
        const profile: StudentProfile = {
          name: newAnswers.name || "Student",
          gpa: parseFloat(newAnswers.gpa) || 3.5,
          sat: parseInt(newAnswers.sat) || 1300,
          ielts: newAnswers.ielts?.toLowerCase() === "n/a" ? 7.0 : parseFloat(newAnswers.ielts) || 7.0,
          major: newAnswers.major || "Computer Science",
          activities: (newAnswers.activities || "").split(",").map((s) => s.trim()).filter(Boolean),
          awards: newAnswers.awards?.toLowerCase() === "none" ? [] : (newAnswers.awards || "").split(",").map((s) => s.trim()).filter(Boolean),
          leadershipRoles: parseInt(newAnswers.leadership) || 0,
          communityService: extras[0]?.startsWith("y") || false,
          researchExperience: extras[1]?.startsWith("y") || false,
        };
        onComplete(profile);
      }, 2000);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="border-b border-border px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
          <Bot className="w-4 h-4 text-accent-foreground" />
        </div>
        <div>
          <h2 className="font-semibold text-sm text-foreground">ETEST AI Advisor</h2>
          <p className="text-xs text-muted-foreground">Building your admission profile</p>
        </div>
        <div className="ml-auto text-xs text-muted-foreground font-mono">
          {step + 1}/{STEPS.length}
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-1 bg-muted">
        <motion.div
          className="h-full bg-accent"
          initial={{ width: 0 }}
          animate={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        />
      </div>

      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 max-w-2xl mx-auto w-full">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className={`flex gap-3 mb-4 ${msg.role === "user" ? "justify-end" : ""}`}
            >
              {msg.role === "bot" && (
                <div className="w-7 h-7 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Bot className="w-3.5 h-3.5 text-accent" />
                </div>
              )}
              <div
                className={`rounded-2xl px-4 py-3 max-w-[80%] text-sm leading-relaxed whitespace-pre-line ${
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground rounded-br-md"
                    : "bg-card text-card-foreground bg-card-glow rounded-bl-md"
                }`}
              >
                {msg.text}
              </div>
              {msg.role === "user" && (
                <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5 text-primary" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        {typing && (
          <div className="flex gap-3 mb-4">
            <div className="w-7 h-7 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
              <Bot className="w-3.5 h-3.5 text-accent" />
            </div>
            <div className="bg-card bg-card-glow rounded-2xl rounded-bl-md">
              <TypingIndicator />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-border px-4 md:px-8 py-4 max-w-2xl mx-auto w-full">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-2"
        >
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={STEPS[Math.min(step, STEPS.length - 1)].placeholder}
            disabled={typing}
            className="flex-1 rounded-xl border border-border bg-card px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || typing}
            className="rounded-xl bg-accent px-4 py-3 text-accent-foreground transition-all hover:shadow-md active:scale-95 disabled:opacity-40"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
