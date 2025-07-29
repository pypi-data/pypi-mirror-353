
import gradio as gr
from app import demo as app
import os

_docs = {'LabanMovementAnalysis': {'description': 'Gradio component for video-based pose analysis with Laban Movement Analysis metrics.', 'members': {'__init__': {'default_model': {'type': 'str', 'default': '"mediapipe"', 'description': 'Default pose estimation model ("mediapipe", "movenet", "yolo")'}, 'enable_visualization': {'type': 'bool', 'default': 'True', 'description': 'Whether to generate visualization video by default'}, 'include_keypoints': {'type': 'bool', 'default': 'False', 'description': 'Whether to include raw keypoints in JSON output'}, 'enable_webrtc': {'type': 'bool', 'default': 'False', 'description': 'Whether to enable WebRTC real-time analysis'}, 'label': {'type': 'typing.Optional[str][str, None]', 'default': 'None', 'description': 'Component label'}, 'every': {'type': 'typing.Optional[float][float, None]', 'default': 'None', 'description': None}, 'show_label': {'type': 'typing.Optional[bool][bool, None]', 'default': 'None', 'description': None}, 'container': {'type': 'bool', 'default': 'True', 'description': None}, 'scale': {'type': 'typing.Optional[int][int, None]', 'default': 'None', 'description': None}, 'min_width': {'type': 'int', 'default': '160', 'description': None}, 'interactive': {'type': 'typing.Optional[bool][bool, None]', 'default': 'None', 'description': None}, 'visible': {'type': 'bool', 'default': 'True', 'description': None}, 'elem_id': {'type': 'typing.Optional[str][str, None]', 'default': 'None', 'description': None}, 'elem_classes': {'type': 'typing.Optional[typing.List[str]][\n    typing.List[str][str], None\n]', 'default': 'None', 'description': None}, 'render': {'type': 'bool', 'default': 'True', 'description': None}}, 'postprocess': {'value': {'type': 'typing.Any', 'description': 'Analysis results'}}, 'preprocess': {'return': {'type': 'typing.Dict[str, typing.Any][str, typing.Any]', 'description': 'Processed data for analysis'}, 'value': None}}, 'events': {}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'LabanMovementAnalysis': []}}}

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
# `gradio_labanmovementanalysis`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_labanmovementanalysis/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_labanmovementanalysis"></a>  
</div>

A Gradio 5 component for video movement analysis using Laban Movement Analysis (LMA) with MCP support for AI agents
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_labanmovementanalysis
```

## Usage

```python
# app.py  ─────────────────────────────────────────────────────────
\"\"\"
Laban Movement Analysis – modernised Gradio Space
Author: Csaba (BladeSzaSza)
\"\"\"

import gradio as gr
import os
from backend.gradio_labanmovementanalysis import LabanMovementAnalysis
# from gradio_labanmovementanalysis import LabanMovementAnalysis

# Import agent API if available
# Initialize agent API if available
agent_api = None
try:
    from gradio_labanmovementanalysis.agent_api import (
        LabanAgentAPI,
        PoseModel,
        MovementDirection,
        MovementIntensity
    )
    HAS_AGENT_API = True
    
    try:
        agent_api = LabanAgentAPI()
    except Exception as e:
        print(f"Warning: Agent API not available: {e}")
        agent_api = None
except ImportError:
    HAS_AGENT_API = False
# Initialize components
try:
    analyzer = LabanMovementAnalysis(
        enable_visualization=True
    )
    print("✅ Core features initialized successfully")
except Exception as e:
    print(f"Warning: Some features may not be available: {e}")
    analyzer = LabanMovementAnalysis()


def process_video_enhanced(video_input, model, enable_viz, include_keypoints):
    \"\"\"Enhanced video processing with all new features.\"\"\"
    if not video_input:
        return {"error": "No video provided"}, None
    
    try:
        # Handle both file upload and URL input
        video_path = video_input.name if hasattr(video_input, 'name') else video_input
        
        json_result, viz_result = analyzer.process_video(
            video_path,
            model=model,
            enable_visualization=enable_viz,
            include_keypoints=include_keypoints
        )
        return json_result, viz_result
    except Exception as e:
        error_result = {"error": str(e)}
        return error_result, None

def process_video_standard(video, model, enable_viz, include_keypoints):
    \"\"\"Standard video processing function.\"\"\"
    if video is None:
        return None, None
    
    try:
        json_output, video_output = analyzer.process_video(
            video,
            model=model,
            enable_visualization=enable_viz,
            include_keypoints=include_keypoints
        )
        return json_output, video_output
    except Exception as e:
        return {"error": str(e)}, None

