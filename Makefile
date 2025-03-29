# Diretórios
SRC_DIR = Examples
FAKE_HEADERS = ../pycparser-main/utils/fake_libc_include 

# Variáveis de compilação
CC = gcc
CFLAGS = -E -nostdinc -I$(FAKE_HEADERS) 

# Encontra todos os arquivos .c no diretório Examples
SRCS = $(wildcard $(SRC_DIR)/*.c)

# Define os arquivos limpos, pré-processados e compilados
PREPROCESSED = $(SRCS:.c=.i)

# Regra padrão: limpar, pré-processar e compilar todos os arquivos
all: preprocess

# Regra para pré-processar cada arquivo limpo
%.i: %.c
	@echo "Pré-processando $<..."
	@$(CC) $(CFLAGS) -o "$@" "$<"

# Pré-processar todos os arquivos limpos
preprocess: $(PREPROCESSED)

# Limpar arquivos gerados
clean:
	rm -f $(PREPROCESSED)

.PHONY: all preprocess clean
