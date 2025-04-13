# Student Page
#### Video Demo:  <URL HERE>
#### Description:
Projeto tem como finalidade ser uma página web direcionada à uma instituição de ensino, aonde é possível vizualizar as informações tanto como professor quanto aluno.
### Utilização
Inicie no terminal do projeto e execute o comando, que inicia o servidor para acessar a página:
```sh
   Flask run 
```

### Libraries Required

- ** Flask **
- ** mysql **
- ** Session **
- ** reportlab **
- ** os **
- ** datetime **
- ** itsdangerous**

### Tecnologias utilizadas
- HTML
- CSS
- PYTHON
- MYSQL

### Estrutura

O projeto foi feito com a utilização de git, para o gerenciamento de versões conforme o caminhar do desenvolvimento.

O código é dividido em 3 categorias, sendo elas:
As páginas principais, que normalmente portam a maior parte dos links para a mudança de rotas sendo caminhos para as funcionalidades; As páginas de acesso, páginas que possuem verificações e validações para acesso; Páginas de conteúdo, dedicados à alguma explicação ou informação, normalmente bem mais simples em comparação com as outras e páginas de conteúdo, das quais contém alguma funcionalidade específica.

- ** Estruturas principais **: 
    - **homepage.html** : Arquivo principal da página de raiz do site
    - **studantpage.html** : Arquivo principal da página de estudante
    - **teacherpage.html** : Arquivo principal da página do professor

- **Páginas de acesso **: 
    - **login.html** : Arquivo de acesso para o login
    - **register.html** : Arquivo de acesso para o cadastro
    - **recover.html** : Arquivo de acesso para recuperação de senha, mandando um email
    - **reset.html** : Arquivo de acesso para de fato fazer a troca de senha

- **Páginas de conteúdo **:     
    - **reports.html** : Arquivo de documentos pdf que serão gerados 
    - **editgrades.html** : Arquivo de para edição de notas dos alunos

### DATABASE

O banco de dados é um banco de dados MySQL, que possui 3 tabelas, sendo elas:

- **users** : Tabela de usuários, que possui o Id, usuário, a senha, o tipo de usuário (professor ou estudante), turno e o curso do usuário (Os ultimos dois casos são para caso o usuario seja aluno).

- **grades** : Tabela de notas, que possui o ID do usuário, o ID do aluno, a nota e a data da nota

### Features

- **Reports**: Dentro de reports.html, é possível gerar um relatório de notas de um determinado aluno, sendo que o aluno é selecionado,+ e o relatório é gerado através de uma função que gera um documento pdf com a nota do aluno selecionado; Também é possível gerar um card e gerar uma declaração caso necessite de um documento mais formal. Não é permitido o aluno qualquer mudança no banco de dados, ou seja, apenas o professor pode alterar a nota do aluno. 

- **Editgrades**: Dentro de editgrades.html, é possível editar as notas de um determinado aluno, sendo que o aluno é selecionado e a nota é editada. Podendo adicionar novas notas (até no máximo 3 trimestres {utiliza um sistema trimestral}).

- **Editgrades and Recover**: Para recuperação de senha, é utilizado o email do usuário, que é enviado para o email cadastrado, e o usuário pode alterar sua senha. Nesse porjeto em específico foi utilizado MailTrap para fazer testes de e-mail, pois é uma ferramenta gratuita que permite testar e-mails em tempo real. Após o envio do email, o usuário pode alterar sua senha na página reset.
