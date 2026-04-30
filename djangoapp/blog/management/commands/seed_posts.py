import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from blog.models import Category, Post, Tag


POST_IDEAS = [
    {
        "category": "Django",
        "tags": ["Python", "Django", "Backend"],
        "title": "Como organizar views em projetos Django",
        "excerpt": "Boas praticas para manter views legiveis, pequenas e faceis de testar.",
        "paragraphs": [
            "Organizar views em Django fica mais simples quando cada funcao tem uma responsabilidade clara. A view deve buscar dados, aplicar regras de apresentacao e entregar o contexto ao template.",
            "Quando a regra comeca a crescer demais, uma boa saida e mover parte da logica para managers, services ou metodos do proprio model. Isso evita arquivos enormes e facilita a manutencao.",
            "Outro ponto importante e padronizar nomes de contexto e templates. Pequenas consistencias reduzem o esforco de entender o projeto depois de algumas semanas longe do codigo.",
        ],
    },
    {
        "category": "Python",
        "tags": ["Python", "Produtividade", "Codigo Limpo"],
        "title": "Pequenos habitos que melhoram seu codigo Python",
        "excerpt": "Alguns cuidados simples deixam o codigo mais claro sem criar complexidade extra.",
        "paragraphs": [
            "Codigo Python costuma ficar melhor quando priorizamos nomes explicitos, funcoes pequenas e retornos simples. Nem sempre e preciso criar uma abstracao nova para resolver um problema.",
            "Uma pratica util e ler o codigo como se fosse texto. Se a leitura trava em muitos detalhes ao mesmo tempo, talvez exista uma funcao escondida ali esperando para nascer.",
            "Ferramentas como formatadores e linters tambem ajudam, mas elas nao substituem criterio. O objetivo e comunicar intencao com clareza.",
        ],
    },
    {
        "category": "Frontend",
        "tags": ["CSS", "Layout", "Responsivo"],
        "title": "Como evitar layouts comprimidos no CSS",
        "excerpt": "Entenda como max-width, padding e containers afetam a leitura de uma pagina.",
        "paragraphs": [
            "Um layout pode parecer comprimido quando o max-width do container e pequeno demais para o tipo de conteudo. Em textos longos, a largura precisa equilibrar conforto de leitura e aproveitamento de tela.",
            "Tambem vale observar se existe padding excessivo dentro do container. Em telas menores, esse padding pode tomar espaco demais e reduzir a area util do conteudo.",
            "Uma boa estrategia e usar variaveis de largura para cada tipo de tela. Assim, posts, grids e cabecalhos podem ter proporcoes diferentes sem conflito.",
        ],
    },
    {
        "category": "Banco de Dados",
        "tags": ["Django ORM", "Banco de Dados", "Performance"],
        "title": "Quando usar select_related no Django ORM",
        "excerpt": "Uma explicacao pratica sobre consultas relacionadas e reducao de queries.",
        "paragraphs": [
            "O select_related e util quando voce precisa carregar objetos ligados por ForeignKey ou OneToOne. Ele faz joins no banco e evita consultas repetidas para cada item da lista.",
            "Em uma lista de posts, por exemplo, carregar a categoria junto com o post pode melhorar bastante a performance quando a categoria aparece no template.",
            "Mesmo assim, vale medir antes de otimizar. O Django Debug Toolbar pode mostrar quantas queries uma pagina executa e ajudar a encontrar gargalos reais.",
        ],
    },
    {
        "category": "Deploy",
        "tags": ["Deploy", "Docker", "Django"],
        "title": "Preparando um projeto Django para deploy",
        "excerpt": "Pontos importantes antes de colocar uma aplicacao Django em producao.",
        "paragraphs": [
            "Antes do deploy, revise configuracoes como DEBUG, ALLOWED_HOSTS, variaveis de ambiente e arquivos estaticos. Esses detalhes costumam separar um ambiente local de uma aplicacao pronta para usuarios.",
            "Tambem e importante cuidar do banco, das migracoes e da coleta de arquivos estaticos. Um processo previsivel reduz surpresas na hora de atualizar o projeto.",
            "Com Docker, o ideal e deixar claro o papel de cada servico. Aplicacao, banco e proxy devem ter responsabilidades bem separadas.",
        ],
    },
    {
        "category": "Testes",
        "tags": ["Testes", "Django", "Qualidade"],
        "title": "Primeiros testes para um blog Django",
        "excerpt": "Ideias de testes simples para validar posts, rotas e paginas publicas.",
        "paragraphs": [
            "Um bom comeco e testar se a pagina inicial responde corretamente e exibe apenas posts publicados. Esse tipo de teste protege uma regra importante do blog.",
            "Depois, vale testar a pagina individual do post, categorias e autores. Esses pontos costumam quebrar quando slugs, filtros ou relacionamentos mudam.",
            "Testes pequenos funcionam como uma rede de seguranca. Eles nao precisam cobrir tudo no inicio, mas devem cobrir o comportamento principal.",
        ],
    },
    {
        "category": "Automacao",
        "tags": ["Scripts", "Django", "Automacao"],
        "title": "Criando comandos customizados no Django",
        "excerpt": "Aprenda quando usar management commands para automatizar tarefas do projeto.",
        "paragraphs": [
            "Management commands sao uma forma elegante de automatizar tarefas dentro do proprio Django. Eles carregam as configuracoes do projeto e permitem usar os models normalmente.",
            "Esse recurso e perfeito para popular dados, limpar registros temporarios, gerar relatorios ou executar rotinas administrativas.",
            "A vantagem sobre scripts soltos e que o comando fica versionado, documentado pelo proprio codigo e facil de rodar por qualquer pessoa do time.",
        ],
    },
    {
        "category": "Conteudo",
        "tags": ["Blog", "Escrita", "Conteudo"],
        "title": "Como escrever posts tecnicos mais claros",
        "excerpt": "Estruture textos tecnicos com exemplos, contexto e conclusoes objetivas.",
        "paragraphs": [
            "Um bom post tecnico costuma comecar explicando o problema antes da solucao. Isso ajuda o leitor a entender por que aquele assunto importa.",
            "Exemplos pequenos tambem fazem diferenca. Eles transformam conceitos abstratos em algo que o leitor pode testar e adaptar.",
            "No fim, uma conclusao curta com os principais aprendizados ajuda a fixar a ideia sem alongar demais o texto.",
        ],
    },
]


