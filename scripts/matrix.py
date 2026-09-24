#!/usr/bin/env python3
"""八爪鱼矩阵：健康检查 + 任务包扇出。

用法:
  python3 scripts/matrix.py health              # 探测所有节点
  python3 scripts/matrix.py fanout <epic-slug> <task-file>...
      把每个任务文件打包为 prompts/<epic>/<task>.md，分派给矩阵节点，
      记录到 docs/matrix-runs/<epic>/assignments.json

任务文件格式：首行 `# 标题`，正文为给该节点 agent 的完整指令。
"""
import json, os, sys, time, urllib.request, concurrent.futures

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODES_FILE = os.path.join(ROOT, '.octopus', 'matrix-nodes.json')


def load_nodes():
    cfg = json.load(open(NODES_FILE, encoding='utf-8'))
    return cfg['nodes'], cfg.get('defaults', {})


def probe(node, timeout):
    start = time.time()
    try:
        req = urllib.request.Request(node['url'], method='GET')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(4096).decode('utf-8', 'ignore')
            ok = 'Octopus' in body
            return {
                'id': node['id'], 'name': node['name'], 'role': node.get('role', '?'),
                'status': 'ok' if ok else f'unexpected (HTTP {resp.status})',
                'latency_ms': int((time.time() - start) * 1000),
            }
    except Exception as e:
        return {'id': node['id'], 'name': node['name'], 'role': node.get('role', '?'),
                'status': f'unreachable: {e}', 'latency_ms': int((time.time() - start) * 1000)}


def cmd_health():
    nodes, defaults = load_nodes()
    overrides = defaults.get('health_timeout_sec_override', {})
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(nodes)) as ex:
        futures = [ex.submit(probe, n, overrides.get(n['id'], defaults.get('health_timeout_sec', 6))) for n in nodes]
        results = [f.result() for f in futures]
    for r in sorted(results, key=lambda x: x['latency_ms']):
        print(f"{r['status']:<12} {r['latency_ms']:>6}ms  {r['id']:<12} {r['name']} ({r['role']})")
    ok = sum(1 for r in results if r['status'] == 'ok')
    print(f'\n{ok}/{len(results)} 节点在线')
    return 0 if ok == len(results) else 1


def cmd_fanout(epic, task_files):
    nodes, defaults = load_nodes()
    by_role = {}
    for n in nodes:
        by_role.setdefault(n.get('role', 'compute'), []).append(n)

    run_dir = os.path.join(ROOT, defaults.get('artifact_root', 'docs/matrix-runs'), epic)
    prompt_dir = os.path.join(run_dir, 'prompts')
    os.makedirs(prompt_dir, exist_ok=True)

    # 载入任务
    tasks = []
    for tf in task_files:
        content = open(tf, encoding='utf-8').read().strip()
        title = content.splitlines()[0].lstrip('# ').strip() or os.path.basename(tf)
        tasks.append({'file': os.path.basename(tf), 'title': title, 'content': content})

    # 轮询分派：开发任务给 dev 角色，部署给 deploy，其余给 compute 轮转
    pools = {role: list(ns) for role, ns in by_role.items()}
    counters = {role: 0 for role in pools}

    def pick(preferred_roles):
        for role in preferred_roles:
            if role in pools and pools[role]:
                pool = pools[role]
                node = pool[counters[role] % len(pool)]
                counters[role] += 1
                return node
        return None

    assignments = []
    for t in tasks:
        hint = 'deploy' if any(k in t['title'] for k in ('部署', 'deploy', '发布')) else None
        hint = hint or ('dev' if any(k in t['title'] for k in ('开发', '实现', 'implement', 'feat')) else None)
        node = pick([hint] if hint else ['compute', 'dev'])
        role = node['role'] if node else 'unassigned'
        prompt_path = os.path.join(prompt_dir, t['file'])
        with open(prompt_path, 'w', encoding='utf-8') as fp:
            fp.write(t['content'] + '\n')
        assignments.append({
            'task': t['title'], 'task_file': t['file'],
            'node_id': node['id'] if node else None,
            'node_name': node['name'] if node else None,
            'node_url': node['url'] if node else None,
            'role': role,
            'prompt': os.path.relpath(prompt_path, ROOT),
            'status': 'dispatched',
        })
        print(f"{'→':>2} {node['name'] if node else 'UNASSIGNED':<10} {t['title']}")

    out = os.path.join(run_dir, 'assignments.json')
    with open(out, 'w', encoding='utf-8') as fp:
        json.dump({'epic': epic, 'created': time.strftime('%Y-%m-%dT%H:%M:%S'), 'assignments': assignments},
                  fp, ensure_ascii=False, indent=1)
    print(f'\nassignments: {os.path.relpath(out, ROOT)}')
    print('下一步：用浏览器打开各 node_url（web 直连），把 prompt 文件内容投喂给对应节点的 agent 会话。')
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'health':
        sys.exit(cmd_health())
    if sys.argv[1] == 'fanout' and len(sys.argv) >= 4:
        sys.exit(cmd_fanout(sys.argv[2], sys.argv[3:]))
    print(__doc__)
    sys.exit(2)
