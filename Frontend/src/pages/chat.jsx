// function Chat() {
//   return (
//     <div className="chat-page">

//       <header className="chat-header">

//         <div className="logo">
//           RAG<span>CHAT</span>
//         </div>

//         <div className="user-area">
//           <span>Welcome, User</span>
//           <button onClick={handleLogout}>Logout</button>
//         </div>

//       </header>

//       <main className="chat-container">

//         <div className="messages">

//           <div className="message user-message">
//             <div className="message-label">
//               You
//             </div>

//             <div className="message-text">
//               What is RAG?
//             </div>
//           </div>

//           <div className="message bot-message">
//             <div className="message-label">
//               RAG Chatbot
//             </div>

//             <div className="message-text">
//               RAG stands for Retrieval-Augmented Generation.
//               It allows an AI system to retrieve relevant
//               information from documents before generating
//               an answer.
//             </div>

//             <button className="speak-button">
//               🔊
//             </button>
//           </div>

//         </div>

//         <div className="chat-input-area">

//           <button className="upload-button">
//             📎
//           </button>

//           <button className="mic-button">
//             🎤
//           </button>

//           <input
//             type="text"
//             placeholder="Ask something..."
//           />

//           <button className="send-button">
//             ➤
//           </button>

//         </div>

//       </main>

//     </div>
//   );
// }

// export default Chat;
import { useNavigate } from "react-router-dom";

function Chat() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Remove saved login information
    localStorage.removeItem("user");

    // Go to login page
    navigate("/login");
  };

  return (
    <div className="chat-page">

      <header className="chat-header">

        <div className="logo">
          RAG<span>CHAT</span>
        </div>

        <div className="user-area">
          <span>Welcome, User</span>

          <button onClick={handleLogout}>
            Logout
          </button>
        </div>

      </header>

      <main className="chat-container">

        <div className="messages">

          <div className="message user-message">
            <div className="message-label">
              You
            </div>

            <div className="message-text">
              What is RAG?
            </div>
          </div>

          <div className="message bot-message">
            <div className="message-label">
              RAG Chatbot
            </div>

            <div className="message-text">
              RAG stands for Retrieval-Augmented Generation.
              It allows an AI system to retrieve relevant
              information from documents before generating
              an answer.
            </div>

            <button className="speak-button">
              🔊
            </button>
          </div>

        </div>

        <div className="chat-input-area">

          <button className="upload-button">
            📎
          </button>

          <button className="mic-button">
            🎤
          </button>

          <input
            type="text"
            placeholder="Ask something..."
          />

          <button className="send-button">
            ➤
          </button>

        </div>

      </main>

    </div>
  );
}

export default Chat;