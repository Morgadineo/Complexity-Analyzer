# Diretórios
SRC_DIR = Examples
FAKE_HEADERS = ../pycparser-main/utils/fake_libc_include 

# Variáveis de compilação
CC = gcc
CFLAGS = -E -nostdinc -I$(FAKE_HEADERS) 

# Diretório alvo (permite sobrescrever com make DIR=...)
DIR ?= $(SRC_DIR)

# Encontra TODOS os arquivos .c recursivamente no diretório-alvo
SRCS = $(shell find $(DIR) -type f -name '*.c')
PREPROCESSED = $(SRCS:.c=.i)

# Regra padrão
all: preprocess

# Pré-processar cada arquivo .c
%.i: %.c
	@echo "Pré-processando $<..."
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -o "$@" "$<"

# Pré-processar todos os arquivos do diretório especificado
preprocess: $(PREPROCESSED)

# Limpar apenas os arquivos .i no diretório especificado
clean:
	@echo "Limpando arquivos *.i em '$(DIR)'..."
	@find "$(DIR)" -type f -name '*.i' -delete

