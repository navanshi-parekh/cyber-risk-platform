"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Bot,
  X,
  Send,
  Sparkles,
  ShieldAlert,
  Building2,
  TrendingDown,
  Layers,
  RefreshCw,
  ChevronRight,
  Maximize2,
  Minimize2
} from "lucide-react";
import { formatINR } from "@/lib/utils";

interface Recommendation {
  control_id: string;
  control_name: string;
  investment_cost_inr: number;
  expected_risk_mitigation_inr: number;
  statutory_alignment: string[];
}

interface AgentQueryResponse {
  query: string;
  executive_summary: string;
  quantified_exposure: {
    baseline_eal_inr: number;
    var_95_inr: number;
    residual_eal_inr: number;
    net_risk_reduction_inr: number;
  };
  regulatory_impact: {
    compliance_score_percent: number;
    statutory_penalty_liability_inr: number;
    failed_mandates_count: number;
  };
  prioritized_roadmap: Recommendation[];
  timestamp: string;
}

interface ChatMessage {
  id: string;
  sender: "user" | "agent";
  text?: string;
  structuredData?: AgentQueryResponse;
  timestamp: string;
}

const PRESET_QUESTIONS = [
  "What is our highest financial risk today and what should we prioritize?",
  "What is our RBI and SEBI compliance penalty liability?",
  "How should we allocate our ₹10 Lakhs security budget for maximum ROSI?",
  "What happens if our patch remediation is delayed by 30 days?",
];

