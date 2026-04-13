import streamlit as st
import pandas as pd
import datetime
import base64
import urllib.parse

# --- 1. إعدادات الصفحة والمظهر ---
st.set_page_config(page_title="نظام باب الآغا - أيوب هاني", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main-header { background-color: #1e3a8a; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1e3a8a; color: white; font-weight: bold; padding: 12px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الذاكرة (لضمان حفظ البيانات عند التنقل) ---
if 'items_df' not in st.session_state:
    initial_data = [["باكيت تركي", 50], ["جرك بالحليب", 100], ["توست ابيض", 130], ["صمون شاورما", 50]]
    st.session_state.items_df = pd.DataFrame(initial_data, columns=["السلعة", "رقم الأمان"])

if 'orders_df' not in st.session_state:
    st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])

if 'final_rep' not in st.session_state:
    st.session_state.final_rep = None

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🍞 لوحة التحكم</h2>", unsafe_allow_html=True)
    menu = st.radio("انتقل إلى:", ["📋 الجرد والطباعة", "🛒 إدارة الطلبيات", "🛠️ إعدادات السلع"])
    st.divider()
    st.info(f"المسؤول: أيوب هاني")

# ضبط توقيت بغداد
iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
iraq_date = iraq_now.strftime("%Y-%m-%d")
iraq_time = iraq_now.strftime("%I:%M %p")

# --- 4. الأقسام الرئيسية ---

# القسم الأول: الجرد والطباعة
if menu == "📋 الجرد والطباعة":
    st.markdown("<div class='main-header'><h1>📋 جرد قسم التوست والحلويات</h1></div>", unsafe_allow_html=True)
    st.write(f"📅 التاريخ: **{iraq_date}** | 🕒 الوقت: **{iraq_time}**")

    with st.form("inventory_form"):
        st.subheader("📝 أدخل بيانات الجرد:")
        results = []
        for i, row in st.session_state.items_df.iterrows():
            c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
            with c1: 
                st.markdown(f"**{row['السلعة']}**")
            with c2: 
                # الحل النهائي لحفظ الرقم عند التنقل: استخدام key فريد وقيمة من الـ session_state
                q = st.number_input("م", min_value=0, key=f"q_{i}", value=st.session_state.get(f"q_{i}", 0))
            with c3: 
                r = st.number_input("ت", min_value=0, key=f"r_{i}", value=st.session_state.get(f"r_{i}", 0))
            with c4: 
                n = st.text_input("ن", key=f"n_{i}", value=st.session_state.get(f"n_{i}", ""), placeholder="ملاحظة..")
            
            results.append({"السلعة": row['السلعة'], "الموجود": q, "التوصية": r, "الملاحظة": n})
        
        submit_btn = st.form_submit_button("🚀 اعتماد الجرد وتوليد التقرير")

    if submit_btn:
        st.session_state.final_rep = results
        st.success("✅ تم الاعتماد بنجاح")

    # المعاينة والطباعة والواتساب
    if st.session_state.final_rep is not None:
        st.divider()
        st.subheader("📄 معاينة التقرير النهائي (جاهز للطباعة A4)")
        
        rows_html = ""
        wa_text = f"📋 *تقرير جرد باب الآغا*\n📅 {iraq_date} | {iraq_time}\n👤 المسؤول: أيوب هاني\n━━━━━━━━━━━━\n"
        
        for x in st.session_state.final_rep:
            if x['الموجود'] > 0 or x['التوصية'] > 0:
                rows_html += f"<tr><td>{x['السلعة']}</td><td>{x['الموجود']}</td><td>{x['التوصية']}</td><td>{x['الملاحظة']}</td></tr>"
                wa_text += f"🔹 *{x['السلعة']}* -> م: {x['الموجود']} | ت: {x['التوصية']}\n"

        orders_html = ""
        if not st.session_state.orders_df.empty:
            wa_text += "\n🛒 *الوصايا والطلبيات:*\n"
            orders_html = "<h3>🛒 الطلبيات والوصايا الإضافية:</h3><ul>"
            for _, row in st.session_state.orders_df.iterrows():
                orders_html += f"<li><b>{row['الطلب']}:</b> {row['التفاصيل']}</li>"
                wa_text += f"• {row['الطلب']}: {row['التفاصيل']}\n"
            orders_html += "</ul>"

        report_design = f"""
        <div dir="rtl" style="font-family: Arial; padding: 25px; border: 2px solid #1e3a8a; background: white; color: black;">
            <center><h1 style="color:#1e3a8a;">مخابز باب الآغا 🥖</h1><h2>تقرير الجرد والوصايا</h2></center>
            <p><b>التاريخ:</b> {iraq_date} | <b>الوقت:</b> {iraq_time} | <b>المسؤول:</b> أيوب هاني</p>
            <hr>
            <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
                <tr style="background: #eee;"><th>السلعة</th><th>الموجود</th><th>التوصية</th><th>الملاحظة</th></tr>
                {rows_html}
            </table>
            {orders_html}
            <br><br>
            <div style="display: flex; justify-content: space-between; font-weight: bold;">
                <span>✍️ توقيع المسؤول (أيوب هاني): ...................</span>
                <span>✍️ توقيع كابتن الصالة: ...................</span>
            </div>
        </div>
        """
        st.markdown(report_design, unsafe_allow_html=True)
        
        c_wa, c_pr = st.columns(2)
        with c_wa:
            encoded_wa = urllib.parse.quote(wa_text + "\nتم بواسطة نظام أيوب الذكي")
            st.markdown(f'<a href="https://wa.me/9647510853103?text={encoded_wa}" target="_blank"><button style="background:#25d366;">📲 إرسال كامل التقرير للواتساب</button></a>', unsafe_allow_html=True)
        with c_pr:
            b64 = base64.b64encode(report_design.encode('utf-8')).decode()
            st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button>🖨️ فتح نسخة الطباعة (A4)</button></a>', unsafe_allow_html=True)

# القسم الثاني: إدارة الطلبيات
elif menu == "🛒 إدارة الطلبيات":
    st.header("🛒 سجل الطلبيات والوصايا")
    with st.form("o_form", clear_on_submit=True):
        name = st.text_input("اسم صاحب الطلب")
        detail = st.text_area("تفاصيل الوصية")
        if st.form_submit_button("حفظ الطلبية"):
            new_o = pd.DataFrame([{"الطلب": name, "التفاصيل": detail}])
            st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_o], ignore_index=True)
            st.success("✅ تم الحفظ")
    
    st.subheader("📋 القائمة الحالية")
    st.table(st.session_state.orders_df)
    if st.button("🗑️ مسح كل الطلبيات"):
        st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])
        st.rerun()

# القسم الثالث: إعدادات السلع
elif menu == "🛠️ إعدادات السلع":
    st.header("🛠️ التحكم في قائمة الأصناف")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("➕ إضافة صنف")
        new_i = st.text_input("اسم المنتج الجديد")
        if st.button("تأكيد الإضافة"):
            st.session_state.items_df = pd.concat([st.session_state.items_df, pd.DataFrame([{"السلعة": new_i, "رقم الأمان": 50}])], ignore_index=True)
            st.rerun()
    with col_b:
        st.subheader("🗑️ حذف صنف")
        to_del = st.selectbox("اختر الصنف:", st.session_state.items_df["السلعة"])
        if st.button("تأكيد الحذف"):
            st.session_state.items_df = st.session_state.items_df[st.session_state.items_df["السلعة"] != to_del]
            st.rerun()
