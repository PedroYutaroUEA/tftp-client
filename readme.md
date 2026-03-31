# Cliente TFTP
Um cliente TFTP (Trivial File Transfer Protocol) leve e assíncrono, implementado em Python com asyncio. Suporta operações de download e upload de arquivos.

# Estrutura do projeto
```
.
├── main.py                   # Utiliza o cliente para acessar o servidor
│
├── protocol/
│   ├── packet.py             # Construtor e parser de pacotes TFTP
│
├── downloads/                # Pasta de recebimento de arquivos
│
└── upload/                   # Pasta de envio de arquivos
```
# Como executar
### Pré-requisitos
* Python 3.10+
### Instalar dependências
