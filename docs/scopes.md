# Scopes disponíveis

O Sabiá expõe os dados do usuário por meio de **scopes OAuth2**. Ao solicitar um scope durante a
autenticação, você recebe os campos correspondentes na resposta de `POST /api/perfil/dados/`, que
é chamado automaticamente pelo `SabiaOAuth2Client.get_user_info()`.

Configure os scopes desejados via `SABIA_SCOPES` nas suas settings:

```python
SABIA_SCOPES = ["cpf", "email", "dados_publicos", "receita_federal", "cnes",
                "experiencia_profissional", "formacao_academica", "cursos_cdp"]
```

!!! warning "Autorização por aplicação"
    Cada scope precisa estar habilitado para a sua aplicação no painel do Sabiá. Solicitar um scope
    não autorizado retorna um erro ou simplesmente omite o campo da resposta.

---

## Scopes obrigatórios

Estes scopes estão sempre presentes independentemente do que for solicitado.

### `dados_publicos`

Perfil público — **sempre retornado**, mesmo que não listado em `SABIA_SCOPES`.

| Campo   | Tipo         | Exemplo                                             |
|---------|--------------|-----------------------------------------------------|
| `name`  | string       | `"Maria Silva"`                                     |
| `avatar`| string (URL) | `"https://login.sabia.ufrn.br/media/avatars/1.jpg"` |

### `cpf`

| Campo | Tipo   | Exemplo         |
|-------|--------|-----------------|
| `cpf` | string | `"12345678900"` |

### `email`

| Campo   | Tipo   | Exemplo                    |
|---------|--------|----------------------------|
| `email` | string | `"maria.silva@email.com"`  |

**Exemplo de resposta com os scopes obrigatórios:**

```json
{
  "name": "Maria Silva",
  "avatar": "https://login.sabia.ufrn.br/media/avatars/1.jpg",
  "cpf": "12345678900",
  "email": "maria.silva@email.com"
}
```

---

## Scopes opcionais

### `receita_federal`

Dados complementares vindos da Receita Federal. Requer que o usuário tenha validado seu cadastro
via CPF. Estes dados são cacheados por até **5 anos** no servidor do Sabiá.

Se o usuário não tiver validado, retorna:
```json
{ "receita_federal": { "erro": "Dados deste usuário não foram validados pela Receita Federal." } }
```

Campos disponíveis (nomes originais do XML do webservice da Receita Federal):

| Campo           | Tipo                | Exemplo              |
|-----------------|---------------------|----------------------|
| `nome`          | string              | `"MARIA SILVA"`      |
| `dtNascimento`  | string (AAAA-MM-DD) | `"1990-05-20"` |
| `sexo`          | string              | `"F"`                |
| `mae`           | string              | `"ANA SILVA"`        |
| `noMunicipio`   | string              | `"NATAL"`            |
| `uf`            | string              | `"RN"`               |

**Exemplo de resposta:**

```json
{
  "receita_federal": {
    "nome": "MARIA SILVA",
    "dtNascimento": "1990-05-20",
    "sexo": "F",
    "mae": "ANA SILVA",
    "noMunicipio": "NATAL",
    "uf": "RN"
  }
}
```

---

### `cnes`

Perfil profissional completo a partir do CNES (Cadastro Nacional de Estabelecimentos de Saúde).
Cacheado por **7 dias** no servidor do Sabiá.

Retorna um objeto com a chave `vinculos`, que é uma lista de vínculos profissionais:

| Campo     | Tipo   | Exemplo               |
|-----------|--------|-----------------------|
| `cnes`    | string | `"2408102"`           |
| `noFant`  | string | `"HOSPITAL DAS CLÍNICAS"` |
| `coMun`   | string | `"240810"`            |
| `noCBO`   | string | `"Médico Clínico"`    |

**Exemplo de resposta:**

```json
{
  "cnes": {
    "vinculos": [
      {
        "cnes": "2408102",
        "noFant": "HOSPITAL DAS CLÍNICAS",
        "coMun": "240810",
        "noCBO": "Médico Clínico"
      }
    ]
  }
}
```

