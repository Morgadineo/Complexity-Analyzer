# Diretórios
SRC_DIR = Examples
FAKE_HEADERS = /lib/pycparser/utils/fake_libc_include 

# Variáveis de compilação
CC = gcc
CFLAGS = -E -nostdinc -I$(FAKE_HEADERS) -I/usr/include
LIBDIR = /usr/lib
LIBS = -lcs50

# Encontra todos os arquivos .c no diretório Examples
SRCS = $(wildcard $(SRC_DIR)/*.c)

# Define os arquivos limpos, pré-processados e compilados
CLEANED = $(SRCS:.c=_limpo.c)
PREPROCESSED = $(CLEANED:.c=_pre.c)
EXECUTABLES = $(SRCS:.c=.out)

# Regra padrão: limpar, pré-processar e compilar todos os arquivos
all: clean_comments preprocess compile

# Regra para limpar comentários de cada arquivo
%_limpo.c: %.c
	@echo "Limpando comentários de $<..."
	@sed -e '/\/\*\*/,/\*\//s/.*//g' -e 's/\/\/.*//g' "$<" > "$@"

# Regra para pré-processar cada arquivo limpo
%_pre.c: %_limpo.c
	@echo "Pré-processando $<..."
	@$(CC) $(CFLAGS) -o "$@" "$<"
	@sed '/^#/d' "$@" > "$@.tmp" && mv "$@.tmp" "$@"

# Limpar comentários de todos os arquivos
clean_comments: $(CLEANED)

# Pré-processar todos os arquivos limpos
preprocess: $(PREPROCESSED)

# Compilar os arquivos pré-processados com as bibliotecas
compile: $(EXECUTABLES)

%.out: %_pre.c
	@echo "Compilando $<..."
	@$(CC) "$<" -o "$@" -L$(LIBDIR) $(LIBS)

# Limpar arquivos gerados
clean:
	rm -f $(CLEANED) $(PREPROCESSED) $(EXECUTABLES)

.PHONY: all clean_comments preprocess compile clean
