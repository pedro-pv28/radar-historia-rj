# Radar História RJ

Site independente, responsivo e sem necessidade de backend pago para acompanhar **concursos e processos seletivos para professores de História, historiadores e vagas ligadas ao patrimônio cultural no estado do Rio de Janeiro**.

## O que está pronto

- Catálogo inicial de **11 oportunidades/linhas de seleção** mapeadas em **13/11/2026**, com links para portais institucionais e banca oficial. Inclui Italva, Sumidouro, Porciúncula, Vassouras, UERJ, UFRJ e UFRRJ.
- Filtros por cargo, região, município, tipo, inscrição online/presencial e situação; busca e ordenação.
- Status das inscrições calculado no horário de Brasília: abertas, previstas, vencidas, ou em apuração.
- Agenda de prazos, favoritos salvos no próprio navegador, exportação CSV e evento `.ics` para calendário.
- Lista separada de achados automáticos **sem confirmação**, evitando afirmar que notícias ou links antigos são vagas abertas.

## Abrir agora

Dê dois cliques em `index.html` no computador. O site funciona **offline com o catálogo inicial**. O botão *Atualizar* precisa de hospedagem para ler o JSON do servidor; não busca editais diretamente do navegador (restrições de CORS dos órgãos).

## Publicar gratuitamente e ligar a verificação diária

1. Crie um repositório público no GitHub (por exemplo `radar-historia-rj`) e **envie o conteúdo da pasta**, mantendo `index.html` na raiz, `data/`, `scripts/` e `.github/`.
2. Em **Settings → Pages → Build and deployment**, selecione **GitHub Actions** como fonte de publicação; salve. Seu endereço será semelhante a `https://SEU-USUARIO.github.io/radar-historia-rj/` (substitua pelo usuário e nome reais).
3. Em **Settings → Actions → General**, habilite Actions e, se necessário, permita que o workflow grave no repositório. O arquivo incluído já declara as permissões de `contents`, `pages` e `id-token`.
4. Em **Actions → Atualizar e publicar Radar História RJ → Run workflow**, execute a primeira publicação, ou simplesmente envie os arquivos à branch `main` (o workflow também roda no `push`). As próximas execuções ficam agendadas diariamente (em torno de 8h05 em Brasília, sujeitas a atrasos e suspensões da plataforma).
5. A atualização escreve em `data/opportunities.json`, publica o site via GitHub Pages e o navegador busca o catálogo na abertura, no botão *Atualizar* e periodicamente enquanto a página estiver aberta.

> **Importante:** a busca automática só cria pistas com status **Em apuração**. A publicação de uma vaga como **confirmada**, com datas, requisitos e vagas, depende de revisar o edital. O robô não determina automaticamente se uma inscrição está realmente aberta. A automação não envia e-mails nem notificações push com o navegador fechado.

## Conferir uma descoberta e promover à lista principal

Abra `data/opportunities.json`, copie o registro desejado de `discovered` para `opportunities`, marque `origin: "verificado"` após a checagem, corrija `org`, `city`, `region`, `title`, `type`, `modality`, `start`, `end`, `deadlineTime`, `slots`, `url`, `sourceName` e `verifiedAt`, e apague o registro de `discovered`. Faça um commit; a página refletirá a mudança. **Não complete campos por suposição.**

### Modelo dos dados

- `opportunities`: concursos com dados revistos manualmente. `origin=verificado` indica confirmação da publicação, **não** elegibilidade individual.
- `origin=correlata`: processo real que pode abranger História, mas precisa de confirmação do componente curricular.
- `discovered` e `origin=descoberta`: links capturados pela varredura, sem validação de cargo, requisitos ou datas.
- `meta.verifiedAt`: data da última curadoria manual (não é alterada pelo robô).
- `meta.automaticScanAt`: data da última execução com pelo menos uma fonte acessível.

## Rodar a varredura no seu computador

```bash
python -m pip install -r requirements.txt
python scripts/update_opportunities.py
python -m http.server 8000
```

Depois acesse `http://localhost:8000/`.

## Limitações e transparência

- As páginas oficiais podem mudar estrutura ou bloquear a leitura automatizada; uma varredura não substitui acompanhamento humano.
- Uma publicação sobre "História" não significa, por si só, uma vaga destinada a um licenciado ou bacharel na área.
- Alguns concursos de magistério superior podem exigir pós-graduação; avalie o edital e sua situação acadêmica.
- Favoritos ficam armazenados **localmente no navegador** e não sincronizam entre aparelhos.
- Não existe cadastro de usuário, backend de notificações nem hospedagem criada automaticamente por este pacote.

**Projeto independente**, sem vínculo com prefeituras, universidades ou bancas organizadoras.