class Command(BaseCommand):
    help = "Cria posts diferentes para popular o blog durante o desenvolvimento."

    def add_arguments(self, parser):
        parser.add_argument(
            "--total",
            type=int,
            default=12,
            help="Quantidade de posts que serao criados.",
        )
        parser.add_argument(
            "--author",
            type=str,
            default="admin",
            help="Username do autor dos posts.",
        )

    def handle(self, *args, **options):
        total = options["total"]
        username = options["author"]

        author, _ = User.objects.get_or_create(
            username=username,
            defaults={
                "email": f"{username}@example.com",
                "is_staff": True,
            },
        )

        created_posts = 0

        for index in range(total):
            idea = POST_IDEAS[index % len(POST_IDEAS)]
            cycle = index // len(POST_IDEAS)
            suffix = f" #{cycle + 1}" if cycle else ""
            title = f"{idea['title']}{suffix}"

            category, _ = Category.objects.get_or_create(name=idea["category"])
            tags = [
                Tag.objects.get_or_create(name=tag_name)[0]
                for tag_name in idea["tags"]
            ]

            shuffled_paragraphs = idea["paragraphs"].copy()
            random.shuffle(shuffled_paragraphs)
            content = "\n".join(
                f"<p>{paragraph}</p>" for paragraph in shuffled_paragraphs
            )

            post, was_created = Post.objects.get_or_create(
                title=title,
                defaults={
                    "excerpt": idea["excerpt"],
                    "content": content,
                    "is_published": True,
                    "created_by": author,
                    "updated_by": author,
                    "category": category,
                },
            )

            if was_created:
                post.tags.set(tags)
                created_posts += 1

        self.stdout.write(
            self.style.SUCCESS(f"{created_posts} posts diferentes foram criados.")
        )
