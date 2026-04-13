import streamlit as st
import pandas as pd
import datetime
import base64
import urllib.parse

# --- 1. إعدادات الصفحة والستايل الاحترافي ---
st.set_page_config(page_title="نظام باب الآغا - أيوب هاني", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main-header { background-color: #1e3a8a; color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #2563eb; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة الذاكرة الصلبة (لضمان حفظ البيانات عند التنقل) ---
if 'items_list' not in st.session_state:
    st.session_state.items_list = ["باكيت تركي", "جرك بالحليب", "توست ابيض", "صمون شاورما"]

if 'orders_list' not in st.session_state:
    st.session_state.orders_list = []

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🍞 لوحة التحكم</h2>", unsafe_allow_html=True)
    menu = st.radio("انتقل إلى:", ["📋 جرد السلع", "🛒 حجز طلبيات", "⚙️ إدارة الأصناف"])
    st.divider()
    st.info("المسؤول: أيوب هاني")

# توقيت العراق (بغداد)
iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
iraq_date = iraq_now.strftime("%d-%m-%Y")
iraq_time = iraq_now.strftime("%I:%M %p")

# --- 4. الأقسام الرئيسية ---

# أ. قسم الجرد
if menu == "📋 جرد السلع":
    st.markdown("<div class='main-header'><h1>📋 نظام جرد مخابز باب الآغا</h1></div>", unsafe_allow_html=True)
    st.write(f"📅 التاريخ: **{iraq_date}** | 🕒 الوقت: **{iraq_time}**")

    # جدول الجرد - الإدخال مباشر لضمان الحفظ اللحظي
    results = []
    st.markdown("### 📝 جدول إدخال الجرد:")
    
    # رأس الجدول
    h1, h2, h3, h4 = st.columns([2, 1, 1, 2])
    h1.write("**نوع السلعة**")
    h2.write("**الكمية**")
    h3.write("**التوصية**")
    h4.write("**الملاحظات**")
    st.divider()

    for i, item in enumerate(st.session_state.items_list):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
        with c1: 
            st.write(f"**{item}**")
        with c2: 
            # استخدام key فريد هو السر في عدم ضياع الأرقام
            m = st.number_input("الكمية", min_value=0, key=f"m_{item}", label_visibility="collapsed")
        with c3: 
            t = st.number_input("التوصية", min_value=0, key=f"t_{item}", label_visibility="collapsed")
        with c4: 
            n = st.text_input("ملاحظة", key=f"n_{item}", placeholder="أدخل ملاحظة...", label_visibility="collapsed")
        
        results.append({"السلعة": item, "الموجود": m, "التوصية": t, "الملاحظة": n})

    st.divider()
    
    # أزرار العمليات
    col_print, col_wa = st.columns(2)
    
    # بناء نص الواتساب والتقرير
    report_rows = ""
    wa_msg = f"📋 *تقرير جرد باب الآغا*\n📅 {iraq_date} | {iraq_time}\n👤 المسؤول: أيوب هاني\n━━━━━━━━━━━━\n"
    
    active_data = [r for r in results if r['الموجود'] > 0 or r['التوصية'] > 0]
    
    for r in active_data:
        report_rows += f"<tr><td>{r['السلعة']}</td><td>{r['الموجود']}</td><td>{r['التوصية']}</td><td>{r['الملاحظة']}</td></tr>"
        wa_msg += f"🔹 *{r['السلعة']}* -> م: {r['الموجود']} | ت: {r['التوصية']}\n"

    # إضافة الطلبيات للتقرير
    orders_html = ""
    if st.session_state.orders_list:
        wa_msg += "\n🛒 *الطلبيات والوصايا:*\n"
        orders_html = "<h3>🛒 الطلبيات والحجوزات الإضافية:</h3><ul>"
        for o in st.session_state.orders_list:
            orders_html += f"<li>{o}</li>"
            wa_msg += f"• {o}\n"
        orders_html += "</ul>"

    # تصميم ورقة A4
    html_template = f"""
    <div dir="rtl" style="font-family: 'Cairo', Arial; padding: 30px; border: 2px solid #1e3a8a; background: white; color: black; min-height: 297mm;">
        <center>
            <h1 style="color:#1e3a8a; margin-bottom:0;">مخابز باب الآغا 🥖</h1>
            <p style="margin-top:5px;">فرع بغداد - تقرير الجرد اليومي</p>
        </center>
        <hr>
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <span><b>التاريخ:</b> {iraq_date}</span>
            <span><b>الوقت:</b> {iraq_time}</span>
            <span><b>المسؤول:</b> أيوب هاني</span>
        </div>
        <table border="1" style="width:100%; border-collapse: collapse; text-align: center; margin-bottom: 20px;">
            <tr style="background-color: #f0f0f0;">
                <th style="padding: 10px;">نوع السلعة</th>
                <th>الكمية المتوفرة</th>
                <th>الكمية الموصى بها</th>
                <th>الملاحظات</th>
            </tr>
            {report_rows}
        </table>
        {orders_html}
        <br><br><br>
        <div style="display: flex; justify-content: space-between; font-weight: bold; margin-top: 50px;">
            <div style="text-align: center; border-top: 1px solid black; width: 200px; padding-top: 5px;">توقيع المسؤول</div>
            <div style="text-align: center; border-top: 1px solid black; width: 200px; padding-top: 5px;">توقيع الكابتن</div>
        </div>
    </div>
    """

    with col_print:
        b64 = base64.b64encode(html_template.encode('utf-8')).decode()
        st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank"><button>🖨️ طباعة تقرير A4</button></a>', unsafe_allow_html=True)

    with col_wa:
        encoded_wa = urllib.parse.quote(wa_msg + "\nتمت البرمجة بواسطة أيوب هاني")
        st.markdown(f'<a href="https://wa.me/9647510853103?text={encoded_wa}" target="_blank"><button style="background-color: #25d366;">📲 إرسال للواتساب</button></a>', unsafe_allow_html=True)

    # معاينة سريعة تحت الأزرار
    with st.expander("🔍 معاينة الورقة قبل الطباعة"):
        st.markdown(html_template, unsafe_allow_html=True)

# ب. قسم الطلبيات
elif menu == "🛒 حجز طلبيات":
    st.title("🛒 سجل حجز الطلبيات والوصايا")
    with st.container(border=True):
        new_order = st.text_area("أدخل تفاصيل الطلبية (الاسم، السلعة، الوقت):")
        if st.button("💾 حفظ الطلبية في السجل"):
            if new_order:
                st.session_state.orders_list.append(new_order)
                st.success("✅ تم حفظ الطلبية بنجاح")
            else:
                st.warning("يرجى كتابة تفاصيل الطلب أولاً")

    st.subheader("📋 القائمة المسجلة اليوم:")
    for i, order in enumerate(st.session_state.orders_list):
        st.info(f"{i+1}. {order}")
    
    if st.button("🗑️ مسح كل الطلبيات"):
        st.session_state.orders_list = []
        st.rerun()

# ج. قسم الإعدادات
elif menu == "⚙️ إدارة الأصناف":
    st.title("⚙️ إدارة قائمة السلع")
    
    col_add, col_rem = st.columns(2)
    
    with col_add:
        st.subheader("➕ إضافة صنف جديد")
        add_name = st.text_input("اسم السلعة:")
        if st.button("تأكيد الإضافة"):
            if add_name and add_name not in st.session_state.items_list:
                st.session_state.items_list.append(add_name)
                st.rerun()

    with col_rem:
        st.subheader("❌ إزالة صنف")
        rem_name = st.selectbox("اختر الصنف المراد حذفه:", st.session_state.items_list)
        if st.button("تأكيد الحذف"):
            st.session_state.items_list.remove(rem_name)
            st.rerun()