# ── 4.  Build UI ─────────────────────────────────────────────────
def create_demo() -> gr.Blocks:
    with gr.Blocks(
        title="Laban Movement Analysis",
        theme='gstaff/sketch',
        fill_width=True,
    ) as demo:

        # ── Hero banner ──
        gr.Markdown(
            \"\"\"
            # 🎭 Laban Movement Analysis 
            
            Pose estimation • AI action recognition • Movement Analysis 
            \"\"\"
        )
        with gr.Tabs():
            # Tab 1: Standard Analysis
            with gr.Tab("🎬 Standard Analysis"):
                gr.Markdown(\"\"\"
                ### Upload a video file to analyze movement using traditional LMA metrics with pose estimation.
                \"\"\")
                # ── Workspace ──
                with gr.Row(equal_height=True):
                    # Input column
                    with gr.Column(scale=1, min_width=260):
                        
                        analyze_btn_enh = gr.Button("🚀 Analyze Movement", variant="primary", size="lg")
                        video_in = gr.Video(label="Upload Video", sources=["upload"], format="mp4")
                        # URL input option
                        url_input_enh = gr.Textbox(
                            label="Or Enter Video URL",
                            placeholder="YouTube URL, Vimeo URL, or direct video URL",
                            info="Leave file upload empty to use URL"
                        )
                       
                        gr.Markdown("**Model Selection**")
                        
                        model_sel = gr.Dropdown(
                            choices=[
                                # MediaPipe variants
                                "mediapipe-lite", "mediapipe-full", "mediapipe-heavy",
                                # MoveNet variants
                                "movenet-lightning", "movenet-thunder",
                                # YOLO v8 variants
                                "yolo-v8-n", "yolo-v8-s", "yolo-v8-m", "yolo-v8-l", "yolo-v8-x",
                                # YOLO v11 variants
                                "yolo-v11-n", "yolo-v11-s", "yolo-v11-m", "yolo-v11-l", "yolo-v11-x"
                            ],
                            value="mediapipe-full",
                            label="Advanced Pose Models",
                            info="15 model variants available"
                        )
                        
                        with gr.Accordion("Analysis Options", open=False):
                            enable_viz = gr.Radio([("Yes", 1), ("No", 0)], value=1, label="Visualization")
                            include_kp = gr.Radio([("Yes", 1), ("No", 0)], value=0, label="Raw Keypoints")

                        gr.Examples(
                            examples=[
                                ["examples/balette.mp4"],
                                ["https://www.youtube.com/shorts/RX9kH2l3L8U"],
                                ["https://vimeo.com/815392738"],
                                ["https://vimeo.com/548964931"],
                                ["https://videos.pexels.com/video-files/5319339/5319339-uhd_1440_2560_25fps.mp4"],
                            ],
                            inputs=url_input_enh,
                            label="Examples"
                        )


                    # Output column
                    with gr.Column(scale=2, min_width=320):
                        viz_out = gr.Video(label="Annotated Video", scale=1, height=400)
                        with gr.Accordion("Raw JSON", open=True):
                            json_out = gr.JSON(label="Movement Analysis", elem_classes=["json-output"])

                # Wiring
                def process_enhanced_input(file_input, url_input, model, enable_viz, include_keypoints):
                    \"\"\"Process either file upload or URL input.\"\"\"
                    video_source = file_input if file_input else url_input
                    return process_video_enhanced(video_source, model, enable_viz, include_keypoints)
                
                analyze_btn_enh.click(
                    fn=process_enhanced_input,
                    inputs=[video_in, url_input_enh, model_sel, enable_viz, include_kp],
                    outputs=[json_out, viz_out],
                    api_name="analyze_enhanced"
                )

        # Footer
        with gr.Row():
            gr.Markdown(
                \"\"\"
                **Built by Csaba Bolyós**  
                [GitHub](https://github.com/bladeszasza) • [HF](https://huggingface.co/BladeSzaSza)
                \"\"\"
            )
    return demo
  
if __name__ == "__main__":
    demo = create_demo()
    demo.launch(server_name="0.0.0.0",
                server_port=int(os.getenv("PORT", 7860)),
                mcp_server=True) 

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `LabanMovementAnalysis`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["LabanMovementAnalysis"]["members"]["__init__"], linkify=[])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, processed data for analysis.
- **As output:** Should return, analysis results.

 ```python
def predict(
    value: typing.Dict[str, typing.Any][str, typing.Any]
) -> typing.Any:
    return value
```
""", elem_classes=["md-custom", "LabanMovementAnalysis-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          LabanMovementAnalysis: [], };
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
