from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
import os
import csv

DATA_FILE = 'pessoas.csv'

# Função para salvar os dados no arquivo CSV
def salvar_dados(nome, data_nascimento):
    with open(DATA_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nome, data_nascimento])

# Função para carregar os dados do arquivo CSV
def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, mode='r') as file:
        reader = csv.reader(file)
        return list(reader)

# Função para filtrar dados por mês de nascimento
def filtrar_por_mes(mes):
    dados = carregar_dados()
    return [p for p in dados if p[1].split('-')[1] == mes]

# Classe que lida com as requisições HTTP
class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.exibir_pagina_principal()
        elif self.path == '/ver_todos':
            self.exibir_todos()
        elif self.path.startswith('/ver_por_mes'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            mes = params.get('mes', [''])[0]
            self.exibir_por_mes(mes)
        elif self.path == '/remover_pessoa':
            self.exibir_pagina_remover()
        elif self.path == '/ver_meses':
            self.exibir_todos_os_meses()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/adicionar':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(body)
            nome = params['nome'][0]
            data_nascimento = params['data_nascimento'][0]
            salvar_dados(nome, data_nascimento)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        elif self.path == '/remover':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(body)
            nome = params['nome'][0]
            remover_pessoa(nome)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

    def exibir_pagina_principal(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }
                h1 { color: #333; }
                form, ul { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
                input[type="text"], input[type="date"] { width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 4px; border: 1px solid #ccc; }
                input[type="submit"] { background: #28a745; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
                input[type="submit"]:hover { background: #218838; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>Adicionar Nova Pessoa</h1>
            <form action="/adicionar" method="POST">
                Nome: <input type="text" name="nome"><br>
                Data de Nascimento (YYYY-MM-DD): <input type="date" name="data_nascimento"><br>
                <input type="submit" value="Adicionar">
            </form>
            <br>
            <a href="/ver_todos">Ver todas as pessoas</a><br>
            <a href="/ver_meses">Ver pessoas por mês</a><br>
            <a href="/remover_pessoa">Remover Pessoa</a>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

    def exibir_todos(self):
        pessoas = carregar_dados()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = "<html><head> <meta charset='UTF-8'> <style>body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; } h1 { color: #333; } ul { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); } a { color: #007bff; text-decoration: none; } a:hover { text-decoration: underline; }</style></head><body><h1>Lista de Todas as Pessoas</h1><ul>"
        for pessoa in pessoas:
            html += f"<li>{pessoa[0]} - {pessoa[1]}</li>"
        html += "</ul><br><a href='/'>Voltar</a></body></html>"
        self.wfile.write(html.encode('utf-8'))

    def exibir_por_mes(self, mes):
        pessoas = filtrar_por_mes(mes)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = f"<html><head><meta charset='UTF-8'><style>body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }} h1 {{ color: #333; }} ul {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }} a {{ color: #007bff; text-decoration: none; }} a:hover {{ text-decoration: underline; }}</style></head><body><h1>Pessoas nascidas em {mes}</h1><ul>"
        for pessoa in pessoas:
            html += f"<li>{pessoa[0]} - {pessoa[1]}</li>"
        html += f"</ul><p>Total: {len(pessoas)}</p><br><a href='/ver_meses'>Ver outro mês</a><br><a href='/'>Voltar</a></body></html>"
        self.wfile.write(html.encode('utf-8'))

    def exibir_todos_os_meses(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        meses = [
            ("01", "Janeiro"), ("02", "Fevereiro"), ("03", "Março"),
            ("04", "Abril"), ("05", "Maio"), ("06", "Junho"),
            ("07", "Julho"), ("08", "Agosto"), ("09", "Setembro"),
            ("10", "Outubro"), ("11", "Novembro"), ("12", "Dezembro")
        ]
        html = "<html><head><meta charset='UTF-8'><style>body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; } h1 { color: #333; } ul { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); } a { color: #007bff; text-decoration: none; } a:hover { text-decoration: underline; }</style></head><body><h1>Ver Pessoas por Mês</h1><ul>"
        for mes_codigo, mes_nome in meses:
            html += f"<li><a href='/ver_por_mes?mes={mes_codigo}'>{mes_nome}</a></li>"
        html += "</ul><br><a href='/'>Voltar</a></body></html>"
        self.wfile.write(html.encode('utf-8'))

    def exibir_pagina_remover(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <html>
        <head>
            <meta charset='UTF-8'>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }
                h1 { color: #333; }
                form { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
                input[type="text"] { width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 4px; border: 1px solid #ccc; }
                input[type="submit"] { background: #dc3545; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
                input[type="submit"]:hover { background: #c82333; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>Remover Pessoa</h1>
            <form action="/remover" method="POST">
                Nome: <input type="text" name="nome"><br>
                <input type="submit" value="Remover">
            </form>
            <br><a href='/'>Voltar</a>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

def remover_pessoa(nome):
    dados = carregar_dados()
    dados = [p for p in dados if p[0] != nome]
    with open(DATA_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(dados)

# Configuração do servidor HTTP
def run(server_class=HTTPServer, handler_class=MyHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Servindo na porta {port}...')
    httpd.serve_forever()

# Executa o servidor
if __name__ == '__main__':
    run()
