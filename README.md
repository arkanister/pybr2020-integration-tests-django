# PyBR2020 - Testes de Integração de APIs REST

O objetivo desse projeto é dar o suporte necessário para a implantação de testes de integração para a API que foi desenvolvida utilizando o Django Framework.

## Setup

Para instalar e rodar o projeto em ambiente local, siga as instruções abaixo:

1. Primeiramente configure e inicie o ambiente virtual da sua preferência. Esse projeto já implementa suporte para Pipenv caso essa seja a sua escolha.

2. Instale as dependências do projeto. Não esqueça de instalar as dependências para o ambiente de desenvolvimento.

3. Entre na pasta `src/` que está na raiz do projeto.

4. Execute as migrações do projeto.

    ```bash
    $ python manage.py migrate
    ``` 

5. Rode o projeto.

    ```bash
    $ python manage.py runserver
    ```

6. Acesse o projeto pela url [http://localhost:8000/](http://localhost:8000/).


## Testes

Todo o projeto foi pré-configurado para a implementação dos testes. Uma vez feito isso, poderemos executar os testes com o comando:

```bash
$ python manage.py test --noinput --verbosity=2
```

## Coverage

Para executar os testes utilizando o [Coverage](https://coverage.readthedocs.io/en/coverage-5.3/) siga os passos abaixo.

```bash
$ coverage run --source '.' manage.py test --noinput --verbosity=2
```

Para exibir o relatório de cobertura, execute o seguinte comando:

```bash
$ coverage report
```

---

Developed By: [https://github.com/arkanister](https://github.com/arkanister)
