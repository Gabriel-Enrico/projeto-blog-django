# Blog Django

Projeto de blog feito com Django, PostgreSQL, Docker e django-summernote.

Este README tambem serve como contexto compacto para agentes de IA entenderem o projeto sem precisar reler todos os arquivos.

## Contexto rapido para agentes de IA

- Projeto Django fica em `djangoapp/`.
- App principal do blog: `djangoapp/blog/`.
- App de configuracao global do site: `djangoapp/site_setup/`.
- Banco usado pelo Docker: PostgreSQL.
- Editor rico usado no admin: `django-summernote`.
- Templates do blog ficam em `djangoapp/blog/templates/blog/`.
- CSS principal fica em `djangoapp/blog/static/blog/css/styles.css`.
- Rotas publicas principais ficam em `djangoapp/blog/urls.py`.
- Models principais ficam em `djangoapp/blog/models.py` e `djangoapp/site_setup/models.py`.
- O projeto usa context processor para disponibilizar `site_setup` em todos os templates.
- Posts publicados sao filtrados por `Post.objects.get_published()`.
- Views publicas retornam `Http404` quando autor, categoria, tag, pagina ou post nao existem.
- Titulos HTML usam `page_title` + `site_setup.title` em `_head.html`.
- Busca publica existe em `/search/` e pesquisa em titulo, resumo e conteudo.
- Slugs sao gerados automaticamente com sufixo aleatorio por `utils.rands.slugify_new`.
- Imagens de posts e favicon sao redimensionados automaticamente ao salvar.
- Existe comando de seed em `djangoapp/blog/management/commands/seed_posts.py`.

## Como rodar com Docker

Subir aplicacao e banco:

```bash
docker compose up --build
```

A aplicacao fica em:

```txt
http://127.0.0.1:8000/
```

Admin:

```txt
http://127.0.0.1:8000/admin/
```

Rodar comandos Django dentro do container:

```bash
docker compose exec djangoapp python manage.py <comando>
```

Exemplos:

```bash
docker compose exec djangoapp python manage.py createsuperuser
docker compose exec djangoapp python manage.py migrate
docker compose exec djangoapp python manage.py collectstatic --noinput
docker compose exec djangoapp python manage.py seed_posts --total 20
```

## Variaveis de ambiente

O Docker usa `dotenv_files/.env`.

Variaveis esperadas:

```txt
SECRET_KEY
DEBUG
ALLOWED_HOSTS
DB_ENGINE
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
```

Em desenvolvimento, `POSTGRES_HOST` normalmente aponta para o servico `psql` do `docker-compose.yaml`.

## Estrutura importante

```txt
.
├── Dockerfile
├── docker-compose.yaml
├── dotenv_files/.env
├── scripts/
│   ├── commands.sh
│   ├── wait_psql.sh
│   ├── makemigrations.sh
│   ├── migrate.sh
│   ├── collectstatic.sh
│   └── runserver.sh
└── djangoapp/
    ├── manage.py
    ├── project/
    │   ├── settings.py
    │   └── urls.py
    ├── blog/
    │   ├── models.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── admin.py
    │   ├── management/commands/seed_posts.py
    │   ├── static/blog/css/
    │   └── templates/blog/
    ├── site_setup/
    │   ├── models.py
    │   ├── admin.py
    │   └── context_processors.py
    └── utils/
        ├── images.py
        ├── model_validators.py
        └── rands.py
```

## Apps

### `blog`

Responsavel por posts, categorias, tags, paginas estaticas, rotas publicas do blog, templates e CSS.

### `site_setup`

Responsavel por configuracoes globais do site:

- titulo do site;
- descricao;
- exibicao de header;
- exibicao de menu;
- exibicao de busca;
- exibicao de descricao;
- exibicao de paginacao;
- exibicao de footer;
- favicon;
- links do menu.

O admin permite criar apenas um registro de `SiteSetup`, por causa de `SiteSetupAdmin.has_add_permission`.

## Models e regras de negocio

### `Post`

Campos principais:

- `title`: titulo do post, maximo de 65 caracteres.
- `slug`: unico, usado na URL publica.
- `excerpt`: resumo, maximo de 150 caracteres.
- `is_published`: controla se o post aparece publicamente.
- `content`: conteudo HTML/texto do post.
- `cover`: imagem de capa opcional.
- `cover_in_post_content`: define se a capa aparece dentro da pagina do post.
- `created_at`: preenchido automaticamente na criacao.
- `updated_at`: atualizado automaticamente a cada save.
- `created_by`: usuario autor, opcional.
- `updated_by`: usuario que editou, opcional.
- `category`: categoria opcional.
- `tags`: varias tags opcionais.

