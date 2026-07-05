import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# পেজ কনফিগারেশন এবং টাইটেল সেটআপ
st.set_page_config(
    page_title="MnS AI Scalper Scanner Pro", 
    page_icon="⚡", 
    layout="centered"
)

st.title("⚡ MnS AI Chart Scalper Scanner Pro")
st.write("১m, ৫m বা ১৫m টাইমফ্রেমের যেকোনো চার্টের স্ক্রিনশট বা ক্যামেরা ফটো আপলোড করো। AI গভীরভাবে স্ক্যান করে ডেডলি সিগন্যাল দেবে।")

# সাইডবার এআই সেটআপ ও এপিআই কি ইনপুট
st.sidebar.header("🔑 AI Engine Setup")
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password", help="গুগল এআই স্টুডিও থেকে আনা ফ্রি কি-টি এখানে বসাও।")

st.sidebar.markdown("""
[👉 ফ্রি Gemini API Key পেতে এখানে ক্লিক করো](https://aistudio.google.com/)
""")

# এপিআই কি চেক এবং কনফিগারেশন
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("⚠️ মামা, অ্যাপটি চালু করতে আগে সাইডবারে তোমার Gemini API Key-টি বসিয়ে নাও।")

# ছবি আপলোড বা লাইভ ক্যামেরা অপশন বেছে নেওয়া
upload_option = st.radio("চার্টের ছবি কীভাবে দিতে চাও মামা?", ("গ্যালারি/স্ক্রিনশট আপলোড", "মোবাইল ক্যামেরা দিয়ে লাইভ ছবি"))

uploaded_file = None
if upload_option == "গ্যালারি/স্ক্রিনশট আপলোড":
    uploaded_file = st.file_uploader("চার্টের স্পষ্ট স্ক্রিনশট সিলেক্ট করো (PNG, JPG, JPEG)...", type=["jpg", "jpeg", "png"])
else:
    uploaded_file = st.camera_input("লাইভ চার্টের সামনে ক্যামেরা ধরে ছবি তোলো...")

if uploaded_file is not None:
    try:
        # ইমেজটি ওপেন করা এবং বাফারিং করা
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Trading Chart", use_container_width=True)
        
        # স্ক্যানিং বাটন ট্রিপল চেক লজিকসহ
        if st.button("🚀 Deep Scan & Generate Scalping Signal"):
            if not api_key:
                st.error("মামা, আগে সাইডবারে API Key-টি পেস্ট করে নাও, তা না হলে AI ইঞ্জিন স্টার্ট হবে না!")
            else:
                with st.spinner("AI চার্টের ক্যান্ডেলস্টিক, ব্রেকআউট এবং ভলিউম গভীরভাবে অ্যানালাইসিস করছে... একটু ধৈর্য ধরো মামা..."):
                    
                    # ইমেজ ফরম্যাট সেফটি চেক (ক্যামেরার ছবির জন্য JPEG ডিফল্ট করা)
                    img_format = image.format if image.format else 'JPEG'
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format=img_format)
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # জেমিনাই মডেলের জন্য প্রিপেয়ার্ড ইমেজ অবজেক্ট
                    chart_image_data = {
                        'mime_type': f'image/{img_format.lower()}',
                        'data': img_byte_arr
                    }
                    
                    # ডেডলি স্ক্যাল্পিং প্রম্পট - প্রো ট্রেডার লজিক সমৃদ্ধ
                    prompt = """
                    You are a legendary, high-conviction institutional Forex and Crypto Scalper who specializes in price action, liquidity sweeps, and order blocks. 
                    Deeply analyze this chart image strictly for ultra-short-term SCALPING (1m, 5m, or 15m timeframes). Do not give vague answers.
                    
                    Provide your final response in Bengali language, but keep core trading terms (like Support, Resistance, Breakout, Stop Loss, Take Profit, BUY, SELL, Liquidity, Order Block, EMA) in English.
                    
                    Strictly format your response into these exact bold sections:
                    
                    ### 📊 Deep Technical Market Structure
                    - **Trend Analysis**: (Identify if Bullish, Bearish, or Choppy/Sideways)
                    - **Candlestick & Price Action**: (Analyze the last 3-5 candles, wicks, volume profile if visible, and patterns like Engulfing, Pinbar, Double Top/Bottom, or Head & Shoulders)
                    - **Key Levels**: (Exact psychological or visible Support and Resistance lines from the image)
                    
                    ### 🎯 Deadly Scalping Signal
                    - **VERDICT**: [STRONG BUY / BUY / STRONG SELL / SELL / AVOID/NO ENTRY]
                    - **Exact Entry Price**: (Based on current market price in the image)
                    - **Stop Loss (SL)**: (Strict tight SL just above/below the structure to maximize Risk-to-Reward)
                    - **Take Profit (TP1 - Quick Scalp)**: 
                    - **Take Profit (TP2 - Extended Move)**: 
                    
                    ### 💡 Scalper's Secret Commentary
                    - Give a brutal, high-conviction reason for this signal. Explain the exact breakout, rejection, or liquidity grab you spotted in the image that makes this a high-probability trade.
                    """
                    
                    # Gemini 1.5 Flash মডেল - যা ইমেজ রিডিং ও স্পিডের জন্য বেস্ট
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content([prompt, chart_image_data])
                    
                    # সাকসেসফুল রেজাল্টアウトপুট
                    st.success("✅ ডিপ স্ক্যানিং সম্পূর্ণ মামা! নিচে তোমার ডেডলি সিগন্যাল রেডি:")
                    st.markdown("---")
                    st.markdown(response.text)
                    st.markdown("---")
                    
    except Exception as e:
        st.error(f"কোথাও একটা টেকনিক্যাল ঝামেলা হয়েছে মামা! দয়া করে সঠিক ছবি দিয়ে আবার চেষ্টা করো। এরর কোড: {str(e)}")

st.markdown("<br><hr><center>⚡ Developed with Deep Validation Logic for Mama's Trading ⚡</center>", unsafe_allowed_html=True)
