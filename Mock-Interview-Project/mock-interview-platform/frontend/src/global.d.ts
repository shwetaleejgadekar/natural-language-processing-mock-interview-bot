// src/global.d.ts
declare global {
    interface SpeechRecognitionEvent extends Event {
        results: SpeechRecognitionResultList;
    }

    interface SpeechRecognitionErrorEvent extends Event {
        error: string;
    }

    interface Window {
        SpeechRecognition: typeof SpeechRecognition;
        webkitSpeechRecognition: typeof SpeechRecognition;
    }
}
   
export {}; // Ensure this file is treated as a module
