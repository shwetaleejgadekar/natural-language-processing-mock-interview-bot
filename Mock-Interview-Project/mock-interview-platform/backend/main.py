import os
import openai
import io
import asyncio  
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
import re

# Load API Key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key is missing! Set the environment variable OPENAI_API_KEY.")

# Initialize FastAPI
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LangChain memory for conversation context
memory = ConversationBufferMemory()
chat_model = ChatOpenAI(model_name="gpt-4-turbo", openai_api_key=OPENAI_API_KEY)
conversation = ConversationChain(llm=chat_model, memory=memory)

# 🎤 AI Voice Streaming
def generate_audio_stream(text: str):
    """Generate AI voice response using OpenAI's new TTS API."""
    response = openai.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=text
    )
    return response.read()  

# 🎙️ Speech-to-Text Processing (Whisper)
def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribes user speech into text using OpenAI's Whisper model."""
    try:
        audio_stream = io.BytesIO(audio_bytes)
        audio_stream.name = "audio.mp3"

        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_stream
        )
        return response.text.strip()  
    except Exception as e:
        print(f"🚨 Whisper Transcription Error: {e}")
        return "Sorry, I couldn't understand your speech. Please try again."
    
# 🎯 Analyze Confidence Using GPT-4
def analyze_confidence(text: str) -> str:
    """Uses GPT-4 to assess the confidence level of the candidate."""
    prompt = f"""
    Analyze the confidence level of the following candidate response:
    "{text}"
    Rate confidence on a scale of 0 to 100 (where 100 is very confident).
    Provide a short explanation.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"🚨 GPT-4 Confidence Analysis Error: {e}")
        return "Confidence analysis failed."



# ✅ WebSocket Endpoint for Real-time AI Interview
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handles real-time, dynamic technical interview conversation via WebSockets."""
    await websocket.accept()
    print("✅ Client connected...")

    try:
        # 🎯 AI Introduction
        ai_response = "Hello and welcome! How are you doing today?."
        await websocket.send_json({"text": ai_response})
        await websocket.send_bytes(generate_audio_stream(ai_response))

        while True:  # ✅ Continuous back-and-forth conversation loop
            print("⌛ Waiting for user response...")
            message = await websocket.receive()  

            if "bytes" in message:  # ✅ User sent an audio response
                user_message = transcribe_audio(message["bytes"])
                await websocket.send_json({"textuser": user_message})
                print(f"🗣️ User (speech): {user_message}")

            elif "text" in message:  # ✅ User sent a text response
                user_message = message["text"]
                print(f"📝 User (text): {user_message}")

            else:
                print("⚠️ Unknown message format received.")
                await websocket.send_json({"text": "I didn't understand your response. Please try again."})
                continue  

            # 🎯 Let AI Decide What to Do Next
            ai_prompt = f"""
            You are conducting a technical interview. 
           
            
            The candidate said: "{user_message}"

            - **Greeting & Introduction**  
            - If this is the start of the interview, greet the candidate warmly based on the current time and wait for their response.  
            - If the candidate introduces themselves, give a very short introduction of yours and ask a follow-up question to learn more about their background in software engineering.  
            - If the candidate confirms readiness, explain the structure of the interview, which includes:  
                - A LeetCode-style coding question  
                - Discussion of their approach  
                - Code implementation  
                - Evaluation of their solution  

            - **Handling Candidate Questions**  
            - If the candidate asks a question before starting, answer naturally and clarify any doubts they have.  

            - **Coding Question Selection & Presentation**  
            - Ask the candidate a LeetCode-style coding question relevant to Data Structures & Algorithms, covering topics such as:  
                - Arrays, Strings, HashTables, Linked Lists, Graphs, Trees, Sorting & Searching, BFS, DFS, Two Pointers, Sliding Window, Heaps, Dynamic Programming, Stacks, Recursion, Queues. 
                - without explicitly mentioning Data Structures and Algorithms word in the response
            - **Format the question as follows:**  
                - **Problem Statement**  
                - **Example Input and Output**  
                - **Constraints**  
            - **Ask the coding question in two separate responses:**  
                - **First Response:** Provide only the **problem statement, example inputs/outputs, and constraints** without extra explanations.  
                - **Second Response:** Follow up with:  
                - "I have posted the question for you. Please take a moment to review it and let me know your understanding and high-level approach."  

            - **Understanding & Approach Discussion**  
            - When the candidate starts discussing their approach, actively listen, analyze, and provide feedback.  
            - Determine if their approach is **brute-force, optimal, or incorrect**.  
            - Ask them to explain the **time and space complexity** of their solution.  
            - If the candidate’s approach is **incorrect or suboptimal**, provide hints to guide them toward an optimal solution without giving away the complete answer.  

            - **Implementation & Code Execution**  
            - If the candidate begins coding, ask if they have any questions.  
            - If they submit their code:  
                - **Evaluate it based on:**  
                - **Correctness** (Does it solve the problem as expected?)  
                - **Efficiency** (Is it optimized for performance?)  
                - **Edge Cases** (Does it handle all scenarios?)  

            - **Behavioral & Soft Skill Assessment**  
            - Observe the candidate’s **confidence level, problem-solving ability, and communication skills** during the discussion.  

            - **Closing the Interview & Feedback**  
            - Always Provide **structured feedback** at the end of the interview, highlighting:  
                - **Strengths** (What they did well)  
                - **Areas for improvement** (Where they can improve)  
                - **Overall confidence rating on a scale of 10**  
                - **Problem-solving skills assessment on a scale of 10**
                - **Communication skills assessment on a scale of 10**
                - **Coding skills assessment on a scale of 10**
            - **Feedback should always be provided before concluding the interview.**

            - **Dynamic Adaptation**  
            - Adjust the conversation flow dynamically based on the candidate’s responses."""  


            ai_response = conversation.predict(input=ai_prompt).strip()

            # ✅ Send AI response
            
            print(f"🤖 AI: {ai_response}")

            # ✅ Send AI voice response
            if "problem statement" in ai_response.lower():
                #ai_response = conversation.predict(input=ai_prompt).strip()

                # ✅ Extract coding question from AI response
                # ✅ Improved regex to capture the full coding problem, including the constraints
                coding_question_match = re.search(
                    r"(?i)(\*\*Problem Statement:\*\*.*?)"  # Captures Problem Statement
                    r"(\n?\*\*Example Input and Output:\*\*.*?)?"  # Captures Example Section (if present)
                    r"(\n?\*\*Constraints:\*\*.*?)(?=\nI have posted the question for you|$)",  # Captures Constraints until the phrase
                    ai_response,
                    flags=re.DOTALL
                )

                # ✅ Ensure both the Problem Statement & Constraints are extracted properly
                if coding_question_match:
                    coding_question_text = (
                        (coding_question_match.group(1) or "").strip() + "\n" +  # Problem Statement
                        (coding_question_match.group(2) or "").strip() + "\n" +  # Example (if exists)
                        (coding_question_match.group(3) or "").strip()  # Constraints (fully captured)
                    ).strip()
                else:   
                    coding_question_text = None  # Prevent sending an incomplete question
                            
                # ✅ Remove the extracted coding question from the AI response
                ai_intro_text = re.sub(
                    r"(?i)\*\*Problem Statement:\*\*.*?(?=\nI have posted the question for you|$)",  
                    "",  # Remove problem statement + example + constraints but keep the remaining response
                    ai_response,
                    flags=re.DOTALL
                ).strip()

                # ✅ Send AI introduction + follow-up message first
                if ai_intro_text:
                    await websocket.send_json({"text": ai_intro_text})
                    await websocket.send_bytes(generate_audio_stream(ai_intro_text))

                # ✅ Send the extracted coding question separately as text-only
                if coding_question_text and "problem statement" in coding_question_text.lower():
                    await websocket.send_json({"text": coding_question_text})

                    # # ✅ Send a separate response asking the candidate to review the question
                    # await websocket.send_bytes(
                    #     generate_audio_stream(
                    #         "I have posted the question for you. Please take a moment to review it and share your understanding and high-level approach."
                    #     )
                    # )
            else:
                await websocket.send_json({"text": ai_response})
                await websocket.send_bytes(generate_audio_stream(ai_response))


            # ✅ Small delay to avoid overlapping responses
            await asyncio.sleep(1.5)

    except WebSocketDisconnect:
        print("❌ Client disconnected.")
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")
