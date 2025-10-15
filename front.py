import streamlit as st
import pandas as pd
import calendar
import altair as alt
from processamento import txt_para_csv, load_conversas_data, movimento_mensal, contar_mensagens,contar_mensagens_por_hora, usuarios_mais_engajados,meses_disponiveis, contar_emojis_por_mes

st.set_page_config(page_title="Monitoramento WhatsApp", layout="wide")


st.markdown("""
<style>
    body {
        background-color: #f5f5f7;
    }

    .main {
        background-color: #f5f5f7;
        padding: 2rem;
    }

    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #ffffff;
        padding: 15px 25px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .header-title {
        font-size: 22px;
        font-weight: 600;
        color: #444;
    }

    .month-select {
        background-color: #e91e63;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 15px;
        font-weight: 500;
    }

    .card {
        padding: 18px;
        border-radius: 15px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
        background-color: #fff;
        text-align: center;
    }

    .card h3 {
        margin-bottom: 6px;
        font-size: 15px;
        color: #666;
    }

    .card p {
        margin: 0;
        font-size: 20px;
        font-weight: 700;
        color: #333;
    }

    .emoji-card {
        
        border-radius: 15px;
        padding: 18px;
        color: #fff;
        text-align: center;
        font-weight: 600;
        background-color: #fff;
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.08);
        border: 1px solid #e0e0e0;

    }

    .emoji-card span {
        font-size: 28px;
        display: block;
    }

            
    .botao-data {
    background-color: #e91e63;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 15px;
    font-weight: 500;
    cursor: pointer;
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    }
</style>
""", unsafe_allow_html=True)

# ------------------- Cabeçalho -------------------
st.markdown("""
<div class="header-container">
    <div class="header-title">📊 Monitoramento de Conversa do WhatsApp</div>
    
</div>
""", unsafe_allow_html=True)

