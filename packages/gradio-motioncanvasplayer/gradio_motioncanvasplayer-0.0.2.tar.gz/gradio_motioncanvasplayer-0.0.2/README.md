---
tags: [gradio-custom-component, HTML, Motion Canvas, Animation, Player, custom-component-track]
title: gradio_motioncanvasplayer
short_description: Motion Canvas Player to render Motion Canvas projects
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_motioncanvasplayer`
<a href="https://pypi.org/project/gradio_motioncanvasplayer/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_motioncanvasplayer"></a> <a href="https://github.com/prathje/gradio-motioncanvasplayer/issues" target="_blank"><img alt="Static Badge" src="https://img.shields.io/badge/Issues-white?logo=github&logoColor=black"></a> <a href="https://huggingface.co/spaces/prathje/gradio_motioncanvasplayer/discussions" target="_blank"><img alt="Static Badge" src="https://img.shields.io/badge/%F0%9F%A4%97%20Discuss-%23097EFF?style=flat&logoColor=black"></a>

This custom component for Gradio displays Motion Canvas projects in the browser. Motion Canvas is a library for generating animations, videos, or presentations via the Canvas API. All animations are defined by code - an excellent playground for AI agents. An exemplary demo for this component is available in this Huggingface Space: https://huggingface.co/spaces/prathje/gradio_motioncanvasplayer. The source code for the included project can be found at: https://github.com/prathje/gradio-motion-canvas-example.

## Installation

```bash
pip install gradio_motioncanvasplayer
```

## Usage

```python

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
```

## `MotionCanvasPlayer`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
str | Callable | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The MotionCanvasPlayer content to display. Only static MotionCanvasPlayer is rendered (e.g. no JavaScript. To render JavaScript, use the `js` or `head` parameters in the `Blocks` constructor). If a function is provided, the function will be called each time the app loads to set the initial value of this component.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The label for this component. Is used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
Timer | float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.</td>
</tr>

<tr>
<td align="left"><code>inputs</code></td>
<td align="left" style="width: 25%;">

```python
Component | Sequence[Component] | set[Component] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, the label will be displayed. If False, the label will be hidden.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the MotionCanvasPlayer DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the MotionCanvasPlayer DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, ...] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.</td>
</tr>

<tr>
<td align="left"><code>min_height</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The minimum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If MotionCanvasPlayer content exceeds the height, the component will expand to fit the content.</td>
</tr>

<tr>
<td align="left"><code>max_height</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The maximum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If content exceeds the height, the component will scroll.</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, the MotionCanvasPlayer component will be displayed in a container. Default is False.</td>
</tr>

<tr>
<td align="left"><code>padding</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, the MotionCanvasPlayer component will have a certain padding (set by the `--block-padding` CSS variable) in all directions. Default is True.</td>
</tr>

<tr>
<td align="left"><code>auto</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, the MotionCanvasPlayer component will automatically play the animation. Default is False.</td>
</tr>

<tr>
<td align="left"><code>quality</code></td>
<td align="left" style="width: 25%;">

```python
number | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The quality of the MotionCanvasPlayer component. Default is None which uses the project's default settings.</td>
</tr>

<tr>
<td align="left"><code>width</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The width of the MotionCanvasPlayer component. Default is None which uses the project's default settings.</td>
</tr>

<tr>
<td align="left"><code>height</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The height of the MotionCanvasPlayer component. Default is None which uses the project's default settings.</td>
</tr>

<tr>
<td align="left"><code>variables</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The variables of the MotionCanvasPlayer component as a JSON string. Default is None.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the MotionCanvasPlayer changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `click` | Triggered when the MotionCanvasPlayer is clicked. |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, (Rarely used) passes the MotionCanvasPlayer as a `str`.
- **As input:** Should return, expects a `str` consisting of valid MotionCanvasPlayer.

 ```python
 def predict(
     value: str | None
 ) -> str | None:
     return value
 ```
 