---

### `experiencia_profissional`

Experiências profissionais cadastradas pelo próprio usuário no Sabiá (complementadas
automaticamente pelo CNES na primeira autenticação com o scope `cnes`). Dados **sempre frescos**
do banco de dados.

Retorna uma **lista** de objetos:

| Campo          | Tipo             | Exemplo                    |
|----------------|------------------|----------------------------|
| `estabelecimento` | string        | `"Hospital das Clínicas"`  |
| `profissao`    | string           | `"Médico Clínico"`         |
| `data_inicio`  | datetime / null  | `"2020-01-15T00:00:00"`    |
| `data_fim`     | datetime / null  | `null`                     |
| `municipio`    | string           | `"Natal - RN"`             |
| `descricao`    | string           | `"Plantões na UTI"`        |

**Exemplo de resposta:**

```json
{
  "experiencia_profissional": [
    {
      "estabelecimento": "Hospital das Clínicas",
      "profissao": "Médico Clínico",
      "data_inicio": "2020-01-15T00:00:00",
      "data_fim": null,
      "municipio": "Natal - RN",
      "descricao": ""
    }
  ]
}
```

Se o usuário não tiver experiências cadastradas:
```json
{ "experiencia_profissional": { "erro": "Nenhuma experiência profissional cadastrada." } }
```

---

### `formacao_academica`

Formação acadêmica cadastrada pelo usuário. Dados **sempre frescos** do banco de dados.

Retorna uma **lista** de objetos:

| Campo            | Tipo         | Exemplo           |
|------------------|--------------|-------------------|
| `instituicao`    | string       | `"UFRN"`          |
| `curso`          | string       | `"Medicina"`      |
| `data_inicio`    | date         | `"2010-03-01"`    |
| `data_fim`       | date / null  | `"2016-12-01"`    |
| `municipio`      | string       | `"Natal - RN"`    |
| `descricao`      | string       | `""`              |
| `grau_formacao`  | string       | `"Graduação"`     |

Valores possíveis para `grau_formacao`:

| Código | Descrição            |
|--------|----------------------|
| `GRA`  | Graduação            |
| `ESP`  | Especialização       |
| `MES`  | Mestrado             |
| `MEP`  | Mestrado Profissional|
| `DTR`  | Doutorado            |
| `PDR`  | Pós-Doutorado        |
| `ENF`  | Ensino Fundamental   |
| `ENM`  | Ensino Médio         |
| `EPT`  | Ed. Prof. Técnica    |
| `ERM`  | Residência Médica    |

**Exemplo de resposta:**

```json
{
  "formacao_academica": [
    {
      "instituicao": "UFRN",
      "curso": "Medicina",
      "data_inicio": "2010-03-01",
      "data_fim": "2016-12-01",
      "municipio": "Natal - RN",
      "descricao": "",
      "grau_formacao": "Graduação"
    }
  ]
}
```

---

### `cursos_cdp`

Cursos realizados na Comunidade de Práticas (CDP). Cacheado por **24 horas** no servidor do Sabiá.

Retorna um objeto com `total` e `data`:

| Campo      | Tipo   | Exemplo              |
|------------|--------|----------------------|
| `total`    | int    | `3`                  |
| `data`     | array  | lista de cursos      |

Cada curso em `data`:

| Campo       | Tipo   | Exemplo                                  |
|-------------|--------|------------------------------------------|
| `title`     | string | `"Humanização em Saúde"`                 |
| `descricao` | string | `"Curso sobre humanização..."`           |
| `vinculo`   | string | `"CDP"`                                  |
| `link`      | string | `"https://cdp.saude.gov.br/cursos/123"`  |
| `status`    | string | `"Concluído"`                            |
| `nid`       | int    | `123`                                    |
| `created`   | string | `"2023-06-01"`                           |
| `type`      | string | `"course"`                               |

**Exemplo de resposta:**

