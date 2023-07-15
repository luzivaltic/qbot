import gradio as gr
from qa_openai import answer_question
import os

port = int(os.environ.get("PORT", 7860))

demo = gr.Interface(fn=answer_question, inputs="text", outputs="text")
if __name__ == "__main__":
    demo.launch(server_port=port,share=True)

gr.close_all()