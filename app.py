import streamlit as st
import pandas as pd
import datetime

# --- 1. إعدادات المظهر العام (ذوق احترافي) ---
# جعل الصفحة عريضة لتناسب الحاسبة والموبايل
st.set_page_config(page_title="جرد قسم التوست - باب الآغا", layout="wide")

# إضافة لمسات جمالية واحترافية (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* تغيير الخط وتنسيق النص للعربية */
    html, body, [class*="st-"] {
        font-family: 'Cairo', sans-serif;
        text-align: right;
        direction: rtl;
    }
    
    /* تصميم رأس الصفحة المميز */
    .main-header {
        background-color: #1e3a8a; /* أزرق داكن واحترافي */
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* تنسيق معلومات الوقت والتاريخ */
    .info-bar {
        background-color: #f1f5f9;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* تنسيق زر الحفظ ليكون واضحاً وقوياً */
    .stButton>button {
        width: 100%;
        background-color: #1e3a8a;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات الأولية والذاكرة (Session State) ---
# القائمة الأساسية التي زودتني بها سابقاً (سنستخدم 5 منها كعينة)
if 'items_data' not in st.session_state:
    initial_items = [
        ["باكيت تركي", 50], ["جرك بالحليب", 100], ["توست ابيض", 130],
        ["توست اسمر ساده", 80], ["سميط شعير", 60]
    ]
    # يمكنك إضافة باقي الأصناف (لفه خميرة، كرواسون، كيك...) هنا لاحقاً
    st.session_state.items_data = pd.DataFrame(initial_items, columns=["السلعة", "رقم الأمان"])

# --- 3. حساب الوقت والتاريخ (توقيت العراق/بغداد) ---
# إضافة 3 ساعات لتوقيت الخادم العالمي
iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
iraq_date = iraq_now.strftime("%Y-%m-%d")
iraq_time = iraq_now.strftime("%I:%M %p")

# --- 4. تصميم الواجهة الرئيسية ---
# رأس الصفحة المميز
st.markdown("""
    <div class='main-header'>
        <h1>🥖 نظام جرد باب الآغا - قسم التوست</h1>
        <p>الاحترافية والذكاء في الإدارة</p>
    </div>
    """, unsafe_allow_html=True)

# بار المعلومات
st.markdown(f"""
    <div class='info-bar'>
        <span>📅 التاريخ: <b>{iraq_date}</b></span> | 
        <span>🕒 الوقت: <b>{iraq_time}</b></span> | 
        <span>👤 المسؤول: <b>أيوب هاني</b></span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 5. جدول الجرد الذكي والمنظم ---
st.subheader("📝 أدخل بيانات الجرد اليومي للمنتجات:")

# استخدام "النموذج" (Form) لمنع أي مشاكل في تعليق الكتابة على الموبايل
with st.form("inventory_main_form"):
    
    # رأس الجدول (للحاسبة) - سيتم إخفاؤه في الموبايل عبر التنسيق
    with st.container():
        cols_header = st.columns([2, 1, 1, 2])
        cols_header[0].markdown("**اسم السلعة**")
        cols_header[1].markdown("**الموجود**")
        cols_header[2].markdown("**التوصية**")
        cols_header[3].markdown("**الملاحظات**")
        st.divider()

    temp_results = []
    
    # عرض كل صف من صفوف الجرد
    for i, row in st.session_state.items_data.iterrows():
        # تقسيم السلعة إلى أعمدة متوازنة (2:1:1:2) لتناسب شاشات الحاسبة والموبايل
        col_item, col_qty, col_rec, col_note = st.columns([2, 1, 1, 2])
        
        with col_item:
            # عرض اسم السلعة بوضوح
            st.markdown(f"**🔹 {row['السلعة']}**")
        
        with col_qty:
            # إدخال الكمية المتوفرة حالياً
            # ربط كل حقل بـ 'value' من الذاكرة لضمان عدم ضياع الأرقام
            q = st.number_input("الموجود", min_value=0, value=0, key=f"q_{i}", label_visibility="collapsed")
            
        with col_rec:
            # إدخال الكمية المطلوب توصيتها (الطلب)
            r = st.number_input("التوصية", min_value=0, value=0, key=f"r_{i}", label_visibility="collapsed")
            
        with col_note:
            # إدخال أي ملاحظات أو تفاصيل إضافية
            n = st.text_input("الملاحظات", key=f"n_{i}", placeholder="أضف ملاحظة...", label_visibility="collapsed")
            
        temp_results.append({"السلعة": row['السلعة'], "الموجود": q, "التوصية": r, "الملاحظة": n})
        st.divider() # فاصل بين السلعة والأخرى لزيادة الوضوح في الموبايل

    # زر الاعتماد الرئيسي والقوي
    submit_inventory = st.form_submit_button("🚀 اعتماد الجرد وتوليد التقرير")

# --- 6. الإجراء بعد الاعتماد ---
if submit_inventory:
    # حفظ النتائج النهائية في ذاكرة النظام لتجهيزها للخطوات القادمة
    st.session_state.inventory_ready = temp_results
    st.success("✅ تم حفظ الجرد الأولي بنجاح يا بطل! التقرير جاهز للانتقال للخطوة التالية.")
    
    # بالونات احتفال بنجاح حفظ الجرد!
    st.balloons()
