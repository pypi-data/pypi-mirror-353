
import gradio as gr
import os

from gradio_motioncanvasplayer import MotionCanvasPlayer

gr.set_static_paths(paths=[os.path.join(os.path.dirname(__file__), "public")])
project_local_path = os.path.join(os.path.dirname(__file__), "public/project-3.17.2.js")
project_api_path = "/gradio_api/file=" + project_local_path


demo = gr.Interface(
    lambda x:x,
    None,  # interactive version of your component, not relevant for this demo
    MotionCanvasPlayer(project_api_path, auto=True, quality=0.5, width=1920, height=1080, variables="{}"),  # static version of your component
    clear_btn=None

)

if __name__ == '__main__':
    demo.launch(server_name="0.0.0.0", server_port=7860)