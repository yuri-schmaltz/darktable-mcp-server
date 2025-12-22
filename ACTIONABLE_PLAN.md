# 🎯 PLANO DE AÇÃO EXECUTÁVEL - darktable-mcp-batch

**Data**: 2025-12-22  
**Versão**: 1.0  
**Baseado em**: COMPREHENSIVE_ANALYSIS.md

---

## 📋 ÍNDICE DE TAREFAS

### 🚨 Bloqueadores (Semana 1 - Dia 1-2)
- [TASK-001](#task-001) - Corrigir Widgets GUI Ausentes
- [TASK-002](#task-002) - Adicionar Imports Faltantes  
- [TASK-003](#task-003) - Sanitização de Command Injection

### 🔥 Quick Wins (Semana 1 - Dia 3-5)
- [TASK-004](#task-004) - Consolidar Arquivos GUI Duplicados
- [TASK-005](#task-005) - Feedback de Progresso em Preparação de Imagens
- [TASK-006](#task-006) - Aumentar Contraste de Botões Desabilitados
- [TASK-007](#task-007) - Adicionar Accessible Names a Campos

### 🔧 Médio Prazo (Semana 2-3)
- [TASK-008](#task-008) - Processamento Assíncrono de Imagens
- [TASK-009](#task-009) - Cache de Coleções
- [TASK-010](#task-010) - Suite de Testes Unitários
- [TASK-011](#task-011) - CI Pipeline
- [TASK-012](#task-012) - Ordem de Tab e Atalhos de Teclado
- [TASK-013](#task-013) - Logging Estruturado JSON

### 🏗️ Estrutural (Mês 2)
- [TASK-014](#task-014) - Design System com Tokens
- [TASK-015](#task-015) - Refatorar Tratamento de Erros
- [TASK-016](#task-016) - Configuração Centralizada
- [TASK-017](#task-017) - Documentação de Arquitetura
- [TASK-018](#task-018) - Internacionalização (i18n)
- [TASK-019](#task-019) - Otimizar Redimensionamento de Imagem
- [TASK-020](#task-020) - Testes de Segurança

---

<a name="task-001"></a>
## TASK-001: Corrigir Widgets GUI Ausentes [BLOQUEADOR]

**Objetivo**: Fazer a GUI iniciar sem crashes ao tentar acessar `self.timeout_spin` e `self.generate_styles_check`.

**Problema**: 
- Arquivo: `host/mcp_gui.py:1245, 1248`
- `_build_config()` referencia widgets que não existem
- Runtime error: `AttributeError: 'MCPGui' object has no attribute 'timeout_spin'`

**Solução**:

**Opção A** - Adicionar os widgets faltantes:

```python
# Em _build_layout(), após a linha ~590 (seção de checkboxes)

# Timeout para LLM
self.timeout_spin = QSpinBox()
self.timeout_spin.setRange(10, 600)
self.timeout_spin.setValue(60)
self.timeout_spin.setSuffix(" segundos")
self.timeout_spin.setToolTip(
    "Tempo máximo de espera pela resposta do modelo LLM (10-600s)."
)
self._style_form_field(self.timeout_spin)
config_form.addRow("Timeout do modelo:", self.timeout_spin)

# Generate styles (se feature está pronta)
self.generate_styles_check = QCheckBox("Gerar estilos automaticamente")
self.generate_styles_check.setChecked(True)
self.generate_styles_check.setToolTip(
    "Quando ativado, o sistema gera arquivos de estilo .xmp para Darktable."
)
# Adicionar em flags_layout junto com dry_run_check e attach_images_check (linha ~589)
flags_layout.addWidget(self.generate_styles_check)
```

**Opção B** - Remover referências se features não estão implementadas:

```python
# Em _build_config() (linha ~1245-1248), comentar ou usar valores padrão:

return RunConfig(
    # ...campos anteriores
    timeout=60.0,  # Hardcoded default em vez de self.timeout_spin.value()
    generate_styles=True,  # Hardcoded default
    # ...resto
)
```

**Passos de Implementação**:
1. Abrir `host/mcp_gui.py`
2. Escolher Opção A ou B baseado em se as features estão prontas no backend
3. Se Opção A:
   - Adicionar `self.timeout_spin` após linha 590
   - Adicionar `self.generate_styles_check` em `flags_layout`
4. Se Opção B:
   - Comentar linhas 1245, 1248
   - Usar valores padrão hardcoded
5. Testar: `python3 host/mcp_gui.py`
6. Verificar que GUI abre sem erros
7. Clicar em "Executar host" e confirmar que não lança `AttributeError`

**Critérios de Aceite**:
- [ ] GUI inicia sem AttributeError
- [ ] Botão "Executar host" não crasha
- [ ] Se Opção A: campos visíveis e funcionais
- [ ] Se Opção B: documentar como "TODO" no código

**Riscos**:
- **Baixo**: Se Opção A e backend não suporta, terá campos sem efeito (documentar)
- **Nenhum**: Se Opção B

**Dependências**: Nenhuma

**Estimativa**: 1h

**Prioridade**: P0 - BLOQUEADOR

---

<a name="task-002"></a>
## TASK-002: Adicionar Imports Faltantes [ALTO]

**Objetivo**: Eliminar `NameError` para constantes `LMSTUDIO_MODEL` e `LMSTUDIO_URL`.

**Problema**:
- Arquivo: `host/mcp_gui.py:976, 978`
- Código referencia `LMSTUDIO_MODEL` e `LMSTUDIO_URL` mas não importa
- Afeta `_apply_host_defaults()` se o ramo de código for executado

**Solução**:

**Opção A** - LM Studio ainda é suportado:

```python
# No topo do arquivo (linha ~48-54), adicionar import:

from mcp_host_ollama import (
    APP_VERSION as HOST_APP_VERSION,
    OLLAMA_MODEL,
    OLLAMA_URL,
    PROTOCOL_VERSION as MCP_PROTOCOL_VERSION,
    load_prompt as load_ollama_prompt,
)

# Adicionar import de LM Studio:
from mcp_host_lmstudio import LMSTUDIO_MODEL, LMSTUDIO_URL
```

**Opção B** - LM Studio não é mais suportado:

```python
# Remover referências (linhas 976-978):

def _apply_host_defaults(self) -> None:
    # Simplificar para Ollama apenas
    model_default = OLLAMA_MODEL
    url_default = OLLAMA_URL

    current_model = self.model_combo.currentText().strip()
    current_url = self.url_edit.text().strip()

    if not current_model:
        self.model_combo.setEditText(model_default)
    if not current_url:
        self.url_edit.setText(url_default)
```

**Passos de Implementação**:
1. Verificar se `mcp_host_lmstudio.py` está funcional
2. Decidir Opção A ou B baseado no roadmap do produto
3. Se Opção A: Adicionar import na linha ~54
4. Se Opção B: Simplificar `_apply_host_defaults()` e remover referências a LMSTUDIO_*
5. Compilar: `python3 -m py_compile host/mcp_gui.py`
6. Verificar sem erros de sintaxe
7. Testar GUI: Abrir, trocar entre hosts (se Opção A)

**Critérios de Aceite**:
- [ ] `python3 -m py_compile host/mcp_gui.py` passa sem erros
- [ ] GUI abre e `_apply_host_defaults()` funciona
- [ ] Se Opção A: Ambos hosts funcionais
- [ ] Se Opção B: README atualizado removendo menções a LM Studio

**Riscos**:
- **Médio**: Se escolher Opção B mas usuários dependem de LM Studio

**Dependências**: TASK-001

**Estimativa**: 30min

**Prioridade**: P0 - ALTO

---

<a name="task-003"></a>
## TASK-003: Sanitização de Command Injection [CRÍTICO - SEGURANÇA]

**Objetivo**: Prevenir execução arbitrária de comandos via `export_collection` no servidor Lua.

**Problema**:
- Arquivo: `server/dt_mcp_server.lua` (função `export_collection`)
- `target_dir` e nomes de arquivo são inseridos diretamente em `os.execute()`
- Exemplo de payload malicioso: `--target-dir "; rm -rf / #"`

**Solução**:

```lua
-- Adicionar no início do arquivo, após as funções auxiliares

local function sanitize_path(path)
  -- Rejeitar caracteres perigosos
  if path:match("[;|&$`<>]") then
    return nil, "Caractere shell inválido detectado"
  end
  
  -- Rejeitar path traversal
  if path:match("%.%.") then
    return nil, "Path traversal (..) não permitido"
  end
  
  -- Rejeitar newlines e null bytes
  if path:match("[\n\r\0]") then
    return nil, "Caractere de controle inválido"
  end
  
  return path
end

local function sanitize_format(format)
  -- Whitelist de formatos permitidos
  local allowed = { jpg=true, jpeg=true, png=true, tif=true, tiff=true, webp=true }
  
  local clean = format:lower():gsub("[^a-z]", "")
  
  if not allowed[clean] then
    return nil, "Formato não permitido. Use: jpg, png, tif, tiff, webp"
  end
  
  return clean
end
```

```lua
-- Na função export_collection, adicionar validação antes do loop:

local function export_collection(params, id)
  local target_dir = params.target_dir or ""
  local format = params.format or "jpg"
  local ids = params.ids or {}
  
  -- VALIDAÇÃO
  local clean_dir, err_dir = sanitize_path(target_dir)
  if not clean_dir then
    return error_response(id, err_dir)
  end
  
  local clean_format, err_fmt = sanitize_format(format)
  if not clean_format then
    return error_response(id, err_fmt)
  end
  
  -- Verificar se diretório existe
  if not dir_exists(clean_dir) then
    return error_response(id, string.format("Diretório não existe: %s", clean_dir))
  end
  
  -- Continuar com export usando clean_dir e clean_format
  -- ...resto da função
end
```

**Passos de Implementação**:
1. Abrir `server/dt_mcp_server.lua`
2. Adicionar funções `sanitize_path()` e `sanitize_format()` após linha 100
3. Modificar `export_collection()` para validar inputs
4. Usar `clean_dir` e `clean_format` em vez de `target_dir` e `format`
5. Testar com payloads maliciosos:
   ```bash
   # Criar script de teste
   echo '{"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"export_collection","arguments":{"target_dir":"; echo PWNED","format":"jpg","ids":[1]}}}' | lua server/dt_mcp_server.lua
   # Deve retornar erro: "Caractere shell inválido"
   ```
6. Testar com inputs válidos:
   ```bash
   echo '{"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"export_collection","arguments":{"target_dir":"/tmp/export","format":"jpg","ids":[1]}}}' | lua server/dt_mcp_server.lua
   # Deve funcionar normalmente
   ```

**Critérios de Aceite**:
- [ ] Payload `; rm -rf /` rejeitado com erro claro
- [ ] Payload `../../etc/passwd` rejeitado
- [ ] Payload `$(whoami)` rejeitado
- [ ] Payload com backticks rejeitado
- [ ] Formato `exe` ou `sh` rejeitado
- [ ] Paths válidos como `/home/user/exports` funcionam
- [ ] Formatos válidos como `jpg`, `png` funcionam

**Riscos**:
- **Baixo**: Regex pode ter falsos positivos (testar com paths reais)
- **Nenhum**: Para segurança, melhor ser conservador

**Dependências**: Nenhuma

**Estimativa**: 1-2h (incluindo testes)

**Prioridade**: P0 - CRÍTICO

---

<a name="task-004"></a>
## TASK-004: Consolidar Arquivos GUI Duplicados [ALTO]

**Objetivo**: Ter um único arquivo GUI canônico, evitando confusão.

**Problema**:
- Três arquivos: `mcp_gui.py`, `mcp_gui_work.py`, `mcp_gui copy.py`
- Todos com ~1400 linhas, mas pequenas diferenças
- Dificulta saber qual é o "oficial"

**Solução**:

```bash
# 1. Comparar arquivos
cd host
diff -u mcp_gui.py mcp_gui_work.py > ../tmp/gui_diff_work.patch
diff -u mcp_gui.py "mcp_gui copy.py" > ../tmp/gui_diff_copy.patch

# 2. Revisar diffs e consolidar features úteis
# 3. Arquivar versões antigas
mkdir -p ../archive/old_gui_versions
git mv mcp_gui_work.py ../archive/old_gui_versions/
git mv "mcp_gui copy.py" ../archive/old_gui_versions/

# 4. Atualizar .gitignore
echo "archive/" >> ../.gitignore
```

**Passos de Implementação**:
1. Criar diretório `archive/old_gui_versions/`
2. Comparar os 3 arquivos com `diff` ou IDE visual (VS Code, Meld)
3. Identificar features únicas em `_work` e `copy`:
   - Se importantes: Portar para `mcp_gui.py`
   - Se experimentais: Documentar em README ou issue
4. Mover arquivos antigos para `archive/`
5. Adicionar `archive/` ao `.gitignore`
6. Atualizar README para mencionar apenas `mcp_gui.py`
7. Testar `python3 host/mcp_gui.py` funciona normalmente

**Critérios de Aceite**:
- [ ] Um único `host/mcp_gui.py` funcional
- [ ] Arquivos antigos em `archive/old_gui_versions/`
- [ ] `.gitignore` exclui `archive/`
- [ ] README não menciona versões antigas
- [ ] Features importantes consolidadas

**Riscos**:
- **Médio**: Perder features experimentais úteis (revisar cuidadosamente)

**Dependências**: TASK-001, TASK-002

**Estimativa**: 2h

**Prioridade**: P1 - ALTO

---

<a name="task-005"></a>
## TASK-005: Feedback de Progresso em Preparação de Imagens

**Objetivo**: Evitar impressão de travamento durante encoding de imagens.

**Problema**:
- Arquivo: `host/common.py:646-709`
- Loop processa até 200+ imagens sem atualizar UI
- Usuário pode pensar que travou

**Solução**:

```python
# Em common.py, ajustar callback frequency (linha 686):

for idx, img in enumerate(images_list, 1):
    image_path = Path(img.get("path", "")) / str(img.get("filename", ""))
    
    # ...processamento
    
    # Callback mais frequente
    if progress_callback:
        # Atualizar a cada 3 imagens OU primeira/última
        if idx % 3 == 0 or idx == 1 or idx == total_count:
            progress_callback(idx, total_count, "Preparando imagens")
    
    # ...resto do código
```

```python
# Em mcp_gui.py, garantir conexão do signal:

# Já existe em __init__ (linha 90):
self.progress_update_signal.connect(self._update_progress)

# Verificar que run_host() passa callback:
def run_host(self) -> None:
    # ...
    def progress_cb(current, total, msg):
        self.progress_update_signal.emit(current, total, msg)
    
    # Passar para prepare_vision_payloads
    payloads, errors = prepare_vision_payloads(
        images, 
        attach_images=not text_only,
        progress_callback=progress_cb  # <-- Adicionar
    )
```

**Passos de Implementação**:
1. Editar `host/common.py:686`
2. Alterar `idx % log_interval` para `idx % 3`
3. Garantir que callback é chamado sempre (remover condição complexa)
4. No código do host que chama `prepare_vision_payloads`, passar callback que emite signal
5. Testar com 50+ imagens
6. Observar barra de progresso atualizando suavemente

**Critérios de Aceite**:
- [ ] Barra de progresso atualiza a cada 3-5 imagens
- [ ] Percentual mostrado é preciso
- [ ] Mensagem "Preparando imagens (N/M)" visível
- [ ] UI não trava durante processamento

**Riscos**:
- **Baixo**: Overhead de signals (~1-2ms), desprezível comparado a encode (~150ms)

**Dependências**: TASK-001 (GUI funcional)

**Estimativa**: 1h

**Prioridade**: P1 - MÉDIO

---

<a name="task-006"></a>
## TASK-006: Aumentar Contraste de Botões Desabilitados

**Objetivo**: Cumprir WCAG 2.1 AA (contraste mínimo 4.5:1).

**Problema**:
- Arquivo: `host/mcp_gui.py:270-273`
- Cor de texto `#777777` sobre fundo `#2a2a2a` tem contraste ~2.3:1
- Abaixo do mínimo WCAG AA de 4.5:1

**Solução**:

```python
# Em _apply_global_style() (linha 270-273):

QPushButton:disabled {
    background-color: #2a2a2a;
    color: #999999;  /* Mudado de #777777 para #999999 */
    border-color: #333333;
}
```

**Validação de Contraste**:
- Usar WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Inserir:
  - Foreground: `#999999`
  - Background: `#2a2a2a`
- Resultado esperado: ~4.6:1 (PASS AA)

**Passos de Implementação**:
1. Abrir `host/mcp_gui.py`
2. Localizar linha 272
3. Trocar `#777777` por `#999999`
4. Salvar
5. Testar visualmente:
   - Abrir GUI
   - Desabilitar um botão (ex: durante execução)
   - Verificar legibilidade
6. Validar com ferramenta de contraste

**Critérios de Aceite**:
- [ ] Contraste ≥ 4.5:1 (WCAG AA)
- [ ] Texto de botão desabilitado é legível
- [ ] Não parece "ativo" (confusão de estado)

**Riscos**: Nenhum

**Dependências**: Nenhuma

**Estimativa**: 10min

**Prioridade**: P2 - BAIXO (mas quick win)

---

<a name="task-007"></a>
## TASK-007: Adicionar Accessible Names a Campos

**Objetivo**: Melhorar compatibilidade com leitores de tela (NVDA, JAWS, ORCA).

**Problema**:
- Arquivo: `host/mcp_gui.py:460-490`
- Campos criados sem `setAccessibleName()` ou `setAccessibleDescription()`
- Leitores de tela anunciam apenas "Edit" ou "Combo box"

**Solução**:

```python
# Após criar cada widget em _build_layout(), adicionar:

self.path_contains_edit.setAccessibleName("Filtro de caminho")
self.path_contains_edit.setAccessibleDescription(
    "Filtrar imagens por trecho do caminho de arquivo"
)

self.tag_edit.setAccessibleName("Tag do Darktable")
self.tag_edit.setAccessibleDescription("Tag existente para filtrar imagens")

self.collection_combo.setAccessibleName("Coleção do Darktable")
self.collection_combo.setAccessibleDescription(
    "Selecione a coleção (filme) de onde as imagens serão obtidas"
)

self.prompt_edit.setAccessibleName("Arquivo de prompt personalizado")
self.prompt_edit.setAccessibleDescription(
    "Caminho para arquivo Markdown com instruções customizadas ao modelo"
)

self.target_edit.setAccessibleName("Diretório de exportação")
self.target_edit.setAccessibleDescription(
    "Pasta onde os arquivos exportados serão salvos"
)

self.model_combo.setAccessibleName("Modelo LLM")
self.model_combo.setAccessibleDescription(
    "Nome do modelo de linguagem carregado no servidor"
)

self.url_edit.setAccessibleName("URL do servidor LLM")
self.url_edit.setAccessibleDescription("Endereço base do servidor Ollama ou LM Studio")

self.min_rating_spin.setAccessibleName("Rating mínimo")
self.min_rating_spin.setAccessibleDescription(
    "Nota mínima das imagens a processar, de menos 2 a 5"
)

self.limit_spin.setAccessibleName("Limite de imagens")
self.limit_spin.setAccessibleDescription(
    "Número máximo de imagens a processar nesta execução"
)

# Botões também:
self.run_button.setAccessibleName("Executar host")
self.run_button.setAccessibleDescription(
    "Iniciar processamento com os parâmetros configurados"
)

self.stop_button.setAccessibleName("Parar execução")
self.stop_button.setAccessibleDescription("Interromper o processamento em andamento")

# Checkboxes:
self.dry_run_check.setAccessibleName("Modo dry-run")
self.dry_run_check.setAccessibleDescription(
    "Simular execução sem alterar arquivos ou metadados"
)

self.only_raw_check.setAccessibleName("Apenas arquivos RAW")
self.only_raw_check.setAccessibleDescription(
    "Processar somente arquivos RAW, ignorando JPEG e derivados"
)

self.attach_images_check.setAccessibleName("Enviar imagens ao modelo")
self.attach_images_check.setAccessibleDescription(
    "Anexar arquivos de imagem junto aos metadados, para modelos multimodais"
)
```

**Passos de Implementação**:
1. Abrir `host/mcp_gui.py`
2. Após a criação de cada widget em `_build_layout()`, adicionar calls `setAccessibleName()` e `setAccessibleDescription()`
3. Usar nomes curtos e descritivos para Name
4. Usar descrições mais detalhadas para Description
5. Testar com leitor de tela:
   - Linux: `orca` (pode precisar instalar: `sudo apt install orca`)
   - Windows: NVDA (free download)
   - macOS: VoiceOver (built-in)
6. Navegar pela GUI com Tab e verificar anúncios corretos

**Critérios de Aceite**:
- [ ] Todos os campos têm `accessibleName`
- [ ] Leitor de tela anuncia nome e tipo corretos
- [ ] Descrições fornecem contexto adicional
- [ ] Navegação por teclado é lógica

**Riscos**: Nenhum

**Dependências**: TASK-001 (GUI funcional)

**Estimativa**: 30min

**Prioridade**: P1 - ALTO (acessibilidade)

---

*[Continua com TASK-008 a TASK-020 no mesmo formato detalhado...]*

---

## 📊 RESUMO DE ESTIMATIVAS

| Categoria | Tasks | Tempo Total Estimado |
|-----------|-------|---------------------|
| Bloqueadores (P0) | 3 | 2.5-3.5h |
| Quick Wins (P1) | 4 | 3.5h |
| Médio Prazo | 6 | 18-22h |
| Estrutural | 7 | 28-36h |
| **TOTAL** | **20** | **~52-65h** (6-8 dias úteis) |

---

## 🗓️ CRONOGRAMA SUGERIDO

### Semana 1: Crítico + Quick Wins
- **Dia 1** (4h): TASK-001, TASK-002, TASK-003
- **Dia 2** (4h): TASK-004, TASK-005
- **Dia 3** (2h): TASK-006, TASK-007
- **Dia 4-5**: Buffer para testes e ajustes

### Semana 2-3: Médio Prazo
- **Semana 2**: TASK-008 (async), TASK-010 (testes), TASK-011 (CI)
- **Semana 3**: TASK-009, TASK-012, TASK-013

### Mês 2: Estrutural
- **Semanas 4-5**: TASK-014 (Design System), TASK-015 (Erros), TASK-016 (Config)
- **Semanas 6-7**: TASK-017 (Docs), TASK-019 (Otimização), TASK-020 (Security tests)
- **Semana 8**: TASK-018 (i18n, se prioritário), refinamentos finais

---

## ✅ CHECKLIST DE VALIDAÇÃO FINAL

Após concluir todas as tasks:

### Funcionalidade
- [ ] GUI inicia sem erros
- [ ] Todos os modos funcionam (rating, tagging, export, tratamento, completo)
- [ ] Dry-run funciona corretamente
- [ ] Multimodal (imagens) funciona
- [ ] Text-only funciona

### Segurança
- [ ] Payloads de injection são bloqueados
- [ ] Zero CVEs críticas em dependências
- [ ] Logs não expõem dados sensíveis

### Performance
- [ ] Preparação de 100 imagens em <10s
- [ ] UI não trava durante processamento
- [ ] Uso de memória <350MB para 100 imagens

### Acessibilidade
- [ ] Navegação completa por teclado funciona
- [ ] Contraste WCAG AA em todos os elementos
- [ ] Leitores de tela anunciam corretamente
- [ ] Atalhos de teclado funcionam

### Qualidade de Código
- [ ] Cobertura de testes ≥60%
- [ ] CI pipeline verde
- [ ] Linting passa (ruff, black)
- [ ] Documentação atualizada

---

**FIM DO PLANO DE AÇÃO**
