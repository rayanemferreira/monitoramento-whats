import pandas as pd
import os
import streamlit as st
import datetime
from collections import Counter
import re
import requests
from io import BytesIO
import csv
import io
from datetime import datetime



CONVERSAS_CSV = "conversas.csv"

def txt_para_csv(text, output_path=CONVERSAS_CSV):
    """Converte um arquivo de texto de conversa WhatsApp em CSV"""
    lines = text.splitlines()

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Data', 'Hora', 'Usuario', 'Mensagem'])

        for line in lines:
            match = re.match(r"(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}) - (.*?): (.*)", line)
            if match:
                data = match.group(1)
                hora = match.group(2)
                usuario = match.group(3)
                mensagem = match.group(4)
                csv_writer.writerow([data, hora, usuario, mensagem])


def load_conversas_data() -> pd.DataFrame:
    """Carrega o CSV de conversas salvo em DataFrame"""
    if os.path.exists(CONVERSAS_CSV):
        data = pd.read_csv(CONVERSAS_CSV, delimiter=',')  
        print("Colunas do CSV:", data.columns)  
        data.columns = data.columns.str.strip().str.replace('"', '') 
        required_columns = ["Data", "Hora", "Usuario", "Mensagem"]
        if not all(col in data.columns for col in required_columns):
            raise ValueError(f"O arquivo CSV de conversas deve conter as colunas: {', '.join(required_columns)}.")
        return data
    else:
        return pd.DataFrame(columns=["Data", "Hora", "Usuario", "Mensagem"])
   
def meses_disponiveis():
    """Retorna lista de meses disponíveis nas conversas"""
    try:
        data = pd.read_csv("conversas.csv", encoding="utf-8", sep=",", quotechar='"')
    except Exception as e:
        print("❌ Erro ao ler CSV:", e)
        return []

    if "Data" not in data.columns:
        print("❌ Coluna 'Data' não encontrada. Colunas detectadas:", list(data.columns))
        return []

    data['Data'] = data['Data'].astype(str).str.strip().str.replace('"', '')
    data['Data'] = pd.to_datetime(data['Data'], format="%d/%m/%Y", errors='coerce')
    data = data.dropna(subset=['Data'])

    if data.empty:
        return []

    meses_unicos = sorted(data['Data'].dt.to_period('M').unique())
    meses = []
    nomes_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    for periodo in meses_unicos:
        ano = int(str(periodo).split('-')[0])
        mes_num = int(str(periodo).split('-')[1])
        nome_mes = nomes_pt.get(mes_num, str(periodo))
        meses.append({"valor": f"{mes_num:02}", "label": f"📅 {nome_mes} {ano}"})

    return meses


    
def movimento_mensal():
    try:
        data = load_conversas_data()

        if data.empty:
            raise Exception("Nenhuma conversa encontrada.")
        
        # Converter corretamente a coluna 'Data' (dia/mês/ano)
        data['Data'] = pd.to_datetime(data['Data'], format="%d/%m/%Y", errors='coerce')

        if data['Data'].isnull().any():
            raise Exception("Existem datas inválidas na base de dados.")
        
        # Contar mensagens por dia
        mensagens_por_data = data.groupby('Data').size().reset_index(name="Mensagens")

        if mensagens_por_data.empty:
            raise Exception("Não foi possível calcular as datas mais movimentadas.")
        
        # Ordenar por data (cronológico)
        mensagens_por_data = mensagens_por_data.sort_values("Data")

    except Exception as e:
        mensagens_por_data = pd.DataFrame(columns=["Data", "Mensagens"])

    return mensagens_por_data



 
