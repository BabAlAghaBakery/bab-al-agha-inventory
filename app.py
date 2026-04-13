import streamlit as st
import pandas as pd
import datetime
import base64
import urllib.parse

# --- 1. إعدادات المظهر العام (هوية باب الآغا) ---
st.set_page_config(page_title="نظام جرد باب الآغا - أيوب هاني", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main-header { background-color: #1e3a8a; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #1e3a8a; color: white; padding: 10px; }
    .stButton>button:hover { background-color: #2563eb; border: 1px solid white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الذاكرة (لضمان حفظ البيانات عند التنقل) ---
if 'items_df' not in st.session_state:
    # القائمة الكاملة التي زودتني بها مسبقاً
    initial_items = [
        ["باكيت تركي", 50], ["باكيت فرنسي اسمر", 50], ["باكيت فرنسي ابيض", 50],
        ["صمون شاورما", 50], ["صمون سداسي", 50], ["صمون كنتاكي حمام", 25],
        ["جرك بالحليب", 100], ["جرك تمر", 40], ["توست ابيض", 130],
        ["توست اسمر ساده", 80], ["كرواسون ابيض", 800], ["سميط شعير", 60]
    ] # يمكنك إضافة باقي الـ 60 صنف من واجهة "إدارة الأصناف" داخل التطبيق
    st.session_state.items_df = pd.DataFrame(initial_items, columns=["السلعة", "رقم الأمان"])

if 'orders_df' not in st.session_state:
    st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])

# مخزن مؤقت للمدخلات لضمان عدم اختفاء الأرقام
if 'tmp_inv' not in st.session_state: st.session_state.tmp_inv = {}
if 'tmp_rec' not in st.session_state: st.session_state.tmp_rec = {}
if 'tmp_note' not in st.session_state: st.session_state.tmp_note = {}

# --- 3. القائمة الجانبية المُنظمة ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3014/3014535.png", width=100)
    st.title("لوحة التحكم")
    st.info(f"المسؤول: أيوب هاني")
    menu = st.radio("القائمة الرئيسية", ["📋 الجرد والطباعة", "🛒 الطلبيات والوصايا", "⚙️ إدارة الأصناف"])

# --- 4. قسم الجرد والطباعة (القلب النابض للنظام) ---
if menu == "📋 الجرد والطباعة":
    st.markdown("<div class='main-header'><h1>📋 جرد قسم التوست - باب الآغا</h1></div>", unsafe_allow_html=True)
    
    # توقيت العراق بدقة (UTC+3)
    iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
    iraq_time = iraq_now.strftime("%I:%M %p")
    iraq_date = iraq_now.strftime("%Y-%m-%d")

    st.subheader(f"📅 التاريخ: {iraq_date} | 🕒 الوقت: {iraq_time}")
    
    inventory_results = []
    
    # عرض السلع للإدخال
    for i, row in st.session_state.items_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                q = st.number_input(f"📦 {row['السلعة']}", min_value=0, key=f"q_{i}", value=st.session_state.tmp_inv.get(i, 0))
                st.session_state.tmp_inv[i] = q
            with col2:
                r = st.number_input("توصية", min_value=0, key=f"r_{i}", value=st.session_state.tmp_rec.get(i, 0))
                st.session_state.tmp_rec[i] = r
            with col3:
                n = st.text_input("ملاحظة", key=f"n_{i}", value=st.session_state.tmp_note.get(i, ""), placeholder="نقص/زيادة...")
                st.session_state.tmp_note[i] = n
            
            inventory_results.append({"السلعة": row['السلعة'], "الموجود": q, "التوصية": r, "الملاحظة": n})
        st.divider()

    if st.button("🚀 اعتماد الجرد وتوليد التقرير النهائي"):
        st.session_state.final_rep = inventory_results
        st.success("✅ تم حفظ الجرد بنجاح! راجع التقرير في الأسفل.")

    if 'final_rep' in st.session_state:
        st.divider()
        st.subheader("📄 معاينة تقرير A4 المطبوع")
        
        # بناء الجداول للطباعة والواتساب
        rows_html = ""
        wa_text = f"📋 *تقرير جرد باب الآغا*\n👤 المسؤول: أيوب هاني\n📅 {iraq_date} | {iraq_time}\n━━━━━━━━━━━━\n"
        
        for item in st.session_state.final_rep:
            if item['الموجود'] > 0 or item['التوصية'] > 0:
                rows_html += f"<tr><td>{item['السلعة']}</td><td>{item['الموجود']}</td><td>{item['التوصية']}</td><td>{item['الملاحظة']}</td></tr>"
                wa_text += f"🔹 *{item['السلعة']}*\n   الموجود: {item['الموجود']} | التوصية: {item['التوصية']}\n"

        orders_html = ""
        if not st.session_state.orders_df.empty:
            wa_text += "\n🛒 *الطلبيات والوصايا:*\n"
            orders_html = "<div style='margin-top:20px;'><h3>🛒 الطلبيات والوصايا الإضافية:</h3><ul>"
            for _, row in st.session_state.orders_df.iterrows():
                orders_html += f"<li><b>{row['الطلب']}:</b> {row['التفاصيل']}</li>"
                wa_text += f"• {row['الطلب']}: {row['التفاصيل']}\n"
            orders_html += "</ul></div>"

        # القالب الاحترافي للطباعة (حل مشكلة اللغة العربية)
        full_html = f"""
        <div dir="rtl" style="font-family: Arial, sans-serif; padding: 30px; border: 4px solid #1e3a8a; background: white; color: black;">
            <center>
                <h1 style="color:#1e3a8a; margin:0;">مخابز باب الآغا 🥖</h1>
                <h2 style="margin:5px;">تقرير جرد قسم التوست</h2>
            </center>
            <p style="font-size:18px;"><b>التاريخ:</b> {iraq_date} | <b>الوقت:</b> {iraq_time}</p>
            <p style="font-size:18px;"><b>المسؤول:</b> أيوب هاني</p>
            <hr style="border: 1px solid #1e3a8a;">
            <table border="1" style="width:100%; border-collapse: collapse; text-align: center; font-size: 16px;">
                <tr style="background-color: #1e3a8a; color: white;">
                    <th>اسم السلعة</th><th>الكمية المتوفرة</th><th>التوصية بالطلب</th><th>الملاحظات</th>
                </tr>
                {rows_html}
            </table>
            {orders_html}
            <br><br>
            <div style="display: flex; justify-content: space-between; font-weight: bold;">
                <span>توقيع كابتن الصالة: ...................</span>
                <span>توقيع مسؤول القسم (أيوب هاني): ...................</span>
            </div>
        </div>
        """
        st.markdown(full_html, unsafe_allow_html=True)

        # زر الواتساب (يرسل الجرد + الوصايا)
        encoded_wa = urllib.parse.quote(wa_text + "\n━━━━━━━━━━━━\nتم بواسطة نظام أيوب الذكي")
        st.markdown(f'<a href="https://wa.me/9647510853103?text={encoded_wa}" target="_blank"><button style="width:100%; background:#25d366; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; font-weight:bold; font-size:16px;">📲 إرسال الجرد كاملاً للواتساب</button></a>', unsafe_allow_html=True)

        # زر الطباعة (حل مشكلة الرموز الغريبة نهائياً)
        b64 = base64.b64encode(full_html.encode('utf-8')).decode()
        st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button style="width:100%; background:#1e3a8a; color:white; padding:15px; border-radius:10px; border:none; cursor:pointer; margin-top:10px; font-weight:bold;">🖨️ فتح نسخة الطباعة (A4 العربية جاهزة)</button></a>', unsafe_allow_html=True)

# --- 5. قسم الطلبيات والوصايا ---
elif menu == "🛒 الطلبيات والوصايا":
    st.header("🛒 إدارة الوصايا والطلبيات")
    with st.form("o_form", clear_on_submit=True):
        t = st.text_input("اسم صاحب الطلب")
        d = st.text_area("تفاصيل الوصية")
        if st.form_submit_button("حفظ الوصية"):
            new_o = pd.DataFrame([{"الطلب": t, "التفاصيل": d}])
            st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_o], ignore_index=True)
            st.rerun()
    
    if not st.session_state.orders_df.empty:
        st.subheader("📋 الوصايا الحالية:")
        for i, row in st.session_state.orders_df.iterrows():
            col_a, col_b = st.columns([5, 1])
            col_a.warning(f"**{row['الطلب']}**: {row['التفاصيل']}")
            if col_b.button("حذف", key=f"del_o_{i}"):
                st.session_state.orders_df = st.session_state.orders_df.drop(i).reset_index(drop=True)
                st.rerun()

# --- 6. قسم إدارة الأصناف ---
elif menu == "⚙️ إدارة الأصناف":
    st.header("⚙️ إدارة قائمة المنتجات")
    with st.expander("➕ إضافة منتج جديد"):
        n = st.text_input("اسم المنتج")
        s = st.number_input("حد الأمان", value=50)
        if st.button("إضافة للقائمة"):
            new_i = pd.DataFrame([{"السلعة": n, "رقم الأمان": s}])
            st.session_state.items_df = pd.concat([st.session_state.items_df, new_i], ignore_index=True)
            st.rerun()
    
    st.subheader("🗑️ حذف منتج من النظام")
    for i, row in st.session_state.items_df.iterrows():
        c1, c2 = st.columns([4, 1])
        c1.write(f"🔹 {row['السلعة']} (حد الأمان: {row['رقم الأمان']})")
        if c2.button("حذف", key=f"d_{i}"):
            st.session_state.items_df = st.session_state.items_df.drop(i).reset_index(drop=True)
            st.rerun()

st.markdown("<div style='text-align:center; color:gray; margin-top:50px;'>حقوق النظام محفوظة لـ مسؤول القسم: أيوب هاني © 2026</div>", unsafe_allow_html=True)
