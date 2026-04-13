import streamlit as st
import pandas as pd
import datetime
import base64
import urllib.parse

# إعداد الصفحة
st.set_page_config(page_title="نظام باب الآغا - أيوب هاني", layout="wide")

# تهيئة البيانات في الذاكرة (Session State) لضمان عدم ضياعها
if 'items_df' not in st.session_state:
    initial_items = [
        ["باكيت تركي", 50], ["باكيت فرنسي اسمر", 50], ["باكيت فرنسي ابيض", 50],
        ["صمون شاورما", 50], ["صمون سداسي", 50], ["صمون كنتاكي حمام", 25],
        ["جرك بالحليب", 100], ["جرك تمر", 40], ["توست ابيض", 130],
        ["توست اسمر ساده", 80], ["كرواسون ابيض", 800]
    ]
    st.session_state.items_df = pd.DataFrame(initial_items, columns=["السلعة", "رقم الأمان"])

if 'orders_df' not in st.session_state:
    st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])

# القائمة الجانبية
st.sidebar.title("🍞 مخابز باب الآغا")
menu = st.sidebar.radio("انتقل إلى:", ["📋 الجرد والطباعة", "🛒 الطلبيات والوصايا", "⚙️ إدارة السلع"])

# --- قسم الجرد والطباعة ---
if menu == "📋 الجرد والطباعة":
    st.header("📋 جرد القسم اليومي")
    
    # توقيت العراق
    iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
    iraq_time = iraq_now.strftime("%I:%M %p")
    iraq_date = iraq_now.strftime("%Y-%m-%d")

    # استخدام FORM لمنع تعليق الكيبورد في الموبايل
    with st.form("inventory_form"):
        st.write("📌 أدخل الكميات واضغط 'اعتماد' في الأسفل")
        temp_results = []
        
        for i, row in st.session_state.items_df.iterrows():
            st.markdown(f"### 📦 {row['السلعة']}")
            c1, c2, c3 = st.columns([1, 1, 2])
            
            with c1:
                q = st.number_input("الموجود", min_value=0, key=f"q_input_{i}")
            with c2:
                r = st.number_input("التوصية", min_value=0, key=f"r_input_{i}")
            with c3:
                n = st.text_input("ملاحظة", key=f"n_input_{i}", placeholder="أضف ملاحظة هنا...")
            
            temp_results.append({"السلعة": row['السلعة'], "الموجود": q, "التوصية": r, "الملاحظة": n})
            st.markdown("---")
            
        submit_button = st.form_submit_button("🚀 اعتماد الجرد وتوليد التقرير")

    if submit_button:
        st.session_state.final_rep = temp_results
        st.success("✅ تم حفظ البيانات! انزل للأسفل للطباعة والواتساب.")

    # عرض النتائج والطباعة (تظهر فقط بعد الضغط على الاعتماد)
    if 'final_rep' in st.session_state:
        # (هنا نضع كود HTML والطباعة والواتساب الذي أرسلته لك سابقاً)
        rows_html = ""
        wa_text = f"📋 *تقرير جرد باب الآغا*\n📅 {iraq_date} | 🕒 {iraq_time}\n👤 المسؤول: أيوب هاني\n━━━━━━━━━━━━\n"
        
        for x in st.session_state.final_rep:
            if x['الموجود'] > 0 or x['التوصية'] > 0:
                rows_html += f"<tr><td>{x['السلعة']}</td><td>{x['الموجود']}</td><td>{x['التوصية']}</td><td>{x['الملاحظة']}</td></tr>"
                wa_text += f"🔹 *{x['السلعة']}*\n   الموجود: {x['الموجود']} | الطلب: {x['التوصية']}\n"

        full_html = f"""
        <div dir="rtl" style="font-family: Arial; padding: 20px; border: 2px solid black; background: white; color: black;">
            <center><h1>مخابز باب الآغا 🥖</h1><h2>تقرير المسؤول: أيوب هاني</h2></center>
            <p><b>التاريخ:</b> {iraq_date} | <b>الوقت:</b> {iraq_time}</p>
            <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
                <tr style="background: #eee;"><th>السلعة</th><th>الموجود</th><th>التوصية</th><th>الملاحظة</th></tr>
                {rows_html}
            </table>
        </div>
        """
        st.markdown(full_html, unsafe_allow_html=True)
        
        # أزرار الواتساب والطباعة
        b64 = base64.b64encode(full_html.encode('utf-8')).decode()
        st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button style="width:100%; padding:15px; background:#1e3a8a; color:white; border-radius:10px;">🖨️ فتح نسخة الطباعة العربية</button></a>', unsafe_allow_html=True)

# --- باقي الأقسام (الطلبيات وإدارة السلع) تبقى كما هي مع التأكد من الـ IF/ELIF ---
elif menu == "🛒 الطلبيات والوصايا":
    st.header("🛒 الطلبيات")
    # كود الطلبيات...

elif menu == "⚙️ إدارة السلع":
    st.header("⚙️ إدارة السلع")
    # كود الإدارة...