def movimentação_hora(data_filtro):

    try:
        data = load_conversas_data()

        if data.empty:
            raise Exception("Nenhuma conversa encontrada.")
        
        # Converter a coluna 'Data' para datetime
        data['Data'] = pd.to_datetime(data['Data'], errors='coerce')

        if data['Data'].isnull().any():
            raise Exception("Existem datas inválidas na base de dados.")
        
        # Se o filtro de data foi passado, aplicar o filtro
        if data_filtro:
            data_filtro = pd.to_datetime(data_filtro, errors='coerce')
            if pd.isnull(data_filtro):
                raise Exception("Formato de data inválido para o filtro.")
            data = data[data['Data'].dt.date == data_filtro.date()]
        
        if data.empty:
            raise Exception("Nenhuma mensagem encontrada para a data filtrada.")

        # Criar nova coluna para hora
        data['Hora'] = pd.to_datetime(data['Hora'], errors='coerce').dt.hour

        # Agrupar por Hora
        mensagens_por_hora = data.groupby('Hora').size()

        if mensagens_por_hora.empty:
            raise Exception("Não foi possível calcular os horários mais movimentados.")

        # Reordenar por hora (crescente)
        mensagens_por_hora = mensagens_por_hora.sort_index()


        top_horas_dict = mensagens_por_hora.to_dict()

    except Exception as e:
        print("Erro:", e)
        top_horas_dict = {}

    return top_horas_dict




def extrair_emojis(texto):
    
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]")
    return emoji_pattern.findall(texto)

def top_emojis():
    try:
    
        data = load_conversas_data()

        if data.empty:
            raise Exception("Nenhuma conversa encontrada")
        
        
        emoji_counter = Counter()

        for mensagem in data['Mensagem']:
            emojis_na_mensagem = extrair_emojis(mensagem)
            emoji_counter.update(emojis_na_mensagem)

        if not emoji_counter:
            raise Exception("Nenhum emoji encontrado nas mensagens. ")

        
        top_5_emojis = emoji_counter.most_common(5)
        top_5_emojis_dict = {emoji: count for emoji, count in top_5_emojis}
        top_5_emojis_dict['Mensagem'] = '✨ Os 4 emojis mais usados:'

    except Exception as e:
        top_5_emojis_dict = {
            'Erro': str(e)  
        }

    return top_5_emojis_dict


def contar_emojis_por_mes(mes: int | None = None, ano: int | None = None, top_n: int = 4):
    """Conta emojis nas mensagens, opcionalmente filtrando por mês/ano, e retorna top_n.

    Retorno: lista de tuplas [(emoji, contagem), ...]
    """
    try:
        data = load_conversas_data()

        if data.empty:
            return []

        data['Data'] = pd.to_datetime(data['Data'], format="%d/%m/%Y", errors='coerce')
        data = data.dropna(subset=['Data'])

        if mes is not None and ano is not None:
            data = data[(data['Data'].dt.month == int(mes)) & (data['Data'].dt.year == int(ano))]

        if data.empty:
            return []

        emoji_counter = Counter()
        for mensagem in data['Mensagem'].dropna().astype(str):
            emoji_counter.update(extrair_emojis(mensagem))

        if not emoji_counter:
            return []

        if top_n is not None and top_n > 0:
            return emoji_counter.most_common(top_n)
        
        # Sem limite: retorna todos em ordem decrescente
        return sorted(emoji_counter.items(), key=lambda x: x[1], reverse=True)
    except Exception:
        return []

def contar_mensagens() -> int:
    """Conta quantas mensagens existem na conversa"""
    df = load_conversas_data()
    return len(df)


def contar_mensagens_por_hora():
    df = load_conversas_data()

    if df.empty:
        return pd.DataFrame(columns=["Hora", "Mensagens"])

    
    df['HoraNum'] = pd.to_datetime(df['Hora'], format='%H:%M', errors='coerce').dt.hour

    
    contagem = df['HoraNum'].value_counts().sort_index()

    
    todas_horas = pd.Series(index=range(24), data=0)
    todas_horas.update(contagem)


    df_horario = pd.DataFrame({
        'Hora': [f"{h}h" for h in todas_horas.index],
        'Mensagens': todas_horas.values
    })

    return df_horario


def usuarios_mais_engajados(top_n=3):
    """Mostra os usuários mais engajados com base no número de mensagens"""
    df = load_conversas_data()
    
    if df.empty:
        print("Nenhuma conversa encontrada.")
        return []
    
    engajamento = df['Usuario'].value_counts().head(top_n)
    
    print("Usuários mais engajados:")
    for i, (usuario, mensagens) in enumerate(engajamento.items(), 1):
        print(f"{i}. {usuario} - {mensagens} mensagens")
    
    return engajamento



    







