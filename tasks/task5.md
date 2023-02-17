# Задача 5. Экспериментальное исследование алгоритмов для регулярных запросов

* **Мягкий дедлайн**: 12.10.2022, 23:59
* **Жёсткий дедлайн**: 19.10.2022, 23:59
* Полный балл: 10

## Задача

Задача посвящена анализу производительности  алгоритма решения задачи достижимости между всеми парами вершин и с заданным множеством стартовых вершин с регулярными ограничениями через.

Исследуются три задачи достижимости, решаемые в предыдущих работах.
- Достижимость между всеми парами вершин
- Достижимость для всего множества заданных вершин
- Достижимость для каждой из заданного множества стартовых вершин.

Вопросы, на которые необходимо ответить в ходе исследования.
- Какое представление разреженных матриц и векторов лучше подходит для каждой из решаемых задач?
- Начиная с какого размера стартового множества выгоднее решать задачу для всех пар и выбирать нужные?
- На сколько решение третьей задачи медленнее решения второй при одинаковых начальных условиях?

Решение данной задачи оформляется как Python notebook. Для того, чтобы обеспечить возможность проверки, необходимо сделать notebook самодостаточным: в него должны быть включены все действия, необходимые для воспроизведения эксперимента. Также в notebook размещается отчет и анализ результатов ваших экспериментов в текстовом виде. Отчет сопровождается диаграммами, таблицами, картинками, если это необходимо для объяснения результатов.

Решением является не просто код, но отчёт об экспериментальном исследовании, который должен являться связанным текстом и содержать (как минимум) следующие разделы:
- Постановка задачи
- Описание исследуемых решений
- Описание набора данных для экспериментов
  - Графы
  - Запросы
- Описание эксперимента
  - Оборудование
  - Что и как замерялось, как эти измерения должны помочь ответить на поставленные вопросы
- Результаты экспериментов
  - Графики, таблицы
- Анализ результатов экспериментов
  - Ответы на поставленные вопросы, аргументация ответов

- [ ] Создать Python notebook, подключить необходимые зависимости.
- [ ] Подключить решения из предыдущих работ.
- [ ] Сформировать набор данных.
  - [ ] Выбрать некоторые графы из [набора](https://jetbrains-research.github.io/CFPQ_Data/dataset/index.html). Не забудьте обосновать, почему выбрали именно эти графы.
  - [ ] Используя функцию из первой домашней работы узнать метки рёбер графов и на основе этой информации сформулировать не менее четырёх различных запросов к каждому графу. Лучше использовать наиболее часто встречающиеся метки. Требования к запросам:
      - Запросы ко всем графам должны следовать некоторому общему шаблону. Например, если есть графы ```g1``` и ```g2``` с различными наборами меток, то ожидается, что запросы к ним будут выглядеть, например, так:
        - ```g1```:
          - ```(l1 | l2)* l3```
          - ```(l3 | l4)+ l1*```
          - ```l1 l2 l3 (l4|l1)*```
        - ```g2```:
          - ```(m1 | m3)* m2```
          - ```(m1 | m3)+ m2*```
          - ```m1 m2 m3 (m3|m1)*```
      - В запросах должны использоваться все общепринятые конструкции регулярных выражений  (замыкание, конкатенация, альтернатива). То есть хотя бы в одном запросе к каждому графу должна быть каждая из этих конструкций.
  - [ ] Для генерации множеств стартовых вершин воспользоваться [этой функцией](https://jetbrains-research.github.io/CFPQ_Data/reference/graphs/generated/cfpq_data.graphs.utils.multiple_source_utils.html#cfpq_data.graphs.utils.multiple_source_utils.generate_multiple_source). Не забывайте, что от того, как именно устроено стартовое множество, сильно зависит время вычисления запроса.
- [ ] Сформулировать этапы эксперимента. Что нужно сделать, чтобы ответить на поставленные вопросы? Почему?
- [ ] Провести необходимые эксперименты, замеры
- [ ] Оформить результаты экспериментов
- [ ] Провести анализ результатов
  - [ ] Ответить на поставленные вопросы
  - [ ] Аргументировать ответы (пользуясь полученными результатами экспериментов)
- [ ] Не забыть опубликовать notebook в репозитории