# ------------------- Upload -------------------
uploaded_file = st.file_uploader("Analise os engajamentos, conteúdos, mais comentados e muito mais", type=["txt"])
if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8")
    txt_para_csv(text)
    df = load_conversas_data()

    meses = meses_disponiveis()

    st.markdown("""
        <style>
        /* Remove o label */
        div[data-testid="stSelectbox"] label {display: none;}

        /* Deixa toda a caixa do select rosa */
        div[data-testid="stSelectbox"] {
            background-color: #f50057 !important;  /* Rosa principal */
            border-radius: 10px !important;
            padding: 0 !important;
            height: 40px !important;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }

        /* Remove o fundo cinza interno */
        div[data-testid="stSelectbox"] > div {
            background-color: transparent !important;
            border: none !important;
        }

        /* Força o fundo rosa em todas as camadas internas */
        div[data-baseweb="select"] {
            background-color: #f50057 !important;
            color: white !important;
            border-radius: 10px !important;
            min-height: 40px !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* Remove o fundo branco dentro do valor selecionado */
        div[data-baseweb="select"] > div {
            background-color: transparent !important;
        }

        /* Texto branco */
        div[data-testid="stSelectbox"] span {
            color: white !important;
            font-weight: 600 !important;
            font-size: 14px !important;
        }

        /* Ícone do calendário e seta */
        div[data-testid="stSelectbox"] svg {
            color: white !important;
            fill: white !important;
        }

        /* Dropdown (menu aberto) também rosa */
        div[data-baseweb="popover"] {
            background-color: #f50057 !important;
            border-radius: 10px !important;
        }

        /* Itens dentro do menu */
        div[data-baseweb="option"] {
            background-color: #f50057 !important;
            color: white !important;
        }

        /* Hover dos itens */
        div[data-baseweb="option"]:hover {
            background-color: #c51162 !important;
        }

        /* Hover da caixa principal */
        div[data-testid="stSelectbox"]:hover {
            background-color: #c51162 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("<h3 style='margin: 0;'>📋 DADOS DA CONVERSA</h3>", unsafe_allow_html=True)

    with col2:
        if meses:
            opcoes = [m["label"] for m in meses]
            mes_selecionado = st.selectbox("", opcoes, key="mes", index=len(opcoes)-1)
        else:
            st.warning("Nenhum mês encontrado.")
    
    # Filtra o DataFrame pelo mês/ano selecionados
    try:
        idx_mes = opcoes.index(mes_selecionado) if meses else None
        mes_num = int(meses[idx_mes]["valor"]) if meses else None
        ano_selecionado = int(mes_selecionado.strip().split()[-1]) if meses else None
    except Exception:
        mes_num = None
        ano_selecionado = None

    df_tratado = df.copy()
    df_tratado['Data'] = pd.to_datetime(df_tratado['Data'], format="%d/%m/%Y", errors='coerce')
    df_tratado = df_tratado.dropna(subset=['Data'])

    if mes_num is not None and ano_selecionado is not None:
        df_filtrado = df_tratado[(df_tratado['Data'].dt.month == mes_num) & (df_tratado['Data'].dt.year == ano_selecionado)]
    else:
        df_filtrado = df_tratado

    # Cards
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card" style="margin-bottom: 12px;"><h3>Tipo de Conversa</h3><p>Grupo</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card" style="margin-bottom: 12px;"><h3>Nome</h3><p>Comunidade Acadêmica - Manaus</p></div>', unsafe_allow_html=True)

    # ------------------- Quantidade de mensagens -------------------
    col1, col2 = st.columns([1, 2])

    quantidade_mensagens = len(df_filtrado)
    engajados = df_filtrado['Usuario'].value_counts().head(3) if not df_filtrado.empty else pd.Series(dtype=int)

    medalhas = ['🥇', '🥈', '🥉']
    linhas_tabela = ""

    for i, (usuario, _) in enumerate(engajados.items()):
        posicao = f"{i+1:02d}"
        medalha = medalhas[i] if i < len(medalhas) else ''
        linhas_tabela += f"""
    <tr style="border-bottom: 1px solid #e6e6e6;">
    <td style="padding: 6px 0; width: 20px;">{posicao}</td>
    <td style="padding: 6px 0;">{medalha} {usuario}</td>
    </tr>
    """

    with col1:
        st.markdown(f"""
    <div class="card" style="height: 120px; display: flex; flex-direction: column; justify-content: center;">
    <h3>💬 Quantidade de Mensagens</h3>
    <p style="font-size: 22px; font-weight: bold; margin: 0;">{quantidade_mensagens:,}</p>
    </div>
    """, unsafe_allow_html=True)

        st.markdown(f"""
    <div class="card" style="
    margin-top:15px;
    height: 220px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    ">
    <h3>👥 Maiores interações</h3>
    <table style="width:100%; border-collapse: collapse; margin-top:10px;">
    {linhas_tabela}
    </table>
    </div>
    """, unsafe_allow_html=True)



    # ------------------- Emojis frequentes -------------------
    with col2:
        # Descobre mês/ano selecionados a partir do label atual
        if meses:
            try:
                idx_mes = opcoes.index(mes_selecionado)
                mes_num = int(meses[idx_mes]["valor"])  # 01..12
                ano_sel = int(mes_selecionado.strip().split()[-1])
            except Exception:
                mes_num, ano_sel = None, None
        else:
            mes_num, ano_sel = None, None

        top_emj = contar_emojis_por_mes(mes=mes_num, ano=ano_sel, top_n=4)

        fundos = ["#ffb300", "#e91e63", "#607d8b", "#f9a825"]

        # Monta grid de 2 colunas sem usar tabela, com cards maiores para ocupar o espaço
        itens_html = "".join([
            (
                f'<div style="background-color:{fundos[i % len(fundos)]};'
                ' display:flex; align-items:center; justify-content:center; gap:10px;'
                ' padding:14px 16px; border-radius:14px; font-weight:700; font-size:16px; line-height:1; color:#fff; height:100%;">'
                f'<span style="font-size:28px; display:block;">{emoji}</span>{qtd}</div>'
            )
            for i, (emoji, qtd) in enumerate(top_emj)
        ])

        st.markdown(f"""
    <div class="card" style="
        margin-top:0;
        height: 355px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;">
        <h3 style="margin: 0 0 8px 0; font-size: 15px;"> Emojis frequentes</h3>
        <div style="display:grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 12px; flex:1;">
            {itens_html}
        </div>
    </div>
        """, unsafe_allow_html=True)
    
        # ------------------- Engajamento diário -------------------
    st.subheader(" Mensagens diárias")

    # Mensagens diárias apenas do mês selecionado, preenchendo dias sem mensagens
    if df_filtrado.empty:
        dados = pd.DataFrame(columns=["Data", "Mensagens", "DataFormatada"])
    else:
        primeiro_dia = df_filtrado['Data'].min()
        ano_mes = (primeiro_dia.year, primeiro_dia.month)
        num_dias = calendar.monthrange(ano_mes[0], ano_mes[1])[1]
        inicio_mes = pd.Timestamp(year=ano_mes[0], month=ano_mes[1], day=1)
        todas_as_datas = pd.date_range(start=inicio_mes, periods=num_dias, freq='D')

        contagem = df_filtrado.groupby('Data').size()
        contagem = contagem.reindex(todas_as_datas, fill_value=0)
        dados = contagem.reset_index()
        dados.columns = ["Data", "Mensagens"]
        dados['DataFormatada'] = dados['Data'].dt.strftime("%d/%m")

        chart = alt.Chart(dados).mark_bar(
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4
        ).encode(
            x=alt.X("DataFormatada:N", title="Dia", sort=dados['DataFormatada'].tolist()),
            y=alt.Y("Mensagens:Q", title="Quantidade de mensagens"),
            tooltip=[
                alt.Tooltip("Data:T", title="Data completa"),
                alt.Tooltip("Mensagens:Q", title="Mensagens")
            ]
        ).properties(height=300)

        st.altair_chart(chart, use_container_width=True)
    if df_filtrado.empty:
        st.warning("Nenhum dado disponível para exibir o engajamento diário.")

    # ------------------- Gráfico de Conteúdo Diário -------------------
    import streamlit as st
    import altair as alt
    import pandas as pd
    import numpy as np

# ------------------- Dados do gráfico de conteúdo -------------------
    dias = list(range(1, 32))
    categorias = ['Carro', 'Esporte', 'Política', 'Educação', 'Compras', 'Economia', 'Internacional', 'Outros']

    np.random.seed(42)
    conteudo_data = {
        'Dia': np.repeat(dias, len(categorias)),
        'Categoria': categorias * len(dias),
        'Porcentagem': np.random.dirichlet(np.ones(len(categorias)), len(dias)).flatten() * 100
    }

    df_conteudo = pd.DataFrame(conteudo_data)

    # ------------------- CSS para o card -------------------
    st.markdown("""
        <style>
        .conteudo-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
            background-color: #fff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        .conteudo-card h3 {
            font-weight: 600;
            font-size: 22px;
            margin-bottom: 5px;
        }
        .conteudo-card p {
            font-size: 14px;
            color: #666;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ------------------- Novo layout: metade rosquinha + metade barras horizontais -------------------
    hdr_l, hdr_r = st.columns([3, 1])
    with hdr_l:
        st.markdown("###  Conteúdo Diário", unsafe_allow_html=True)
    with hdr_r:
        # Seleção de dia do mês atual (mesmo tamanho visual do seletor de mês)
        if mes_num is not None and ano_selecionado is not None:
            num_dias_conteudo = calendar.monthrange(ano_selecionado, mes_num)[1]
        else:
            num_dias_conteudo = 31
        opcoes_dia_labels = [f"{str(d).zfill(2)}" for d in range(1, num_dias_conteudo + 1)]
        st.markdown('<div style="max-width: 220px; margin-left:auto;">', unsafe_allow_html=True)
        dia_label = st.selectbox("", opcoes_dia_labels, index=0, key="conteudo_dia")
        st.markdown('</div>', unsafe_allow_html=True)
    dia_escolhido = int(dia_label)

    dados_dia = df_conteudo[df_conteudo['Dia'] == dia_escolhido]

    col_left, col_right = st.columns(2)

    with col_left:
        donut = alt.Chart(dados_dia).mark_arc(innerRadius=80, cornerRadius=6).encode(
            theta=alt.Theta('Porcentagem:Q'),
            color=alt.Color('Categoria:N', scale=alt.Scale(scheme='category10'), legend=alt.Legend(title="")),
            tooltip=['Categoria', alt.Tooltip('Porcentagem:Q', format='.1f')]
        ).properties(height=320)

        st.altair_chart(donut, use_container_width=True)

    with col_right:
        dados_dia = dados_dia.copy()
        dados_dia['CategoriaLabel'] = dados_dia['Categoria'] + '  ' + dados_dia['Porcentagem'].round(1).astype(str) + '%'
        barras = alt.Chart(dados_dia).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
            y=alt.Y('CategoriaLabel:N', sort='-x', title=''),
            x=alt.X('Porcentagem:Q', title='%'),
            color=alt.Color('Categoria:N', legend=None, scale=alt.Scale(scheme='category10')),
            tooltip=['Categoria', alt.Tooltip('Porcentagem:Q', format='.1f')]
        ).properties(height=320)

        st.altair_chart(barras, use_container_width=True)



    # ------------------- Gráfico de Engajamento por Hora -------------------
    import streamlit as st
    import pandas as pd
    import numpy as np
    import altair as alt

    # Prepara lista de dias disponíveis conforme mês selecionado

    
    st.markdown("""
        <style>
            .card-container {
                background-color: #fff;
                padding: 25px 30px 10px 30px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                margin-top: 30px;
                margin-bottom: 30px;
            }

            .header-engajamento {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .titulo-engajamento {
                font-size: 18px;
                font-weight: 600;
                color: #e91e63;
                margin: 0;
            }

            .botao-data {
                    background-color: #e91e63;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 15px;
                    font-weight: 500;
                    cursor: pointer;
                    appearance: none;
                    -webkit-appearance: none;
                    -moz-appearance: none;
            }

            .subtitulo {
                font-size: 16px;
                font-weight: 600;
                text-align: center;
                margin: 15px 0 10px 0;
                color: #333;
            }

            /* Selectbox do dia (apenas dentro do card) menor e mais arredondado */
            .card-container div[data-testid="stSelectbox"] {
                min-height: 32px !important;
                border-radius: 12px !important;
                padding: 0 !important;
            }
            .card-container div[data-baseweb="select"] {
                min-height: 32px !important;
                border-radius: 12px !important;
            }
            .card-container div[data-testid="stSelectbox"] span {
                font-size: 13px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # CONTAINER com tudo (card)
    with st.container():

        # Cabeçalho e seletor de dia (somente dias do mês selecionado)
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown("""
                <div class="header-engajamento">
                    <h3 class="titulo-engajamento"> Horários de Engajamento</h3>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            if not df_filtrado.empty:
                dias_disponiveis = sorted(df_filtrado['Data'].dt.date.unique())
                opcoes_dias = [f"📅 {d.strftime('%d/%m/%Y')}" for d in dias_disponiveis]
                mapa_label_para_data = {label: d for label, d in zip(opcoes_dias, dias_disponiveis)}
                st.markdown('<div style="max-width: 260px; margin-left:auto;">', unsafe_allow_html=True)
                dia_label_selecionado = st.selectbox("", opcoes_dias, key="dia", index=len(opcoes_dias)-1)
                st.markdown('</div>', unsafe_allow_html=True)
                dia_selecionado = mapa_label_para_data.get(dia_label_selecionado)
            else:
                dia_selecionado = None
                st.warning("Nenhum dia disponível neste mês.")

        st.markdown("<div class=\"subtitulo\">Quantidade de mensagens por hora</div>", unsafe_allow_html=True)

        # Monta dados por hora somente para o dia selecionado
        if dia_selecionado is not None:
            df_dia = df_filtrado[df_filtrado['Data'].dt.date == dia_selecionado]
            if not df_dia.empty:
                df_dia = df_dia.copy()
                df_dia['HoraNum'] = pd.to_datetime(df_dia['Hora'], format='%H:%M', errors='coerce').dt.hour
                contagem = df_dia['HoraNum'].value_counts().sort_index()
                todas_horas = pd.Series(index=range(24), data=0)
                todas_horas.update(contagem)

                df_horario = pd.DataFrame({
                    'Hora': [f"{h}h" for h in todas_horas.index],
                    'Mensagens': todas_horas.values
                })

                hora_mais_movimento = df_horario.loc[df_horario['Mensagens'].idxmax(), 'Hora']

                bar_chart = alt.Chart(df_horario).mark_bar(
                    cornerRadiusTopLeft=3,
                    cornerRadiusTopRight=3
                ).encode(
                    x=alt.X('Hora:N', title='', sort=None),
                    y=alt.Y('Mensagens:Q', title=''),
                    color=alt.condition(
                        alt.datum.Hora == hora_mais_movimento,
                        alt.value('#ff9800'),
                        alt.value('#3f51b5')
                    ),
                    tooltip=['Hora', 'Mensagens']
                ).properties(height=300)

                st.altair_chart(bar_chart, use_container_width=True)
            else:
                st.info("Não há mensagens neste dia.")
        else:
            st.info("Selecione um dia para ver os horários de engajamento.")
        # removido wrapper externo em branco
