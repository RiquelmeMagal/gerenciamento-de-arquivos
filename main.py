import os
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

# Criando o objeto console para usar as funcionalidades do Rich
console = Console()

# Definindo a classe para cada bloco no disco
class DiskBlock:
    def __init__(self):
        self.char = None  # Armazena um caractere do arquivo
        self.next = -1    # Ponteiro para o próximo bloco (-1 indica o fim do arquivo)

# Definindo a entrada da tabela de arquivos
class FileEntry:
    def __init__(self, name, size, start):
        self.name = name    # Nome do arquivo
        self.size = size    # Tamanho do arquivo em caracteres
        self.start = start  # Índice do bloco inicial no disco

# Classe principal do sistema de arquivos
class FileSystem:
    def __init__(self, disk_size=32):
        self.disk_size = disk_size
        self.disk = [DiskBlock() for _ in range(disk_size)]  # Disco representado por uma lista de blocos
        self.file_table = {}  # Tabela de arquivos
        self.free_map = [True] * disk_size  # Mapa de bits para gerenciar blocos livres

    # Função para limpar a tela
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    # Função para imprimir o estado atual do disco
    def print_disk(self):
        table = Table(title="📀 Estado Atual do Disco", show_header=True, header_style="bold yellow")
        table.add_column("Bloco", style="bold", width=6, justify="center")
        table.add_column("Char", width=8, justify="center")
        table.add_column("Ponteiro", justify="center")
        for idx, block in enumerate(self.disk):
            char = f"[cyan]{block.char}[/cyan]" if block.char is not None else "[green]Livre[/green]"
            next_ptr = f"[magenta]{block.next}[/magenta]" if block.next != -1 else "-"
            table.add_row(f"{idx}", char, next_ptr)
        console.print(table)

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
            console.print(f"[red bold]❌ Erro: Arquivo '{name}' já existe.[/red bold]")
            return

        size = len(content)
        free_blocks = self.find_free_blocks(size)
        if not free_blocks:
            console.print("[red bold]❌ Erro: Memória insuficiente para criar o arquivo.[/red bold]")
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
        console.print(f"[bold green]✅ Arquivo '{name}' criado com sucesso![/bold green]")

    # Função para ler o conteúdo de um arquivo
    def read_file(self, name):
        file = self.file_table.get(name)
        if not file:
            console.print(f"[red bold]❌ Erro: Arquivo '{name}' não encontrado.[/red bold]")
            return

        content = []
        current = file.start
        while current != -1:
            block = self.disk[current]
            content.append(block.char)
            current = block.next

        content_str = ''.join(content)
        panel = Panel(f"[white]{content_str}[/white]", title=f"[bold blue]📄 Conteúdo do arquivo '{name}'[/bold blue]", border_style="blue")
        console.print(panel)

    # Função para excluir um arquivo
    def delete_file(self, name):
        file = self.file_table.pop(name, None)
        if file is None:
            console.print(f"[red bold]❌ Erro: Arquivo '{name}' não encontrado.[/red bold]")
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

        console.print(f"[bold green]🗑️ Arquivo '{name}' excluído com sucesso![/bold green]")

    # Função para listar todos os arquivos no sistema
    def list_files(self):
        console.print("[bold blue]\n📂 Tabela de Arquivos:[/bold blue]")
        if not self.file_table:
            console.print("[yellow]⚠️ Nenhum arquivo armazenado.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold yellow")
        table.add_column("Nome", style="bold cyan", width=15)
        table.add_column("Tamanho", justify="center")
        table.add_column("Endereço", justify="center")
        for file in self.file_table.values():
            table.add_row(f"[white]{file.name}[/white]", f"{file.size}", f"{file.start}")
        console.print(table)

# Função principal para interação com o usuário
def main():
    fs = FileSystem()

    while True:
        fs.clear_screen()
        console.print("[bold magenta]=== 🖥️  Simulação de Sistema de Arquivos ===[/bold magenta]\n")
        console.print("[bold][1][/bold] 📁 Criar Arquivo")
        console.print("[bold][2][/bold] 📖 Ler Arquivo")
        console.print("[bold][3][/bold] 🗑️ Excluir Arquivo")
        console.print("[bold][4][/bold] 📋 Listar Arquivos")
        console.print("[bold][5][/bold] 💾 Imprimir Disco")
        console.print("[bold][0][/bold] ❌ Sair\n")
        escolha = Prompt.ask("[bold green]Escolha uma opção[/bold green]", choices=["1", "2", "3", "4", "5", "0"], default="0")

        if escolha == '1':
            name = Prompt.ask("[bold green]Digite o nome do arquivo[/bold green]")
            content = Prompt.ask("[bold green]Digite o conteúdo do arquivo (palavra)[/bold green]")
            fs.create_file(name, content)
            fs.print_disk()
            console.input("\nPressione ⏎ para continuar...")
        elif escolha == '2':
            name = Prompt.ask("[bold green]Digite o nome do arquivo para leitura[/bold green]")
            fs.read_file(name)
            fs.print_disk()
            console.input("\nPressione ⏎ para continuar...")
        elif escolha == '3':
            name = Prompt.ask("[bold green]Digite o nome do arquivo para excluir[/bold green]")
            fs.delete_file(name)
            fs.print_disk()
            console.input("\nPressione ⏎ para continuar...")
        elif escolha == '4':
            fs.list_files()
            console.input("\nPressione ⏎ para continuar...")
        elif escolha == '5':
            fs.print_disk()
            console.input("\nPressione ⏎ para continuar...")
        elif escolha == '0':
            console.print("[bold red]\n👋 Saindo do sistema de arquivos. Até logo![/bold red]")
            break
        else:
            console.print("[red bold]❌ Opção inválida. Tente novamente.[/red bold]")
            console.input("\nPressione ⏎ para continuar...")

if __name__ == "__main__":
    main()
