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
import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { apiFetch, getStoredToken } from "../api";
import { useAuth } from "../auth";

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

function AssistantMarkdown({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>,
        table: ({ children }) => <div className="markdown-table-wrap"><table>{children}</table></div>,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

function Chat() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // ============================================================
  // STATES
  // ============================================================

  // Real conversation, starts empty (was previously hardcoded JSX)
  const [messages, setMessages] = useState([welcomeMessage()]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);
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
    logout();
    navigate("/login");
  };

  const loadDocuments = useCallback(async () => {
    if (!getStoredToken()) return;
    try {
      const response = await apiFetch("/documents", {}, { auth: true });
      if (response.status === 401) {
        logout();
        navigate("/login", { replace: true });
        return;
      }
      if (!response.ok) throw new Error("Could not load your documents.");
      const result = await response.json();
      const loadedDocuments = result.documents || [];
      setDocuments(loadedDocuments);
      const readyIds = new Set(
        loadedDocuments.filter((document) => document.status === "ready").map((document) => document.document_id)
      );
      setSelectedDocumentIds((previous) => previous.filter((id) => readyIds.has(id)));
    } catch (error) {
      console.error("Document library error:", error);
      setStatusMessage(error.message || "Could not load your documents.");
    } finally {
      setIsLoadingDocuments(false);
    }
  }, [logout, navigate]);

  // ============================================================
  // LOAD THE CONVERSATION SIDEBAR
  // ============================================================

  useEffect(() => {
    let isActive = true;
    const token = getStoredToken();

    if (!token) {
      navigate("/login", { replace: true });
      return () => {
        isActive = false;
      };
    }

    const loadConversations = async () => {
      try {
        const response = await apiFetch("/chats", {}, { auth: true });

        if (response.status === 401) {
          logout();
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
  }, [navigate, logout]);

  useEffect(() => {
    const loadTimer = window.setTimeout(() => {
      void loadDocuments();
    }, 0);
    return () => window.clearTimeout(loadTimer);
  }, [loadDocuments]);

  const handleNewChat = () => {
    if (isSending || isLoadingConversation) return;
    setActiveChatId(null);
    setMessages([welcomeMessage()]);
    setInputText("");
    setStatusMessage("");
  };

  const handleConversationSelect = async (chatId) => {
    const token = getStoredToken();
    if (!token || isSending || isLoadingConversation || chatId === activeChatId) return;

    setIsLoadingConversation(true);
    setStatusMessage("");
    try {
      const response = await apiFetch(`/chats/${chatId}/messages`, {}, { auth: true });
      if (response.status === 401) {
        handleLogout();
        return;
      }
      if (!response.ok) throw new Error("Could not open this conversation.");

      const result = await response.json();
      const restoredMessages = (result.messages || []).map((entry) => ({
        id: entry.message_id,
        role: entry.role === "assistant" ? "bot" : "user",
        text: entry.content,
        sources: entry.sources || [],
      }));
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
    const token = getStoredToken();
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
      const response = await apiFetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          top_k: 5,
          chat_id: isLegacyConversation ? null : activeChatId,
          document_ids: selectedDocumentIds,
        }),
      }, { auth: true });

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

      if (result.chat_id) {
        setActiveChatId(result.chat_id);
        setConversations((previous) => {
          const current = previous.find((chat) => chat.chat_id === result.chat_id);
          const updatedChat = {
            chat_id: result.chat_id,
            title: current?.title || question.replace(/\s+/g, " ").slice(0, 60),
            updated_at: new Date().toISOString(),
            created_at: current?.created_at || new Date().toISOString(),
            message_count: (current?.message_count || 0) + 2,
          };
          return [updatedChat, ...previous.filter((chat) => chat.chat_id !== result.chat_id)];
        });
      }

      setMessages((previous) => [
        ...previous,
        {
          id: nextMessageId(),
          role: "bot",
          text: result.answer,
          sources: result.sources || [],
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
    const token = getStoredToken();

    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    setIsUploading(true);
    setStatusMessage(`Uploading "${file.name}"...`);

    try {
      const response = await apiFetch("/documents/upload", {
        method: "POST",
        body: formData,
      }, { auth: true });

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
      await loadDocuments();

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

  const toggleDocumentSelection = (documentId) => {
    setSelectedDocumentIds((previous) => (
      previous.includes(documentId)
        ? previous.filter((id) => id !== documentId)
        : [...previous, documentId]
    ));
  };

  const handleRenameConversation = async (conversation) => {
    const title = window.prompt("Rename conversation", conversation.title);
    if (title === null) return;
    const normalized = title.trim();
    if (!normalized) {
      setStatusMessage("Conversation title cannot be blank.");
      return;
    }
    try {
      const response = await apiFetch(`/chats/${conversation.chat_id}`, {
        method: "PATCH", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: normalized }),
      }, { auth: true });
      if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || "Could not rename conversation.");
      const result = await response.json();
      setConversations((previous) => previous.map((item) => item.chat_id === result.chat_id ? { ...item, title: result.title, updated_at: result.updated_at } : item));
    } catch (error) { setStatusMessage(error.message || "Could not rename conversation."); }
  };

  const handleDeleteConversation = async (conversation) => {
    if (!window.confirm("Delete this conversation?")) return;
    try {
      const response = await apiFetch(`/chats/${conversation.chat_id}`, { method: "DELETE" }, { auth: true });
      if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || "Could not delete conversation.");
      setConversations((previous) => previous.filter((item) => item.chat_id !== conversation.chat_id));
      if (activeChatId === conversation.chat_id) handleNewChat();
    } catch (error) { setStatusMessage(error.message || "Could not delete conversation."); }
  };

  const handleDeleteDocument = async (documentId, filename) => {
    if (isUploading || !window.confirm(`Delete "${filename}" and its indexed data?`)) return;

    try {
      const response = await apiFetch(`/documents/${documentId}`, { method: "DELETE" }, { auth: true });
      if (response.status === 401) {
        handleLogout();
        return;
      }
      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(errorBody?.detail || "Could not delete the document.");
      }
      setStatusMessage(`"${filename}" was deleted.`);
      await loadDocuments();
      setSelectedDocumentIds((previous) => previous.filter((id) => id !== documentId));
    } catch (error) {
      console.error("Document deletion error:", error);
      setStatusMessage(error.message || "Could not delete the document.");
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
      await apiFetch("/voice/stop", {
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

      const response = await apiFetch("/voice/speak", {
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
      apiFetch("/voice/stop", {
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
          Doc<span>Chat</span>
        </div>

        <div className="user-area">
          <span>Welcome, {user?.name || "User"}</span>
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
            New Chat
          </button>
          <p className="history-heading">Conversations</p>
          <div className="conversation-list">
            {isLoadingHistory && <p className="conversation-empty">Loading chats...</p>}
            {!isLoadingHistory && !conversations.length && (
              <p className="conversation-empty">Your conversations will appear here.</p>
            )}
            {conversations.map((conversation) => (
              <div className="conversation-item" key={conversation.chat_id}>
                <button
                  className={conversation.chat_id === activeChatId ? "active" : ""}
                  type="button"
                  onClick={() => handleConversationSelect(conversation.chat_id)}
                  disabled={isSending || isLoadingConversation}
                  title={conversation.title}
                >
                  {conversation.title}
                </button>
                {conversation.chat_id !== "legacy-history" && (
                  <span className="conversation-actions">
                    <button type="button" onClick={() => handleRenameConversation(conversation)} disabled={isSending} aria-label={`Rename ${conversation.title}`}>Rename</button>
                    <button type="button" onClick={() => handleDeleteConversation(conversation)} disabled={isSending} aria-label={`Delete ${conversation.title}`}>Delete</button>
                  </span>
                )}
              </div>
            ))}
          </div>
          <div className="conversation-list" aria-label="Document library">
            <p className="history-heading">Your Documents</p>
            <button
              className="new-chat-button"
              type="button"
              onClick={() => void loadDocuments()}
              disabled={isLoadingDocuments || isUploading}
            >
              Refresh Documents
            </button>
            {isLoadingDocuments && <p className="conversation-empty">Loading documents...</p>}
            {!isLoadingDocuments && !documents.length && (
              <p className="conversation-empty">Uploaded documents will appear here.</p>
            )}
            {documents.map((document) => (
              <div
                className={`conversation-item document-row ${selectedDocumentIds.includes(document.document_id) ? "selected" : ""} ${document.status === "ready" ? "" : "disabled"}`}
                key={document.document_id}
                role={document.status === "ready" ? "button" : undefined}
                tabIndex={document.status === "ready" ? 0 : undefined}
                aria-pressed={document.status === "ready" ? selectedDocumentIds.includes(document.document_id) : undefined}
                onClick={document.status === "ready" ? () => toggleDocumentSelection(document.document_id) : undefined}
                onKeyDown={document.status === "ready" ? (event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    toggleDocumentSelection(document.document_id);
                  }
                } : undefined}
              >
                <span title={document.original_filename}>📄 {document.original_filename} {selectedDocumentIds.includes(document.document_id) && "✓"}</span>
                <small>{document.status} · {document.chunk_count} chunks</small>
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    handleDeleteDocument(document.document_id, document.original_filename);
                  }}
                  disabled={document.status === "processing" || isUploading}
                >
                  Delete
                </button>
              </div>
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
                {message.role === "bot" ? <AssistantMarkdown content={message.text} /> : message.text}
              </div>

              {message.role === "bot" && (
                <>
                {message.sources?.length > 0 && (
                  <div className="message-sources">
                    Sources: {message.sources.map((source) => (
                      <div key={`${source.document_id}-${source.chunk_index}`}>
                        {source.filename} — {source.page ? `page ${source.page}` : `chunk ${source.chunk_index}`}
                      </div>
                    ))}
                  </div>
                )}
                <button
                  className="speak-button"
                  onClick={() => handleSpeak(message.id, message.text)}
                  title={speakingId === message.id ? "Stop reading" : "Read answer aloud"}
                  type="button"
                >
                  {speakingId === message.id ? "⏹" : "🔊"}
                </button>
                </>
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

        {selectedDocumentIds.length > 0 && (
          <div className="selected-document-chips" aria-label="Documents selected for chat">
            <span>Using documents:</span>
            {documents.filter((document) => selectedDocumentIds.includes(document.document_id)).map((document) => (
              <button
                type="button"
                key={document.document_id}
                onClick={() => toggleDocumentSelection(document.document_id)}
                aria-label={`Remove ${document.original_filename} from chat`}
              >
                📄 {document.original_filename} ×
              </button>
            ))}
          </div>
        )}

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
            placeholder={isLoadingHistory ? "Loading your conversation..." : "Ask a question about your documents..."}
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
