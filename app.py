import streamlit as st
import pandas as pd
import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام جرد باب الآغا", layout="wide")

# --- 1. قاعدة البيانات الأساسية ---
if 'items_df' not in st.session_state:
    # أضفت لك عينة من السلع، يمكنك زيادتها لاحقاً
    data = [
        ["باكيت تركي", 50], ["صمون شاورما", 50], ["جرك برازيلي", 150], 
        ["توست ابيض", 130], ["توست اسمر ساده", 80]
    ]
    st.session_state.items_df = pd.DataFrame(data, columns=["السلعة", "رقم الأمان"])

# --- 2. حساب الوقت والتاريخ (توقيت بغداد) ---
# إضافة 3 ساعات لتوقيت الخادم العالمي
iraq_now = datetime.datetime.now() + datetime.timedelta(hours=3)
iraq_date = iraq_now.strftime("%Y-%m-%d")
iraq_time = iraq_now.strftime("%I:%M %p")

# --- 3. واجهة الجرد ---
st.title("🥖 نظام جرد باب الآغا")
st.write(f"📅 التاريخ: **{iraq_date}** | 🕒 الوقت: **{iraq_time}**")
st.write("👤 المسؤول: **أيوب هاني**")
st.divider()

# استخدام Form لحل مشكلة تعليق الكتابة في الموبايل
with st.form("inventory_step1"):
    st.subheader("📝 إدخال بيانات الجرد اليومي")
    
    inventory_data = []
    
    for i, row in st.session_state.items_df.iterrows():
        st.markdown(f"### 📦 {row['السلعة']}")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # إدخال الكمية الموجودة
            qty = st.number_input(f"الموجود ({row['السلعة']})", min_value=0, key=f"q_{i}", step=1)
        
        with col2:
            # حساب الحالة تلقائياً (كافٍ أو غير كافٍ)
            status = "✅ كافٍ" if qty >= row['رقم الأمان'] else "⚠️ غير كافٍ"
            st.write(f"الحالة: **{status}**")
            
        with col3:
            # خانة الملاحظات
            note = st.text_input("ملاحظات إضافية", key=f"n_{i}", placeholder="مثلاً: بانتظار الخبز...")
        
        inventory_data.append({"السلعة": row['السلعة'], "الموجود": qty, "الحالة": status, "الملاحظة": note})
        st.divider()

    # زر الحفظ والاعتماد
    submit = st.form_submit_button("💾 حفظ بيانات الجرد")

if submit:
    st.session_state.step1_done = inventory_data
    st.success("✅ تم حفظ الجرد الأولي بنجاح!")
    st.balloons()