```json
{
  "cursos_cdp": {
    "total": 1,
    "data": [
      {
        "title": "Humanização em Saúde",
        "descricao": "Curso sobre humanização no atendimento.",
        "vinculo": "CDP",
        "link": "https://cdp.saude.gov.br/cursos/123",
        "status": "Concluído",
        "nid": 123,
        "created": "2023-06-01",
        "type": "course"
      }
    ]
  }
}
```

---

## Resumo dos scopes

| Scope                     | Obrigatório | Cache      | Fonte              |
|---------------------------|-------------|------------|--------------------|
| `dados_publicos`          | Sim         | Nenhum     | Banco do Sabiá     |
| `cpf`                     | Sim         | Nenhum     | Banco do Sabiá     |
| `email`                   | Sim         | Nenhum     | Banco do Sabiá     |
| `receita_federal`         | Não         | 5 anos     | Webservice RF      |
| `cnes`                    | Não         | 7 dias     | API do CNES        |
| `experiencia_profissional`| Não         | Nenhum     | Banco do Sabiá     |
| `formacao_academica`      | Não         | Nenhum     | Banco do Sabiá     |
| `cursos_cdp`              | Não         | 24 horas   | API da CDP         |

---

## Mapeando campos para o seu model (`SABIA_USER_ATTR_MAP`)

Após a autenticação, os dados retornados pelo Sabiá precisam ser salvos no seu `AUTH_USER_MODEL`.
Use `SABIA_USER_ATTR_MAP` nas settings para declarar esse mapeamento.

A convenção é `{campo_do_model: campo_do_sabiá}`:

```python
SABIA_USER_ATTR_MAP = {
    "username": "cpf",
    "email":    "email",
}
```

### Dividindo o nome em dois campos

Use uma **tupla** como chave para dividir o valor do Sabiá no primeiro espaço:

```python
SABIA_USER_ATTR_MAP = {
    "username": "cpf",
    "email":    "email",
    ("first_name", "last_name"): "name",   # "Maria Silva Santos" → "Maria" + "Silva Santos"
}
```

### Acessando campos de scopes opcionais (objeto)

O scope `receita_federal` retorna um **objeto** (dict), portanto seus campos individuais podem
ser extraídos com notação de ponto:

```python
SABIA_SCOPES = ["cpf", "email", "receita_federal"]

SABIA_USER_ATTR_MAP = {
    "username":         "cpf",
    "email":            "email",
    ("first_name", "last_name"): "name",
    "nome_mae":         "receita_federal.mae",
    "sexo":             "receita_federal.sexo",
    "data_nascimento":  "receita_federal.dtNascimento",
}
```

Se o scope não estiver disponível (usuário não validado, erro de API, etc.), os campos
correspondentes são simplesmente ignorados — o usuário ainda é criado com os demais atributos.

!!! note "Scopes que retornam listas"
    Os scopes `cnes`, `experiencia_profissional`, `formacao_academica` e `cursos_cdp` retornam
    **listas de objetos**, não um objeto único. A notação de ponto não se aplica a eles; para
    persistir esses dados, use o campo virtual `fulljson` descrito abaixo.

### Salvando o JSON completo (`fulljson`)

Use a chave especial `"fulljson"` para mapear o JSON inteiro retornado pelo Sabiá para um campo
do seu model (por exemplo, um `JSONField`):

```python
SABIA_USER_ATTR_MAP = {
    "username":     "cpf",
    "email":        "email",
    "perfil_json":  "fulljson",   # salva todo o payload em um JSONField
}
```

Isso é especialmente útil quando você usa scopes como `cnes`, `experiencia_profissional` ou
`cursos_cdp` e quer persistir os dados brutos sem precisar ter um campo para cada atributo.

### Exemplo: model com campo `cpf` nativo e nome único

```python
# settings.py
SABIA_USER_LOOKUP_FIELD = "cpf"   # campo usado no get_or_create

SABIA_USER_ATTR_MAP = {
    "cpf":   "cpf",
    "email": "email",
    "nome":  "name",   # nome completo em um único campo
}
```

Consulte [Configuration](configuration.md) para a referência completa de todas as opções.
