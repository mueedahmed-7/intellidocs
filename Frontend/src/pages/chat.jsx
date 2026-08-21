// import { useRef, useState } from "react";
// import { useNavigate } from "react-router-dom";

// function Chat() {

//   const navigate = useNavigate();

//   // ============================================================
//   // STATES
//   // ============================================================

//   const [speaking, setSpeaking] = useState(false);

//   // Text inside chat input
//   const [inputText, setInputText] = useState("");

//   // Status message
//   const [statusMessage, setStatusMessage] = useState("");

//   // Microphone state
//   const [listening, setListening] = useState(false);

//   // Speech recognition reference
//   const recognitionRef = useRef(null);

//   // Used to prevent automatic restart when user manually stops
//   const manuallyStoppedRef = useRef(false);



//   // ============================================================
//   // LOGOUT
//   // ============================================================

//   const handleLogout = () => {

//     localStorage.removeItem("user");

//     navigate("/login");

//   };



//   // ============================================================
//   // TEXT TO SPEECH
//   // ============================================================

//   const handleSpeak = async () => {

//     if (speaking) {
//       return;
//     }

//     try {

//       setSpeaking(true);
//       setStatusMessage("Speaking...");

//       const formData = new FormData();

//       formData.append(
//         "text",
//         "RAG stands for Retrieval-Augmented Generation. It allows an AI system to retrieve relevant information from documents before generating an answer."
//       );


//       const response = await fetch(
//         "http://127.0.0.1:8000/voice/speak",
//         {
//           method: "POST",
//           body: formData,
//         }
//       );


//       const result = await response.json();


//       console.log(
//         "TTS response:",
//         result
//       );


//       if (!result.success) {

//         setStatusMessage(
//           result.message ||
//           "Text to speech failed."
//         );

//         return;
//       }


//       setStatusMessage(
//         "Speech completed."
//       );

//     } catch (error) {

//       console.error(
//         "TTS error:",
//         error
//       );

//       setStatusMessage(
//         "Could not connect to voice backend."
//       );

//     } finally {

//       setSpeaking(false);

//     }

//   };



//   // ============================================================
//   // SPEECH TO TEXT
//   // ============================================================

//   const handleMic = () => {

//     // ----------------------------------------------------------
//     // BROWSER SUPPORT
//     // ----------------------------------------------------------

//     const SpeechRecognition =
//       window.SpeechRecognition ||
//       window.webkitSpeechRecognition;


//     if (!SpeechRecognition) {

//       setStatusMessage(
//         "Speech recognition is not supported. Please use Google Chrome."
//       );

//       return;
//     }



//     // ----------------------------------------------------------
//     // STOP MICROPHONE
//     // ----------------------------------------------------------

//     if (listening) {

//       manuallyStoppedRef.current = true;

//       if (recognitionRef.current) {

//         recognitionRef.current.stop();

//       }

//       setListening(false);

//       setStatusMessage(
//         "Recording stopped."
//       );

//       return;
//     }



//     // ----------------------------------------------------------
//     // CREATE RECOGNITION OBJECT
//     // ----------------------------------------------------------

//     const recognition =
//       new SpeechRecognition();


//     recognitionRef.current =
//       recognition;



//     // ----------------------------------------------------------
//     // IMPORTANT SETTINGS
//     // ----------------------------------------------------------

//     recognition.lang = "en-US";

//     // Keep listening for longer speech
//     recognition.continuous = true;

//     // Show partial results while speaking
//     recognition.interimResults = true;

//     recognition.maxAlternatives = 1;



//     // ----------------------------------------------------------
//     // START
//     // ----------------------------------------------------------

//     manuallyStoppedRef.current = false;

//     setListening(true);

//     setStatusMessage(
//       "Listening... Speak your question."
//     );


//     try {

//       recognition.start();

//     } catch (error) {

//       console.error(
//         "Could not start recognition:",
//         error
//       );

//       setListening(false);

//     }



//     // ==========================================================
//     // WHEN MICROPHONE STARTS
//     // ==========================================================

//     recognition.onstart = () => {

