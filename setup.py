from cx_Freeze import setup, Executable
import os

# Definindo os arquivos adicionais a serem incluídos no pacote
inclusao_dados = [
    ('assets', 'assets'),
    ('background', 'background'),
    ('esqueleto', 'esqueleto'),
    ('sounds', 'sounds'),
    ('valkyrie', 'valkyrie'),
    ('Valkyrie_boss', 'Valkyrie_boss'),
    ('README.md', 'README.md')  # Incluindo o arquivo README.md
]

# Definindo o nome do executável
executavel = Executable(
    script='plataforma_game.py',
    base=None,  # Se o seu jogo for gráfico, base deve ser None
    icon=None   # Se você tiver um ícone, pode definir aqui
)

# Configurando o cx_Freeze
setup(
    name="Esqueleto vs Valquírias",
    version="1.0",
    description="Jogo de plataforma",
    options={"build_exe": {"packages": ["pygame", "cv2"], "include_files": inclusao_dados}},
    executables=[executavel],
)
