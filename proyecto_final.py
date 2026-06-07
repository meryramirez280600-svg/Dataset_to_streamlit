# -*- coding: utf-8 -*-
"""
Dashboard de Calidad del Aire - Valle del Aburrá
Archivo para despliegue en Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide", page_title="Dashboard Calidad del Aire 💨")

# --- Cargar y preparar los datos ---
@st.cache_data
def load_data():
    df = pd.read_csv('Datesetlimpio_uso.csv')
    df['Fechas/horas del máximo'] = pd.to_datetime(df['Fechas/horas del máximo'], errors='coerce')
    df['Fechas/horas del mínimo'] = pd.to_datetime(df['Fechas/horas del mínimo'], errors='coerce')
    return df

df_aire = load_data()

# Definir límites de contaminación
pollution_limits = {
    'PM10': 50,   # ugm3, promedio anual
    'PM2.5': 25,  # ugm3, promedio anual
    'NO2': 200,   # ugm3, promedio anual
    'SO2': 50,    # ugm3, promedio anual
    'O3': 100     # ugm3, promedio anual
}

# Categorías de variables
gases_contaminantes = ['NO', 'NO2', 'SO2', 'SO2_TR', 'O3', 'CO']
material_particulado = ['PM10', 'PM2.5', 'PST']
meteorological_variables_list = ['VViento', 'DViento', 'TAire', 'TAire2', 'TAire10',
                                  'PLiquida', 'P', 'HAire', 'HAire2', 'HAire10', 'RGlobal', 'RUVb']
all_defined_contaminants = gases_contaminantes + material_particulado

def get_variable_type(variable):
    if variable in gases_contaminantes:
        return 'Gases Contaminantes'
    elif variable in material_particulado:
        return 'Material Particulado'
    elif variable in meteorological_variables_list:
        return 'Variables Meteorológicas'
    return 'Otros'

# --- Título y Descripción ---
st.title('📊 Dashboard de Calidad del Aire en el Valle del Aburrá')
st.markdown('Explora los datos de calidad del aire y parámetros meteorológicos en el Valle del Aburrá. Utiliza los filtros para personalizar tu análisis.')

# --- Columnas auxiliares ---
df_aire['Broad_Tipo_Variable'] = df_aire['Variable'].apply(
    lambda x: 'Variables Meteorológicas' if x in meteorological_variables_list else 'Contaminantes'
)
df_aire['Grupo Variable'] = df_aire['Variable'].apply(get_variable_type)

# --- Sidebar para Filtros ---
st.sidebar.header('⚙️ Opciones de Filtro')

anio_options = ['Todas'] + sorted(df_aire['Año'].unique().tolist())
anio_seleccionado = st.sidebar.selectbox('Selecciona el Año', options=anio_options, index=0)

broad_tipo_variable_options = ['Todas'] + sorted(df_aire['Broad_Tipo_Variable'].unique().tolist())
broad_tipo_variable_seleccionada = st.sidebar.selectbox('Selecciona el Tipo de Variable', options=broad_tipo_variable_options, index=0)

variable_options = ['Todas'] + sorted(df_aire['Variable'].unique().tolist())
variable_seleccionada = st.sidebar.selectbox('Selecciona la Variable', options=variable_options, index=0)

municipio_options = ['Todas'] + sorted(df_aire['Nombre del Municipio'].unique().tolist())
municipio_seleccionado = st.sidebar.selectbox('Selecciona el Municipio', options=municipio_options, index=0)

grupo_variable_options = sorted(df_aire['Grupo Variable'].unique().tolist())
grupo_variable_seleccionado = st.sidebar.multiselect(
    'Selecciona el Grupo de Variable',
    options=grupo_variable_options,
    default=grupo_variable_options
)

autoridad_seleccionada = st.sidebar.multiselect(
    'Selecciona la Autoridad Ambiental',
    options=sorted(df_aire['Autoridad Ambiental'].unique()),
    default=sorted(df_aire['Autoridad Ambiental'].unique())
)

tipo_estacion_seleccionada = st.sidebar.multiselect(
    'Selecciona el Tipo de Estación',
    options=sorted(df_aire['Tipo de Estación'].unique()),
    default=sorted(df_aire['Tipo de Estación'].unique())
)

# --- Aplicar filtros ---
df_filtered = df_aire.copy()

if anio_seleccionado != 'Todas':
    df_filtered = df_filtered[df_filtered['Año'] == anio_seleccionado]

# DataFrame separado para la matriz de correlación
df_for_correlation_matrix = df_aire.copy()
if anio_seleccionado != 'Todas':
    df_for_correlation_matrix = df_for_correlation_matrix[df_for_correlation_matrix['Año'] == anio_seleccionado]
if municipio_seleccionado != 'Todas':
    df_for_correlation_matrix = df_for_correlation_matrix[df_for_correlation_matrix['Nombre del Municipio'] == municipio_seleccionado]
df_for_correlation_matrix = df_for_correlation_matrix[
    (df_for_correlation_matrix['Autoridad Ambiental'].isin(autoridad_seleccionada)) &
    (df_for_correlation_matrix['Tipo de Estación'].isin(tipo_estacion_seleccionada)) &
    (df_for_correlation_matrix['Grupo Variable'].isin(grupo_variable_seleccionado))
]

if broad_tipo_variable_seleccionada != 'Todas':
    df_filtered = df_filtered[df_filtered['Broad_Tipo_Variable'] == broad_tipo_variable_seleccionada]
if variable_seleccionada != 'Todas':
    df_filtered = df_filtered[df_filtered['Variable'] == variable_seleccionada]
if municipio_seleccionado != 'Todas':
    df_filtered = df_filtered[df_filtered['Nombre del Municipio'] == municipio_seleccionado]

df_filtered = df_filtered[
    (df_filtered['Autoridad Ambiental'].isin(autoridad_seleccionada)) &
    (df_filtered['Tipo de Estación'].isin(tipo_estacion_seleccionada)) &
    (df_filtered['Grupo Variable'].isin(grupo_variable_seleccionado))
]

if df_filtered.empty:
    st.warning('⚠️ No hay datos que coincidan con los filtros seleccionados. Por favor, ajusta tus filtros.')
    st.stop()

# --- KPIs ---
st.subheader('📈 Indicadores Clave de Rendimiento (KPIs)')
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label='Concentración Promedio 📊', value=f'{df_filtered["Promedio"].mean():.2f}')
with col2:
    st.metric(label='Pico Máximo Registrado ⬆️', value=f'{df_filtered["Promedio"].max():.2f}')
with col3:
    st.metric(label='Total Días de Excedencias 🚫', value=f'{df_filtered["Días de excedencias"].sum():,}')
with col4:
    st.metric(label='Número de Registros 📝', value=f'{len(df_filtered):,}')

st.markdown('---')

# --- Gráficos con Tabs ---
st.subheader('📊 Visualizaciones de Datos')
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Histórico y Tendencias",
    "Comportamiento de Datos",
    "Mapas y Límites Legales",
    "Análisis Geográfico",
    "Tablas de Resumen"
])

with tab1:
    st.markdown('### Evolución Temporal del Promedio por Variable')
    fig1_line = px.line(
        df_filtered.groupby(['Año', 'Variable'])['Promedio'].mean().reset_index(),
        x='Año', y='Promedio', color='Variable',
        title='Promedio de Valor por Año y Variable',
        markers=True, template='plotly_dark'
    )
    st.plotly_chart(fig1_line, use_container_width=True)

    st.markdown('### Días de Excedencias por Año')
    excedencias_anual = df_filtered.groupby('Año')['Días de excedencias'].sum().reset_index()
    fig6 = px.line(
        excedencias_anual, x='Año', y='Días de excedencias',
        title='Total de Días de Excedencias por Año',
        markers=True, template='plotly_dark'
    )
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown('### Tendencia Anual Promedio por Variable (Area Chart)')
    area_data = df_filtered.groupby(['Año', 'Variable'])['Promedio'].mean().reset_index()
    fig_area = px.area(
        area_data, x='Año', y='Promedio', color='Variable',
        title='Promedio Anual por Variable (Tendencia)',
        line_group='Variable', template='plotly_dark'
    )
    st.plotly_chart(fig_area, use_container_width=True)

with tab2:
    st.markdown('### Promedio de Valor por Municipio')
    fig2 = px.bar(
        df_filtered.groupby('Nombre del Municipio')['Promedio'].mean().reset_index().sort_values(by='Promedio', ascending=False),
        x='Nombre del Municipio', y='Promedio', color='Nombre del Municipio',
        title='Promedio de Valor por Municipio',
        labels={'Promedio': 'Promedio del Valor'}, template='plotly_dark'
    )
    fig2.update_traces(width=0.8)
    fig2.update_layout(bargap=0.3, title_font_size=16,
                       xaxis_title="Municipio", yaxis_title="Valor Promedio de Contaminación", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('### Percentil 98 por Variable')
    percentil_98_data = df_filtered.groupby('Variable')['Percentil 98'].mean().reset_index().sort_values(by='Percentil 98', ascending=False)
    fig_percentil_98 = px.bar(
        percentil_98_data, x='Variable', y='Percentil 98', color='Variable',
        title='Percentil 98 por Variable',
        labels={'Percentil 98': 'Valor del Percentil 98'}, template='plotly_dark'
    )
    fig_percentil_98.update_traces(width=0.9)
    fig_percentil_98.update_layout(bargap=0.3, title_font_size=16,
                                   xaxis_title="Variables Medidas", yaxis_title="Promedio del Percentil 98")
    st.plotly_chart(fig_percentil_98, use_container_width=True)

    st.markdown('### Dispersión: Promedio vs. Representatividad Temporal por Variable')
    if not df_filtered.empty:
        fig_scatter = px.scatter(
            df_filtered, x='Representatividad Temporal', y='Promedio', color='Variable',
            hover_name='Variable',
            title='Relación entre el Promedio y la Representatividad Temporal por Variable',
            labels={'Representatividad Temporal': 'Representatividad Temporal (%)', 'Promedio': 'Valor Promedio'},
            template='plotly_dark'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No hay datos suficientes para generar el gráfico de dispersión.")

    st.markdown('### Histograma de la Variable Promedio con Media y Mediana')
    if not df_filtered.empty:
        media = df_filtered["Promedio"].mean()
        mediana = df_filtered["Promedio"].median()
        fig_hist = px.histogram(
            df_filtered, x="Promedio", nbins=40,
            title="Distribución de la Variable Promedio",
            labels={'Promedio': 'Valor del Promedio', 'count': 'Frecuencia'},
            template='plotly_dark'
        )
        fig_hist.update_traces(marker_color='#00FA9A', marker_line_color='white', marker_line_width=0.5)
        fig_hist.add_vline(x=media, line_dash="dash", line_color="red", line_width=2.5,
                           annotation_text=f"Media: {media:.2f}", annotation_position="top right",
                           annotation_font_color="red")
        fig_hist.add_vline(x=mediana, line_dash="dashdot", line_color="orange", line_width=2.5,
                           annotation_text=f"Mediana: {mediana:.2f}", annotation_position="top left",
                           annotation_font_color="orange")
        fig_hist.update_layout(bargap=0.15, title_font_size=16,
                               xaxis_title="Valor del Promedio", yaxis_title="Frecuencia", showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No hay datos suficientes para generar el histograma.")

with tab3:
    st.markdown('### Ubicación de las Estaciones de Monitoreo')
    if 'Latitud' in df_filtered.columns and 'Longitud' in df_filtered.columns:
        df_filtered['Tipo de Variable'] = df_filtered['Variable'].apply(get_variable_type)
        map_data = df_filtered[['Estación', 'Latitud', 'Longitud', 'Variable', 'Promedio', 'Tipo de Estación', 'Tipo de Variable']].drop_duplicates(subset=['Estación', 'Latitud', 'Longitud'])
        if not map_data.empty:
            st.map(map_data.rename(columns={'Latitud': 'lat', 'Longitud': 'lon'}))
        else:
            st.warning('No hay datos de ubicación para las estaciones seleccionadas.')
    else:
        st.warning('Las columnas de latitud y longitud no están disponibles en el dataset.')

    st.markdown('### Concentración Promedio por Variable con Límites de Contaminación')
    df_filtered['Tipo de Variable'] = df_filtered['Variable'].apply(get_variable_type)
    df_pollutants_for_limits = df_filtered[df_filtered['Tipo de Variable'].isin(['Gases Contaminantes', 'Material Particulado'])]
    avg_concentration = df_pollutants_for_limits.groupby(['Variable', 'Unidades'])['Promedio'].mean().reset_index()

    fig5 = px.bar(
        avg_concentration, x='Variable', y='Promedio', color='Promedio',
        color_continuous_scale=px.colors.sequential.Plasma,
        title='Promedio de Concentración por Variable Contaminante con Límites de Referencia',
        template='plotly_dark'
    )
    fig5.update_traces(width=0.6)
    for variable, limit in pollution_limits.items():
        if variable in avg_concentration['Variable'].values:
            unit = avg_concentration[avg_concentration['Variable'] == variable]['Unidades'].iloc[0]
            if unit in ['ugm3', 'ug/m3']:
                fig5.add_hline(y=limit, annotation_text=f'Límite {variable}: {limit} {unit}',
                               annotation_position='top right', line_dash='dot',
                               line_color='red', line_width=1.5)
    fig5.update_layout(bargap=0.3, title_font_size=16,
                       xaxis_title="Variable Contaminante", yaxis_title="Concentración Promedio",
                       coloraxis_colorbar=dict(title="Promedio"))
    st.plotly_chart(fig5, use_container_width=True)

with tab4:
    st.markdown('### Mapa de Calor de Correlación entre Variables Meteorológicas y Contaminantes')
    all_variables_in_data_for_corr = df_for_correlation_matrix['Variable'].unique().tolist()
    actual_meteorological_vars_for_corr = [v for v in meteorological_variables_list if v in all_variables_in_data_for_corr]
    actual_contaminant_vars_for_corr = [v for v in all_defined_contaminants if v in all_variables_in_data_for_corr]
    correlation_columns_for_heatmap = actual_meteorological_vars_for_corr + actual_contaminant_vars_for_corr

    if len(correlation_columns_for_heatmap) > 1:
        df_for_corr_pivot = df_for_correlation_matrix[
            df_for_correlation_matrix['Variable'].isin(correlation_columns_for_heatmap)
        ].groupby(['Año', 'Variable'])['Promedio'].mean().reset_index()
        df_corr_matrix_data = df_for_corr_pivot.pivot_table(index='Año', columns='Variable', values='Promedio')

        if not df_corr_matrix_data.empty and len(df_corr_matrix_data.columns) > 1:
            corr_matrix = df_corr_matrix_data.corr()
            fig_heatmap = px.imshow(
                corr_matrix, text_auto=True, aspect="auto",
                title='Correlación entre Variables (Meteorológicas y Contaminantes)',
                color_continuous_scale='RdBu_r', labels=dict(color="Coef. Correlación"),
                width=900, height=800, template='plotly_dark'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("No hay suficientes datos para calcular la correlación con los filtros actuales.")
    else:
        st.info("No hay suficientes variables para generar el mapa de calor de correlación.")

    st.markdown('### Distribución de Contaminación por Municipio')
    if not df_filtered.empty:
        stats_municipio = df_filtered.groupby('Nombre del Municipio')['Promedio'].agg(['mean', 'std']).dropna().reset_index()
        stats_municipio = stats_municipio.sort_values(by='mean', ascending=False).head(10)
        if not stats_municipio.empty:
            fig_error_bar = px.bar(
                stats_municipio, x='Nombre del Municipio', y='mean', error_y='std',
                title='Promedio de Contaminación por Municipio con su Desviación Estándar',
                labels={'mean': 'Valor de Contaminación', 'Nombre del Municipio': 'Municipio'},
                template='plotly_dark'
            )
            fig_error_bar.update_traces(
                marker_color='seagreen', width=0.4,
                error_y=dict(thickness=2, color='white', width=6)
            )
            fig_error_bar.update_layout(bargap=0.3, title_font_size=16,
                                        xaxis_title="Municipio", yaxis_title="Promedio de Contaminación",
                                        showlegend=False)
            st.plotly_chart(fig_error_bar, use_container_width=True)
        else:
            st.info("No hay datos suficientes para generar el gráfico de barras por municipio.")
    else:
        st.info("No hay datos suficientes para generar el gráfico de barras por municipio.")

with tab5:
    st.markdown('### Top 5 Contaminantes del Aire más Representativos (Promedio)')
    all_contaminant_variables_for_top5 = gases_contaminantes + material_particulado
    df_pollutants_top5 = df_filtered[df_filtered['Variable'].isin(all_contaminant_variables_for_top5)]
    if not df_pollutants_top5.empty:
        top_5_pollutants = df_pollutants_top5.groupby('Variable')['Promedio'].mean().sort_values(ascending=False).head(5)
        st.dataframe(top_5_pollutants.reset_index().rename(columns={'Promedio': 'Promedio Anual'}))
    else:
        st.info("No hay datos de variables contaminantes para calcular el Top 5.")

    st.markdown('### Comparación Anual de Contaminantes con Límites de Referencia')
    df_contaminants_annual = df_filtered[df_filtered['Variable'].isin(all_defined_contaminants)]
    if not df_contaminants_annual.empty:
        df_comparison_annual = df_contaminants_annual.groupby(['Año', 'Variable'])['Promedio'].mean().reset_index()
        df_comparison_annual['Límite Sugerido'] = df_comparison_annual['Variable'].map(pollution_limits)
        variable_units_map = df_aire[['Variable', 'Unidades']].drop_duplicates().set_index('Variable')['Unidades'].to_dict()
        df_comparison_annual['Unidades'] = df_comparison_annual['Variable'].map(variable_units_map)
        st.dataframe(
            df_comparison_annual[['Año', 'Variable', 'Promedio', 'Límite Sugerido', 'Unidades']]
            .dropna(subset=['Límite Sugerido'])
            .sort_values(by=['Año', 'Variable'])
        )
    else:
        st.info("No hay datos de variables contaminantes para generar la tabla de comparación anual.")

    st.markdown('### Máximo Valor Registrado por Variable')
    max_value_per_variable = df_filtered.groupby('Variable')['Máximo'].max().reset_index().sort_values(by='Máximo', ascending=False)
    fig_max_var = px.bar(
        max_value_per_variable, x='Variable', y='Máximo', color='Variable',
        title='Máximo Valor Registrado por Variable',
        labels={'Máximo': 'Valor Máximo'}, template='plotly_dark'
    )
    fig_max_var.update_traces(width=0.6)
    fig_max_var.update_layout(bargap=0.3, title_font_size=16,
                              xaxis_title="Variables", yaxis_title="Valor Máximo Registrado", showlegend=False)
    st.plotly_chart(fig_max_var, use_container_width=True)

    st.markdown('---')
    with st.expander("Ver Datos Filtrados"):
        st.dataframe(df_filtered)
