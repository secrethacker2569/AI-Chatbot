import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import scrolledtext
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")


Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GROQ_API_KEY")

client = Groq(api_key=GroqAPIKey)


messages = []


System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""


SystemChatBot = [
    {"role": "system", "content":System}
]


try:
    with open(r"Chatlog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:

    with open(r"Chatlog.json", "w") as f:
        dump([], f)


def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")


    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} seconds.\n"
    return data


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response. """

    try:

        with open(r"Chatlog.json", "r") as f:
            messages = load(f)


        messages.append({"role": "user", "content": f"{Query}"})


        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""


        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")


        messages.append({"role": "assistant", "content": Answer})


        with open(r"Chatlog.json", "w") as f:
            dump(messages, f, indent=4)


        return AnswerModifier(Answer=Answer)
    
    except Exception as e:

        print(f"Error: {e}")
        with open(r"Chatlog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)
    
        

# Handle sending
def send_message(event=None):
    user_msg = input_box.get("1.0", "end-1c").strip()
    if not user_msg:
        return

    chat_area.config(state='normal')
    chat_area.insert("end", f"You: {user_msg}\n", "user")

    bot_reply = ChatBot(user_msg)
    chat_area.insert("end", f"Bot: {bot_reply}\n\n", "bot")
    chat_area.config(state='disabled')
    input_box.delete("1.0", "end")

# App window
root = ttk.Window(themename="darkly") 
root.title("Zenthos.ai")
root.geometry("600x600")


# Chat display
chat_area = scrolledtext.ScrolledText(
    root, wrap="word", font=("Segoe UI", 11), state='disabled', height=25
)
chat_area.pack(padx=15, pady=(15, 0), fill="both", expand=True)
chat_area.tag_config("user", foreground="blue")
chat_area.tag_config("bot", foreground="green")

# Bottom frame
bottom_frame = ttk.Frame(root)
bottom_frame.pack(padx=15, pady=15, fill="x")

# Input box (Text widget, no bootstyle!)
input_box = ttk.Text(bottom_frame, height=3, font=("Segoe UI", 11), wrap="word")
input_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
input_box.focus()

# Send button
send_btn = ttk.Button(bottom_frame, text="Send", bootstyle="success", command=send_message)
send_btn.pack(side="right")

# Bind Enter and Shift+Enter
def on_key_press(event):
    if event.keysym == 'Return' and not event.state & 0x0001:  # Enter without Shift
        send_message()
        return "break"

input_box.bind("<KeyPress>", on_key_press)

root.mainloop()
