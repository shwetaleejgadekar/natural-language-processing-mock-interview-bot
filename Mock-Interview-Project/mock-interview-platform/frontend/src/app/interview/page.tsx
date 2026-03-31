"use client";

import React, { useState, useEffect, useRef } from "react";
import { Box, Button, Container, Typography, Alert, Grid } from "@mui/material";
import Editor from "@monaco-editor/react";

const API_WS_URL = "ws://localhost:8000/ws"; // WebSocket URL

const AIInterview: React.FC = () => {
    const [conversation, setConversation] = useState<string[]>([]);
    const [question, setQuestion] = useState<string>("");
    const [userCode, setUserCode] = useState<string>("");
    const [error, setError] = useState<string>("");
    const [ws, setWs] = useState<WebSocket | null>(null);
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    useEffect(() => {
        const websocket = new WebSocket(API_WS_URL);
        websocket.binaryType = "arraybuffer";

        websocket.onopen = () => {
            console.log("✅ WebSocket connected!");
            setConversation((prev) => [...prev, "🤖 AI: Connection established!"]);
        };

        websocket.onmessage = async (event: MessageEvent<ArrayBuffer | string>) => {
            try {
                if (event.data instanceof ArrayBuffer) {
                    const audioBlob = new Blob([event.data], { type: "audio/mpeg" });
                    const audioUrl = URL.createObjectURL(audioBlob);

                    if (audioRef.current) {
                        audioRef.current.src = audioUrl;
                        audioRef.current.play().catch((err) => console.error("Audio Play Error:", err));
                    }
                } else if (typeof event.data === "string") {
                    const parsedData = JSON.parse(event.data);

                    if (!!parsedData.text) {
                        setConversation((prev) => [...prev, `🤖 AI: ${parsedData.text}`]);

                    
                    if (!!parsedData.text && parsedData.text.toLowerCase().includes("**problem statement:**")) {
                            const questionasked = parsedData.text.split("problem statement")[1];
                            setQuestion(parsedData.text);
                    }
                }

                if (!!parsedData.textuser) {
                    setConversation((prev) => [...prev, `🗣️ USER: ${parsedData.textuser}`]);
                }


                }
            } catch (err) {
                console.error("Error processing WebSocket message:", err);
            }
        };

        websocket.onerror = () => {
            setError("WebSocket connection failed.");
        };

        // websocket.onclose = () => {
        //     setConversation((prev) => [...prev, "❌ Disconnected from AI interviewer."]);
        // };

        setWs(websocket);

        return () => {
            websocket.close();
        };
    }, []);

    // ✅ Start Recording
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);

            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (error) {
            setError("🎤 Microphone access denied. Please allow microphone permissions.");
            console.error("🎤 Microphone Error:", error);
        }
    };

    // ✅ Stop Recording & Send Audio
    const stopRecording = () => {
        if (!mediaRecorderRef.current) return;
        
        mediaRecorderRef.current.stop();
        setIsRecording(false);
    
        mediaRecorderRef.current.onstop = async () => {
            try {
                // ✅ Convert to a valid format before sending
                const audioBlob = new Blob(audioChunksRef.current, { type: "audio/mp3" });
                sendAudio(audioBlob);
            } catch (error) {
                console.error("🚨 Audio Processing Error:", error);
                setError("Failed to process audio. Please try again.");
            }
        };
    };
    

    // ✅ Send Audio to WebSocket
    const sendAudio = async (audioBlob: Blob) => {
        try {
            if (ws && ws.readyState === WebSocket.OPEN) {
                const file = new File([audioBlob], "audio.mp3", { type: "audio/mp3" });
    
                // Convert file to ArrayBuffer and send it
                const reader = new FileReader();
                reader.readAsArrayBuffer(file);
                reader.onloadend = () => {
                    const audioBuffer = reader.result;
                    if (audioBuffer) {
                        ws.send(audioBuffer); // ✅ Send file instead of raw bytes
                        setConversation((prev) => [...prev, "🗣️ You sent an audio message."]);
                    }
                };
            }
        } catch (error) {
            console.error("🚨 Audio Conversion Error:", error);
            setError("Failed to process audio. Please try again.");
        }
    };
    

    

    const submitCode = () => {
        if (!userCode.trim()) {
            setError("Code cannot be empty!");
            return;
        }

        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ code: userCode }));
            setConversation((prev) => [...prev, `💻 You submitted your code!`]);
        } else {
            setError("WebSocket is not connected.");
        }
    };

    return (
        <Container maxWidth="lg">
            <Box textAlign="center" mt={4}>
                <Typography variant="h4">AI Technical Interview</Typography>
                {/* {error && <Alert severity="error">{error}</Alert>} */}
            </Box>

            <Grid container spacing={2} mt={4}>
                <Grid item xs={12} md={5}>
                    <Box p={3} bgcolor="#e0e0e0" borderRadius={2} width="100%" minHeight="80px">
                        <Typography variant="h6" fontWeight="bold" color="black">
                            📝 Coding Question:
                        </Typography>
                        <Typography variant="body1" color="black" ml={1} fontSize="1.1rem">
                            {question || "Waiting for question..."}
                        </Typography>
                    </Box>
                </Grid>

                <Grid item xs={12} md={7}>
                    <Typography variant="h6">💻 Your Code:</Typography>
                    <Editor
                        height="300px"
                        defaultLanguage="python"
                        theme="vs-dark"
                        value={userCode}
                        onChange={(value) => setUserCode(value || "")}
                    />
                    <Button variant="contained"  onClick={submitCode}  sx={{ mt: 2, backgroundColor: '#059669', '&:hover': { backgroundColor: '#e64a19' } }}
                    >
                        Submit Code
                    </Button>
                     {/* Bottom Section: Conversation Transcript */}
            <Box mt={4} p={3} bgcolor="#eef2f3" borderRadius={2}>
                <Typography variant="h6">🗣️ Conversation Transcript:</Typography>
                <Box sx={{ maxHeight: "200px", overflowY: "auto", p: 1 }}>
                    {conversation.map((line, index) => (
                        <Typography key={index} variant="body1" color="Black">{line}</Typography>
                    ))}
                </Box>
            </Box>
                </Grid>
            </Grid>

            {/* 🎤 Record Button
            <Box textAlign="center" mt={4}>
                <Button
                    variant="contained"
                    color={isRecording ? "secondary" : "primary"}
                    onMouseDown={startRecording}
                    onMouseUp={stopRecording}
                    onMouseLeave={stopRecording} // Stop if user moves away
                    sx={{ fontSize: "1.2rem", p: 2 }}
                >
                    {isRecording ? "🎤 Recording... Release to Send" : "🎙️ Hold to Record"}
                </Button>
            </Box> */}

            {/* 🎤 Record Button */}
            <Box textAlign="center" mt={6}>
                <Button
                    variant="contained"
                    onMouseDown={startRecording}
                    onMouseUp={stopRecording}
                    onMouseLeave={stopRecording} // Stop if user moves away
                    sx={{
                        fontSize: "1.2rem",
                        p: 2,
                        backgroundColor: isRecording ? "#d32f2f" : "#059669", // Red when recording, green otherwise
                        "&:hover": {
                            backgroundColor: isRecording ? "#b71c1c" : "#047857", // Darker green on hover
                        },
                    }}
                >
                    {isRecording ? "🎤 Recording... Release to Send" : "🎙️ Hold to Record"}
                </Button>
            </Box>


            {/* Hidden audio element for AI-generated speech */}
            <audio ref={audioRef} hidden />
        </Container>
    );
};

export default AIInterview;
