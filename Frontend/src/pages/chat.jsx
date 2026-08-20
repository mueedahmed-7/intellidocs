// // // function Chat() {
// // //   return (
// // //     <div className="chat-page">

// // //       <header className="chat-header">

// // //         <div className="logo">
// // //           RAG<span>CHAT</span>
// // //         </div>

// // //         <div className="user-area">
// // //           <span>Welcome, User</span>
// // //           <button onClick={handleLogout}>Logout</button>
// // //         </div>

// // //       </header>

// // //       <main className="chat-container">

// // //         <div className="messages">

// // //           <div className="message user-message">
// // //             <div className="message-label">
// // //               You
// // //             </div>

// // //             <div className="message-text">
// // //               What is RAG?
// // //             </div>
// // //           </div>

// // //           <div className="message bot-message">
// // //             <div className="message-label">
// // //               RAG Chatbot
// // //             </div>

// // //             <div className="message-text">
// // //               RAG stands for Retrieval-Augmented Generation.
// // //               It allows an AI system to retrieve relevant
// // //               information from documents before generating
// // //               an answer.
// // //             </div>

// // //             <button className="speak-button">
// // //               🔊
// // //             </button>
// // //           </div>

// // //         </div>

// // //         <div className="chat-input-area">

// // //           <button className="upload-button">
// // //             📎
// // //           </button>

// // //           <button className="mic-button">
// // //             🎤
// // //           </button>

// // //           <input
// // //             type="text"
// // //             placeholder="Ask something..."
// // //           />

// // //           <button className="send-button">
// // //             ➤
// // //           </button>

// // //         </div>

// // //       </main>

// // //     </div>
// // //   );
// // // }

// // // export default Chat;
// // import { useNavigate } from "react-router-dom";

// // function Chat() {
// //   const navigate = useNavigate();

// //   const handleLogout = () => {
// //     // Remove saved login information
// //     localStorage.removeItem("user");

// //     // Go to login page
// //     navigate("/login");
// //   };

// //   return (
// //     <div className="chat-page">

// //       <header className="chat-header">

// //         <div className="logo">
// //           RAG<span>CHAT</span>
// //         </div>

// //         <div className="user-area">
// //           <span>Welcome, User</span>

// //           <button onClick={handleLogout}>
// //             Logout
// //           </button>
// //         </div>

// //       </header>

// //       <main className="chat-container">

// //         <div className="messages">

// //           <div className="message user-message">
// //             <div className="message-label">
// //               You
// //             </div>

// //             <div className="message-text">
// //               What is RAG?
// //             </div>
// //           </div>

// //           <div className="message bot-message">
// //             <div className="message-label">
// //               RAG Chatbot
// //             </div>

// //             <div className="message-text">
// //               RAG stands for Retrieval-Augmented Generation.
// //               It allows an AI system to retrieve relevant
// //               information from documents before generating
// //               an answer.
// //             </div>

// //             <button className="speak-button">
// //               🔊
// //             </button>
// //           </div>

// //         </div>

// //         <div className="chat-input-area">

// //           <button className="upload-button">
// //             📎
// //           </button>

// //           <button className="mic-button">
// //             🎤
// //           </button>

// //           <input
// //             type="text"
// //             placeholder="Ask something..."
// //           />

// //           <button className="send-button">
// //             ➤
// //           </button>

// //         </div>

// //       </main>

// //     </div>
// //   );
// // }

// // export default Chat;

// import { useState } from "react";
// import { useNavigate } from "react-router-dom";

// function Chat() {

//   const navigate = useNavigate();

//   const [speaking, setSpeaking] = useState(false);
//   const [message, setMessage] = useState("");

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
//       setMessage("Speaking...");

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

//         setMessage(
//           result.message ||
//           "Text to speech failed."
//         );

//         return;
//       }


//       setMessage(
//         "Speech completed."
//       );

//     } catch (error) {

//       console.error(
//         "TTS error:",
//         error
//       );

//       setMessage(
//         "Could not connect to voice backend."
//       );

//     } finally {

//       setSpeaking(false);

//     }
//   };


//   return (

//     <div className="chat-page">

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


//             {/* =================================================
//                 TTS BUTTON
//             ================================================= */}

//             <button
//               className="speak-button"
//               onClick={handleSpeak}
//               disabled={speaking}
//               title="Read answer aloud"
//             >

//               {speaking ? "🔊..." : "🔊"}

//             </button>

//           </div>


//         </div>


//         {/* =====================================================
//             STATUS
//         ===================================================== */}

//         {message && (

//           <p>
//             {message}
//           </p>

//         )}


//         {/* =====================================================
//             CHAT INPUT
//         ===================================================== */}

//         <div className="chat-input-area">


//           <button
//             className="upload-button"
//           >
//             📎
//           </button>


