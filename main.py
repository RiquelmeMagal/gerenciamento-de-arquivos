# Definindo a classe para cada bloco no disco
class DiskBlock:
    def __init__(self):
        self.char = None  # Armazena um caractere do arquivo
        self.next = -1    # Ponteiro para o próximo bloco (-1 indica o fim do arquivo)


# Definindo a entrada da tabela de arquivos
class FileEntry:
    def __init__(self, name, size, start):
        self.name = name  # Nome do arquivo
        self.size = size  # Tamanho do arquivo em caracteres
        self.start = start  # Índice do bloco inicial no disco


# Classe principal do sistema de arquivos
class FileSystem:
    def __init__(self, disk_size=32):
        self.disk_size = disk_size
        self.disk = [DiskBlock() for _ in range(disk_size)]  # Disco representado por uma lista de blocos
        self.file_table = {}  # Tabela de arquivos agora é um dicionário para melhorar a eficiência de busca
        self.free_map = [True] * disk_size  # Mapa de bits para gerenciar blocos livres

    # Função para imprimir o estado atual do disco
    def print_disk(self):
        from tabulate import tabulate

        table = []
        for idx, block in enumerate(self.disk):
            char = block.char if block.char is not None else "-"
            next_ptr = block.next if block.next != -1 else "Nulo"
            status = "Livre" if self.free_map[idx] else f"{char}\t{next_ptr}"
            table.append([idx, char if self.free_map[idx] else status, next_ptr if not self.free_map[idx] else "-"])

        headers = ["Índice", "Char", "Próximo"]
        print("\nEstado atual do disco:")
        print(tabulate(table, headers=headers, tablefmt="grid"))
        print()

    # Função para encontrar blocos livres suficientes para armazenar um arquivo
    def find_free_blocks(self, required):
        free_indices = [i for i, free in enumerate(self.free_map) if free]
        if len(free_indices) >= required:
            return free_indices[:required]
        else:
            return None

    # Função para criar um novo arquivo
    def create_file(self, name, content):
        if name in self.file_table:
            print(f"Erro: Arquivo '{name}' já existe.")
            return

        size = len(content)
        free_blocks = self.find_free_blocks(size)
        if not free_blocks:
            print("Erro: Memória insuficiente para criar o arquivo.")
            return

        # Alocar blocos no disco
        for i, char in enumerate(content):
            block_idx = free_blocks[i]
            self.disk[block_idx].char = char
            if i < size - 1:
                self.disk[block_idx].next = free_blocks[i + 1]
            else:
                self.disk[block_idx].next = -1  # Último bloco
            self.free_map[block_idx] = False

        # Adicionar entrada na tabela de arquivos
        new_file = FileEntry(name, size, free_blocks[0])
        self.file_table[name] = new_file
        print(f"Arquivo '{name}' criado com sucesso.")

    # Função para ler o conteúdo de um arquivo
    def read_file(self, name):
        file = self.file_table.get(name)
        if not file:
            print(f"Erro: Arquivo '{name}' não encontrado.")
            return

        content = []
        current = file.start
        while current != -1:
            block = self.disk[current]
            content.append(block.char)
            current = block.next

        content_str = ''.join(content)
        print(f"Conteúdo do arquivo '{name}': {content_str}")

    # Função para excluir um arquivo
    def delete_file(self, name):
        file = self.file_table.pop(name, None)
        if file is None:
            print(f"Erro: Arquivo '{name}' não encontrado.")
            return

        current = file.start
        while current != -1:
            block = self.disk[current]
            next_block = block.next
            # Liberar o bloco
            self.disk[current].char = None
            self.disk[current].next = -1
            self.free_map[current] = True
            current = next_block

        print(f"Arquivo '{name}' excluído com sucesso.")

    # Função para listar todos os arquivos no sistema
    def list_files(self):
        if not self.file_table:
            print("Nenhum arquivo no sistema.")
            return
        print("\nTabela de Arquivos:")
        print("Nome\t\tTamanho\tEndereço")
        for file in self.file_table.values():
            print(f"{file.name}\t{file.size}\t{file.start}")
        print()


# Função principal para interação com o usuário
def main():
    fs = FileSystem()

    while True:
        print("Sistema de Arquivos Simples")
        print("1. Criar Arquivo")
        print("2. Ler Arquivo")
        print("3. Excluir Arquivo")
        print("4. Listar Arquivos")
        print("5. Imprimir Disco")
        print("6. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            name = input("Digite o nome do arquivo: ")
            content = input("Digite o conteúdo do arquivo (palavra): ")
            fs.create_file(name, content)
            fs.print_disk()
        elif escolha == '2':
            name = input("Digite o nome do arquivo para leitura: ")
            fs.read_file(name)
            fs.print_disk()
        elif escolha == '3':
            name = input("Digite o nome do arquivo para excluir: ")
            fs.delete_file(name)
            fs.print_disk()
        elif escolha == '4':
            fs.list_files()
        elif escolha == '5':
            fs.print_disk()
        elif escolha == '6':
            print("Saindo do sistema de arquivos.")
            break
        else:
            print("Opção inválida. Tente novamente.\n")


if __name__ == "__main__":
    main()
