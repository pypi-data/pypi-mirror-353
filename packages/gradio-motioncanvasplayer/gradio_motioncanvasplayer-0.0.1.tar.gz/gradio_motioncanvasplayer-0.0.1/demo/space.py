
import gradio as gr
from app import demo as app
import os

_docs = {'MotionCanvasPlayer': {'description': 'Creates a component to display arbitrary MotionCanvasPlayer output. As this component does not accept user input, it is rarely used as an input component.\n', 'members': {'__init__': {'value': {'type': 'str | Callable | None', 'default': 'None', 'description': 'The MotionCanvasPlayer content to display. Only static MotionCanvasPlayer is rendered (e.g. no JavaScript. To render JavaScript, use the `js` or `head` parameters in the `Blocks` constructor). If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'The label for this component. Is used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool', 'default': 'False', 'description': 'If True, the label will be displayed. If False, the label will be hidden.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the MotionCanvasPlayer DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the MotionCanvasPlayer DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'min_height': {'type': 'int | None', 'default': 'None', 'description': 'The minimum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If MotionCanvasPlayer content exceeds the height, the component will expand to fit the content.'}, 'max_height': {'type': 'int | None', 'default': 'None', 'description': 'The maximum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If content exceeds the height, the component will scroll.'}, 'container': {'type': 'bool', 'default': 'False', 'description': 'If True, the MotionCanvasPlayer component will be displayed in a container. Default is False.'}, 'padding': {'type': 'bool', 'default': 'True', 'description': 'If True, the MotionCanvasPlayer component will have a certain padding (set by the `--block-padding` CSS variable) in all directions. Default is True.'}, 'auto': {'type': 'bool | None', 'default': 'False', 'description': 'If True, the MotionCanvasPlayer component will automatically play the animation. Default is False.'}, 'quality': {'type': 'number | None', 'default': 'None', 'description': "The quality of the MotionCanvasPlayer component. Default is None which uses the project's default settings."}, 'width': {'type': 'int | None', 'default': 'None', 'description': "The width of the MotionCanvasPlayer component. Default is None which uses the project's default settings."}, 'height': {'type': 'int | None', 'default': 'None', 'description': "The height of the MotionCanvasPlayer component. Default is None which uses the project's default settings."}, 'variables': {'type': 'str | None', 'default': 'None', 'description': 'The variables of the MotionCanvasPlayer component as a JSON string. Default is None.'}}, 'postprocess': {'value': {'type': 'str | None', 'description': 'Expects a `str` consisting of valid MotionCanvasPlayer.'}}, 'preprocess': {'return': {'type': 'str | None', 'description': '(Rarely used) passes the MotionCanvasPlayer as a `str`.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the MotionCanvasPlayer changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'click': {'type': None, 'default': None, 'description': 'Triggered when the MotionCanvasPlayer is clicked.'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'MotionCanvasPlayer': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_motioncanvasplayer`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

Motion Canvas Player to render Motion Canvas projects
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_motioncanvasplayer
```

## Usage

```python

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
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `MotionCanvasPlayer`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["MotionCanvasPlayer"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["MotionCanvasPlayer"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, (Rarely used) passes the MotionCanvasPlayer as a `str`.
- **As output:** Should return, expects a `str` consisting of valid MotionCanvasPlayer.

 ```python
def predict(
    value: str | None
) -> str | None:
    return value
```
""", elem_classes=["md-custom", "MotionCanvasPlayer-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          MotionCanvasPlayer: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