//       console.log(
//         "Speech recognition started"
//       );

//       setListening(true);

//       setStatusMessage(
//         "Listening... Speak your question."
//       );

//     };



//     // ==========================================================
//     // SPEECH RESULT
//     // ==========================================================

//     recognition.onresult = (event) => {

//       let finalTranscript = "";

//       let interimTranscript = "";


//       for (
//         let i = event.resultIndex;
//         i < event.results.length;
//         i++
//       ) {

//         const transcript =
//           event.results[i][0].transcript;


//         if (
//           event.results[i].isFinal
//         ) {

//           finalTranscript += transcript;

//         } else {

//           interimTranscript += transcript;

//         }

//       }



//       // --------------------------------------------------------
//       // FINAL TEXT
//       // --------------------------------------------------------

//       if (finalTranscript) {

//         setInputText(
//           previous =>
//             previous +
//             finalTranscript +
//             " "
//         );

//       }



//       // --------------------------------------------------------
//       // INTERIM TEXT
//       // --------------------------------------------------------

//       if (interimTranscript) {

//         setStatusMessage(
//           `Listening: ${interimTranscript}`
//         );

//       }

//     };



//     // ==========================================================
//     // ERROR
//     // ==========================================================

//     recognition.onerror = (event) => {

//       console.error(
//         "Speech recognition error:",
//         event.error
//       );


//       if (
//         event.error === "not-allowed"
//       ) {

//         setListening(false);

//         setStatusMessage(
//           "Microphone permission was denied."
//         );

//         return;
//       }


//       if (
//         event.error === "no-speech"
//       ) {

//         setStatusMessage(
//           "No speech detected. Keep speaking or try again."
//         );

//         return;
//       }


//       if (
//         event.error === "aborted"
//       ) {

//         return;
//       }


//       setStatusMessage(
//         `Speech recognition error: ${event.error}`
//       );

//     };



//     // ==========================================================
//     // RECOGNITION ENDED
//     // ==========================================================

//     recognition.onend = () => {

//       console.log(
//         "Speech recognition ended"
//       );


//       // --------------------------------------------------------
//       // USER DID NOT PRESS STOP
//       // --------------------------------------------------------

//       if (
//         !manuallyStoppedRef.current
//       ) {

//         console.log(
//           "Restarting speech recognition..."
//         );


//         try {

//           recognition.start();

//           setListening(true);

//           setStatusMessage(
//             "Listening... Continue speaking."
//           );

//         } catch (error) {

//           console.log(
//             "Recognition restart failed:",
//             error
//           );

//         }

//       } else {

//         setListening(false);

//       }

//     };

//   };



//   // ============================================================
//   // SEND MESSAGE
//   // ============================================================

//   const handleSend = () => {

//     if (!inputText.trim()) {
//       return;
//     }


//     console.log(
//       "Message to send:",
//       inputText
//     );


//     // RAG API will be connected here later

//     setStatusMessage(
//       "Message ready to send."
//     );

//   };



//   // ============================================================
//   // UI
//   // ============================================================

//   return (

//     <div className="chat-page">


//       {/* ======================================================
//           HEADER
//       ====================================================== */}

//       <header className="chat-header">

//         <div className="logo">
//           RAG<span>CHAT</span>
//         </div>


//         <div className="user-area">

//           <span>
//             Welcome, User
//           </span>


//           <button
//             onClick={handleLogout}
//           >
//             Logout
//           </button>

//         </div>

//       </header>



//       {/* ======================================================
//           CHAT
//       ====================================================== */}

//       <main className="chat-container">


//         <div className="messages">


//           {/* ==================================================
//               USER MESSAGE
//           ================================================== */}

//           <div className="message user-message">

//             <div className="message-label">
//               You
//             </div>


//             <div className="message-text">
//               What is RAG?
//             </div>

//           </div>



//           {/* ==================================================
//               BOT MESSAGE
//           ================================================== */}

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



//             {/* TEXT TO SPEECH */}

//             <button
//               className="speak-button"
//               onClick={handleSpeak}
//               disabled={speaking}
//               title="Read answer aloud"
//             >

