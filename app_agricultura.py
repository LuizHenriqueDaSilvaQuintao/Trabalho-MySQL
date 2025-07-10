# app_agricultura.py

import mysql.connector
from mysql.connector import Error

# --- Configurações do Banco de Dados ---
# ATENÇÃO: Substitua 'sua_senha' pela sua senha real do MySQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'agricultura_familiar',
    'user': 'root',
    'password': '' 
}

# --- Funções de Conexão e Criação de Tabelas ---

def create_db_connection():
    """Cria e retorna uma conexão com o banco de dados MySQL."""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Conexão com o banco de dados MySQL estabelecida com sucesso!")
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
    return connection

def create_tables(connection):
    """Cria as tabelas 'vendedores' e 'produtos' no banco de dados."""
    cursor = connection.cursor()
    
    create_vendedores_table_sql = """
    CREATE TABLE IF NOT EXISTS vendedores (
        id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
        nome VARCHAR(50),
        contato VARCHAR(55) UNIQUE,
        localizacao VARCHAR(55)
    )
    """
    
    create_produtos_table_sql = """
    CREATE TABLE IF NOT EXISTS produtos (
        id INT PRIMARY KEY AUTO_INCREMENT,
        nome_produto VARCHAR(50),
        descricao TEXT,
        preco DECIMAL(10,2), -- Preço por kg
        id_vendedor INT,
        FOREIGN KEY (id_vendedor) REFERENCES vendedores(id)
    )
    """
    
    try:
        print("Criando tabela 'vendedores'...")
        cursor.execute(create_vendedores_table_sql)
        print("Tabela 'vendedores' criada ou já existente.")
        
        
        print("Criando tabela 'produtos'...")
        cursor.execute(create_produtos_table_sql)
        print("Tabela 'produtos' criada ou já existente.")
        
        connection.commit()
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        cursor.close()

# --- Funções de Cadastro e Busca ---

def insert_vendedor(connection, nome, contato, localizacao):
    """Insere um novo vendedor no banco de dados."""
    cursor = connection.cursor()
    sql = "INSERT INTO vendedores (nome, contato, localizacao) VALUES (%s, %s, %s)"
    val = (nome, contato, localizacao)
    try:
        cursor.execute(sql, val)
        connection.commit()
        print(f"Vendedor '{nome}' inserido com sucesso! ID: {cursor.lastrowid}")
        return cursor.lastrowid
    except Error as e:
        if e.errno == 1062:
            print(f"Erro: O contato '{contato}' já existe para outro vendedor. Por favor, use um contato único.")
        else:
            print(f"Erro ao inserir vendedor: {e}")
        return None
    finally:
        cursor.close()

def insert_produto(connection, nome_produto, descricao, preco, id_vendedor):
    """Insere um novo produto no banco de dados, associado a um vendedor."""
    cursor = connection.cursor()
    sql = "INSERT INTO produtos (nome_produto, descricao, preco, id_vendedor) VALUES (%s, %s, %s, %s)"
    val = (nome_produto, descricao, preco, id_vendedor)
    try:
        cursor.execute(sql, val)
        connection.commit()
        print(f"Produto '{nome_produto}' inserido com sucesso!")
    except Error as e:
        print(f"Erro ao inserir produto: {e}")
    finally:
        cursor.close()

