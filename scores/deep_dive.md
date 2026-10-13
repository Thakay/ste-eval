## A. Overall by judge x generator x arm (separates self-preference from arm effect)

|                         |   base |   lite |   scoped |   full |
|:------------------------|-------:|-------:|---------:|-------:|
| ('opus', 'claude-opus') |   8.19 |   7.81 |     8    |   7.94 |
| ('opus', 'codex-sol')   |   7.69 |   6.81 |     6.94 |   6.75 |
| ('sol', 'claude-opus')  |   7.06 |   7.88 |     7.75 |   7.69 |
| ('sol', 'codex-sol')    |   8.19 |   7.62 |     7.88 |   7.75 |

## A2. Nuance and naturalness by generator x arm


nuance

| gen         |   base |   lite |   scoped |   full |
|:------------|-------:|-------:|---------:|-------:|
| claude-opus |   4.16 |   4.12 |     4.22 |   4.12 |
| codex-sol   |   4.47 |   3.81 |     4.19 |   3.94 |

naturalness

| gen         |   base |   lite |   scoped |   full |
|:------------|-------:|-------:|---------:|-------:|
| claude-opus |   4.34 |   3.81 |     3.84 |   4.06 |
| codex-sol   |   4.47 |   4.06 |     4.06 |   4.19 |

esl_ease

| gen         |   base |   lite |   scoped |   full |
|:------------|-------:|-------:|---------:|-------:|
| claude-opus |   3.97 |   4.62 |     4.47 |   4.75 |
| codex-sol   |   4.31 |   4.81 |     4.62 |   4.72 |

checklist

| gen         |   base |   lite |   scoped |   full |
|:------------|-------:|-------:|---------:|-------:|
| claude-opus |   0.96 |   0.94 |     0.94 |   0.94 |
| codex-sol   |   0.82 |   0.8  |     0.81 |   0.77 |

## A3. Rank (1 best, 4 worst) by judge x generator x arm

|                         |   base |   lite |   scoped |   full |
|:------------------------|-------:|-------:|---------:|-------:|
| ('opus', 'claude-opus') |   2.19 |   2.62 |     2.5  |   2.69 |
| ('opus', 'codex-sol')   |   1.5  |   3    |     2.62 |   2.88 |
| ('sol', 'claude-opus')  |   3.38 |   2.06 |     2.25 |   2.31 |
| ('sol', 'codex-sol')    |   1.69 |   3.12 |     2.62 |   2.56 |

## B. Tokens: thinking vs visible, by generator x arm (means per reply)

|                           |   input_tokens |   thinking |   visible_out |   seconds |   cost_usd |
|:--------------------------|---------------:|-----------:|--------------:|----------:|-----------:|
| ('claude-opus', 'base')   |         4297   |     2853.7 |        1311.4 |      43.2 |        0.1 |
| ('claude-opus', 'full')   |         9839   |     4306.1 |        1177.9 |      55.5 |        0.2 |
| ('claude-opus', 'lite')   |         4703   |     4612.9 |        1252.1 |      57.7 |        0.1 |
| ('claude-opus', 'scoped') |         4825   |     4747.3 |        1371.9 |      60.9 |        0.2 |
| ('codex-sol', 'base')     |        10798.4 |     1002.9 |         437.6 |      53.7 |      nan   |
| ('codex-sol', 'full')     |        14393.4 |     1772.8 |         405.3 |      76.7 |      nan   |
| ('codex-sol', 'lite')     |        11066.4 |     1835.2 |         425.8 |      84.1 |      nan   |
| ('codex-sol', 'scoped')   |        11141.4 |     1654.6 |         418.4 |      78   |      nan   |

## C. Artifacts and formatting

| arm    |   mentions_ste |   kept_as_is |   bullets |   bold |
|:-------|---------------:|-------------:|----------:|-------:|
| base   |           0.03 |            0 |      8.56 |   6.97 |
| lite   |           0    |            0 |     12.12 |   4.44 |
| scoped |           0    |            0 |     12.78 |   4.31 |
| full   |           0    |            0 |      8.28 |   4.09 |

## D. Invented facts and errors listed by judges, per arm (count)

| arm    |   error |   invented |
|:-------|--------:|-----------:|
| base   |      37 |         13 |
| lite   |      30 |          7 |
| scoped |      32 |         17 |
| full   |      33 |          5 |
