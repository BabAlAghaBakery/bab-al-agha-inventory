import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# --- 1. الإعدادات ---
st.set_page_config(page_title="باب الآغا - أيوب", layout="wide")

# --- 2. الذاكرة ---
if 'items' not in st.session_state:
    st.session_state.items = ["باكيت تركي", "جرك بالحليب", "توست ابيض"]
if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 3. الوقت ---
iraq_time = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%d-%m-%Y %I:%M %p")

# --- 4. القائمة الجانبية ---
menu = st.sidebar.radio("القائمة:", ["الجرد", "الطلبيات", "إضافة صنف"])

# --- 5. قسم الجرد ---
if menu == "الجرد":
    st.title("📋 جرد باب الآغا")
    st.write(f"📅 {iraq_time}")
    
    current_data = []
    for item in st.session_state.items:
        col = st.columns([2, 1, 1])
        with col[0]: st.write(f"**{item}**")
        # استخدام key بسيط جداً لضمان عدم ضياع الأرقام
        with col[1]: m = st.number_input(f"موجو {item}", min_value=0, key=f"m_{item}")
        with col[2]: t = st.number_input(f"توصي {item}", min_value=0, key=f"t_{item}")
        current_data.append({"الاسم": item, "م": m, "ت": t})

    if st.button("🚀 إرسال التقرير"):
        # بناء نص الواتساب بطريقة بسيطة ومضمونة
        txt = f"*تقرير جرد باب الآغا*\n📅 {iraq_time}\n\n"
        for d in current_data:
            if d['م'] > 0 or d['ت'] > 0:
                txt += f"• {d['الاسم']}: م({d['م']}) ت({d['ت']})\n"
        
        if st.session_state.orders:
            txt += "\n🛒 *الطلبيات الإضافية:*\n"
            for o in st.session_state.orders:
                txt += f"- {o}\n"
        
        # رابط الواتساب المباشر
        link = f"https://wa.me/9647510853103?text={urllib.parse.quote(txt)}"
        st.markdown(f'[✅ اضغط هنا للإرسال عبر واتساب]({link})')
        
        # عرض التقرير بشكل بسيط جداً ليقرأه الموبايل
        st.subheader("التقرير النهائي:")
        st.table(pd.DataFrame([d for d in current_data if d['م']>0 or d['ت']>0]))

# --- 6. قسم الطلبيات ---
elif menu == "الطلبيات":
    st.title("🛒 تسجيل الطلبيات")
    new_order = st.text_area("اكتب الطلبية هنا:")
    if st.button("حفظ الطلبية"):
        st.session_state.orders.append(new_order)
        st.success("تم الحفظ")
    st.write(st.session_state.orders)

# --- 7. إضافة صنف ---
elif menu == "إضافة صنف":
    new_i = st.text_input("اسم الصنف:")
    if st.button("إضافة"):
        st.session_state.items.append(new_i)
        st.rerun()
