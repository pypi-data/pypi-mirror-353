# Gaticos

**Gaticos** es una utilidad de línea de comandos (CLI) para mostrar frases aleatorias de gatos en la terminal, acompañadas de arte ASCII. Es ideal para alegrar tu día con un toque felino y funciona en cualquier sistema compatible con Python 3.12+.

## Instalación

Puedes instalar el paquete usando Poetry, pip o directamente desde el repositorio/clon local:

```bash
pip install .
# o usando poetry
poetry install
```

## Uso rápido

Muestra un "miau" en la terminal:

```bash
gaticos --count 3
```

Muestra una frase aleatoria de gato con arte ASCII:

```bash
gaticos animame
```

## Comandos disponibles

- `gaticos --count N`: Imprime N veces "Miau!" en la terminal.
- `gaticos animame`: Muestra una frase aleatoria de gato decorada con arte ASCII.

## Ejemplo de salida

```
$ gaticos animame
        ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿Frase aleatoria⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
        ...
```

## Requisitos

- Python >= 3.12
- click >= 8.2.1

## Autor

- mendicoder@gmail.com

## Licencia

MIT
