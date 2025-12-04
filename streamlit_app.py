import streamlit as st
import io
import tempfile
import os

# Check pydub availability
try:
    from pydub import AudioSegment
except ImportError:
    st.error("❌ pydub not installed. Add to requirements.txt: `pydub`")
    st.stop()

st.set_page_config(page_title="Voice Changer", layout="wide")
st.title("🎵 Voice Changer Web App")
st.markdown("### Upload MP3/WAV → Adjust Speed & Pitch → Download Modified Audio")

# File uploader
uploaded_file = st.file_uploader(
    "Choose an audio file", 
    type=['mp3', 'wav', 'm4a', 'flac'],
    help="Supports MP3, WAV, M4A, FLAC files"
)

if uploaded_file is not None:
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name
    
    try:
        # Load and display original audio
        sound = AudioSegment.from_file(temp_path)
        st.success(f"✅ Loaded: **{len(sound)/1000:.1f} seconds**")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.audio(temp_path, format="audio/wav")
        with col2:
            st.info("👆 Play original audio")
        
        # Controls in columns
        col_speed, col_pitch = st.columns(2)
        with col_speed:
            speed = st.slider(
                "⚡ Speed", 
                min_value=0.5, max_value=2.0, value=1.0, step=0.1,
                help="0.5 = 50% slower, 2.0 = 2x faster"
            )
        with col_pitch:
            pitch = st.slider(
                "🎤 Pitch", 
                min_value=0.5, max_value=1.5, value=1.0, step=0.1,
                help="0.5 = deeper voice, 1.5 = higher voice"
            )
        
        # Process button
        if st.button("🚀 **Modify & Download**", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing your audio..."):
                # Apply speed change
                sped_sound = sound._spawn(
                    sound.raw_data, 
                    overrides={"frame_rate": int(sound.frame_rate * speed)}
                )
                
                # Apply pitch change
                pitched_sound = sped_sound._spawn(
                    sped_sound.raw_data, 
                    overrides={"frame_rate": int(sped_sound.frame_rate * pitch)}
                )
                
                # Normalize frame rate back to original
                final_sound = pitched_sound.set_frame_rate(sound.frame_rate)
                
                # Export to buffer for download
                buffer = io.BytesIO()
                final_sound.export(buffer, format="wav")
                buffer.seek(0)
                
                # Display results
                st.success(f"✅ **Complete!** Speed: {speed:.1f}x | Pitch: {pitch:.1f}x")
                
                col_result1, col_result2 = st.columns([2, 1])
                with col_result1:
                    st.audio(buffer, format="audio/wav")
                with col_result2:
                    st.info("👆 Play modified audio")
                
                # Download button
                st.download_button(
                    label="📥 **Download Modified Audio**",
                    data=buffer,
                    file_name=f"voice_modified_{speed:.1f}x_{pitch:.1f}p.wav",
                    mime="audio/wav",
                    use_container_width=True
                )
                
                st.balloons()
                
    except Exception as e:
        st.error(f"❌ Audio processing error: {str(e)}")
        st.info("Try a different audio file (MP3/WAV recommended)")
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

else:
    st.info(
        "👈 **Upload an audio file** (MP3, WAV, M4A) to start modifying!\n\n"
        "💡 **Tips:**\n"
        "• Clear speech works best\n"
        "• 5-30 second clips recommended\n"
        "• Phone recordings work great!"
    )
