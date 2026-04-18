# Broad Open-Source Director + Script Audit

## Director (VGAI / mutex / schema)

| Model | shots | issues | status | chars | lat | cost |
|-------|------:|-------:|:------:|------:|----:|-----:|
| deepseek__deepseek-v3.2-speciale | 0 | 1 | OK | 33026 | 373.2s | $0.0099 |
| minimax__minimax-m2.5 | 6 | 3 | OK | 4160 | 81.9s | $0.0018 |
| minimax__minimax-m2.7 | 6 | 7 | OK | 4681 | 82.2s | $0.0022 |
| mistralai__mistral-large-2512 | 6 | 2 | OK | 6122 | 23.9s | $0.0029 |
| mistralai__mistral-small-creative | 0 | 1 | OK | 4664 | 10.9s | $0.0004 |
| moonshotai__kimi-k2-thinking | 6 | 1 | OK | 4192 | 128.1s | $0.0107 |
| moonshotai__kimi-k2.5 | 6 | 1 | OK | 6572 | 98.1s | $0.0000 |
| nvidia__nemotron-3-super-120b-a12b | 6 | 1 | OK | 4951 | 77.0s | $0.0007 |
| qwen__qwen3-max-thinking | 6 | 1 | OK | 7909 | 62.5s | $0.0084 |
| qwen__qwen3.5-397b-a17b | 6 | 1 | OK | 4576 | 201.6s | $0.0263 |
| qwen__qwen3.6-plus | 6 | 1 | OK | 5421 | 148.5s | $0.0161 |
| stepfun__step-3.5-flash | 6 | 1 | OK | 4706 | 125.1s | $0.0024 |
| xiaomi__mimo-v2-flash | 6 | 0 | OK | 3218 | 7.5s | $0.0003 |
| xiaomi__mimo-v2-pro | 6 | 1 | OK | 6264 | 52.0s | $0.0128 |
| z-ai__glm-5.1 | 6 | 1 | OK | 4861 | 57.2s | $0.0153 |

## Director issue details

### deepseek__deepseek-v3.2-speciale  (1 issues)
- SCHEMA: not valid JSON (Expecting value: line 1 column 1 (char 0))

### minimax__minimax-m2.5  (3 issues)
- shot#1[ms_waist_up]: VGAI violation — black_ankle_boots (anchor=foot) not in ['ear', 'face', 'hand', 'neck', 'torso']
- shot#1[ms_waist_up]: VGAI violation — sheer_black_tights (anchor=leg) not in ['ear', 'face', 'hand', 'neck', 'torso']
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### minimax__minimax-m2.7  (7 issues)
- shot#0[ws_establishing]: VGAI violation — black_pencil_skirt (anchor=torso) not in []
- shot#0[ws_establishing]: VGAI violation — sheer_black_tights (anchor=leg) not in []
- shot#0[ws_establishing]: VGAI violation — black_ankle_boots (anchor=foot) not in []
- shot#1[ms_waist_up]: VGAI violation — sheer_black_tights (anchor=leg) not in ['ear', 'face', 'hand', 'neck', 'torso']
- shot#1[ms_waist_up]: VGAI violation — stocking_toes (anchor=foot) not in ['ear', 'face', 'hand', 'neck', 'torso']
- shot#3[cu_face]: VGAI violation — sheer_black_tights (anchor=leg) not in ['ear', 'face', 'neck']
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### mistralai__mistral-large-2512  (2 issues)
- shot#1[ms_waist_up]: VGAI violation — sheer_black_tights (anchor=leg) not in ['ear', 'face', 'hand', 'neck', 'torso']
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### mistralai__mistral-small-creative  (1 issues)
- SCHEMA: not valid JSON (Expecting ',' delimiter: line 53 column 82 (char 4088))

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

### xiaomi__mimo-v2-flash  — CLEAN (6 shots)

### xiaomi__mimo-v2-pro  (1 issues)
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

### z-ai__glm-5.1  (1 issues)
- shot#5[back_reveal_walking]: VGAI violation — black_pencil_skirt (anchor=torso) not in ['foot', 'hand', 'leg', 'torso_back']

## Script (length / refusal / bifurcation)

| Model | chars | has A/B markers | issues | status | lat | cost |
|-------|------:|:---------------:|:------:|:------:|----:|-----:|
| deepseek__deepseek-v3.2-speciale | 12687 | Y | BANNED PHRASE: '她的签名款'; BANNED PHRASE: '她一贯的'; BANNED PHRASE: '如往常般' | OK | 365.2s | $0.0098 |
| minimax__minimax-m2.5 | 2164 | N | — | OK | 24.2s | $0.0039 |
| minimax__minimax-m2.7 | 1852 | N | — | OK | 25.0s | $0.0020 |
| mistralai__mistral-large-2512 | 4242 | N | — | OK | 107.2s | $0.0068 |
| mistralai__mistral-small-creative | 2272 | N | — | OK | 19.2s | $0.0007 |
| moonshotai__kimi-k2-thinking | 2640 | N | — | OK | 140.2s | $0.0074 |
| moonshotai__kimi-k2.5 | 2050 | N | — | OK | 32.5s | $0.0000 |
| nvidia__nemotron-3-super-120b-a12b | 23 | N | — | OK | 1.3s | $0.0001 |
| qwen__qwen3-max-thinking | 1610 | N | — | OK | 38.7s | $0.0053 |
| qwen__qwen3.5-397b-a17b | 1971 | N | — | OK | 147.1s | $0.0176 |
| qwen__qwen3.6-plus | 2220 | N | — | OK | 160.2s | $0.0172 |
| stepfun__step-3.5-flash | 4664 | N | — | OK | 133.3s | $0.0017 |
| xiaomi__mimo-v2-flash | 4113 | N | — | OK | 30.3s | $0.0009 |
| xiaomi__mimo-v2-pro | 2391 | N | — | OK | 52.5s | $0.0094 |
| z-ai__glm-5.1 | 2910 | N | — | OK | 217.7s | $0.0361 |