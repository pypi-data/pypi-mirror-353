# Test Package



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Лайнап создания
### 1. Создать pyproject.toml в корне
Использовать свои мета данные. В дальнейшем поддерживать версионнность.
```toml
[tool.poetry]
name = "test_package"
version = "0.1.0"
description = "Тестовый пакет-зависимость"
authors = ["Large Pemp <qwe@qwe.qwe>"]
license = "MIT"
readme = "README.md"
packages = [
    { include = "src" }
]

[tool.poetry.dependencies]
python = "^3.10"

... далее оосновные зависимости

```

### Commit + push
```bash
git add .
git commit -m "Init commit."
git push origin master

```

### Установка тега версионирования
```bash
git tag v0.1.0
git push origin v0.1.0

```

### Добавление пакета в другом проекте
1. Poetry add: `poetry add git+https://gitlab.host.com/<gitname>/test-package.git@v0.1.0#egg=test-package`

2. Вручную в poetry dependencies: `my-test-package = { git = "https://gitlab.host.com/<gitname>/my-test-package.git", tag = "v0.1.0" }`
`
