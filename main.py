import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Catálogo de Séries")
DB_NAME = "series.db"


class Serie(BaseModel):
    titulo: str
    genero: str
    ano_lancamento: int
    temporadas: int


def cria_conexao():
    conexao = sqlite3.connect(DB_NAME)
    conexao.row_factory = sqlite3.Row
    return conexao


def cria_tabela():
    with cria_conexao() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                genero TEXT NOT NULL,
                ano_lancamento INTEGER NOT NULL,
                temporadas INTEGER NOT NULL
            )
            """
        )


@app.on_event("startup")
def startup():
    cria_tabela()


@app.get("/")
def home():
    return {"mensagem": "Catálogo de Séries em construção"}


@app.post("/series")
def cadastrar_serie(serie: Serie):
    if serie.ano_lancamento <= 1900:
        raise HTTPException(status_code=400, detail="O ano de lançamento deve ser maior que 1900.")
    if serie.temporadas <= 0:
        raise HTTPException(status_code=400, detail="O número de temporadas deve ser positivo.")

    with cria_conexao() as conexao:
        cursor = conexao.execute(
            "INSERT INTO series (titulo, genero, ano_lancamento, temporadas) VALUES (?, ?, ?, ?)",
            (serie.titulo.strip(), serie.genero.strip(), serie.ano_lancamento, serie.temporadas),
        )
        serie_id = cursor.lastrowid

    return {
        "id": serie_id,
        "titulo": serie.titulo.strip(),
        "genero": serie.genero.strip(),
        "ano_lancamento": serie.ano_lancamento,
        "temporadas": serie.temporadas,
    }


@app.get("/series")
def listar_series():
    with cria_conexao() as conexao:
        cursor = conexao.execute(
            "SELECT id, titulo, genero, ano_lancamento, temporadas FROM series ORDER BY titulo"
        )
        series = [dict(linha) for linha in cursor.fetchall()]

    return series


@app.get("/series/{titulo}")
def buscar_serie(titulo: str):
    with cria_conexao() as conexao:
        cursor = conexao.execute(
            "SELECT id, titulo, genero, ano_lancamento, temporadas FROM series WHERE lower(titulo) = lower(?)",
            (titulo,),
        )
        serie = cursor.fetchone()

    if serie is None:
        raise HTTPException(status_code=404, detail="Série não encontrada.")

    return dict(serie)
