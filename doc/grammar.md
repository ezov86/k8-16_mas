# Грамматика микроассемблера
## Синтаксис описания грамматики
* () — группировка.
* [] - 0 или 1 повторение.
* ? — 0 или 1 повторение.
* \* — 0 и более повторений.
* \+ — одно и более повторение.
* regex(x) — регулярное выражение PCRE x.
* x — нетерминал с именем x.
* \<x\> — терминал с именем x.
* a | b — a или b.
* 'x' — токен x.

## Грамматика

```
S' ::= ϵ | (<macros_def>* <macroinstruction_def>+)

<macros_def> ::= <inline_macros_def> | <multiline_macros_def>

<inline_macros_def> ::= '%mi' <id_with_params> <microinstruction>

<multiline_macros_def> ::= '%m' <id_with_params> '{' <microinstruction_with_label>+ '}'

<macroinstruction_def> ::= '%i' <id_with_params> '{' <microinstruction_with_label>+ '}'

<microinstruction_with_label> ::= [<id> ':'] <microinstruction>

<microinstruction> ::= <bit_masks> ['@' <id>] ';'

<bit_masks> ::= <id_with_params> ('|' <id_with_params>)*

<id_with_params> ::= <id> ['(' <params> ')']

<params> ::= <id> (',' <id>)*
```

## \<id\> (рег. выражение)
``` <id> ::= regex([^\s|;(),%{}@:]+) ```

## Комментарии и другие игнорируемые символы (рег. выражение)
``` <ignored> ::= regex((#[^\n\r]*)|(\t \r)) ```