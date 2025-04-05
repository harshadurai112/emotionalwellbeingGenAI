import streamlit as st

# Static Room and Phone Number
room_name = "MentalHealthSupportRoom123"
room_url = f"https://meet.jit.si/{room_name}"
phone_number = "8754124789"

# UI
st.set_page_config(page_title="Free Mental Health Call", layout="wide")
st.title("🧠 Free Mental Health Support Call")

st.markdown("""
Welcome to the AI Mental Wellbeing Agent.  
When you're feeling overwhelmed, connect instantly with a support professional through this **secure, free, in-app call**, or tap to call us directly.
""")

# Show Call Button
if st.button("📞 Start Free Video Call Now"):
    st.success("Call launched below. Make sure to allow microphone and camera access.")
    
    # Jitsi iframe
    st.components.v1.html(f"""
        <iframe 
            src="{room_url}#config.startWithVideoMuted=false&config.startWithAudioMuted=false&userInfo.displayName='User'" 
            style="height: 600px; width: 100%; border: 0px;" 
            allow="camera; microphone; fullscreen; display-capture"
        ></iframe>
    """, height=600)

# Display the phone call option
st.markdown(f"""
---  
📱 Prefer a voice call instead?

👉 [Click here to call us now](tel:{phone_number})  
📞 Or dial manually: **{phone_number}**
""")
