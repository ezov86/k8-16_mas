# Формат конфигурационного файла
Конфигурационный файл нужен для описания микроархитектуры. Это делает микроассемблер гораздо более гибким и независимым от конкретного процессора. По-умолчанию путём к файлу является `default_config.json`, но его можно заменить через аргументы командной строки (***TODO: сделать описание аргументов***). Конфигурация описывается в формате JSON.

Список параметров конфигурации:

| Имя | Обязательно | Описание | Тип | 
| --- | --- | --- | --- |
| `name` | + | Имя архитектуры. | `string` |
| `description` | - | Описание (микроассемблером не используется, но полезно для человека, читающего файл). | `string` |
| `mi_adr_size` | + | Размер адреса микроинструкции (в битах). | `number` |
| `inst_opc_size` | + | Размер опкода инструкции (в битах). | `number` |
| `nop_value` | + | Значение, которое записывается в микроинструкцию вместо директивы `!nop`. | `number` | 
| `ctrl_bits_names` | + | Список имён управляющих битов (сигналов), сначала идут младшие в микроинструкции, затем старшие. | `array` |
| `conflicts` | + | Список конфликтов (см. далее). | `array` |

## Конфликты
В процессоре одновременная установка некоторых управляющих сигналов может привести к неправильной работе. Пример: имеется сигнал `r`, считывающий данные из некоторого регистра на шину, и `w`, записывающий данные с той же шины в тот же регистр. Включение сразу двух этих битов бессмысленно и приведет к неправильному выполнению.

В целях обеспечения защиты от случайных ошибок программиста, предусмотрена система, проверяющая наличие в одной микроинструкции двух и более конфликтующих сигналов. Список конфликтующих сигналов устанавливается в конфигурации. Не всегда возможно предусмотреть все конфликтные ситуации, поэтому при их нахождении выдается только предупреждение, а не ошибка.

Для описания конфликтов используется два списка:
1. `all` - список названий управляющих битов, все из которых должны быть установлены для определения ситуации как конфликтной.
2. `one_of` - список названий управляющих битов, из которых хотя бы один должен быть установлен для определения ситуации как конфликтной.

Все условия должны быть применимы к обоим спискам соответственно описанию выше. Можно записать в виде логического выражения: (активны все биты из `all`) И (активен 1 бит или более из `one_of`).

## Пример
```
{
  "name": "example",
  
  "mi_adr_size": 4,
  "inst_opc_size": 4,
  "nop_value": 0,

  "ctrl_bits_names": [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f"
  ],

  "conflicts": [
    {
      "one_of": [
        "a",
        "b"
      ],
      "all": []
    },
    {
      "one_of": [
        "a",
        "c"
      ],
      "all": ["f"]
    }
  ]
}
```

Данный пример описывает микроархитектуру, имеющую следующие особенности:
1. имя - `example`;
2. размер адреса микроинструкции - `4`;
3. размер опкода инструкции - `4`;
4. значение `!nop` - 0.
5. управляющие биты: `a`, `b`, `c`, `d`, `e`, `f`;
6. конфликты:
    * a или b при любых значениях других битов;
    * а или c при f.

В ходе разбора конфигурации также определяется количество управляющих битов и итоговый размер микроинструкции, который равен сумме количества управляющих битов и `mi_adr_size`.

Если при описании необходимо добавить зарезервированные или неиспользуемые сигналы, то их следует называть `!RESERVED0`, 
`!RESERVED1`, `!RESERVED2`, `!RESERVED3`, ...