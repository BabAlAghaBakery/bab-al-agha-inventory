import streamlit as st
import pandas as pd
import datetime
import base64
import urllib.parse

# --- 1. الإعدادات الأساسية ---
st.set_page_config(page_title="نظام باب الآغا - أيوب هاني", layout="wide")

# --- 2. تهيئة الذاكرة (Session State) ---
# التأكد من تعريف كل شيء في البداية لمنع الأخطاء الحمراء
if 'items_df' not in st.session_state:
    st.session_state.items_df = pd.DataFrame([["باكيت تركي", 50], ["جرك بالحليب", 100], ["توست ابيض", 130]], columns=["السلعة", "رقم الأمان"])

if 'orders_df' not in st.session_state:
    st.session_state.orders_df = pd.DataFrame(columns=["الطلب", "التفاصيل"])

# --- 3. القائمة الجانبية ---
with st.sidebar:
    st.header("🍞 لوحة التحكم")
    menu = st.radio("انتقل إلى:", ["📋 الجرد", "🛒 الطلبيات", "⚙️ الإعدادات"])
    st.info("المسؤول: أيوب هاني")

# توقيت العراق
iraq_date = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d-%m-%Y")

# --- 4. الأقسام الرئيسية ---

if menu == "📋 الجرد":
    st.title("📋 نظام الجرد اليومي")
    st.write(f"📅 التاريخ: {iraq_date}")
    
    # عرض الإدخالات بدون FORM لضمان الحفظ اللحظي
    results = []
    for i, row in st.session_state.items_df.iterrows():
        c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
        with c1: st.write(f"**{row['السلعة']}**")
        with c2: 
            q = st.number_input("م", min_value=0, key=f"inv_q_{i}")
        with c3: 
            r = st.number_input("ت", min_value=0, key=f"inv_r_{i}")
        with c4: 
            n = st.text_input("ملاحظة", key=f"inv_n_{i}")
        results.append({"السلعة": row['السلعة'], "الموجود": q, "التوصية": r, "الملاحظة": n})

    if st.button("🚀 توليد التقرير النهائي"):
        st.session_state.final_data = results
        st.success("تم تجهيز التقرير بالأسفل!")

    # عرض التقرير والطباعة
    if 'final_data' in st.session_state:
        rows_html = ""
        wa_text = f"📋 *جرد باب الآغا* \n📅 {iraq_date}\n\n"
        for x in st.session_state.final_data:
            if x['الموجود'] > 0 or x['التوصية'] > 0:
                rows_html += f"<tr><td>{x['السلعة']}</td><td>{x['الموجود']}</td><td>{x['التوصية']}</td><td>{x['الملاحظة']}</td></tr>"
                wa_text += f"• {x['السلعة']}: م({x['الموجود']}) ت({x['التوصية']})\n"
        
        # إضافة الطلبيات للواتساب
        if not st.session_state.orders_df.empty:
            wa_text += "\n🛒 *الطلبيات:* \n"
            for _, o in st.session_state.orders_df.iterrows():
                wa_text += f"- {o['الطلب']}: {o['التفاصيل']}\n"

        report_html = f"""
        <div dir="rtl" style="font-family: Arial; padding: 20px; border: 2px solid #1e3a8a; background: white; color: black;">
            <center><h2 style="color:#1e3a8a;">مخابز باب الآغا 🥖</h2></center>
            <p>📅 التاريخ: {iraq_date} | 👤 المسؤول: أيوب هاني</p>
            <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
                <tr style="background:#eee;"><th>السلعة</th><th>م</th><th>ت</th><th>ملاحظة</th></tr>
                {rows_html}
            </table>
            <br>
            <div style="display: flex; justify-content: space-between;">
                <span>توقيع المسؤول: ...........</span>
                <span>توقيع الكابتن: ...........</span>
            </div>
        </div>
        """
        st.markdown(report_html, unsafe_allow_html=True)
        
        # أزرار الواتساب والطباعة
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<a href="https://wa.me/9647510853103?text={urllib.parse.quote(wa_text)}" target="_blank"><button style="width:100%; background:#25d366; color:white; border:none; padding:10px; border-radius:5px;">📲 إرسال واتساب</button></a>', unsafe_allow_html=True)
        with col2:
            b64 = base64.b64encode(report_html.encode('utf-8')).decode()
            st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button style="width:100%; background:#1e3a8a; color:white; border:none; padding:10px; border-radius:5px;">🖨️ طباعة A4</button></a>', unsafe_allow_html=True)

elif menu == "🛒 الطلبيات":
    st.title("🛒 تسجيل الطلبيات")
    t1 = st.text_input("اسم الطلب")
    t2 = st.text_area("التفاصيل")
    if st.button("حفظ الطلبية"):
        st.session_state.orders_df = pd.concat([st.session_state.orders_df, pd.DataFrame([{"الطلب": t1, "التفاصيل": t2}])], ignore_index=True)
        st.rerun()
    st.table(st.session_state.orders_df)

elif menu == "⚙️ الإعدادات":
    st.title("⚙️ إدارة السلع")
    new_i = st.text_input("أضف صنف جديد")
    if st.button("إضافة"):
        st.session_state.items_df = pd.concat([st.session_state.items_df, pd.DataFrame([[new_i, 50]], columns=["السلعة", "رقم الأمان"])], ignore_index=True)
        st.rerun()