//           {/* MIC BUTTON */}

//           <button
//             className="mic-button"
//             onClick={handleSpeak}
//             disabled={speaking}
//             title="Speak chatbot response"
//           >

//             {speaking ? "🔊" : "🎤"}

//           </button>


//           <input
//             type="text"
//             placeholder="Ask something..."
//           />


//           <button
//             className="send-button"
//           >
//             ➤
//           </button>


//         </div>


//       </main>

//     </div>

//   );
// }

// export default Chat;
// import { useRef, useState } from "react";
// import { useNavigate } from "react-router-dom";

// function Chat() {

//   const navigate = useNavigate();

//   const [speaking, setSpeaking] = useState(false);
//   const [message, setMessage] = useState("");

//   // Speech-to-text state
//   const [listening, setListening] = useState(false);

//   const recognitionRef = useRef(null);


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
//       setMessage("Speaking...");

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

//         setMessage(
//           result.message ||
//           "Text to speech failed."
//         );

//         return;
//       }

//       setMessage(
//         "Speech completed."
//       );

//     } catch (error) {

//       console.error(
//         "TTS error:",
//         error
//       );

//       setMessage(
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

//     // Browser compatibility
//     const SpeechRecognition =
//       window.SpeechRecognition ||
//       window.webkitSpeechRecognition;


//     // ------------------------------------------------------------
//     // CHECK SUPPORT
//     // ------------------------------------------------------------

//     if (!SpeechRecognition) {

//       setMessage(
//         "Speech recognition is not supported. Please use Google Chrome."
//       );

//       return;
//     }


//     // ------------------------------------------------------------
//     // STOP LISTENING IF ALREADY ACTIVE
//     // ------------------------------------------------------------

//     if (listening) {

//       if (recognitionRef.current) {
//         recognitionRef.current.stop();
//       }

//       return;
//     }


//     // ------------------------------------------------------------
//     // CREATE SPEECH RECOGNITION
//     // ------------------------------------------------------------

//     const recognition =
//       new SpeechRecognition();


//     // ------------------------------------------------------------
//     // SETTINGS
//     // ------------------------------------------------------------

//     recognition.lang = "en-US";

//     recognition.continuous = false;

//     recognition.interimResults = true;


//     // ------------------------------------------------------------
//     // WHEN MICROPHONE STARTS
//     // ------------------------------------------------------------

//     recognition.onstart = () => {

//       console.log(
//         "Speech recognition started"
//       );

//       setListening(true);

//       setMessage(
//         "Listening..."
//       );

//     };


//     // ------------------------------------------------------------
//     // SPEECH RESULT
//     // ------------------------------------------------------------

//     recognition.onresult = (event) => {

//       let transcript = "";

//       for (
//         let i = event.resultIndex;
//         i < event.results.length;
//         i++
//       ) {

//         transcript +=
//           event.results[i][0].transcript;

//       }

//       console.log(
//         "Transcript:",
//         transcript
//       );

//       // Put speech into chat input
//       setMessage(transcript);

//     };


//     // ------------------------------------------------------------
//     // ERROR
//     // ------------------------------------------------------------

//     recognition.onerror = (event) => {

//       console.error(
//         "Speech recognition error:",
//         event.error
//       );

//       setListening(false);


//       if (event.error === "not-allowed") {

//         setMessage(
//           "Microphone permission was denied."
//         );

//       } else if (event.error === "no-speech") {

//         setMessage(
//           "No speech detected. Try again."
//         );

//       } else {

//         setMessage(
//           "Speech recognition failed."
//         );

//       }

//     };


//     // ------------------------------------------------------------
//     // RECOGNITION ENDED
//     // ------------------------------------------------------------

//     recognition.onend = () => {

//       console.log(
//         "Speech recognition ended"
//       );

//       setListening(false);

//     };


//     recognitionRef.current = recognition;


//     // ------------------------------------------------------------
//     // START MICROPHONE
//     // ------------------------------------------------------------

//     recognition.start();

//   };


//   return (

//     <div className="chat-page">


//       {/* ========================================================
//           HEADER
//       ======================================================== */}

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


//       {/* ========================================================
//           CHAT
//       ======================================================== */}

//       <main className="chat-container">


//         <div className="messages">


//           {/* USER MESSAGE */}

//           <div className="message user-message">

//             <div className="message-label">
//               You
//             </div>

//             <div className="message-text">
//               What is RAG?
//             </div>

//           </div>


//           {/* BOT MESSAGE */}

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


//             {/* =================================================
//                 TEXT TO SPEECH BUTTON
//             ================================================= */}

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


//         {/* =====================================================
//             STATUS
//         ===================================================== */}

//         {message && (

//           <p>
//             {message}
//           </p>

//         )}


//         {/* =====================================================
//             CHAT INPUT
//         ===================================================== */}

