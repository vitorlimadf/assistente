import speech_recognition as sr
import pyttsx3

from agente_graph import generate_thread_id, chatbot, generate_conversation_title
from conversation_storage import save_conversation

# initialize engines once to avoid delays on every utterance
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()


def speak(text: str) -> None:
    """Speak text using the system TTS engine (pyttsx3)."""
    tts_engine.say(text)
    tts_engine.runAndWait()


def listen() -> str:
    """Capture audio from the microphone and return recognized text."""
    with sr.Microphone() as source:
        print("Fale algo...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language="pt-BR")
    except sr.UnknownValueError:
        print("Não entendi. Tente novamente.")
        return ""
    except sr.RequestError as e:
        print(f"Erro de reconhecimento: {e}")
        return ""


def main() -> None:
    """Run a voice-only chat session on the command line."""
    thread_id = generate_thread_id()
    messages = []

    print("Assistente de voz iniciado. Pressione Ctrl+C para sair.")
    while True:
        try:
            text = listen()
            if not text:
                continue
            messages.append({"role": "user", "content": text})
            print(f"Você: {text}")

            response_text = ""
            for chunk in chatbot(messages[-1], thread_id=thread_id):
                if not isinstance(chunk, list):
                    response_text += chunk
                    print(chunk, end="", flush=True)
            print()

            messages.append({"role": "assistant", "content": response_text})
            speak(response_text)

            title = None
            if len(messages) >= 2 and messages[1].get("role"):
                title = generate_conversation_title(messages)
            save_conversation(thread_id, messages, title=title)
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break


if __name__ == "__main__":
    main()