export const AiChatDrawer: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [inputValue, setInputValue] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome-msg",
      sender: "agent",
      text: "Hello. I am your **CISO Decision-Support AI**. You can ask plain-language questions about our quantified loss exposure, 0-1 Knapsack capital allocations, or RBI/SEBI regulatory compliance liabilities.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSendMessage = async (queryText?: string) => {
    const query = (queryText || inputValue).trim();
    if (!query || loading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/agent/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          budget_limit: 1000000.0,
        }),
      });

      if (!res.ok) {
        throw new Error(`Agent query failed: ${res.statusText}`);
      }

      const responseData: AgentQueryResponse = await res.json();

      const agentMessage: ChatMessage = {
        id: `agent-${Date.now()}`,
        sender: "agent",
        structuredData: responseData,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: `agent-err-${Date.now()}`,
        sender: "agent",
        text: `Error connecting to Executive Agent: ${err.message || "Make sure FastAPI is running on port 8000."}`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-slate-950 font-bold rounded-full shadow-2xl shadow-cyan-900/50 border border-cyan-400/40 transition-all transform hover:scale-105 ${
          isOpen ? "hidden" : "flex"
        }`}
      >
        <Sparkles className="w-5 h-5 text-slate-950 animate-pulse" />
        <span className="text-xs font-semibold tracking-wide">Ask Executive AI</span>
      </button>

      {/* Sliding Drawer Container */}
      {isOpen && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex flex-col bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl shadow-slate-950/90 overflow-hidden transition-all duration-300 ${
            isExpanded
              ? "w-[92vw] md:w-[720px] h-[86vh]"
              : "w-[92vw] sm:w-[460px] h-[640px]"
          }`}
        >
          {/* Top Header */}
          <div className="flex items-center justify-between px-4 py-3.5 bg-slate-950 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-xl">
                <Bot className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-100">
                    CISO Decision-Support AI
                  </span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-mono">
                    Open FAIR + MILP
                  </span>
                </div>
                <p className="text-[10px] text-slate-400">
                  Real-Time Exposure & Regulatory Advisor
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
                title={isExpanded ? "Collapse" : "Expand"}
              >
                {isExpanded ? (
                  <Minimize2 className="w-4 h-4" />
                ) : (
                  <Maximize2 className="w-4 h-4" />
                )}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Starter Question Chips */}
          <div className="px-3 py-2 bg-slate-950/60 border-b border-slate-800 flex gap-1.5 overflow-x-auto scrollbar-none">
            {PRESET_QUESTIONS.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(q)}
                disabled={loading}
                className="text-[10px] whitespace-nowrap px-2.5 py-1 bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-cyan-300 border border-slate-700 rounded-full transition shrink-0"
              >
                {q.length > 34 ? `${q.slice(0, 34)}...` : q}
              </button>
            ))}
          </div>

          {/* Chat Message Stream */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-900/60 text-xs">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${
                  msg.sender === "user" ? "items-end" : "items-start"
                }`}
              >
                {/* Text Bubble */}
                {msg.text && (
                  <div
                    className={`p-3 rounded-2xl max-w-[85%] leading-relaxed ${
                      msg.sender === "user"
                        ? "bg-cyan-600 text-slate-950 font-medium rounded-tr-none"
                        : "bg-slate-950 border border-slate-800 text-slate-200 rounded-tl-none"
                    }`}
                  >
                    {msg.text}
                  </div>
                )}

                {/* Structured Agent Response Output */}
                {msg.structuredData && (
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl rounded-tl-none p-4 max-w-[95%] space-y-3.5 shadow-md">
                    {/* Executive Summary Narrative */}
                    <div className="text-slate-200 leading-relaxed">
                      {msg.structuredData.executive_summary}
                    </div>

                    {/* Financial & Compliance Key Metrics Grid */}
                    <div className="grid grid-cols-2 gap-2 pt-1">
                      <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-xl">
                        <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                          <ShieldAlert className="w-3 h-3 text-red-400" />
                          <span>Baseline 95% VaR</span>
                        </div>
                        <div className="text-sm font-bold font-mono text-red-400 mt-1">
                          {formatINR(msg.structuredData.quantified_exposure.var_95_inr)}
                        </div>
                      </div>

                      <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-xl">
                        <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                          <Building2 className="w-3 h-3 text-amber-400" />
                          <span>Penalty Liability</span>
                        </div>
                        <div className="text-sm font-bold font-mono text-amber-400 mt-1">
                          {formatINR(
                            msg.structuredData.regulatory_impact.statutory_penalty_liability_inr
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Prioritized Mitigation Roadmap */}
                    {msg.structuredData.prioritized_roadmap.length > 0 && (
                      <div className="space-y-1.5 pt-1 border-t border-slate-800">
                        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                          <Layers className="w-3 h-3 text-cyan-400" />
                          <span>Optimized Investment Allocation:</span>
                        </div>
                        <div className="space-y-1.5">
                          {msg.structuredData.prioritized_roadmap.map((rec) => (
                            <div
                              key={rec.control_id}
                              className="p-2 bg-slate-900/80 border border-slate-800 rounded-lg flex items-center justify-between text-[11px]"
                            >
                              <div>
                                <div className="font-semibold text-slate-200">
                                  {rec.control_id}: {rec.control_name}
                                </div>
                                <div className="text-[9px] text-slate-400">
                                  {rec.statutory_alignment.join(", ")}
                                </div>
                              </div>
                              <div className="text-right font-mono shrink-0 ml-2">
                                <div className="text-slate-200 font-bold">
                                  {formatINR(rec.investment_cost_inr)}
                                </div>
                                <div className="text-[9px] text-emerald-400">
                                  -{formatINR(rec.expected_risk_mitigation_inr)} EAL
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <span className="text-[9px] text-slate-500 font-mono mt-1 px-1">
                  {msg.timestamp}
                </span>
              </div>
            ))}

            {loading && (
              <div className="flex items-center gap-2 p-3 bg-slate-950 border border-slate-800 rounded-2xl rounded-tl-none w-fit text-slate-400 text-xs">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                <span>Synthesizing FAIR models and statutory rules...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Bottom Chat Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-3 bg-slate-950 border-t border-slate-800 flex items-center gap-2"
          >
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about risk exposure, budget ROI, or RBI mandates..."
              disabled={loading}
              className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
            />
            <button
              type="submit"
              disabled={loading || !inputValue.trim()}
              className="p-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-slate-950 rounded-xl font-bold transition shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
};