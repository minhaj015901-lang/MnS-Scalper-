import streamlit as st
import google.generativeai as genai
from PIL import Image

# পেজ কনফিগারেশন
st.set_page_config(page_title="MnS AI Chart Scalper", page_icon="⚡", layout="centered")

# টাইটেল ও বর্ণনা
st.title("⚡ MnS AI Chart Scalper Scanner Pro")
st.write("১m, ৫m বা ১৫m টাইমফ্রেমের যেকোনো চার্টের স্ক্রিনশট বা ক্যামেরা ফটো আপলোড করো। AI গভীরভাবে স্ক্যান করে ডেডলি সিগন্যাল দেবে।")

# সরাসরি কোডেই চাবি সেট করে দেওয়া হলো (ঝামেলা মুক্তির জন্য)
API_KEY = "AQ.Ab8RN6IDRq1rnpJ5gVGMs3GW1PNfy9Jd0YeKpSSTPNXL8wP3jw"
genai.configure(api_key=API_KEY)

# সাইডবার অপশনাল রাখা হলো (চাইলে চাবি বদলানো যাবে, না দিলেও সমস্যা নেই)
st.sidebar.header("🔑 AI Engine Setup")
user_api_key = st.sidebar.text_input("Enter Gemini API Key (Optional):", type="password")
if user_api_key:
    genai.configure(api_key=user_api_key)

# ইমেজ আপলোড অপশন
st.subheader("চার্টের ছবি কীভাবে দিতে চাও মামা?")
source_option = st.radio("পদ্ধতি সিলেক্ট করো:", ("গ্যালারি/স্ক্রিনশট আপলোড", "মোবাইল ক্যামেরা দিয়ে লাইভ ছবি"))

uploaded_file = None
if source_option == "গ্যালারি/স্ক্রিনশট আপলোড":
    uploaded_file = st.file_uploader("চার্টের স্পষ্ট স্ক্রিনশট সিলেক্ট করো (PNG, JPG, JPEG)...", type=["png", "jpg", "jpeg"])
else:
    uploaded_file = st.camera_input("ক্যামেরা দিয়ে চার্টের ছবি তোলো...")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Trading Chart", use_container_width=True)
    
    # স্ক্যান বাটন
    if st.button("🚀 Deep Scan & Generate Scalping Signal"):
        with st.spinner("🔮 মামা, AI চার্ট অ্যানালাইসিস করছে... একটু অপেক্ষা করো..."):
            try:
                # প্রম্পট সেটআপ (SMC & ICT Concepts)
                prompt = (
                    "You are an expert high-frequency gold (XAUUSD) scalper and technical analyst using Smart Money Concepts (SMC) and ICT. "
                    "Analyze this uploaded trading chart image deeply. Identify Market Structure (BOS/CHoCH), Order Blocks, Fair Value Gaps (FVG), "
                    "Liquidity pools, and current trend. Provide a highly precise scalping signal (BUY/SELL/HOLD), with an exact Entry Level, "
                    "Take Profit (TP) targets, and a strict Stop Loss (SL). Format your response beautifully in Bengali with clear sections and bold text."
                )
                
                # মডেল কল করা
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content([prompt, image])
                
                # ফলাফল দেখানো
                st.success("✅ স্ক্যান সম্পূর্ণ হয়েছে মামা!")
                st.markdown("### 📊 AI Scalping Analysis & Signal:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"কোথাও একটা টেকনিক্যাল ঝামেলা হয়েছে মামা! দয়া করে সঠিক ছবি দিয়ে আবার চেষ্টা করো। এরর কোড: {e}")