def search_produtos(connection, termo_busca):
    """Busca produtos por nome ou descrição e exibe nome do vendedor, contato e preço por kg."""
    cursor = connection.cursor(dictionary=True)
    sql = """
    SELECT 
        p.nome_produto, 
        p.preco, 
        v.nome AS nome_vendedor, 
        v.contato AS contato_vendedor
    FROM 
        produtos p
    JOIN 
        vendedores v ON p.id_vendedor = v.id
    WHERE 
        p.nome_produto LIKE %s OR p.descricao LIKE %s
    """
    termo_busca_like = f"%{termo_busca}%"
    val = (termo_busca_like, termo_busca_like)
    
    try:
        cursor.execute(sql, val)
        results = cursor.fetchall()
        if results:
            print(f"\n--- Resultados da Busca por '{termo_busca}' ---")
            for row in results:
                print(f"  Produto: {row['nome_produto']}")
                print(f"    Vendedor: {row['nome_vendedor']}")
                print(f"    Contato: {row['contato_vendedor']}")
                print(f"    Preço por Kg: R${row['preco']:.2f}")
                print("-" * 30)
        else:
            print(f"\nNenhum produto encontrado para '{termo_busca}'.")
        return results
    except Error as e:
        print(f"Erro ao buscar produtos: {e}")
        return []
    finally:
        cursor.close()

def get_all_vendedores(connection):
    """Retorna uma lista de todos os vendedores (ID e Nome)."""
    cursor = connection.cursor(dictionary=True)
    sql = "SELECT id, nome FROM vendedores"
    try:
        cursor.execute(sql)
        vendedores = cursor.fetchall()
        return vendedores
    except Error as e:
        print(f"Erro ao obter vendedores: {e}")
        return []
    finally:
        cursor.close()

# --- Função Principal ---

def main():
    """Função principal para gerenciar as operações do sistema."""
    connection = create_db_connection()
    if connection:
        create_tables(connection)

        while True:
            print("\n--- Menu Principal ---")
            print("1. Cadastrar Vendedor e seu Primeiro Produto")
            print("2. Cadastrar Produto Adicional para um Vendedor Existente")
            print("3. Consultar Produtos") # Opção renomeada
            print("4. Sair") # Opção de sair agora é 4
            
            choice = input("Escolha uma opção: ")

            if choice == '1':
                nome_vendedor = input("Nome do Vendedor: ")
                contato_vendedor = input("Contato do Vendedor (telefone/email): ")
                localizacao_vendedor = input("Localização do Vendedor (cidade/região): ")
                
                vendedor_id = insert_vendedor(connection, nome_vendedor, contato_vendedor, localizacao_vendedor)
                
                if vendedor_id:
                    print("\n--- Agora, cadastre o primeiro produto deste vendedor ---")
                    nome_produto = input("Nome do Produto: ")
                    descricao_produto = input("Descrição do Produto: ")
                    try:
                        preco_produto = float(input("Preço do Produto (por Kg): ")) # Indicando que é por Kg
                        insert_produto(connection, nome_produto, descricao_produto, preco_produto, vendedor_id)
                    except ValueError:
                        print("Entrada inválida para Preço. O produto não foi cadastrado.")
                
            elif choice == '2':
                vendedores = get_all_vendedores(connection)
                if not vendedores:
                    print("Nenhum vendedor cadastrado. Cadastre um vendedor primeiro.")
                    continue
                
                print("\n--- Vendedores Cadastrados ---")
                for v in vendedores:
                    print(f"ID: {v['id']} - Nome: {v['nome']}")
                
                try:
                    id_vendedor = int(input("Digite o ID do vendedor para associar o produto: "))
                    if not any(v['id'] == id_vendedor for v in vendedores):
                        print("ID de vendedor inválido. Tente novamente.")
                        continue

                    nome_produto = input("Nome do Produto: ")
                    descricao = input("Descrição do Produto: ")
                    preco = float(input("Preço do Produto (por Kg): ")) # Indicando que é por Kg
                    insert_produto(connection, nome_produto, descricao, preco, id_vendedor)
                except ValueError:
                    print("Entrada inválida para ID ou Preço. Por favor, digite um número.")
                
            elif choice == '3': # Agora esta é a opção de consulta de produtos
                termo_busca = input("Digite o nome ou descrição do produto para consultar: ")
                search_produtos(connection, termo_busca)
            
            elif choice == '4': # Opção de sair agora é 4
                print("Saindo do programa. Até mais!")
                break
            
            else:
                print("Opção inválida. Por favor, escolha uma opção válida.")

        connection.close()
        print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()