//               {speaking
//                 ? "🔊..."
//                 : "🔊"
//               }

//             </button>

//           </div>


//         </div>



//         {/* ====================================================
//             STATUS
//         ==================================================== */}

//         {statusMessage && (

//           <p>
//             {statusMessage}
//           </p>

//         )}



//         {/* ====================================================
//             CHAT INPUT
//         ==================================================== */}

//         <div className="chat-input-area">


//           {/* --------------------------------------------------
//               UPLOAD
//           -------------------------------------------------- */}

//           <button
//             className="upload-button"
//             type="button"
//           >
//             📎
//           </button>



//           {/* --------------------------------------------------
//               MICROPHONE
//           -------------------------------------------------- */}

//           <button
//             className={
//               listening
//                 ? "mic-button listening"
//                 : "mic-button"
//             }
//             onClick={handleMic}
//             type="button"
//             title={
//               listening
//                 ? "Stop recording"
//                 : "Speak your question"
//             }
//           >

//             {listening
//               ? "⏹️"
//               : "🎤"
//             }

//           </button>



//           {/* --------------------------------------------------
//               TEXT INPUT
//           -------------------------------------------------- */}

//           <input
//             type="text"
//             value={inputText}
//             onChange={(e) =>
//               setInputText(e.target.value)
//             }
//             placeholder="Ask something..."
//           />



//           {/* --------------------------------------------------
//               SEND
//           -------------------------------------------------- */}

//           <button
//             className="send-button"
//             type="button"
//             onClick={handleSend}
//           >

//             ➤

//           </button>


//         </div>


//       </main>


//     </div>

//   );

// }


// export default Chat;
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_URL } from "../api";

const API_BASE_URL = API_URL;

let messageIdCounter = 0;
function nextMessageId() {
  messageIdCounter += 1;
  return `msg-${Date.now()}-${messageIdCounter}`;
}

function welcomeMessage() {
  return {
    id: nextMessageId(),
    role: "bot",
    text: "Hi! Ask me anything, or upload a document and I'll answer from it.",
  };
}

