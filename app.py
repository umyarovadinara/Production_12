import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка страницы
st.set_page_config(page_title="Дашборд отгрузки стали", layout="wide")

st.title("📊 Аналитика производства стали S700MC")

# Загрузка данных
@st.cache_data
def load_data():
    # Предполагаем расширение .xlsx, так как это Excel
    df = pd.read_excel("ProductionS700MC.xlsx")
    # Преобразуем дату в формат datetime, если такой столбец есть
    # Если столбца "Дата" нет, создадим тестовую колонку для демонстрации динамики
    if 'Дата' in df.columns:
        df['Дата'] = pd.to_datetime(df['Дата'])
    return df

try:
    df = load_data()

    # --- САЙДБАР (ФИЛЬТРЫ) ---
    st.sidebar.header("Фильтры")
    
    recipient = st.sidebar.multiselect(
        "Выберите грузополучателя:",
        options=df["Грузополучатель"].unique(),
        default=df["Грузополучатель"].unique()
    )

    thickness = st.sidebar.slider(
        "Толщина:",
        float(df["Толщина"].min()),
        float(df["Толщина"].max()),
        (float(df["Толщина"].min()), float(df["Толщина"].max()))
    )

    # Фильтрация датафрейма
    mask = (
        df["Грузополучатель"].isin(recipient) &
        df["Толщина"].between(*thickness)
    )
    df_filtered = df[mask]

    # --- ОСНОВНЫЕ ПОКАЗАТЕЛИ ---
    total_mass = df_filtered["Масса"].sum()
    st.metric("Общий объем производства", f"{total_mass:,.2f} тонн")

    col1, col2 = st.columns(2)

    with col1:
        # а) Динамика производства (если есть столбец Дата)
        if 'Дата' in df_filtered.columns:
            st.subheader("Динамика по дням")
            daily_prod = df_filtered.groupby('Дата')['Масса'].sum().reset_index()
            fig_date = px.line(daily_prod, x='Дата', y='Масса', markers=True)
            st.plotly_chart(fig_date, use_container_width=True)
        else:
            st.info("Добавьте столбец 'Дата' для отображения динамики.")

        # в) По грузополучателям
        st.subheader("Объем по грузополучателям")
        fig_rec = px.bar(df_filtered, x='Грузополучатель', y='Масса', color='Грузополучатель')
        st.plotly_chart(fig_rec, use_container_width=True)

    with col2:
        # б) В разрезе толщин и ширин
        st.subheader("Распределение: Толщина vs Ширина")
        fig_scatter = px.scatter(
            df_filtered, 
            x="Толщина", 
            y="Ширина", 
            size="Масса", 
            color="Грузополучатель",
            hover_name="Грузополучатель"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Дополнительная гистограмма толщин
        st.subheader("Объем по толщинам")
        fig_thick = px.histogram(df_filtered, x="Толщина", y="Масса", nbins=20)
        st.plotly_chart(fig_thick, use_container_width=True)

    # Таблица данных
    with st.expander("Посмотреть исходные данные"):
        st.write(df_filtered)

except Exception as e:
    st.error(f"Ошибка при загрузке файла: {e}")
    st.info("Убедитесь, что файл 'ProductionS700MC.xlsx' лежит в том же репозитории на GitHub, что и этот код.")