Regras:

- Se `slug` estiver vazio, ele e gerado automaticamente com `slugify_new(title, 4)`.
- `Post.objects.get_published()` retorna apenas posts com `is_published=True`, ordenados por `-pk`.
- `get_absolute_url()` retorna a URL do post se publicado; se nao publicado, retorna a home.
- Se a capa mudar, `resize_image(self.cover, 900)` redimensiona a imagem para largura maxima de 900px.
- No admin, `created_by` e definido ao criar e `updated_by` ao editar.
- Na view `post`, posts inexistentes ou nao publicados retornam `Http404`.
- O template `post.html` renderiza titulo, autor, data, categoria, resumo, conteudo HTML e tags reais do banco.

### `Category`

Campos:

- `name`;
- `slug`.

Regras:

- Se `slug` estiver vazio, ele e gerado automaticamente com `slugify_new(name, 4)`.
- Usada para filtrar posts em `/category/<slug>/`.

### `Tag`

Campos:

- `name`;
- `slug`.

Regras:

- Se `slug` estiver vazio, ele e gerado automaticamente com `slugify_new(name)`.
- Relacao many-to-many com `Post`.

### `Page`

Campos:

- `title`;
- `slug`;
- `is_published`;
- `content`.

Regras:

- Se `slug` estiver vazio, ele e gerado automaticamente com `slugify_new(title, 4)`.
- A rota `/page/<slug>/` busca apenas paginas com `is_published=True`.
- Paginas inexistentes ou nao publicadas retornam `Http404`.
- O template `page.html` renderiza `{{ page.title }}` e `{{ page.content|safe }}`.

### `PostAttachment`

Extende `django_summernote.models.AbstractAttachment`.

Regras:

- Se `name` estiver vazio, usa o nome do arquivo enviado.
- Se o arquivo mudar, redimensiona com largura maxima de 900px.
- Configurado em `SUMMERNOTE_CONFIG["attachment_model"]`.

### `SiteSetup`

Campos:

- `title`;
- `description`;
- `show_header`;
- `show_search`;
- `show_menu`;
- `show_description`;
- `show_pagination`;
- `show_footer`;
- `favicon`.

Regras:

- Disponibilizado globalmente nos templates como `site_setup`.
- O admin impede criar mais de um setup.
- O favicon deve ser PNG, validado por `validate_png`.
- Se o favicon mudar, e redimensionado para largura maxima de 32px.

### `MenuLink`

Campos:

- `text`;
- `url_or_path`;
- `new_tab`;
- `site_setup`.

Regras:

- Links sao exibidos no header se `site_setup.show_menu=True`.
- Se `new_tab=True`, o link abre com `target="_blank"`.

## Rotas

Rotas globais em `djangoapp/project/urls.py`:

```txt
/                 -> include blog.urls
/summernote/      -> django_summernote.urls
/admin/           -> Django admin
/media/...        -> servido apenas em DEBUG=True
```

Rotas do app `blog`:

```txt
/                         -> blog:index
/post/<slug:slug>/        -> blog:post
/page/<slug:slug>/        -> blog:page
/created_by/<int:pk>/     -> blog:created_by
/category/<slug:slug>/    -> blog:category
/tag/<slug:slug>/         -> blog:tag
/search/                  -> blog:search
```

## Views publicas

### `index`

- Busca `Post.objects.get_published().order_by("-pk")`.
- Pagina com `Paginator`.
- Usa `PER_PAGE = 9`.
- Renderiza `blog/pages/index.html`.
- Envia `page_title = "Home - "`.

### `created_by`

- Busca o usuario por `author_pk`.
- Se o usuario nao existir, retorna `Http404`.
- Filtra posts publicados por `created_by__pk=author_pk`.
- Monta o titulo com nome e sobrenome do usuario; se nao houver `first_name`, usa `username`.
- Usa paginacao.
- Renderiza `blog/pages/index.html`.

### `category`

- Filtra posts publicados por `category__slug=slug`.
- Usa paginacao.
- Se nao houver posts na categoria, retorna `Http404`.
- Monta `page_title` com o nome da categoria.
- Renderiza `blog/pages/index.html`.

### `tag`

- Filtra posts publicados por `tags__slug=slug`.
- Usa paginacao.
- Se nao houver posts na tag, retorna `Http404`.
- Monta `page_title` com o nome da primeira tag do primeiro post retornado.
- Renderiza `blog/pages/index.html`.

### `search`

