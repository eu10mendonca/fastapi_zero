# #Exemplo de uso do SQLAlchemy 2.0 com mapeamento baseado em dataclasss e tipagem - ORM

# from datetime import datetime

# from sqlalchemy import DateTime, String, create_engine, func
# from sqlalchemy.orm import Mapped, Session, mapped_column, registry

# engine = create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
# )


# reg = registry()


# @reg.mapped_as_dataclass
# class Comment:
#     __tablename__ = "comments"

#     id: Mapped[int] = mapped_column(init=False, primary_key=True)
#     name: Mapped[str] = mapped_column(String, nullable=False)
#     comment: Mapped[str] = mapped_column(String, nullable=False)
#     live: Mapped[str] = mapped_column(String, nullable=False)
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True), init=False, server_default=func.now()
#     )


# reg.metadata.create_all(engine)  # Criar as tabelas no banco de dados


# c = Comment(
#     name="Eudes Mendonça", comment="Ótimo vídeo!", live="FastAPI com SQLAlchemy"
# )

# with Session(engine) as session:
#     session.add(c)
#     session.commit()
#     session.refresh(c)  # Atualiza o objeto com os dados do banco, incluindo o ID gerado
#     print(c)


####################----------------------------#################################################

# Exemplo de uso do SQLAlchemy 2.0 com mapeamento baseado em DeclarativeBase e tipagem - ORM

# from datetime import datetime

# from sqlalchemy import DateTime, Integer, String, create_engine, func
# from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# engine = create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
# )


# class Base(DeclarativeBase): ...


# class Comment(Base):
#     __tablename__ = "comments"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String, nullable=False)
#     comment: Mapped[str] = mapped_column(String, nullable=False)
#     live: Mapped[str] = mapped_column(String, nullable=False)
#     created_at: Mapped[DateTime] = mapped_column(
#         DateTime(timezone=True), nullable=False, server_default=func.now()
#     )


# Base.metadata.create_all(engine)  # Criar as tabelas no banco de dados


# c = Comment(
#     name="Eudes Mendonça", comment="Ótimo vídeo!", live="FastAPI com SQLAlchemy"
# )

# with Session(engine) as session:
#     session.add(c)
#     session.commit()
#     session.refresh(c)  # Atualiza o objeto com os dados do banco, incluindo o ID gerado
#     print(c)

####################----------------------------#################################################


## Exemplo de uso do SQLAlchemy 2.0 com mapeamento baseado em DeclarativeBase - Modelo antigo

# from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
# from sqlalchemy.orm import DeclarativeBase, Session


# class Base(DeclarativeBase): ...


# class Comment(Base):
#     __tablename__ = "comments"

#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#     comment = Column(String, nullable=False)
#     live = Column(String, nullable=False)
#     created_at = Column(
#         DateTime(timezone=True), nullable=False, server_default=func.now()
#     )


# engine = create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
# )

# Base.metadata.create_all(engine)  # Criar as tabelas no banco de dados

# c = Comment(
#     name="Eudes Mendonça", comment="Ótimo vídeo!", live="FastAPI com SQLAlchemy"
# )

# with Session(engine) as session:
#     session.add(c)
#     session.commit()
#     session.refresh(c)  # Atualiza o objeto com os dados do banco, incluindo o ID gerado
#     print(c)

####################----------------------------#################################################


# Exemplo utilizando DeclarativeBase e Scalar

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

engine = create_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
)


class Base(DeclarativeBase): ...


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[str] = mapped_column(String, nullable=False)
    live: Mapped[str] = mapped_column(String, nullable=False)
    senha: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"Comment(id={self.id}, name='{self.name}', comment='{self.comment}', live='{self.live}', senha='{self.senha}', created_at='{self.created_at}')"


# Base.metadata.create_all(engine)  # Criar as tabelas no banco de dados


c = Comment(
    name="Eudes Mendonça",
    comment="Ótimo vídeo!",
    live="FastAPI com SQLAlchemy",
    senha="123456",
)

# with Session(engine) as session:
#     session.add(c)
#     session.commit()
#     session.refresh(c)  # Atualiza o objeto com os dados do banco, incluindo o ID gerado
#     print(c)

with Session(engine) as session:
    comment = session.execute(select(Comment).where(Comment.id == 2)).scalar_one()
    print(comment)
    # session.delete(comment)
    # session.commit()

##Exemplo pegando vários com fetchmany

with Session(engine) as session:
    result = session.execute(select(Comment)).scalars()
    print(result.fetchmany(3))

## Exemplo já transformando em lista utilzando o scalars.all()

with Session(engine) as session:
    result = session.execute(select(Comment)).scalars().all()
    # for comment in result:
    #     if comment.id == 2:
    #         comment.comment = "Comentário atualizado"
    #         session.commit()

    for comment in result:
        print(comment)