// The model commonly uses Markdown for emphasis. Render the safe inline
// formatting we support instead of displaying its Markdown characters.
function renderBotText(text) {
  return text.split(/(\*\*[^*]+?\*\*|`[^`]+?`)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }

    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={index}>{part.slice(1, -1)}</code>;
    }

    return part;
  });
}

function Chat() {
  const navigate = useNavigate();

  // ============================================================
  // STATES
  // ============================================================

  // Real conversation, starts empty (was previously hardcoded JSX)
  const [messages, setMessages] = useState([welcomeMessage()]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const messagesEndRef = useRef(null);

  // Which message is currently being spoken (null when nothing is playing)
  const [speakingId, setSpeakingId] = useState(null);
  const ttsAbortControllerRef = useRef(null);

  // Waiting for the /chat API to respond
  const [isSending, setIsSending] = useState(false);

  // Text inside chat input
  const [inputText, setInputText] = useState("");

  // Status / error banner text
  const [statusMessage, setStatusMessage] = useState("");

  // Document upload state
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  // Microphone state
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);
  const manuallyStoppedRef = useRef(false);

  // ============================================================
  // LOGOUT
  // ============================================================

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_name");
    localStorage.removeItem("user_email");
    navigate("/login");
  };

  // ============================================================
  // LOAD THE CONVERSATION SIDEBAR
  // ============================================================

  useEffect(() => {
    let isActive = true;
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/login", { replace: true });
      return () => {
        isActive = false;
      };
    }

    const loadConversations = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/chats`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.status === 401) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("user_id");
          localStorage.removeItem("user_name");
          localStorage.removeItem("user_email");
          navigate("/login", { replace: true });
          return;
        }

        if (!response.ok) {
          throw new Error("Could not load your saved conversations.");
        }

        const result = await response.json();
        if (isActive) {
          setConversations(result.chats || []);
        }
      } catch (error) {
        console.error("Conversation history error:", error);
        if (isActive) {
          setStatusMessage(error.message || "Could not load saved conversations.");
        }
      } finally {
        if (isActive) {
          setIsLoadingHistory(false);
        }
      }
    };

    loadConversations();

    return () => {
      isActive = false;
    };
  }, [navigate]);

  const handleNewChat = () => {
    if (isSending || isLoadingConversation) return;
    setActiveChatId(null);
    setMessages([welcomeMessage()]);
    setInputText("");
    setStatusMessage("");
  };

  const handleConversationSelect = async (chatId) => {
    const token = localStorage.getItem("access_token");
    if (!token || isSending || isLoadingConversation || chatId === activeChatId) return;

    setIsLoadingConversation(true);
    setStatusMessage("");
    try {
      const response = await fetch(`${API_BASE_URL}/chats/${chatId}/messages`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.status === 401) {
        handleLogout();
        return;
      }
      if (!response.ok) throw new Error("Could not open this conversation.");

      const result = await response.json();
      const restoredMessages = (result.messages || []).flatMap((entry) => [
        { id: `${entry.id}-question`, role: "user", text: entry.question },
        { id: `${entry.id}-answer`, role: "bot", text: entry.answer },
      ]);
      setActiveChatId(chatId);
      setMessages(restoredMessages.length ? restoredMessages : [welcomeMessage()]);
    } catch (error) {
      console.error("Conversation load error:", error);
      setStatusMessage(error.message || "Could not open this conversation.");
    } finally {
      setIsLoadingConversation(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending, isLoadingHistory, isLoadingConversation]);

  // ============================================================
  // SEND MESSAGE -> POST /chat
  // ============================================================

  const handleSend = async () => {
    const question = inputText.trim();
    const token = localStorage.getItem("access_token");
    const isLegacyConversation = activeChatId === "legacy-history";

    if (!question || isSending || isLoadingHistory || isLoadingConversation) {
      return;
    }

    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    const userMessage = {
      id: nextMessageId(),
      role: "user",
      text: question,
    };

    setMessages((previous) => isLegacyConversation ? [userMessage] : [...previous, userMessage]);
    setInputText("");
    setStatusMessage("");
    setIsSending(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          question,
          top_k: 5,
          chat_id: isLegacyConversation ? null : activeChatId,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);

        if (response.status === 401) {
          handleLogout();
          return;
        }

        throw new Error(
          errorBody?.detail || `Request failed with status ${response.status}.`
        );
      }

      const result = await response.json();

      setActiveChatId(result.chat_id);
      setConversations((previous) => {
        const current = previous.find((chat) => chat.id === result.chat_id);
        const updatedChat = {
          id: result.chat_id,
          title: current?.title || question.replace(/\s+/g, " ").slice(0, 60),
          updated_at: new Date().toISOString(),
        };
        return [updatedChat, ...previous.filter((chat) => chat.id !== result.chat_id)];
      });

      setMessages((previous) => [
        ...previous,
        {
          id: nextMessageId(),
          role: "bot",
          text: result.answer,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((previous) => [
        ...previous,
        {
          id: nextMessageId(),
          role: "bot",
          text: "Sorry, I couldn't reach the server. Please try again.",
        },
      ]);

      setStatusMessage(error.message || "Could not connect to chat backend.");
    } finally {
      setIsSending(false);
    }
  };

  const handleInputKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  // ============================================================
  // DOCUMENT UPLOAD -> POST /documents/upload
  // ============================================================

  const handleUploadClick = () => {
    if (isUploading || isLoadingHistory || isLoadingConversation) {
      return;
    }
    fileInputRef.current?.click();
  };

  const handleFileSelected = async (event) => {
    const file = event.target.files?.[0];

    // Reset the input so selecting the same file again still fires onChange
    event.target.value = "";

    if (!file) {
      return;
    }

    const allowedExtensions = [".pdf", ".docx", ".txt", ".md"];
    const extension = file.name
      .slice(file.name.lastIndexOf("."))
      .toLowerCase();

    if (!allowedExtensions.includes(extension)) {
      setStatusMessage(
        `Unsupported file type "${extension}". Allowed: ${allowedExtensions.join(", ")}`
      );
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    setIsUploading(true);
    setStatusMessage(`Uploading "${file.name}"...`);

    try {
      const response = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);

        if (response.status === 401) {
          handleLogout();
          return;
        }

        throw new Error(
          errorBody?.detail || `Upload failed with status ${response.status}.`
        );
      }

      const result = await response.json();

      setStatusMessage(
        `"${result.filename}" uploaded and indexed (${result.chunks_stored} chunks).`
      );

      setMessages((previous) => [
        ...previous,
        {
          id: nextMessageId(),
          role: "bot",
          text: `I've indexed "${result.filename}". Ask me anything about it.`,
        },
      ]);
    } catch (error) {
      console.error("Upload error:", error);
      setStatusMessage(error.message || "Could not upload document.");
    } finally {
      setIsUploading(false);
    }
  };

  // ============================================================
  // TEXT TO SPEECH -> POST /voice/speak
  // ============================================================

  const handleStopSpeak = async () => {
    const controller = ttsAbortControllerRef.current;
    ttsAbortControllerRef.current = null;

    if (controller) {
      controller.abort();
    }

    setSpeakingId(null);
    setStatusMessage("Speech stopped.");

    try {
      await fetch(`${API_BASE_URL}/voice/stop`, {
        method: "POST",
      });
    } catch (error) {
      // The local request was still cancelled, even if the stop endpoint is
      // temporarily unreachable.
      console.error("Could not stop server-side speech:", error);
    }
  };

  const handleSpeak = async (messageId, text) => {
    if (speakingId === messageId) {
      await handleStopSpeak();
      return;
    }

    if (speakingId) {
      await handleStopSpeak();
      return;
    }

    const controller = new AbortController();
    ttsAbortControllerRef.current = controller;

    try {
      setSpeakingId(messageId);
      setStatusMessage("Speaking...");

      const formData = new FormData();
      formData.append("text", text);

      const response = await fetch(`${API_BASE_URL}/voice/speak`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      const result = await response.json();

      if (!result.success) {
        setStatusMessage(result.message || "Text to speech failed.");
        return;
      }

      setStatusMessage("Speech completed.");
    } catch (error) {
      if (error.name === "AbortError") {
        return;
      }
      console.error("TTS error:", error);
      setStatusMessage("Could not connect to voice backend.");
    } finally {
      if (ttsAbortControllerRef.current === controller) {
        ttsAbortControllerRef.current = null;
        setSpeakingId(null);
      }
    }
  };

  useEffect(() => () => {
    const controller = ttsAbortControllerRef.current;
    if (controller) {
      controller.abort();
      fetch(`${API_BASE_URL}/voice/stop`, {
        method: "POST",
        keepalive: true,
      }).catch(() => {});
    }
  }, []);

  // ============================================================
  // SPEECH TO TEXT (browser Web Speech API)
  // ============================================================

  const handleMic = () => {
    if (isLoadingHistory || isLoadingConversation) return;
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setStatusMessage(
        "Speech recognition is not supported. Please use Google Chrome."
      );
      return;
    }

    // Stop microphone if already listening
    if (listening) {
      manuallyStoppedRef.current = true;

      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }

      setListening(false);
      setStatusMessage("Recording stopped.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.lang = "en-US";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    manuallyStoppedRef.current = false;
    setListening(true);
    setStatusMessage("Listening... Speak your question.");

    try {
      recognition.start();
    } catch (error) {
      console.error("Could not start recognition:", error);
      setListening(false);
    }

    recognition.onstart = () => {
      setListening(true);
      setStatusMessage("Listening... Speak your question.");
    };

    recognition.onresult = (event) => {
      let finalTranscript = "";
      let interimTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;

        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      if (finalTranscript) {
        setInputText((previous) => (previous + finalTranscript + " ").trimStart());
      }

      if (interimTranscript) {
        setStatusMessage(`Listening: ${interimTranscript}`);
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);

      if (event.error === "not-allowed") {
        setListening(false);
        setStatusMessage("Microphone permission was denied.");
        return;
      }

      if (event.error === "no-speech") {
        setStatusMessage("No speech detected. Keep speaking or try again.");
        return;
      }

      if (event.error === "aborted") {
        return;
      }

      setStatusMessage(`Speech recognition error: ${event.error}`);
    };

    recognition.onend = () => {
      if (!manuallyStoppedRef.current) {
        try {
          recognition.start();
          setListening(true);
          setStatusMessage("Listening... Continue speaking.");
        } catch (error) {
          console.log("Recognition restart failed:", error);
        }
      } else {
        setListening(false);
      }
    };
  };

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="chat-page">
      {/* HEADER */}
      <header className="chat-header">
        <div className="logo">
          RAG<span>CHAT</span>
        </div>

        <div className="user-area">
          <span>Welcome, User</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </header>

      {/* CHAT */}
      <main className="chat-workspace">
        <aside className="history-sidebar" aria-label="Chat history">
          <button
            className="new-chat-button"
            type="button"
            onClick={handleNewChat}
            disabled={isSending || isLoadingConversation}
          >
            + New chat
          </button>
          <p className="history-heading">Previous chats</p>
          <div className="conversation-list">
            {isLoadingHistory && <p className="conversation-empty">Loading chats...</p>}
            {!isLoadingHistory && !conversations.length && (
              <p className="conversation-empty">Your conversations will appear here.</p>
            )}
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                className={
                  conversation.id === activeChatId
                    ? "conversation-item active"
                    : "conversation-item"
                }
                type="button"
                onClick={() => handleConversationSelect(conversation.id)}
                disabled={isSending || isLoadingConversation}
                title={conversation.title}
              >
                {conversation.title}
              </button>
            ))}
          </div>
        </aside>

        <section className="chat-container">
        <div className="messages">
          {isLoadingConversation && (
            <div className="history-loading">Opening conversation...</div>
          )}
          {messages.map((message) => (
            <div
              key={message.id}
              className={
                message.role === "user"
                  ? "message user-message"
                  : "message bot-message"
              }
            >
              <div className="message-label">
                {message.role === "user" ? "You" : "RAG Chatbot"}
              </div>

              <div className="message-text">
                {message.role === "bot" ? renderBotText(message.text) : message.text}
              </div>

              {message.role === "bot" && (
                <button
                  className="speak-button"
                  onClick={() => handleSpeak(message.id, message.text)}
                  title={speakingId === message.id ? "Stop reading" : "Read answer aloud"}
                  type="button"
                >
                  {speakingId === message.id ? "⏹" : "🔊"}
                </button>
              )}
            </div>
          ))}

          {isSending && (
            <div className="message bot-message">
              <div className="message-label">RAG Chatbot</div>
              <div className="message-text">Thinking...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* STATUS */}
        {statusMessage && <p className="status-message">{statusMessage}</p>}

        {/* CHAT INPUT */}
        <div className="chat-input-area">
          {/* Hidden file input, triggered by the paperclip button */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelected}
            accept=".pdf,.docx,.txt,.md"
            style={{ display: "none" }}
          />

          <button
            className="upload-button"
            type="button"
            onClick={handleUploadClick}
            disabled={isUploading}
            title="Upload a document"
          >
            {isUploading ? "⏳" : "📎"}
          </button>

          <button
            className={listening ? "mic-button listening" : "mic-button"}
            onClick={handleMic}
            type="button"
            title={listening ? "Stop recording" : "Speak your question"}
          >
            {listening ? "⏹️" : "🎤"}
          </button>

          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleInputKeyDown}
            placeholder={isLoadingHistory ? "Loading your conversation..." : "Ask something..."}
            disabled={isLoadingHistory || isLoadingConversation}
          />

          <button
            className="send-button"
            type="button"
            onClick={handleSend}
            disabled={isSending || isLoadingHistory || isLoadingConversation || !inputText.trim()}
          >
            ➤
          </button>
        </div>
        </section>
      </main>
    </div>
  );
}

export default Chat;
