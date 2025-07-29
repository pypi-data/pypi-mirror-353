---
title: Laban Movement Analysis
emoji: 🏃
colorFrom: purple
colorTo: green
app_file: app.py
sdk: gradio
sdk_version: 5.33.0
pinned: false
tags:
- laban-movement-analysis
- pose-estimation
- movement-analysis
- video-analysis
- youtube
- vimeo
- mcp
- agent-ready
- computer-vision
- mediapipe
- yolo
- gradio
short_description: Professional movement analysis with pose estimation and AI
license: apache-2.0
---

# `gradio_labanmovementanalysis`
<a href="https://pypi.org/project/gradio_labanmovementanalysis/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_labanmovementanalysis"></a>  

A Gradio 5 component for video movement analysis using Laban Movement Analysis (LMA) with MCP support for AI agents

## Installation

```bash
pip install gradio_labanmovementanalysis
```

## Usage

```python
# app.py  ─────────────────────────────────────────────────────────
"""
Laban Movement Analysis – modernised Gradio Space
Author: Csaba (BladeSzaSza)
"""

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
    """Enhanced video processing with all new features."""
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
    """Standard video processing function."""
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
            """
            # 🎭 Laban Movement Analysis 
            
            Pose estimation • AI action recognition • Movement Analysis 
            """
        )
        with gr.Tabs():
            # Tab 1: Standard Analysis
            with gr.Tab("🎬 Standard Analysis"):
                gr.Markdown("""
                ### Upload a video file to analyze movement using traditional LMA metrics with pose estimation.
                """)
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
                    """Process either file upload or URL input."""
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
                """
                **Built by Csaba Bolyós**  
                [GitHub](https://github.com/bladeszasza) • [HF](https://huggingface.co/BladeSzaSza)
                """
            )
    return demo
  
if __name__ == "__main__":
    demo = create_demo()
    demo.launch(server_name="0.0.0.0",
                server_port=int(os.getenv("PORT", 7860)),
                mcp_server=True) 

```

## `LabanMovementAnalysis`

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
<td align="left"><code>default_model</code></td>
<td align="left" style="width: 25%;">

```python
str
```

</td>
<td align="left"><code>"mediapipe"</code></td>
<td align="left">Default pose estimation model ("mediapipe", "movenet", "yolo")</td>
</tr>

<tr>
<td align="left"><code>enable_visualization</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">Whether to generate visualization video by default</td>
</tr>

<tr>
<td align="left"><code>include_keypoints</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">Whether to include raw keypoints in JSON output</td>
</tr>

<tr>
<td align="left"><code>enable_webrtc</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">Whether to enable WebRTC real-time analysis</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[str][str, None]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Component label</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[float][float, None]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[bool][bool, None]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[int][int, None]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[bool][bool, None]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[str][str, None]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[typing.List[str]][
    typing.List[str][str], None
]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">None</td>
</tr>
</tbody></table>




### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, processed data for analysis.
- **As input:** Should return, analysis results.

 ```python
 def predict(
     value: typing.Dict[str, typing.Any][str, typing.Any]
 ) -> typing.Any:
     return value
 ```
 
