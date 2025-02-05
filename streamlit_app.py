import requests
import time
import streamlit as st

# Define a constant for the passcode
PASSCODE = st.secrets["passcode"]

# Sidebar for passcode input
st.sidebar.header("Access Control")
input_passcode = st.sidebar.text_input("Enter Passcode", type="password")

if input_passcode == PASSCODE:
    # Streamlit application title
    st.title("SDXL-Base Image Generation")

    # Row 1: Prompt and Negative Prompt
    col1, col2 = st.columns(2)

    with col1:
        prompt = st.text_area(
            "Prompt", "A beautiful landscape with a river and mountains", height=100
        )

    with col2:
        negprompt = st.text_area(
            "Don't want in the image",
            "deformed, bad anatomy, disfigured, poorly drawn face",
            height=100,
        )

    # Row 2: Aspect Ratio and Style
    col3, col4 = st.columns(2)

    with col3:
        aspect_ratio = st.selectbox(
            "Aspect Ratio",
            ["square", "portrait", "landscape"],
            help="Choose the aspect ratio of the generated image.",
        )

    with col4:
        style = st.selectbox(
            "Style",
            [
                "anime",
                "enhance",
                "photographic",
                "digital-art",
                "comic-book",
                "fantasy-art",
                "analog-film",
                "neonpunk",
                "isometric",
                "lowpoly",
                "origami",
                "line-art",
                "craft-clay",
                "cinematic",
                "3d-model",
                "pixel-art",
                "texture",
                "futuristic",
                "realism",
                "watercolor",
                "photorealistic",
            ],
            help="Select the artistic style of the generated image.",
        )

    # Row 3: Checkmarks for Enhance, Optimize, and Safe Filter
    col5, col6, col7 = st.columns(3)

    with col5:
        enhance = st.checkbox("Enhance", value=False)

    with col6:
        optimize = st.checkbox("Optimize", value=False)

    with col7:
        safe_filter = st.checkbox("Safe Filter", value=False)

    # Input fields for Samples, Seed, Steps, and Guidance Scale
    st.markdown("---")
    col8, col9 = st.columns(2)

    with col8:
        samples = st.number_input(
            "Samples",
            min_value=1,
            value=1,
            max_value=4,
            help="Number of images to generate.",
        )
        seed = st.number_input(
            "Seed", min_value=0, value=1234, help="Random seed for generation."
        )

    with col9:
        steps = st.number_input(
            "Steps",
            min_value=30,
            max_value=500,
            value=50,
            help="Number of steps for image generation.",
        )
        guidance_scale = st.number_input(
            "Guidance Scale",
            min_value=0.0,
            value=7.5,
            format="%.1f",
            help="Controls the strength of guidance for generation.",
        )

    # Add a visual space
    st.markdown("---")

    # Button to generate image
    if st.button("Generate Image"):
        with st.spinner("Generating image..."):
            # First API for generating images
            first_api = "https://api.monsterapi.ai/v1/generate/sdxl-base"

            payload = {
                "aspect_ratio": aspect_ratio,
                "enhance": enhance,
                "guidance_scale": guidance_scale,
                "negprompt": negprompt,
                "optimize": optimize,
                "prompt": prompt,
                "safe_filter": safe_filter,
                "samples": samples,
                "seed": seed,
                "steps": steps,
                "style": style,
            }

            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {st.secrets['monsterapi_key']}",
            }

            # Step 1: Send request to the first API
            response = requests.post(first_api, json=payload, headers=headers)
            response_data = response.json()

            if "process_id" in response_data:
                status_url = response_data["status_url"]
                st.success("Image generation started.")

                # Initialize progress bar
                progress_bar = st.progress(0)
                completed = False

                # Step 2: Poll the status URL until the image is completed
                while not completed:
                    # Poll API for status
                    status_response = requests.get(status_url, headers=headers)
                    status_data = status_response.json()

                    if status_data["status"] == "COMPLETED":
                        completed = True
                        output_urls = status_data["result"].get("output", [])
                        for url in output_urls:
                            st.image(
                                url, caption="Generated Image", use_container_width=True
                            )
                            st.success(f"Image generation completed. Output URL: {url}")
                    elif status_data["status"] in ["IN_PROGRESS", "IN_QUEUE"]:
                        # Update the progress bar
                        progress = 0.5  # Adjust logic based on actual status as needed
                        progress_bar.progress(progress)
                        time.sleep(5)  # Wait before checking again
                    else:
                        completed = True
                        st.error("Unexpected status received: " + str(status_data))

                # Reset progress bar to complete
                progress_bar.progress(100)

            else:
                st.error("Failed to initiate image generation: " + str(response_data))
else:
    st.warning("Please enter a valid passcode to access the application.")
