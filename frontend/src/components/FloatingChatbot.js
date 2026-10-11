import React, { useEffect, useRef, useState } from "react";
import { askChatbot } from "../services/api";
import "./FloatingChatbot.css";

export default function FloatingChatbot() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! 👋 I’m ScholarNexus Assistant. Ask me about scholarship eligibility, deadlines, amounts, or required documents." }
  ]);
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, open]);

  const sendMessage = async (event) => {
    event?.preventDefault();
    const text = question.trim();
    if (!text || sending) return;
    setMessages((current) => [...current, { role: "user", text }]);
    setQuestion("");
    setSending(true);
    try {
      const response = await askChatbot(text);
      const answer = response?.data?.answer || response?.data?.message || "Sorry, I couldn’t find an answer. Please try asking another way.";
      setMessages((current) => [...current, { role: "assistant", text: String(answer) }]);
    } catch (error) {
      const detail = error?.response?.data?.message || error?.response?.data?.error;
      setMessages((current) => [...current, { role: "assistant", text: detail ? `I couldn’t connect: ${detail}` : "I couldn’t connect to the chatbot. Please check that the backend is running on port 5000 and try again." }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="sn-chatbot-root">
      {open && (
        <section className="sn-chat-panel" aria-label="ScholarNexus chatbot">
          <header className="sn-chat-header">
            <div><strong>ScholarNexus Assistant</strong><small>Scholarship help, anytime</small></div>
            <button type="button" aria-label="Close chatbot" onClick={() => setOpen(false)}>×</button>
          </header>
          <div className="sn-chat-messages" aria-live="polite">
            {messages.map((message, index) => (
              <div key={`${index}-${message.role}`} className={`sn-chat-message ${message.role === "user" ? "sn-chat-user" : "sn-chat-assistant"}`}>
                {message.text.split("\n").map((line, i) => <React.Fragment key={i}>{i > 0 && <br />}{line.replace(/^\s*[•*-]\s*/, "• ")}</React.Fragment>)}
              </div>
            ))}
            {sending && <div className="sn-chat-message sn-chat-assistant">Thinking…</div>}
            <div ref={bottomRef} />
          </div>
          <form className="sn-chat-form" onSubmit={sendMessage}>
            <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask about scholarships…" aria-label="Your message" />
            <button type="submit" disabled={!question.trim() || sending} aria-label="Send message">➤</button>
          </form>
        </section>
      )}
      <button type="button" className="sn-chat-launcher" aria-label={open ? "Close chatbot" : "Open chatbot"} onClick={() => setOpen((value) => !value)}>
        {open ? "×" : "💬"}
      </button>
    </div>
  );
}
