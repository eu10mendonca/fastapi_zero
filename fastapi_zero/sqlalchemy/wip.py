# Criando conexão síncrona simples
# from sqlalchemy import create_engine

# engine = create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
# )

# connection = engine.connect()
# connection.close()

#############====================================================##########################


# Criando conexão síncrona e executando um comando com sql
# from sqlalchemy import create_engine, text

# engine = create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
# )

# connection = engine.connect()
# sql = text("select * from comments")
# result = connection.execute(sql)
# connection.close()

#############====================================================##########################

# Transação com gerenciador de contexto (dessa forma o gerenciador de contexto garante
# que a conexão seja fechada mesmo que ocorra um erro)
# from sqlalchemy import create_engine, text

# engine = create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
# )

# with engine.connect() as connection:
#     sql = text("select * from comments")
#     result = connection.execute(sql)
#     print(result.fetchall())

#############====================================================##########################

# # Criando a conexão de forma assíncrona
# from sqlalchemy.ext.asyncio import create_async_engine
# from asyncio import run

# from sqlalchemy import text

# async_engine = create_async_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
# )

# async def main():
#     async with async_engine.connect() as async_connection:
#         sql = text("select * from comments")
#         result = await async_connection.execute(sql)
#         print(result.fetchall())

# run(main())

#############====================================================##########################

# Criando diversas transações de forma síncrona na mesma conexão
# from sqlalchemy import create_engine, text

# engine = create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
# )

# query = "select * from comments limit 10 offset {of}"

# with engine.connect() as connection:
#     with connection.begin():
#         sql = text(query.format(of=0))
#         result1 = connection.execute(sql)
#     with connection.begin():
#         sql = text(query.format(of=1))
#         result2 = connection.execute(sql)
#     with connection.begin():
#         sql = text(query.format(of=2))
#         result3 = connection.execute(sql)

#############====================================================##########################

# métodos importantes do result:

# fetchone() -> retorna a próxima linha do resultado ou None se não houver mais linhas
# fetchall() -> retorna todas as linhas do resultado como uma lista de tuplas
# fetchmany(size) -> retorna as próximas 'size' linhas do resultado como uma lista
# partitions(size) -> retorna um iterador que divide o resultado em partições de um tamanho específico
# first() -> retorna a primeira linha do resultado ou None se não houver mais linhas


# from sqlalchemy import create_engine, text

# engine = create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
# )

# query = "select * from comments limit 10 offset {of}"

# with engine.connect() as connection:
#     with connection.begin():
#         sql = text(query.format(of=0))
#         result1 = connection.execute(sql)
#     with connection.begin():
#         sql = text(query.format(of=1))
#         result2 = connection.execute(sql)
#     with connection.begin():
#         sql = text(query.format(of=2))
#         result3 = connection.execute(sql)
#         print(result3.fetchall())


#############====================================================##########################

# Utilizando Metadata e Table para criar tabelas e colunas de forma programática
# import sqlalchemy as sa

# engine = sa.create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=True
# )


# metadata = sa.MetaData()

# t = sa.Table(
#     "comments",
#     metadata,
#     sa.Column("id", sa.Integer(), nullable=False),
#     sa.Column("name", sa.String(), nullable=False),
#     sa.Column("comment", sa.String(), nullable=False),
#     sa.Column("live", sa.String(), nullable=False),
#     sa.Column("created_at", sa.DateTime(), nullable=False),
#     sa.PrimaryKeyConstraint("id"),
# )

# metadata.create_all(engine)

#############====================================================##########################
# Utilizando o Inspector para inspecionar as tabelas e colunas do banco de dados

# import sqlalchemy as sa

# engine = sa.create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=False
# )


# inspect = sa.inspect(engine)
# print(inspect.get_table_names())
# print(inspect.get_columns("comments"))

#############====================================================##########################
# Utilizando o Table para refletir uma tabela já existente no banco de dados

# import sqlalchemy as sa

# metadata = sa.MetaData()
# engine = sa.create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=False
# )

# t = sa.Table("comments", metadata, autoload_with=engine)

# print(t)
# print(t.c)
# print(t.c.id)
#############====================================================##########################
# Construindo consultas SQL de forma programática utilizando o Table e os métodos select, insert, update e delete
# from sqlalchemy import MetaData, Table, create_engine, delete, insert, select, update

# metadata = MetaData()
# engine = create_engine(
#     "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_zero", echo=False
# )

# t = Table("comments", metadata, autoload_with=engine)

# sql = select(t)
# print(sql)

# with engine.connect() as connection:
#     result = connection.execute(sql)
#     print(result.fetchall())

# # CoumpoundSelect -> é um objeto que representa uma consulta SQL composta por várias subconsultas,
# # como UNION, INTERSECT ou EXCEPT. Ele permite combinar os resultados de várias consultas em uma única consulta composta.
# sql = (
#     select(t.c.id, t.c.name)
#     .where(t.c.name == "Eudes")
#     .limit(10)
#     .offset(0)
#     .order_by(t.c.id.desc())
# )

# print(sql)

# with engine.connect() as connection:
#     result = connection.execute(sql)
#     print(result.fetchmany(5))


# # Statement com conectivos lógicos

# sql = select(t.c.name, t.c.comment).where(
#     (t.c.name == "Eudes") | (t.c.name == "Maria") & (t.c.live == "youtube")
# )

# print(sql)

# with engine.connect() as connection:
#     result = connection.execute(sql)
#     print(result.fetchall())


# sql = insert(t).values(
#     name="Eudes",
#     comment="Ótimo vídeo!",
#     live="youtube",
#     created_at="2024-06-01 12:00:00",
# )

# print(sql)

# with engine.connect() as connection:
#     result = connection.execute(sql)
#     connection.commit()
#     print(result.inserted_primary_key)


# sql = update(t).where(t.c.id == 3).values(comment="Comentário atualizado")

# print(sql)
# with engine.connect() as connection:
#     result = connection.execute(sql)
#     connection.commit()
#     print(result.rowcount)


# sql = delete(t).where(t.c.id == 3)

# print(sql)
# with engine.connect() as connection:
#     result = connection.execute(sql)
#     connection.commit()
#     print(result.rowcount)


# Definindo schemas utilizando objetos do Python - ORM
# from sqlalchemy import Column, DateTime, Integer, String, func
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry

# class Base(DeclarativeBase): ...


# Sem definição de tipos - Tradicional 1.0
# class Comment(Base):
#     __tablename__ = "comments"

#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False)
#     comment = Column(String, nullable=False)
#     live = Column(String, nullable=False)
#     created_at = Column(DateTime, nullable=False, server_default=func.now())


# Com definição de tipos - Com Typing - Mais indicado
# class Comment(Base):
#     __tablename__ = "comments"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String, nullable=False)
#     comment: Mapped[str] = mapped_column(String, nullable=False)
#     live: Mapped[str] = mapped_column(String, nullable=False)
#     created_at: Mapped[DateTime] = mapped_column(
#         DateTime, nullable=False, server_default=func.now()
# )

# Utilizando DataClasses para definir os schemas do ORM - Modelo com Dataclass
# reg = registry()


# @reg.mapped_as_dataclass
# class Comment:
#     __tablename__ = "comments"

#     id: Mapped[int] = mapped_column(Integer, init=False, primary_key=True)
#     name: Mapped[str] = mapped_column(String, nullable=False)
#     comment: Mapped[str] = mapped_column(String, nullable=False)
#     live: Mapped[str] = mapped_column(String, nullable=False)
#     created_at: Mapped[DateTime] = mapped_column(
#         DateTime, init=False, nullable=False, server_default=func.now()
#     )