- Le o parametro `search` da query string.
- Remove espacos extras com `.strip()`.
- Pesquisa em `title`, `excerpt` e `content` usando `icontains`.
- Limita o resultado aos primeiros `PER_PAGE` posts.
- Envia `search_value` para manter o campo de busca preenchido no header.
- Renderiza `blog/pages/index.html`.

### `post`

- Busca o primeiro post publicado com `slug`.
- Se nao encontrar post publicado, retorna `Http404`.
- Envia `page_title` com o titulo do post.
- Renderiza `blog/pages/post.html`.

O template `post.html` renderiza dados reais:

- capa, quando `post.cover` existe e `cover_in_post_content=True`;
- titulo;
- autor com link para `/created_by/<id>/`;
- data formatada;
- categoria com link para `/category/<slug>/`;
- resumo;
- conteudo com `{{ post.content|safe }}`;
- tags com links para `/tag/<slug>/`.

O template tambem carrega CodeMirror no bloco `additional_head` para destacar blocos de codigo usados no conteudo.

### `page`

- Busca `Page` publicada por `slug`.
- Se nao encontrar pagina publicada, retorna `Http404`.
- Envia `page_title` com o titulo da pagina.
- Renderiza `blog/pages/page.html`.

## Templates

Base:

- `blog/base.html`

Partials:

- `_head.html`: metatags, CSS e Font Awesome.
- `_header.html`: hero, menu e busca apontando para `blog:search`.
- `_pagination.html`: paginacao para objetos paginados.
- `_footer.html`: rodape e script para inicializar CodeMirror em blocos de codigo.
- `_post-card.html`: card de post na listagem.
- `_temp.html`: conteudo demonstrativo legado; nao e usado diretamente pelo `post.html` atual.

Paginas:

- `pages/index.html`: listagem de posts.
- `pages/post.html`: pagina interna do post.
- `pages/page.html`: pagina estatica.

## CSS e layout

CSS principal:

```txt
djangoapp/blog/static/blog/css/styles.css
```

CSS reset/remedy:

```txt
djangoapp/blog/static/blog/css/remedy.css
```

Variaveis importantes:

- `--mw-grid: 124rem`: largura maxima da grid/listagem.
- `--mw-post: 72rem`: largura estreita padrao.
- `--mw-single-post: 90rem`: largura especifica da pagina interna de post.

A pagina interna do post usa:

```css
.single-post .section-content-narrow {
  max-width: var(--mw-single-post);
}
```

## Comando para popular posts

Arquivo:

```txt
djangoapp/blog/management/commands/seed_posts.py
```

Uso:

```bash
docker compose exec djangoapp python manage.py seed_posts --total 20
```

Com autor especifico:

```bash
docker compose exec djangoapp python manage.py seed_posts --total 20 --author admin
```

Regras do comando:

- Cria usuario autor se nao existir.
- Cria categorias se nao existirem.
- Cria tags se nao existirem.
- Cria posts publicados.
- Evita duplicar posts com o mesmo titulo usando `get_or_create`.
- Gera conteudos variados a partir de temas predefinidos.

## Scripts do container

O `Dockerfile` executa `scripts/commands.sh`, que roda:

```txt
wait_psql.sh      -> espera Postgres ficar disponivel
migrate.sh        -> cria migracoes e aplica migracoes
collectstatic.sh  -> coleta arquivos estaticos
runserver.sh      -> inicia runserver em 0.0.0.0:8000
```

## Utilitarios

### `utils.rands`

- `random_letters(k=5)`: gera letras/numeros aleatorios.
- `slugify_new(text, k=5)`: cria slug com sufixo aleatorio.

### `utils.images`

- `resize_image(image_django, new_width=800, optimize=True, quality=60)`: redimensiona imagem no `MEDIA_ROOT`.

### `utils.model_validators`

- `validate_png(image)`: valida se arquivo termina com `.png`.

## Estado atual e pontos de atencao

- A busca existe, mas retorna no maximo `PER_PAGE` itens e nao usa `Paginator` na view `search`.
- `_temp.html` continua no projeto como conteudo demonstrativo, mas nao e mais usado diretamente pelo `post.html`.
- O footer ainda possui alguns textos e links fixos de exemplo.
- `site_setup` pode ser `None` se nenhum `SiteSetup` existir; templates assumem que ele existe.
- Ambiente local pode precisar de venv; pelo Docker, as dependencias sao instaladas automaticamente.

## Dependencias Python

Arquivo:

```txt
djangoapp/requirements.txt
```

Dependencias atuais:

```txt
django
psycopg2-binary
pillow
django-summernote>=0.8.20.0,<0.8.21
```
