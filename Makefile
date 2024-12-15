# Diretórios
SRC_DIR = Examples
FAKE_HEADERS = /home/morgado/.local/lib/pycparser/utils/fake_libc_include

# Variáveis de compilação
CC = gcc
CFLAGS = -E -nostdinc -I$(FAKE_HEADERS) -I/usr/include  # Inclua o caminho para cs50.h
LIBDIR = /usr/lib  # Diretório onde libcs50.a está localizado
LIBS = -lcs50

# Encontra todos os arquivos .c no diretório Examples
SRCS = $(wildcard $(SRC_DIR)/*.c)

# Define os arquivos pré-processados e limpos
PREPROCESSED = $(SRCS:.c=_pre.c)
CLEANED = $(SRCS:.c=_pre_limpo.c)

# Regra padrão: pré-processar, limpar e compilar todos os arquivos
all: clean compile

# Regra para pré-processar e limpar cada arquivo
$(SRC_DIR)/%_pre_limpo.c: $(SRC_DIR)/%.c
	@echo "Pré-processando $<..."
	@$(CC) $(CFLAGS) -o "$(@D)/$*_pre.c" "$<"
	@sed '/^#/d' "$(@D)/$*_pre.c" > "$@"

# Compilar os arquivos limpos com as bibliotecas
compile: $(CLEANED)
	@echo "Compilando com bibliotecas..."
	@for file in $(CLEANED); do \
		base=$${file%_pre_limpo.c}; \
		echo "Compilando $$base.c..."; \
		$(CC) $$base.c -o $$base.out -L$(LIBDIR) $(LIBS); \
    done

# Limpar arquivos gerados
clean:
	rm -f $(PREPROCESSED) $(CLEANED) $(SRC_DIR)/*.out

.PHONY: all clean compile
