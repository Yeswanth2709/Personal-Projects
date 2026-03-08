import { useState, useRef, useEffect } from "react";
import { API_CONFIG } from "../config";

const ChatBot = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content:
        "Hello! I'm your Annual Report 2024-25 Assistant. I can help you analyze financial data, revenue trends, expenses, and more from the company's annual report. What would you like to know?",
      timestamp: new Date().toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const sessionId = useRef(`session_${Date.now()}`); // Unique session for conversation context

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Call FastAPI backend to get bot response
  const callBackendAPI = async (userMessage) => {
    try {
      const response = await fetch(
        `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: userMessage,
            session_id: sessionId.current, // Include session ID for conversation context
          }),
        },
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // Return formatted response with content and sources
      return {
        content:
          data.content ||
          data.response ||
          data.message ||
          "I received your question but couldn't process it.",
        sources: data.sources || [],
      };
    } catch (error) {
      console.error("Error calling backend API:", error);
      throw error;
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userQuestion = inputMessage;

    // Add user message
    const userMsg = {
      id: messages.length + 1,
      role: "user",
      content: userQuestion,
      timestamp: new Date().toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage("");
    setIsTyping(true);

    try {
      // Call the backend API
      const response = await callBackendAPI(userQuestion);

      const botMsg = {
        id: messages.length + 2,
        role: "assistant",
        content: response.content,
        sources: response.sources,
        timestamp: new Date().toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      // Handle errors gracefully
      const errorMsg = {
        id: messages.length + 2,
        role: "assistant",
        content: `⚠️ I'm having trouble connecting to the server. Please make sure:\n\n• The backend server is running\n• The API endpoint is correct (${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT})\n• CORS is properly configured on the backend\n\nError: ${error.message}`,
        timestamp: new Date().toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickQuestions = [
    "What was our revenue in 2024?",
    "Show me expense breakdown",
    "What's our profit margin?",
    "Tell me about cash flow",
  ];

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl h-[90vh] bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/20 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-linear-to-r from-purple-600 to-blue-600 p-6 border-b border-white/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                <svg
                  className="w-7 h-7 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">
                  Financial Report Assistant
                </h1>
                <p className="text-white/80 text-sm">
                  Ask me anything about financial data
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-white/90 text-sm font-medium">Online</span>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} animate-fadeIn`}
            >
              <div
                className={`flex gap-3 max-w-[80%] ${message.role === "user" ? "flex-row-reverse" : ""}`}
              >
                {/* Avatar */}
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                    message.role === "user"
                      ? "bg-linear-to-br from-blue-500 to-purple-500"
                      : "bg-linear-to-br from-green-400 to-cyan-500"
                  }`}
                >
                  {message.role === "user" ? (
                    <svg
                      className="w-6 h-6 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="w-6 h-6 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                      />
                    </svg>
                  )}
                </div>

                {/* Message Content */}
                <div
                  className={`flex flex-col gap-2 ${message.role === "user" ? "items-end" : "items-start"}`}
                >
                  <div
                    className={`rounded-2xl p-4 ${
                      message.role === "user"
                        ? "bg-linear-to-br from-blue-500 to-purple-600 text-white"
                        : "bg-white/90 text-gray-800 shadow-lg"
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">
                      {message.content}
                    </div>

                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200 space-y-1">
                        <p className="text-xs font-semibold text-gray-600 mb-2">
                          📎 Sources:
                        </p>
                        {message.sources.map((source, idx) => (
                          <div
                            key={idx}
                            className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded inline-block mr-2"
                          >
                            {source}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <span className="text-xs text-white/60">
                    {message.timestamp}
                  </span>
                </div>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start animate-fadeIn">
              <div className="flex gap-3 max-w-[80%]">
                <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 bg-linear-to-br from-green-400 to-cyan-500">
                  <svg
                    className="w-6 h-6 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <div className="bg-white/90 rounded-2xl p-4 shadow-lg">
                  <div className="flex gap-1">
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        <div className="px-6 py-3 border-t border-white/10">
          <div className="flex gap-2 flex-wrap">
            {quickQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => setInputMessage(question)}
                className="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white text-xs rounded-full transition-all duration-200 border border-white/20 hover:scale-105"
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="p-6 bg-white/5 border-t border-white/20">
          <div className="flex gap-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about financial reports..."
              className="flex-1 bg-white/10 text-white placeholder-white/50 rounded-2xl px-6 py-4 focus:outline-none focus:ring-2 focus:ring-purple-500 border border-white/20 backdrop-blur-sm"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim()}
              className="px-8 py-4 bg-linear-to-r from-purple-500 to-blue-500 text-white rounded-2xl hover:from-purple-600 hover:to-blue-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
            >
              Send
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default ChatBot;
