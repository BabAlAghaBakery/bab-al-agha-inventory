import streamlit as st
import pandas as pd
import datetime
import base64
import urllib.parse

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="نظام باب الآغا - أيوب هاني", layout="wide")

# تصميم المظهر
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main-header { background-color: #1e3a8a; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الذاكرة (Session State) ---
# تعريف الجداول فوراً لمنع الخطأ الأحمر AttributeError
if 'items_df' not in st.session_state:
    initial_data = [["باكيت تركي", 50], ["جرك بالحليب", 100], ["توست ابيض", 130]]
    st.session_state.items_df = pd.DataFrame(initial_data, columns=["السلعة", "رقم الأمان"])

if 'orders_df' not in st.session_state:
    st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])

if 'final_rep' not in st.session_state:
    st.session_state.final_rep = None

# --- 3. القائمة الجانبية ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🍞 لوحة التحكم</h2>", unsafe_allow_html=True)
    menu = st.radio("انتقل إلى:", ["📋 الجرد والطباعة", "🛒 إدارة الطلبيات", "🛠️ إعدادات السلع"])
    st.divider()
    st.info("المسؤول: أيوب هاني")

# توقيت العراق
iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
iraq_date = iraq_now.strftime("%d-%m-%Y")
iraq_time = iraq_now.strftime("%I:%M %p")

# --- 4. الأقسام ---

if menu == "📋 الجرد والطباعة":
    st.markdown("<div class='main-header'><h1>📋 جرد قسم التوست والحلويات</h1></div>", unsafe_allow_html=True)
    st.write(f"📅 **التاريخ:** {iraq_date} | 🕒 **الوقت:** {iraq_time}")

    # نموذج الجرد
    with st.form("inventory_form"):
        st.subheader("📝 أدخل بيانات الجرد:")
        current_results = []
        
        for i, row in st.session_state.items_df.iterrows():
            cols = st.columns([2, 1, 1, 2])
            with cols[0]: st.markdown(f"**{row['السلعة']}**")
            # السر في حفظ الأرقام هو استخدام value=st.session_state.get
            with cols[1]: q = st.number_input("م", min_value=0, key=f"q_{i}", value=st.session_state.get(f"q_{i}", 0))
            with cols[2]: r = st.number_input("ت", min_value=0, key=f"r_{i}", value=st.session_state.get(f"r_{i}", 0))
            with cols[3]: n = st.text_input("ن", key=f"n_{i}", value=st.session_state.get(f"n_{i}", ""), placeholder="ملاحظة..")
            current_results.append({"السلعة": row['السلعة'], "الموجود": q, "التوصية": r, "الملاحظة": n})
        
        if st.form_submit_button("🚀 اعتماد الجرد وتوليد التقرير"):
            st.session_state.final_rep = current_results
            st.success("✅ تم حفظ الجرد في الذاكرة")

    # عرض التقرير والطباعة والواتساب
    if st.session_state.final_rep:
        st.divider()
        st.subheader("🔍 معاينة التقرير النهائي")
        
        rows_html = ""
        wa_text = f"📋 *جرد باب الآغا*\n📅 {iraq_date}\n👤 المسؤول: أيوب هاني\n━━━━━━━━━━━━\n"
        
        for x in st.session_state.final_rep:
            if x['الموجود'] > 0 or x['التوصية'] > 0:
                rows_html += f"<tr><td>{x['السلعة']}</td><td>{x['الموجود']}</td><td>{x['التوصية']}</td><td>{x['الملاحظة']}</td></tr>"
                wa_text += f"🔹 *{x['السلعة']}* -> م: {x['الموجود']} | ت: {x['التوصية']}\n"

        orders_html = ""
        if not st.session_state.orders_df.empty:
            wa_text += "\n🛒 *الوصايا والطلبيات:*\n"
            orders_html = "<h3>🛒 الوصايا الإضافية:</h3><ul>"
            for _, r in st.session_state.orders_df.iterrows():
                orders_html += f"<li><b>{r['الطلب']}:</b> {r['التفاصيل']}</li>"
                wa_text += f"• {r['الطلب']}: {r['التفاصيل']}\n"
            orders_html += "</ul>"

        # تصميم الورقة (A4)
        full_html = f"""
        <div dir="rtl" style="font-family: 'Cairo', Arial; padding: 20px; border: 1px solid #ccc; background: white; color: black;">
            <center><h2>مخابز باب الآغا 🥖</h2><h3>تقرير الجرد اليومي</h3></center>
            <p>📅 {iraq_date} | 👤 المسؤول: أيوب هاني</p>
            <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
                <tr style="background: #f0f0f0;"><th>السلعة</th><th>الموجود</th><th>التوصية</th><th>الملاحظة</th></tr>
                {rows_html}
            </table>
            {orders_html}
            <br><br>
            <div style="display: flex; justify-content: space-between;">
                <span>✍️ توقيع المسؤول: .................</span>
                <span>✍️ توقيع الكابتن: .................</span>
            </div>
        </div>
        """
        st.markdown(full_html, unsafe_allow_html=True)
        
        # أزرار الواتساب والطباعة
        c1, c2 = st.columns(2)
        with c1:
            encoded_wa = urllib.parse.quote(wa_text)
            st.markdown(f'<a href="https://wa.me/9647510853103?text={encoded_wa}" target="_blank"><button style="width:100%; background:#25d366; color:white; border:none; padding:10px; border-radius:5px;">📲 إرسال للواتساب</button></a>', unsafe_allow_html=True)
        with c2:
            b64 = base64.b64encode(full_html.encode('utf-8')).decode()
            st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button style="width:100%; background:#1e3a8a; color:white; border:none; padding:10px; border-radius:5px;">🖨️ فتح للطباعة (A4)</button></a>', unsafe_allow_html=True)

elif menu == "🛒 إدارة الطلبيات":
    st.header("🛒 تسجيل الوصايا والطلبيات")
    with st.form("o_form", clear_on_submit=True):
        name = st.text_input("اسم الزبون/الطلب")
        detail = st.text_area("التفاصيل")
        if st.form_submit_button("حفظ الطلب"):
            new_row = pd.DataFrame([{"الطلب": name, "التفاصيل": detail}])
            st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_row], ignore_index=True)
            st.success("✅ تم الحفظ")
    st.table(st.session_state.orders_df)
    if st.button("🗑️ مسح القائمة"):
        st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])
        st.rerun()

elif menu == "🛠️ إعدادات السلع":
    st.header("🛠️ إعدادات الأصناف")
    col1, col2 = st.columns(2)
    with col1:
        new_item = st.text_input("اسم الصنف الجديد")
        if st.button("➕ إضافة"):
            add_df = pd.DataFrame([{"السلعة": new_item, "رقم الأمان": 50}])
            st.session_state.items_df = pd.concat([st.session_state.items_df, add_df], ignore_index=True)
            st.rerun()
    with col2:
        to_del = st.selectbox("حذف صنف:", st.session_state.items_df["السلعة"])
        if st.button("🗑️ حذف"):
            st.session_state.items_df = st.session_state.items_df[st.session_state.items_df["السلعة"] != to_del]
            st.rerun()