//         <div className="chat-input-area">


//           {/* ---------------------------------------------------
//               UPLOAD
//           --------------------------------------------------- */}

//           <button
//             className="upload-button"
//             type="button"
//           >
//             📎
//           </button>


//           {/* ---------------------------------------------------
//               MICROPHONE
//           --------------------------------------------------- */}

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
//                 ? "Stop listening"
//                 : "Speak your question"
//             }
//           >

//             {listening
//               ? "🔴"
//               : "🎤"
//             }

//           </button>


//           {/* ---------------------------------------------------
//               TEXT INPUT
//           --------------------------------------------------- */}

//           <input
//             type="text"
//             value={
//               listening
//                 ? message
//                 : message
//             }
//             onChange={(e) =>
//               setMessage(e.target.value)
//             }
//             placeholder="Ask something..."
//           />


//           {/* ---------------------------------------------------
//               SEND
//           --------------------------------------------------- */}

//           <button
//             className="send-button"
//             type="button"
//             onClick={() => {

//               console.log(
//                 "Message to send:",
//                 message
//               );

//               // RAG API will be connected here
//             }}
//           >

//             ➤

//           </button>


//         </div>


//       </main>

//     </div>

//   );

// }

// export default Chat;

import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

function Chat() {

  const navigate = useNavigate();

  // ============================================================
  // STATES
  // ============================================================

  const [speaking, setSpeaking] = useState(false);

  // Text inside chat input
  const [inputText, setInputText] = useState("");

  // Status message
  const [statusMessage, setStatusMessage] = useState("");

  // Microphone state
  const [listening, setListening] = useState(false);

  // Speech recognition reference
  const recognitionRef = useRef(null);

  // Used to prevent automatic restart when user manually stops
  const manuallyStoppedRef = useRef(false);



  // ============================================================
  // LOGOUT
  // ============================================================

  const handleLogout = () => {

    localStorage.removeItem("user");

    navigate("/login");

  };



  // ============================================================
  // TEXT TO SPEECH
  // ============================================================

  const handleSpeak = async () => {

    if (speaking) {
      return;
    }

    try {

      setSpeaking(true);
      setStatusMessage("Speaking...");

      const formData = new FormData();

      formData.append(
        "text",
        "RAG stands for Retrieval-Augmented Generation. It allows an AI system to retrieve relevant information from documents before generating an answer."
      );


      const response = await fetch(
        "http://127.0.0.1:8000/voice/speak",
        {
          method: "POST",
          body: formData,
        }
      );


      const result = await response.json();


      console.log(
        "TTS response:",
        result
      );


      if (!result.success) {

        setStatusMessage(
          result.message ||
          "Text to speech failed."
        );

        return;
      }


      setStatusMessage(
        "Speech completed."
      );

    } catch (error) {

      console.error(
        "TTS error:",
        error
      );

      setStatusMessage(
        "Could not connect to voice backend."
      );

    } finally {

      setSpeaking(false);

    }

  };



  // ============================================================
  // SPEECH TO TEXT
  // ============================================================

  const handleMic = () => {

    // ----------------------------------------------------------
    // BROWSER SUPPORT
    // ----------------------------------------------------------

    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;


    if (!SpeechRecognition) {

      setStatusMessage(
        "Speech recognition is not supported. Please use Google Chrome."
      );

      return;
    }



    // ----------------------------------------------------------
    // STOP MICROPHONE
    // ----------------------------------------------------------

    if (listening) {

      manuallyStoppedRef.current = true;

      if (recognitionRef.current) {

        recognitionRef.current.stop();

      }

      setListening(false);

      setStatusMessage(
        "Recording stopped."
      );

      return;
    }



    // ----------------------------------------------------------
    // CREATE RECOGNITION OBJECT
    // ----------------------------------------------------------

    const recognition =
      new SpeechRecognition();


    recognitionRef.current =
      recognition;



    // ----------------------------------------------------------
    // IMPORTANT SETTINGS
    // ----------------------------------------------------------

    recognition.lang = "en-US";

    // Keep listening for longer speech
    recognition.continuous = true;

    // Show partial results while speaking
    recognition.interimResults = true;

    recognition.maxAlternatives = 1;



    // ----------------------------------------------------------
    // START
    // ----------------------------------------------------------

    manuallyStoppedRef.current = false;

    setListening(true);

    setStatusMessage(
      "Listening... Speak your question."
    );


    try {

      recognition.start();

    } catch (error) {

      console.error(
        "Could not start recognition:",
        error
      );

      setListening(false);

    }



    // ==========================================================
    // WHEN MICROPHONE STARTS
    // ==========================================================

    recognition.onstart = () => {

      console.log(
        "Speech recognition started"
      );

      setListening(true);

      setStatusMessage(
        "Listening... Speak your question."
      );

    };



    // ==========================================================
    // SPEECH RESULT
    // ==========================================================

    recognition.onresult = (event) => {

      let finalTranscript = "";

      let interimTranscript = "";


      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {

        const transcript =
          event.results[i][0].transcript;


        if (
          event.results[i].isFinal
        ) {

          finalTranscript += transcript;

        } else {

          interimTranscript += transcript;

        }

      }



      // --------------------------------------------------------
      // FINAL TEXT
      // --------------------------------------------------------

      if (finalTranscript) {

        setInputText(
          previous =>
            previous +
            finalTranscript +
            " "
        );

      }



      // --------------------------------------------------------
      // INTERIM TEXT
      // --------------------------------------------------------

      if (interimTranscript) {

        setStatusMessage(
          `Listening: ${interimTranscript}`
        );

      }

    };



    // ==========================================================
    // ERROR
    // ==========================================================

    recognition.onerror = (event) => {

      console.error(
        "Speech recognition error:",
        event.error
      );


      if (
        event.error === "not-allowed"
      ) {

        setListening(false);

        setStatusMessage(
          "Microphone permission was denied."
        );

        return;
      }


      if (
        event.error === "no-speech"
      ) {

        setStatusMessage(
          "No speech detected. Keep speaking or try again."
        );

        return;
      }


      if (
        event.error === "aborted"
      ) {

        return;
      }


      setStatusMessage(
        `Speech recognition error: ${event.error}`
      );

    };



    // ==========================================================
    // RECOGNITION ENDED
    // ==========================================================

    recognition.onend = () => {

      console.log(
        "Speech recognition ended"
      );


      // --------------------------------------------------------
      // USER DID NOT PRESS STOP
      // --------------------------------------------------------

      if (
        !manuallyStoppedRef.current
      ) {

        console.log(
          "Restarting speech recognition..."
        );


        try {

          recognition.start();

          setListening(true);

          setStatusMessage(
            "Listening... Continue speaking."
          );

        } catch (error) {

          console.log(
            "Recognition restart failed:",
            error
          );

        }

      } else {

        setListening(false);

      }

    };

  };



  // ============================================================
  // SEND MESSAGE
  // ============================================================

  const handleSend = () => {

    if (!inputText.trim()) {
      return;
    }


    console.log(
      "Message to send:",
      inputText
    );


    // RAG API will be connected here later

    setStatusMessage(
      "Message ready to send."
    );

  };



  // ============================================================
  // UI
  // ============================================================

  return (

    <div className="chat-page">


      {/* ======================================================
          HEADER
      ====================================================== */}

      <header className="chat-header">

        <div className="logo">
          RAG<span>CHAT</span>
        </div>


        <div className="user-area">

          <span>
            Welcome, User
          </span>


          <button
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>



      {/* ======================================================
          CHAT
      ====================================================== */}

      <main className="chat-container">


        <div className="messages">


          {/* ==================================================
              USER MESSAGE
          ================================================== */}

          <div className="message user-message">

            <div className="message-label">
              You
            </div>


            <div className="message-text">
              What is RAG?
            </div>

          </div>



          {/* ==================================================
              BOT MESSAGE
          ================================================== */}

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



            {/* TEXT TO SPEECH */}

            <button
              className="speak-button"
              onClick={handleSpeak}
              disabled={speaking}
              title="Read answer aloud"
            >

              {speaking
                ? "🔊..."
                : "🔊"
              }

            </button>

          </div>


        </div>



        {/* ====================================================
            STATUS
        ==================================================== */}

        {statusMessage && (

          <p>
            {statusMessage}
          </p>

        )}



        {/* ====================================================
            CHAT INPUT
        ==================================================== */}

        <div className="chat-input-area">


          {/* --------------------------------------------------
              UPLOAD
          -------------------------------------------------- */}

          <button
            className="upload-button"
            type="button"
          >
            📎
          </button>



          {/* --------------------------------------------------
              MICROPHONE
          -------------------------------------------------- */}

          <button
            className={
              listening
                ? "mic-button listening"
                : "mic-button"
            }
            onClick={handleMic}
            type="button"
            title={
              listening
                ? "Stop recording"
                : "Speak your question"
            }
          >

            {listening
              ? "⏹️"
              : "🎤"
            }

          </button>



          {/* --------------------------------------------------
              TEXT INPUT
          -------------------------------------------------- */}

          <input
            type="text"
            value={inputText}
            onChange={(e) =>
              setInputText(e.target.value)
            }
            placeholder="Ask something..."
          />



          {/* --------------------------------------------------
              SEND
          -------------------------------------------------- */}

          <button
            className="send-button"
            type="button"
            onClick={handleSend}
          >

            ➤

          </button>


        </div>


      </main>


    </div>

  );

}


export default Chat;