"use client";

import { useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { text: input, fromUser: true };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userMessage.text }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      const botMessage = { text: data.response, fromUser: false };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage = {
        text: "Sorry, something went wrong. Please try again.",
        fromUser: false,
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "0 auto",
        fontFamily: "sans-serif",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
      }}
    >
      <h1 style={{ textAlign: "center" }}>RAG Chatbot</h1>
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "10px",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
        }}
      >
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              alignSelf: msg.fromUser ? "flex-end" : "flex-start",
              backgroundColor: msg.fromUser ? "#dcf8c6" : "#f0f0f0",
              padding: "8px 12px",
              borderRadius: "16px",
              maxWidth: "70%",
              wordWrap: "break-word",
              color: "black",
            }}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <form
        onSubmit={handleSendMessage}
        style={{ display: "flex", marginTop: "10px" }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          style={{
            flex: 1,
            padding: "10px",
            borderRadius: "8px",
            border: "1px solid #ccc",
          }}
          disabled={isLoading}
        />
        <button
          type="submit"
          style={{
            padding: "10px 20px",
            borderRadius: "8px",
            border: "none",
            backgroundColor: "#0070f3",
            color: "white",
            cursor: "pointer",
            marginLeft: "10px",
          }}
          disabled={isLoading}
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
}
