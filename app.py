import streamlit as st
import pandas as pd
import datetime
import base64
import urllib.parse

# --- 1. إعدادات الصفحة والمظهر ---
st.set_page_config(page_title="نظام جرد باب الآغا - أيوب هاني", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main-header { background-color: #1e3a8a; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1e3a8a; color: white; font-weight: bold; padding: 12px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الذاكرة (Session State) ---
if 'items_df' not in st.session_state:
    initial_data = [["باكيت تركي", 50], ["جرك بالحليب", 100], ["توست ابيض", 130]]
    st.session_state.items_df = pd.DataFrame(initial_data, columns=["السلعة", "رقم الأمان"])

if 'orders_df' not in st.session_state:
    st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])

# --- 3. القائمة الجانبية ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🍞 لوحة التحكم</h2>", unsafe_allow_html=True)
    menu = st.radio("انتقل إلى:", ["📋 الجرد والطباعة", "🛒 إدارة الطلبيات", "🛠️ إعدادات السلع"])
    st.divider()
    st.info(f"المسؤول: أيوب هاني")

# توقيت العراق (بغداد)
iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
iraq_date = iraq_now.strftime("%Y-%m-%d")
iraq_time = iraq_now.strftime("%I:%M %p")

# --- 4. الأقسام الرئيسية ---

if menu == "📋 الجرد والطباعة":
    st.markdown("<div class='main-header'><h1>📋 جرد قسم التوست والحلويات</h1></div>", unsafe_allow_html=True)
    st.write(f"📅 التاريخ: **{iraq_date}** | 🕒 الوقت: **{iraq_time}**")

    with st.form("inventory_form"):
        st.subheader("📝 أدخل بيانات الجرد:")
        results = []
        for i, row in st.session_state.items_df.iterrows():
            c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
            with c1: st.markdown(f"**{row['السلعة']}**")
                        with c2: 
                q = st.number_input("الموجود", min_value=0, key=f"q_{i}", value=st.session_state.get(f"q_{i}", 0))
            with c3: 
                r = st.number_input("التوصية", min_value=0, key=f"r_{i}", value=st.session_state.get(f"r_{i}", 0))
            with c4: 
                n = st.text_input("الملاحظة", key=f"n_{i}", value=st.session_state.get(f"n_{i}", ""), placeholder="ملاحظة..")

            results.append({"السلعة": row['السلعة'], "الموجود": q, "التوصية": r, "الملاحظة": n})
        
        if st.form_submit_button("🚀 اعتماد الجرد وتوليد التقرير والمعاينة"):
            st.session_state.final_rep = results

    if 'final_rep' in st.session_state:
        st.divider()
        st.subheader("🔍 معاينة التقرير النهائي (A4)")
        
        # بناء جدول الجرد
        rows_html = ""
        wa_text = f"📋 *تقرير جرد باب الآغا*\n📅 {iraq_date} | {iraq_time}\n👤 المسؤول: أيوب هاني\n━━━━━━━━━━━━\n"
        
        for x in st.session_state.final_rep:
            if x['الموجود'] > 0 or x['التوصية'] > 0:
                rows_html += f"<tr><td>{x['السلعة']}</td><td>{x['الموجود']}</td><td>{x['التوصية']}</td><td>{x['الملاحظة']}</td></tr>"
                wa_text += f"🔹 *{x['السلعة']}* -> موجود: {x['الموجود']} | طلب: {x['التوصية']}\n"

        # إضافة الطلبيات للتقرير والواتساب
        orders_html = ""
        if not st.session_state.orders_df.empty:
            wa_text += "\n🛒 *الوصايا والطلبيات:*\n"
            orders_html = "<h3>🛒 الطلبيات والوصايا الإضافية:</h3><ul>"
            for _, row in st.session_state.orders_df.iterrows():
                orders_html += f"<li><b>{row['الطلب']}:</b> {row['التفاصيل']}</li>"
                wa_text += f"• {row['الطلب']}: {row['التفاصيل']}\n"
            orders_html += "</ul>"

        # تصميم التقرير للطباعة (مع التواقيع)
        report_design = f"""
        <div dir="rtl" style="font-family: 'Cairo', Arial; padding: 30px; border: 2px solid #1e3a8a; background: white; color: black;">
            <center><h1 style="color:#1e3a8a;">مخابز باب الآغا 🥖</h1><h2>تقرير الجرد والوصايا</h2></center>
            <p><b>التاريخ:</b> {iraq_date} | <b>الوقت:</b> {iraq_time} | <b>المسؤول:</b> أيوب هاني</p>
            <hr>
            <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
                <tr style="background: #eee;"><th>السلعة</th><th>الموجود</th><th>التوصية</th><th>الملاحظة</th></tr>
                {rows_html}
            </table>
            {orders_html}
            <br><br><br>
            <div style="display: flex; justify-content: space-between; font-weight: bold;">
                <span>✍️ توقيع المسؤول (أيوب هاني): ...................</span>
                <span>✍️ توقيع كابتن الصالة: ...................</span>
            </div>
        </div>
        """
        st.markdown(report_design, unsafe_allow_html=True)
        
        c_wa, c_pr = st.columns(2)
        with c_wa:
            # زر الواتساب (يرسل كل شيء)
            encoded_wa = urllib.parse.quote(wa_text + "\nتم بواسطة نظام أيوب الذكي")
            st.markdown(f'<a href="https://wa.me/9647510853103?text={encoded_wa}" target="_blank"><button style="background:#25d366;">📲 إرسال التقرير كامل للواتساب</button></a>', unsafe_allow_html=True)
        with c_pr:
            # زر الطباعة A4
            b64 = base64.b64encode(report_design.encode('utf-8')).decode()
            st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button>🖨️ فتح نسخة الطباعة (A4)</button></a>', unsafe_allow_html=True)

elif menu == "🛒 إدارة الطلبيات":
    st.header("🛒 سجل الطلبيات والوصايا")
    with st.form("o_form", clear_on_submit=True):
        name = st.text_input("اسم صاحب الطلب")
        detail = st.text_area("تفاصيل الوصية")
        if st.form_submit_button("حفظ الطلبية"):
            st.session_state.orders_df = pd.concat([st.session_state.orders_df, pd.DataFrame([{"الطلب": name, "التفاصيل": detail}])], ignore_index=True)
            st.success("✅ تم حفظ الطلب بنجاح")
    st.table(st.session_state.orders_df)
    if st.button("🗑️ مسح كل الطلبيات"):
        st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])
        st.rerun()

elif menu == "🛠️ إعدادات السلع":
    st.header("🛠️ إضافة أو حذف أصناف")
    col_a, col_b = st.columns(2)
    with col_a:
        new_i = st.text_input("اسم المنتج الجديد")
        if st.button("➕ إضافة"):
            st.session_state.items_df = pd.concat([st.session_state.items_df, pd.DataFrame([{"السلعة": new_i, "رقم الأمان": 50}])], ignore_index=True)
            st.rerun()
    with col_b:
        to_del = st.selectbox("اختر صنفاً لحذفه:", st.session_state.items_df["السلعة"])
        if st.button("🗑️ حذف"):
            st.session_state.items_df = st.session_state.items_df[st.session_state.items_df["السلعة"] != to_del]
            st.rerun()
