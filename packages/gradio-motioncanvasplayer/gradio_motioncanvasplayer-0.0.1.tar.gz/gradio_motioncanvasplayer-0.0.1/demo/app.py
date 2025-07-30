
import gradio as gr
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from gradio_motioncanvasplayer import MotionCanvasPlayer

project_path = "/gradio_api/file=demo/public/project-3.17.2.js"

# create a FastAPI app
app = FastAPI()


# mount FastAPI StaticFiles server
#app.mount("/public", StaticFiles(directory='demo/public'), name="public")

example = MotionCanvasPlayer().example_value()

gr.set_static_paths(paths=[Path.cwd().absolute()/"demo/public"])

demo = gr.Interface(
    lambda x:x,
    None,  # interactive version of your component
    MotionCanvasPlayer(project_path, auto=True, quality=0.5, width=1920, height=1080, variables="{}"),  # static version of your component
    clear_btn=None,
    flagging_mode=None
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
    
)


demo.launch(server_name="0.0.0.0", server_port=7860)


#app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    pass
    # serve the app
    #uvicorn.run(app, host="0.0.0.0", port=7860)