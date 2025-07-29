# streamlit-tetrascience-ui

Tetrascience UI components for [Streamlit](https://streamlit.io/).

## Installation

```bash
pip install streamlit-tetrascience-ui
```

## Usage

```python
import streamlit as st
import streamlit_tetrascience_ui as ui

# Example: Simple interactive component
name = st.text_input("Enter your name:", value="Streamlit")
count = ui.my_component(name, key="example")
st.write(f"Button clicked {count} times!")

# Example: Histogram component
hist_data = [
    {"label": "A", "values": [1, 2, 3]},
    {"label": "B", "values": [4, 5, 6]},
]
ui.histogram_component(
    name="My Histogram",
    dataSeries=hist_data,
    width=400,
    height=300,
    title="Histogram Example",
    xTitle="Bins",
    yTitle="Frequency",
    bargap=0.2,
    showDistributionLine=True,
    key="hist1"
)
```

## Features

- Custom Streamlit components for Tetrascience UI
- Easy integration and usage
- Example components: `my_component`, `histogram_component`

## License

MIT
