import React, { useState, useEffect } from "react";
import { marked } from "marked";
import jsPDF from "jspdf";

function App() {
  const [topic, setTopic] = useState("");
  const [result, setResult] = useState("");
  const [displayText, setDisplayText] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  // 🚀 PARAGRAPH TYPING (NO FLICKER)
  useEffect(() => {
    if (!result) return;

    const paragraphs = result.split("\n\n");
    let index = 0;

    setDisplayText("");

    const interval = setInterval(() => {
      setDisplayText((prev) => prev + paragraphs[index] + "\n\n");
      index++;

      if (index >= paragraphs.length) {
        clearInterval(interval);
      }
    }, 2000); // ⏱️ 2 sec per paragraph

    return () => clearInterval(interval);
  }, [result]);

  // 🚀 Generate document
  const generateDoc = async () => {
    if (!topic) {
      alert("Enter a topic");
      return;
    }

    setLoading(true);
    setResult("");
    setDisplayText("");

    try {
      const response = await fetch("/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic }),
      });

      const data = await response.json();
      console.log(data);

      if (data.error) {
        alert("Error: " + data.error);
        setLoading(false);
        return;
      }

      // ✅ DELAY to avoid instant render flicker
      setTimeout(() => {
        setResult(data.result);
      }, 300);

      // Save to history
      setHistory([{ topic, content: data.result }, ...history]);

    } catch (error) {
      alert("Backend error!");
    }

    setLoading(false);
  };

  // 📄 Download PDF
  const downloadPDF = () => {
    const doc = new jsPDF();
    doc.text(result, 10, 10);
    doc.save("document.pdf");
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      
      {/* 🧠 SIDEBAR */}
      <div style={{
        width: "250px",
        background: "#161b22",
        color: "white",
        padding: "20px",
        overflowY: "auto"
      }}>
        <h3>🧠 History</h3>

        {history.map((item, index) => (
          <div
            key={index}
            onClick={() => {
              setResult(item.content);
              setDisplayText(item.content); // instant show
            }}
            style={{
              cursor: "pointer",
              padding: "10px",
              borderBottom: "1px solid gray"
            }}
          >
            {item.topic}
          </div>
        ))}
      </div>

      {/* 💬 MAIN UI */}
      <div style={{
        flex: 1,
        background: "#0d1117",
        color: "white",
        padding: "30px"
      }}>
        <h1 style={{ color: "#58a6ff" }}>🤖 AI Document Studio</h1>

        <input
          type="text"
          placeholder="Enter topic..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          style={{
            padding: "12px",
            width: "300px",
            borderRadius: "6px",
            border: "none",
            marginRight: "10px"
          }}
        />

        <button onClick={generateDoc} style={{
          padding: "12px 20px",
          background: "#58a6ff",
          border: "none",
          borderRadius: "6px"
        }}>
          Generate
        </button>

        <button onClick={downloadPDF} style={{
          padding: "12px 20px",
          marginLeft: "10px",
          background: "green",
          border: "none",
          borderRadius: "6px"
        }}>
          Download PDF
        </button>

        {loading && <p>⏳ AI is thinking...</p>}

        {/* 📄 OUTPUT */}
        <div style={{
          marginTop: "30px",
          background: "white",
          color: "black",
          padding: "30px",
          borderRadius: "10px",
          height: "400px",
          overflowY: "auto",
          boxShadow: "0 0 10px rgba(0,0,0,0.2)"
        }}>
          <div
            dangerouslySetInnerHTML={{
              __html: marked(displayText), // ✅ ONLY displayText (no flicker)
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default App;