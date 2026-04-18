# Broad Open-Source Director + Script Audit

## Director (VGAI / mutex / schema)

| Model | shots | issues | status | chars | lat | cost |
|-------|------:|-------:|:------:|------:|----:|-----:|
| deepseek__deepseek-v3.2-speciale | 0 | 1 | OK | 32037 | 341.6s | $0.0099 |
| minimax__minimax-m2.5 | 6 | 3 | OK | 3689 | 41.4s | $0.0016 |
| mistralai__mistral-large-2512 | 6 | 4 | OK | 5360 | 21.4s | $0.0026 |
| mistralai__mistral-small-creative | 0 | 1 | OK | 3472 | 8.6s | $0.0004 |
| moonshotai__kimi-k2-thinking | 6 | 1 | OK | 5348 | 359.5s | $0.0170 |
| moonshotai__kimi-k2.5 | 6 | 1 | OK | 5974 | 117.0s | $0.0000 |
| nvidia__nemotron-3-super-120b-a12b | 6 | 1 | OK | 5986 | 78.8s | $0.0008 |
| qwen__qwen3-max-thinking | 6 | 1 | OK | 7880 | 61.2s | $0.0083 |
| qwen__qwen3.5-397b-a17b | 6 | 1 | OK | 5472 | 71.4s | $0.0257 |
| qwen__qwen3.6-plus | 6 | 1 | OK | 5912 | 136.2s | $0.0147 |
| stepfun__step-3.5-flash | 6 | 1 | OK | 5108 | 106.8s | $0.0022 |
| z-ai__glm-5.1 | 6 | 1 | OK | 4914 | 65.4s | $0.0183 |

## Director issue details

### deepseek__deepseek-v3.2-speciale  (1 issues)
- SCHEMA: not valid JSON (Expecting value: line 1 column 1 (char 0))

### minimax__minimax-m2.5  (3 issues)
- shot#1[ms_waist_up]: VGAI violation — sheer_black_tights (anchor=leg) not in ['ear', 'face', 'hand', 'neck', 'torso']
- shot#1[ms_waist_up]: VGAI violation — black_ankle_boots (anchor=foot) not in ['ear', 'face', 'hand', 'neck', 'torso']
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### mistralai__mistral-large-2512  (4 issues)
- shot#0[ws_establishing]: VGAI violation — black_pencil_skirt (anchor=torso) not in []
- shot#0[ws_establishing]: VGAI violation — sheer_black_tights (anchor=leg) not in []
- shot#0[ws_establishing]: VGAI violation — black_ankle_boots (anchor=foot) not in []
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### mistralai__mistral-small-creative  (1 issues)
- SCHEMA: not valid JSON (Expecting ',' delimiter: line 53 column 58 (char 3097))

### moonshotai__kimi-k2-thinking  (1 issues)
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### moonshotai__kimi-k2.5  (1 issues)
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### nvidia__nemotron-3-super-120b-a12b  (1 issues)
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### qwen__qwen3-max-thinking  (1 issues)
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### qwen__qwen3.5-397b-a17b  (1 issues)
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### qwen__qwen3.6-plus  (1 issues)
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### stepfun__step-3.5-flash  (1 issues)
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### z-ai__glm-5.1  (1 issues)
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

## Script (length / refusal / bifurcation)

| Model | chars | has A/B markers | issues | status | lat | cost |
|-------|------:|:---------------:|:------:|:------:|----:|-----:|
| deepseek__deepseek-v3.2-speciale | 12422 | Y | BANNED PHRASE: '她的签名款'; BANNED PHRASE: '她一贯的'; BANNED PHRASE: '如往常般' | OK | 365.7s | $0.0098 |
| minimax__minimax-m2.5 | 2380 | N | — | OK | 27.6s | $0.0024 |
| mistralai__mistral-large-2512 | 2673 | N | — | OK | 66.2s | $0.0044 |
| mistralai__mistral-small-creative | 2082 | N | — | OK | 17.4s | $0.0007 |
| moonshotai__kimi-k2-thinking | 4224 | N | — | OK | 447.6s | $0.0293 |
| moonshotai__kimi-k2.5 | 1625 | N | — | OK | 41.2s | $0.0000 |
| nvidia__nemotron-3-super-120b-a12b | 14105 | N | BANNED PHRASE: '她的签名款'; BANNED PHRASE: '她一贯的'; BANNED PHRASE: '如往常般' | OK | 36.9s | $0.0041 |
| qwen__qwen3-max-thinking | 1736 | N | — | OK | 42.9s | $0.0057 |
| qwen__qwen3.5-397b-a17b | 461 | N | — | OK | 273.5s | $0.0190 |
| qwen__qwen3.6-plus | 1939 | N | — | OK | 130.1s | $0.0141 |
| stepfun__step-3.5-flash | 2979 | N | — | OK | 132.6s | $0.0013 |
| z-ai__glm-5.1 | 2353 | N | — | OK | 57.9s | $0.0361 |