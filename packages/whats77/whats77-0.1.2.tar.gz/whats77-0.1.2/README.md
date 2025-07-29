# Whats77

**Versão**: 0.1.1

Whats77 é um facilitador para o uso da API WhatsApp (ZAPI). Este pacote abstrai a autenticação e diversas ações da API, como envio de mensagens de texto, áudio e documentos.

## Instalação

Antes de instalar, assegure-se de ter o Python 3.8 ou superior instalado.

Instale o pacote diretamente via pip:

```bash
pip install whats77
```

## Configuração

O Whats77 utiliza variáveis de ambiente para configurar a autenticação. Crie um arquivo `.env` na raiz do seu projeto com o seguinte formato:

```env
INSTANCE_ID=seu_instance_id
TOKEN=seu_token
SECURITY_TOKEN=seu_security_token
```

### Configuração Manual

Se preferir, você também pode fornecer os tokens diretamente na inicialização da classe `Whats77`:

```python
from whats77 import Whats77

# Inicialização manual com credenciais
whatsapp = Whats77(
    instance_id="seu_instance_id",
    token="seu_token",
    security_token="seu_security_token"
)
```

## Uso

### Inicialização da Classe

A classe `Whats77` é responsável por gerenciar a autenticação e as ações. As credenciais podem ser fornecidas diretamente ou carregadas do arquivo `.env`.

```python
from whats77 import Whats77

# Inicializa a classe com credenciais carregadas do .env
whatsapp = Whats77()
```

### Envio de Mensagens

#### Enviar mensagem de texto

```python
# Envia uma mensagem de texto
whatsapp.send_text(
    phone_number="+5511999999999",
    message="Olá, isso é um teste!"
)
```

#### Enviar documento

```python
whatsapp.send_document(
    phone_number="+5511999999999",
    file_path="/caminho/para/arquivo.pdf",
    document_type="pdf",
    caption="Segue o relatório em anexo."
)
```

#### Enviar áudio

```python
# Converte o arquivo de áudio para Base64
base64_audio = Whats77.parse_to_base64("/caminho/para/audio.mp3")

# Envia o áudio
whatsapp.send_audio(
    phone_number="+5511999999999",
    base64_audio=base64_audio
)
```

### Normalização e Validação de Números

A classe `Whats77` fornece métodos utilitários para trabalhar com números de telefone.

#### Normalizar número de telefone

```python
normalized_number = Whats77.normalize_phone_number("11999999999")
print(normalized_number)  # Saída: 5511999999999
```

#### Validar número de WhatsApp

```python
is_valid = Whats77.is_valid_whatsapp_number("5511999999999")
print(is_valid)  # Saída: True
```

## Dependências

- `requests>=2.0.0`
- `python-dotenv>=0.21.0`

Certifique-se de instalar as dependências via pip se ainda não estiverem presentes no seu ambiente.
