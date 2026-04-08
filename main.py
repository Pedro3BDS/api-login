from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel

app = FastAPI()

# ---------------- BANCO DE DADOS ----------------

DATABASE_URL = "sqlite:///./usuarios.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# ---------------- TABELA ----------------

class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True)
    senha = Column(String)

Base.metadata.create_all(bind=engine)

# ---------------- MODELOS ----------------

class Usuario(BaseModel):
    nome: str
    email: str
    senha: str

class Login(BaseModel):
    email: str
    senha: str

# ---------------- ROTAS ----------------

# Rota inicial
@app.get("/")
def home():
    return {"mensagem": "API funcionando!"}

# Criar usuário
@app.post("/usuarios")
def criar_usuario(usuario: Usuario):
    db = SessionLocal()

    # Verifica se email já existe
    if db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first():
        return {"erro": "Email já cadastrado"}

    novo_usuario = UsuarioDB(
        nome=usuario.nome,
        email=usuario.email,
        senha=usuario.senha
    )

    db.add(novo_usuario)
    db.commit()

    return {"mensagem": "Usuário criado com sucesso"}

# Listar usuários
@app.get("/usuarios")
def listar_usuarios():
    db = SessionLocal()
    usuarios = db.query(UsuarioDB).all()

    return [
        {"id": u.id, "nome": u.nome, "email": u.email}
        for u in usuarios
    ]

# Login
@app.post("/login")
def login(dados: Login):
    db = SessionLocal()

    user = db.query(UsuarioDB).filter(
        UsuarioDB.email == dados.email,
        UsuarioDB.senha == dados.senha
    ).first()

    if user:
        return {"mensagem": "Login realizado com sucesso"}

    return {"erro": "Email ou senha inválidos"}

# Atualizar usuário
@app.put("/usuarios/{id}")
def atualizar_usuario(id: int, usuario: Usuario):
    db = SessionLocal()
    user = db.query(UsuarioDB).filter(UsuarioDB.id == id).first()

    if user:
        user.nome = usuario.nome
        user.email = usuario.email
        user.senha = usuario.senha
        db.commit()
        return {"mensagem": "Usuário atualizado"}

    return {"erro": "Usuário não encontrado"}

# Deletar usuário
@app.delete("/usuarios/{id}")
def deletar_usuario(id: int):
    db = SessionLocal()
    user = db.query(UsuarioDB).filter(UsuarioDB.id == id).first()

    if user:
        db.delete(user)
        db.commit()
        return {"mensagem": "Usuário deletado"}

    return {"erro": "Usuário não encontrado"}