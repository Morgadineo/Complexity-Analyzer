# Diretórios
SRC_DIR = Examples
FAKE_HEADERS = ../pycparser-main/utils/fake_libc_include 

# Variáveis de compilação
CC = gcc
CFLAGS = -E -nostdinc -I$(FAKE_HEADERS) 

# Encontra TODOS os arquivos .c recursivamente em Examples e subpastas
SRCS = $(shell find $(SRC_DIR) -type f -name '*.c')

# Define os arquivos pré-processados (mesma estrutura de pastas, mas com extensão .i)
PREPROCESSED = $(SRCS:.c=.i)

# Regra padrão: pré-processar todos os arquivos
all: preprocess

# Regra para pré-processar cada arquivo .c
%.i: %.c
	@echo "Pré-processando $<..."
	@mkdir -p $(dir $@)  # Garante que o diretório de saída existe
	@$(CC) $(CFLAGS) -o "$@" "$<"

# Pré-processar todos os arquivos
preprocess: $(PREPROCESSED)

# Limpar arquivos gerados (incluindo subpastas)
clean:
	find $(SRC_DIR) -type f -name '*.i' -delete

.PHONY: all preprocess clean
