#!/usr/bin/env python3
"""
Codebase Cartographer — Local Web App
Usage: python cartographer.py /path/to/your/project [--port 3000]
Opens an interactive dashboard in your browser.
"""
import os, sys, json, re, hashlib, threading, webbrowser, time, subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ── Import scanner from same directory ──
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

# Read dashboard HTML
DASHBOARD_PATH = SCRIPT_DIR / 'dashboard.html'

# ── Config ──
IGNORE_DIRS = {'node_modules','.git','__pycache__','.next','dist','build','.build','DerivedData','Pods','venv','.venv','env','.env','vendor','target','bin','obj','.idea','.vscode','.gradle','.dart_tool','coverage','.cache','.turbo','out','.output','.expo','.swiftpm','xcuserdata'}
IGNORE_FILES = {'.DS_Store','Thumbs.db','package-lock.json','yarn.lock','pnpm-lock.yaml','Podfile.lock','poetry.lock'}
LANG_MAP = {'.py':'python','.js':'javascript','.jsx':'javascript','.ts':'typescript','.tsx':'typescript','.swift':'swift','.m':'objc','.rs':'rust','.go':'go','.rb':'ruby','.java':'java','.kt':'kotlin','.c':'c','.h':'c','.cpp':'cpp','.hpp':'cpp','.cs':'c_sharp','.dart':'dart','.php':'php','.lua':'lua','.vue':'javascript','.svelte':'javascript'}

BINDING_PATTERNS = {
    'swift':{'protocols':r'protocol\s+(\w+)','delegates':r'(\w+Delegate|\w+DataSource)','notifications':r'NotificationCenter\.\w+\.\w+\(.*?name:\s*[.\w]*(\w+)','core_data':r'@FetchRequest|NSManagedObject|NSPersistentContainer','combine':r'@Published|PassthroughSubject|CurrentValueSubject|\.sink\b','swiftui_env':r'@Environment|@EnvironmentObject|@StateObject|@ObservedObject|@AppStorage','api_calls':r'URLSession|URLRequest|\.dataTask|async\s+let|try\s+await','keychain':r'Keychain|SecItem|kSecClass','userdefaults':r'UserDefaults\.\w+'},
    'python':{'imports':r'^(?:from\s+(\S+)\s+import|import\s+(\S+))','decorators':r'@(\w+)','api_endpoints':r'@(?:app|router|api)\.\w+\(\s*[\'"]([^\'"]+)','db_models':r'class\s+\w+\(.*(?:Model|Base|db\.Model)','env_vars':r'os\.(?:environ|getenv)\s*[\[\(]\s*[\'"](\w+)','signals':r'\.connect\(|signal\(|@receiver'},
    'javascript':{'imports':r'(?:import\s+.*?from\s+[\'"]([^\'"]+)|require\s*\(\s*[\'"]([^\'"]+))','exports':r'(?:export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)|module\.exports)','api_routes':r'(?:app|router)\.\s*(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)','event_emitters':r'\.on\s*\(\s*[\'"](\w+)|\.emit\s*\(\s*[\'"](\w+)','env_vars':r'process\.env\.(\w+)','hooks':r'use[A-Z]\w+','context':r'createContext|useContext|\.Provider'},
    'typescript':{'imports':r'(?:import\s+.*?from\s+[\'"]([^\'"]+)|require\s*\(\s*[\'"]([^\'"]+))','exports':r'(?:export\s+(?:default\s+)?(?:class|function|const|let|var|interface|type|enum)\s+(\w+))','interfaces':r'interface\s+(\w+)','api_routes':r'(?:app|router)\.\s*(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)','decorators':r'@(\w+)','env_vars':r'process\.env\.(\w+)'},
    'rust':{'imports':r'use\s+([\w:]+)','traits':r'trait\s+(\w+)','unsafe':r'unsafe\s+\{','ffi':r'extern\s+"C"'},
    'go':{'imports':r'import\s+(?:\(\s*)?["\s]*([^"\s\)]+)','interfaces':r'type\s+(\w+)\s+interface','goroutines':r'go\s+\w+','http_handlers':r'http\.Handle(?:Func)?\s*\(\s*[\'"]([^\'"]+)'},
    'java':{'imports':r'import\s+([\w.]+)','interfaces':r'interface\s+(\w+)','annotations':r'@(\w+)','spring_endpoints':r'@(?:Get|Post|Put|Delete|Patch|Request)Mapping\s*\(\s*[\'"]?([^\'")\s]+)'},
    'kotlin':{'imports':r'import\s+([\w.]+)','annotations':r'@(\w+)','coroutines':r'(?:launch|async|withContext|suspend\s+fun)'},
    'c_sharp':{'imports':r'using\s+([\w.]+)','interfaces':r'interface\s+(\w+)','attributes':r'\[(\w+)'},
    'ruby':{'imports':r'require\s+[\'"]([^\'"]+)','routes':r'(?:get|post|put|delete|patch)\s+[\'"]([^\'"]+)'},
    'dart':{'imports':r'import\s+[\'"]([^\'"]+)','providers':r'Provider|ChangeNotifier|Riverpod|Bloc'},
    'php':{'imports':r'(?:use|require|include)(?:_once)?\s+[\'"]?([^\'";\s]+)','routes':r'Route::\w+\(\s*[\'"]([^\'"]+)'},
}

CONCERN_KEYWORDS = {
    'authentication':['auth','login','logout','token','jwt','session','password','oauth','signin','signup','credential'],
    'database':['database','db','model','schema','migration','query','sql','core_data','realm','sqlite','mongo'],
    'networking':['api','http','fetch','request','url','endpoint','rest','graphql','socket','network'],
    'ui / views':['view','screen','component','widget','layout','page','ui','button','form','modal','navigation'],
    'state management':['state','store','redux','context','provider','viewmodel','observable','published','combine','bloc'],
    'configuration':['config','env','environment','settings','constants','keys','secret'],
    'payments':['payment','stripe','billing','subscription','purchase','storekit','iap','checkout'],
    'testing':['test','spec','mock','stub','fixture','assert'],
    'security':['security','encrypt','decrypt','keychain','hash','ssl','cert'],
    'notifications':['notification','push','alert','apns','fcm','messaging'],
    'analytics':['analytics','tracking','event','metric','log','telemetry','firebase'],
}

TAG_EXPLAIN = {
    '🔌 interface':'Defines a contract other files must follow. Changes break implementers.',
    '📡 event-driven':'Sends/receives events. Changes silently break listeners.',
    '🌐 api-endpoint':'Handles API requests. Route/response changes affect all clients.',
    '📤 api-consumer':'Makes network calls. URL/payload changes cause failures.',
    '💾 data-model':'Defines data storage. Schema changes can corrupt data.',
    '⚙️ config-dependent':'Reads env vars/config. Missing values = runtime crashes.',
    '🔄 state-management':'Manages app state. Changes ripple through UI.',
    '⚠️ unsafe-code':'Contains unsafe/low-level code. Memory safety risks.',
    '⚡ concurrent':'Uses concurrency. Race conditions easy to introduce.',
}

def gen_english(node, all_nodes, edges):
    lines = []; n = node; risk = n['risk_score']; fi = n['fan_in']
    if risk >= 75: lines.append(f"⚠️ **{n['name']}** is critical. Treat changes with extreme care.")
    elif risk >= 50: lines.append(f"🟡 **{n['name']}** is important — several parts of your project rely on it.")
    elif risk >= 25: lines.append(f"🟢 **{n['name']}** has moderate connections. Fairly safe but check linked files.")
    else: lines.append(f"✅ **{n['name']}** is isolated. Low risk to modify.")
    if fi > 5: lines.append(f"**{fi} other files depend on this.** Changes cascade widely.")
    elif fi > 0: lines.append(f"{fi} file{'s' if fi>1 else ''} depend{'s' if fi==1 else ''} on this.")
    for tag in n.get('tags',[]):
        if tag in TAG_EXPLAIN: lines.append(f"**{tag}** — {TAG_EXPLAIN[tag]}")
    deps = [next((x['name'] for x in all_nodes if x['id']==e['source']),None) for e in edges if e['target']==n['id']]
    deps = [d for d in deps if d]
    if deps: lines.append(f"**If you change this, these may break:** {', '.join(deps[:8])}")
    return '\n\n'.join(lines)


class Scanner:
    def __init__(self, root, project_id=None):
        self.root = Path(root).resolve()
        self.project_id = project_id or hashlib.md5(str(self.root).encode()).hexdigest()[:12]
        self.nodes = {}; self.edges = []; self.bps = []; self.contents = {}; self.imap = defaultdict(list)

    def scan(self):
        self._discover(); self._parse(); self._resolve(); self._tag(); self._risk(); self._git(); self._tests(); self._concerns()
        return self._output()

    def _discover(self):
        for dp, dns, fns in os.walk(self.root):
            dns[:] = [d for d in dns if d not in IGNORE_DIRS and not d.startswith('.')]
            for f in fns:
                if f in IGNORE_FILES or f.startswith('.'): continue
                fp = Path(dp)/f; ext = fp.suffix.lower()
                if ext not in LANG_MAP: continue
                rel = str(fp.relative_to(self.root)); fid = hashlib.md5((self.project_id + ':' + rel).encode()).hexdigest()[:12]
                try:
                    st = fp.stat(); content = fp.read_text(errors='replace'); lc = content.count('\n')+1
                    self.contents[fid] = content
                except: continue
                self.nodes[fid] = {'id':fid,'path':str(fp),'relative_path':rel,'name':f,'extension':ext,'language':LANG_MAP[ext],'size_bytes':st.st_size,'line_count':lc,'imports':[],'exports':[],'binding_points':[],'tags':[],'risk_score':0,'fan_in':0,'fan_out':0,'last_modified':datetime.fromtimestamp(st.st_mtime).isoformat(),'git_changes':0,'has_tests':False,'complexity_hint':'low','concerns':[],'plain_english':''}

    def _parse(self):
        for fid, n in self.nodes.items():
            content = self.contents.get(fid,''); lang = n['language']
            pats = BINDING_PATTERNS.get(lang, {})
            for pn, pat in pats.items():
                try:
                    for i, line in enumerate(content.split('\n'), 1):
                        for m in re.findall(pat, line):
                            if isinstance(m, tuple): m = next((x for x in m if x), '')
                            if m:
                                n['binding_points'].append({'name':m,'type':pn,'line':i})
                                self.bps.append({'name':m,'bp_type':pn,'file_id':fid,'line':i})
                                if pn == 'imports':
                                    n['imports'].append(m); self.imap[m].append(fid)
                except re.error: pass
            # Complexity by line count
            if n['line_count'] > 300: n['complexity_hint'] = 'high'
            elif n['line_count'] > 100: n['complexity_hint'] = 'medium'

    def _resolve(self):
        lk = {}
        for fid, n in self.nodes.items():
            rel = n['relative_path']; stem = Path(rel).stem; ne = str(Path(rel).with_suffix(''))
            for k in [rel, ne, stem, ne.replace('/','.'), './'+ne, '../'+ne]: lk[k] = fid
            parts = ne.split('/')
            if len(parts)>=2: lk['/'.join(parts[-2:])]=fid; lk['.'.join(parts[-2:])]=fid
        for fid, n in self.nodes.items():
            for imp in n['imports']:
                t = lk.get(imp) or lk.get(imp.lstrip('./').replace('.','/')) or lk.get(imp.lstrip('./').replace('/','.')); 
                if t and t != fid:
                    self.edges.append({'source':fid,'target':t,'edge_type':'import','label':imp})
                    self.nodes[t]['fan_in'] += 1; n['fan_out'] += 1

    def _tag(self):
        tm = {'protocols':'🔌 interface','interfaces':'🔌 interface','traits':'🔌 interface','delegates':'📡 event-driven','event_emitters':'📡 event-driven','signals':'📡 event-driven','combine':'📡 event-driven','api_endpoints':'🌐 api-endpoint','api_routes':'🌐 api-endpoint','http_handlers':'🌐 api-endpoint','routes':'🌐 api-endpoint','spring_endpoints':'🌐 api-endpoint','api_calls':'📤 api-consumer','db_models':'💾 data-model','core_data':'💾 data-model','env_vars':'⚙️ config-dependent','hooks':'🔄 state-management','context':'🔄 state-management','swiftui_env':'🔄 state-management','providers':'🔄 state-management','decorators':'🏷️ decorated','annotations':'🏷️ decorated','unsafe':'⚠️ unsafe-code','ffi':'⚠️ unsafe-code','goroutines':'⚡ concurrent','coroutines':'⚡ concurrent'}
        for fid, n in self.nodes.items():
            tags = set()
            for bp in n['binding_points']:
                tag = tm.get(bp['type'])
                if tag: tags.add(tag)
            n['tags'] = list(tags)

    def _risk(self):
        mfi = max((n['fan_in'] for n in self.nodes.values()), default=1) or 1
        mfo = max((n['fan_out'] for n in self.nodes.values()), default=1) or 1
        mlc = max((n['line_count'] for n in self.nodes.values()), default=1) or 1
        risky = {'🌐 api-endpoint','💾 data-model','⚠️ unsafe-code','📡 event-driven'}
        for n in self.nodes.values():
            s = (n['fan_in']/mfi)*35 + (n['fan_out']/mfo)*15 + min(len(n['binding_points'])/10,1)*25 + (n['line_count']/mlc)*10 + (len(set(n['tags'])&risky)/max(len(risky),1))*15
            n['risk_score'] = round(min(s, 100), 1)

    def _git(self):
        try:
            r = subprocess.run(['git','-C',str(self.root),'log','--format=','--name-only','--since=6 months ago'], capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                counts = defaultdict(int)
                for l in r.stdout.strip().split('\n'):
                    if l.strip(): counts[l.strip()] += 1
                mc = max(counts.values(), default=1) or 1
                for n in self.nodes.values():
                    n['git_changes'] = counts.get(n['relative_path'], 0)
                    if n['git_changes'] > 0: n['risk_score'] = round(min(n['risk_score']+(n['git_changes']/mc)*10, 100), 1)
        except: pass

    def _tests(self):
        tp = ['test_','_test.','.test.','spec.','_spec.','Test.','Tests.']; td = {'tests','test','__tests__','spec'}
        for n in self.nodes.values():
            it = any(p in n['name'] for p in tp) or any(d in n['relative_path'].split('/') for d in td)
            n['has_tests'] = it
            if it: n['tags'].append('🧪 test'); n['risk_score'] = max(n['risk_score']-20, 0)

    def _concerns(self):
        for fid, n in self.nodes.items():
            cl = self.contents.get(fid,'').lower(); pl = n['relative_path'].lower(); nl = n['name'].lower()
            bpn = set(bp['name'].lower() for bp in n['binding_points'])
            cons = []
            for c, kws in CONCERN_KEYWORDS.items():
                sc = sum(3 if kw in nl else 2 if kw in pl else 2 if kw in bpn else 1 if kw in cl else 0 for kw in kws)
                if sc >= 3: cons.append(c)
            n['concerns'] = cons

    def _output(self):
        nl = list(self.nodes.values()); el = self.edges
        for n in nl: n['plain_english'] = gen_english(n, nl, el)
        groups = defaultdict(list)
        for n in nl:
            parts = n['relative_path'].split('/'); groups[parts[0] if len(parts)>1 else '.'].append(n['id'])
        cc = defaultdict(list)
        for n in nl:
            for c in n.get('concerns',[]): cc[c].append({'id':n['id'],'name':n['name'],'risk':n['risk_score']})
        total = len(nl) or 1; tested = sum(1 for n in nl if n['has_tests'] or '🧪 tested' in n['tags'])
        cu = sum(1 for n in nl if n['risk_score']>=50 and not n['has_tests']); avg = sum(n['risk_score'] for n in nl)/total
        health = max(0,min(100,round(100 - avg*0.4 - (cu/total)*30 + (tested/total)*20)))
        sn = sorted(nl, key=lambda x: x['risk_score'], reverse=True)
        crit = [{'file':n['relative_path'],'risk_score':n['risk_score'],'fan_in':n['fan_in'],'tags':n['tags'],'binding_points':len(n['binding_points'])} for n in sn[:20] if n['risk_score']>15]
        ac = self._agent_ctx(crit, nl)
        out_nodes = [{'id':n['id'],'path':n['relative_path'],'name':n['name'],'language':n['language'],'lines':n['line_count'],'size':n['size_bytes'],'imports':n['imports'],'exports':n['exports'],'binding_points':n['binding_points'],'tags':n['tags'],'risk_score':n['risk_score'],'fan_in':n['fan_in'],'fan_out':n['fan_out'],'complexity':n['complexity_hint'],'git_changes':n['git_changes'],'has_tests':n['has_tests'],'concerns':n.get('concerns',[]),'plain_english':n['plain_english']} for n in nl]
        return {'metadata':{'project_root':str(self.root),'project_name':self.root.name,'scanned_at':datetime.now().isoformat(),'total_files':len(out_nodes),'total_edges':len(el),'total_binding_points':len(self.bps),'languages':list(set(n['language'] for n in nl)),'health_score':health},'nodes':out_nodes,'edges':el,'groups':dict(groups),'concern_clusters':dict(cc),'critical_files':crit,'agent_context':ac}

    def _agent_ctx(self, crit, nl):
        lines = ["# ⚠️ CODEBASE RISK MAP — READ BEFORE MODIFYING","","## 🔴 Critical Files (DO NOT modify without review)",""]
        for cf in crit[:10]: lines.append(f"- **{cf['file']}** — Risk: {cf['risk_score']}/100 | Dependents: {cf['fan_in']} | {' '.join(cf['tags'])}")
        lines += ["","## 🟡 Binding Points",""]
        for n in nl:
            if len(n.get('binding_points',[])) > 1:
                types = set(bp['type'] for bp in n['binding_points'])
                lines.append(f"- `{n['relative_path']}`: {', '.join(types)}")
        lines += ["","## 🟢 Safe to Modify",""]
        for n in sorted(nl, key=lambda x: x['risk_score'])[:10]:
            if n['risk_score'] < 15: lines.append(f"- `{n['relative_path']}` (risk: {n['risk_score']})")
        return '\n'.join(lines)

# ── Web Server ──
# Multi-project support (max 2 projects)
PROJECTS = {}  # {project_id: {'root': path, 'scan_data': {...}, 'chat_history': []}}
CURRENT_PROJECT_ID = None  # Currently active project
MAX_PROJECTS = 2  # Enforce limit

RECENT_PROJECTS_FILE = Path.home() / '.cartographer_history'

# ── DeepSeek Chat State ──
CONFIG_FILE = Path(__file__).parent / '.cartographer_config.json'
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
SELECTED_MODEL = 'deepseek-chat'  # or 'deepseek-reasoner'

def generate_project_id(path):
    """Generate unique ID from absolute path"""
    abs_path = str(Path(path).resolve())
    return hashlib.md5(abs_path.encode()).hexdigest()[:12]

def get_recent_projects():
    if RECENT_PROJECTS_FILE.exists():
        return [p.strip() for p in RECENT_PROJECTS_FILE.read_text().strip().split('\n') if p.strip() and Path(p.strip()).is_dir()]
    return []

def add_recent_project(path):
    recent = get_recent_projects()
    path = str(Path(path).resolve())
    if path in recent:
        recent.remove(path)
    recent.insert(0, path)
    RECENT_PROJECTS_FILE.write_text('\n'.join(recent[:10]))

def load_config():
    """Load API key and settings from config file"""
    global DEEPSEEK_API_KEY, SELECTED_MODEL
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            # Only override if not set via environment variable
            if not os.environ.get('DEEPSEEK_API_KEY'):
                api_key = config.get('api_key', '')
                if api_key:
                    DEEPSEEK_API_KEY = api_key
            model = config.get('model', '')
            if model:
                SELECTED_MODEL = model
            return True
        except Exception as e:
            print(f"  ⚠️  Failed to load config: {e}")
    return False

def save_config():
    """Save API key and settings to config file"""
    global DEEPSEEK_API_KEY, SELECTED_MODEL
    try:
        config = {
            'api_key': DEEPSEEK_API_KEY,
            'model': SELECTED_MODEL,
            'saved_at': datetime.now().isoformat()
        }
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
        return True
    except Exception as e:
        print(f"  ⚠️  Failed to save config: {e}")
        return False

def do_rescan(project_id=None):
    global CURRENT_PROJECT_ID, PROJECTS

    if project_id is None:
        project_id = CURRENT_PROJECT_ID

    if project_id and project_id in PROJECTS:
        path = PROJECTS[project_id]['root']
        PROJECTS[project_id]['scan_data'] = Scanner(path, project_id).scan()
        return PROJECTS[project_id]['scan_data']

    return {}

def load_project(path):
    global CURRENT_PROJECT_ID, PROJECTS
    # Strip quotes that might be added around paths with spaces
    path = str(path).strip().strip('"').strip("'")
    path = str(Path(path).resolve())
    if not Path(path).is_dir():
        raise ValueError(f"Not a directory: {path}")

    # Check project limit
    project_id = generate_project_id(path)
    if project_id not in PROJECTS and len(PROJECTS) >= MAX_PROJECTS:
        raise ValueError(f"Maximum {MAX_PROJECTS} projects allowed. Close one first.")

    # Initialize project if new
    if project_id not in PROJECTS:
        PROJECTS[project_id] = {
            'root': path,
            'name': Path(path).name,
            'scan_data': {},
            'chat_history': []
        }

    # Scan project (pass project_id to Scanner)
    PROJECTS[project_id]['scan_data'] = Scanner(path, project_id).scan()
    CURRENT_PROJECT_ID = project_id

    add_recent_project(path)
    return {
        'project_id': project_id,
        'project_name': PROJECTS[project_id]['name'],
        'scan_data': PROJECTS[project_id]['scan_data']
    }

# ── DeepSeek Chat Functions ──
def build_codebase_context(query, project_id=None, include_files=[]):
    """Build intelligent context from Scanner data without vector DB"""
    global CURRENT_PROJECT_ID, PROJECTS

    if project_id is None:
        project_id = CURRENT_PROJECT_ID

    if not project_id or project_id not in PROJECTS:
        return "No codebase loaded."

    # Use local reference to this project's scan data
    SCAN_DATA = PROJECTS[project_id]['scan_data']

    if not SCAN_DATA or not SCAN_DATA.get('nodes'):
        return "No codebase loaded."

    context_parts = []

    # 1. Project overview (metadata)
    meta = SCAN_DATA.get('metadata', {})
    context_parts.append(
        f"PROJECT: {meta.get('project_name', 'Unknown')}\n"
        f"HEALTH: {meta.get('health_score', 0)}/100\n"
        f"LANGUAGES: {', '.join(meta.get('languages', []))}\n"
        f"TOTAL FILES: {meta.get('total_files', 0)}"
    )

    # 2. Agent context (already curated risk map)
    agent_ctx = SCAN_DATA.get('agent_context', '')
    if agent_ctx:
        context_parts.append(agent_ctx)

    # 3. Smart file selection based on query keywords
    query_lower = query.lower()
    relevant_files = []

    # Extract file references from query
    import re
    file_patterns = [
        r'in\s+([a-zA-Z0-9_/.-]+\.[a-z]+)',  # "in auth.py"
        r'`([a-zA-Z0-9_/.-]+\.[a-z]+)`',     # "`src/api.ts`"
        r'file\s+([a-zA-Z0-9_/.-]+\.[a-z]+)',  # "file Header.tsx"
        r'([a-zA-Z0-9_/-]+\.(?:py|ts|tsx|js|jsx|java|go|rs|cpp|c|h))\b'  # Direct file names
    ]

    mentioned_files = []
    for pattern in file_patterns:
        mentioned_files.extend(re.findall(pattern, query_lower))

    # Deduplicate
    mentioned_files = list(set(mentioned_files))

    # Add explicitly mentioned files first
    for file_ref in mentioned_files:
        for node in SCAN_DATA.get('nodes', []):
            if file_ref in node['path'].lower():
                relevant_files.insert(0, node['id'])
                break

    # Match by concerns (auth, api, database, etc.)
    for concern, files in SCAN_DATA.get('concern_clusters', {}).items():
        if concern in query_lower:
            relevant_files.extend([f['id'] for f in files[:3]])  # Top 3 per concern

    # Match by file paths
    for node in SCAN_DATA.get('nodes', []):
        path_lower = node.get('path', '').lower()
        name_lower = node.get('name', '').lower()
        # Check if any word from query is in path or name
        for word in query_lower.split():
            if len(word) > 2 and (word in path_lower or word in name_lower):
                relevant_files.append(node['id'])
                break

    # Add explicitly requested files from API
    relevant_files.extend(include_files)

    # Deduplicate and limit to 10 files
    relevant_files = list(dict.fromkeys(relevant_files))[:10]

    # 4. Add file details with plain_english explanations
    for file_id in relevant_files:
        node = next((n for n in SCAN_DATA.get('nodes', []) if n['id'] == file_id), None)
        if node:
            tags_str = ', '.join(node.get('tags', []))
            context_parts.append(
                f"\nFILE: {node.get('path', 'Unknown')}\n"
                f"RISK: {node.get('risk_score', 0)}/100\n"
                f"TAGS: {tags_str}\n"
                f"CONCERNS: {', '.join(node.get('concerns', []))}\n"
                f"EXPLANATION: {node.get('plain_english', 'No explanation available.')}"
            )

    # Join and truncate to ~8K tokens (~32K chars)
    full_context = '\n\n'.join(context_parts)
    return full_context[:32000]  # Safety truncate

def call_deepseek(message, context, model='deepseek-chat', project_id=None):
    """Make API call to DeepSeek with model-specific optimization"""
    global CURRENT_PROJECT_ID, PROJECTS, DEEPSEEK_API_KEY

    if project_id is None:
        project_id = CURRENT_PROJECT_ID

    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY not set. Configure it via the settings or set the DEEPSEEK_API_KEY environment variable.")

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI library not installed. Run: pip install openai")

    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )

    # Model-specific prompt optimization
    if model == 'deepseek-reasoner':  # R1 model
        # R1: Minimal system prompt, explicit task format
        system_content = ""  # R1 performs better with no system prompt
        temperature = 0.6  # Optimal for R1 reasoning
        user_message = f"""Task: {message}

Codebase Context:
{context}

Output Format:
1. Analysis (explain the issue/requirement)
2. Code changes (show as code diffs with file paths like `// File: path/to/file.ext`)
3. Testing plan (how to verify the changes)

Use markdown code blocks with file paths for all code suggestions."""
    else:  # V3 model (deepseek-chat)
        # V3: Rich system prompt, conversational
        system_content = f"""You are a senior software architect analyzing a codebase and proposing code changes.

Codebase Context:
{context}

When proposing code changes:
1. Use markdown code blocks with file paths: ```lang\n// File: path/to/file.ext\ncode here\n```
2. Show clear before/after diffs when modifying existing code
3. Reference specific files, risk scores, and patterns from the context
4. Be concise but actionable
5. Include file paths in every code block for easy copying

Example format:
```typescript
// File: src/components/Header.tsx
interface HeaderProps {{
  showSearch: boolean;  // <- ADD THIS LINE
}}
```"""
        temperature = 0.7
        user_message = message

    messages = []
    if system_content:
        messages.append({
            "role": "system",
            "content": system_content
        })

    # Add recent chat history (last 10 messages) - Use project-specific chat history
    if project_id and project_id in PROJECTS:
        messages.extend(PROJECTS[project_id]['chat_history'][-10:])

    # Add current message
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=2000
    )

    assistant_message = response.choices[0].message.content

    # Update chat history - Store in project-specific chat history
    if project_id and project_id in PROJECTS:
        PROJECTS[project_id]['chat_history'].append({"role": "user", "content": message})
        PROJECTS[project_id]['chat_history'].append({"role": "assistant", "content": assistant_message})

    return assistant_message

class Handler(BaseHTTPRequestHandler):
    def get_project_id_from_query(self):
        """Extract project_id from query params"""
        from urllib.parse import parse_qs
        query = urlparse(self.path).query
        params = parse_qs(query)
        return params.get('project_id', [CURRENT_PROJECT_ID])[0] if params.get('project_id') else CURRENT_PROJECT_ID

    def do_GET(self):
        p = urlparse(self.path).path
        if p == '/api/scan':
            project_id = self.get_project_id_from_query()
            if project_id and project_id in PROJECTS:
                self._json(PROJECTS[project_id]['scan_data'])
            else:
                self._json({'metadata':{},'nodes':[],'edges':[]})
        elif p == '/api/rescan':
            project_id = self.get_project_id_from_query()
            result = do_rescan(project_id)
            self._json(result if result else {'metadata':{},'nodes':[],'edges':[]})
        elif p == '/api/agent-context':
            project_id = self.get_project_id_from_query()
            if project_id and project_id in PROJECTS:
                self._text(PROJECTS[project_id]['scan_data'].get('agent_context',''))
            else:
                self._text('')
        elif p == '/api/project-root':
            project_id = self.get_project_id_from_query()
            if project_id and project_id in PROJECTS:
                self._json({'project_root': PROJECTS[project_id]['root']})
            else:
                self._json({'project_root': ''})
        elif p == '/api/projects':
            projects_list = [
                {
                    'id': pid,
                    'name': pdata['name'],
                    'root': pdata['root'],
                    'health': pdata['scan_data'].get('metadata', {}).get('health_score', 0),
                    'file_count': len(pdata['scan_data'].get('nodes', [])),
                    'is_current': pid == CURRENT_PROJECT_ID
                }
                for pid, pdata in PROJECTS.items()
            ]
            self._json({'projects': projects_list})
        elif p == '/api/recent-projects': self._json({'projects': get_recent_projects()})
        elif p == '/api/chat/history':
            project_id = self.get_project_id_from_query()
            if project_id and project_id in PROJECTS:
                self._json({'messages': PROJECTS[project_id]['chat_history']})
            else:
                self._json({'messages': []})
        elif p in ('/','/index.html'): self._html()
        else: self.send_error(404)

    def do_POST(self):
        global CURRENT_PROJECT_ID, PROJECTS, DEEPSEEK_API_KEY, SELECTED_MODEL
        p = urlparse(self.path).path
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8')

        try:
            data = json.loads(body) if body else {}
        except:
            self.send_error(400, 'Invalid JSON')
            return

        if p == '/api/projects/unload':
            project_id = data.get('project_id')
            if project_id in PROJECTS:
                del PROJECTS[project_id]
                if CURRENT_PROJECT_ID == project_id:
                    CURRENT_PROJECT_ID = list(PROJECTS.keys())[0] if PROJECTS else None
            self._json({'success': True})

        elif p == '/api/projects/activate':
            project_id = data.get('project_id')
            if project_id in PROJECTS:
                CURRENT_PROJECT_ID = project_id
                self._json({'success': True, 'project_id': project_id})
            else:
                self.send_error(404, 'Project not found')

        elif p == '/api/read-file':
            project_id = data.get('project_id', CURRENT_PROJECT_ID)
            if not project_id or project_id not in PROJECTS:
                self.send_error(400, 'No project loaded')
                return

            rel_path = data.get('path', '')
            if not rel_path:
                self.send_error(400, 'Missing path parameter')
                return

            full_path = Path(PROJECTS[project_id]['root']) / rel_path
            try:
                # Security: ensure we stay within PROJECT_ROOT
                full_path.resolve().relative_to(Path(PROJECTS[project_id]['root']).resolve())
                content = full_path.read_text(errors='replace')
                self._json({'path': rel_path, 'content': content})
            except ValueError:
                self.send_error(403, 'Access denied: path outside project')
            except FileNotFoundError:
                self.send_error(404, 'File not found')
            except Exception as e:
                self.send_error(500, str(e))

        elif p == '/api/exec-command':
            project_id = data.get('project_id', CURRENT_PROJECT_ID)
            if not project_id or project_id not in PROJECTS:
                self.send_error(400, 'No project loaded')
                return

            cmd = data.get('command', '')
            if not cmd:
                self.send_error(400, 'Missing command parameter')
                return

            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=str(PROJECTS[project_id]['root']),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                self._json({
                    'command': cmd,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                })
            except subprocess.TimeoutExpired:
                self.send_error(408, 'Command timeout')
            except Exception as e:
                self.send_error(500, str(e))

        elif p == '/api/glob-files':
            project_id = data.get('project_id', CURRENT_PROJECT_ID)
            if not project_id or project_id not in PROJECTS:
                self.send_error(400, 'No project loaded')
                return

            pattern = data.get('pattern', '')
            if not pattern:
                self.send_error(400, 'Missing pattern parameter')
                return

            try:
                import glob as gb
                root = Path(PROJECTS[project_id]['root'])
                matches = list(gb.glob(str(root / pattern), recursive=True))
                rel_matches = [str(Path(m).relative_to(root)) for m in matches if Path(m).is_file()]
                self._json({'pattern': pattern, 'matches': rel_matches})
            except Exception as e:
                self.send_error(500, str(e))

        elif p == '/api/load-project':
            path = data.get('path', '')
            if not path:
                self.send_error(400, 'Missing path parameter')
                return

            try:
                result = load_project(path)
                self._json(result)
            except ValueError as e:
                self.send_error(400, str(e))
            except Exception as e:
                self.send_error(500, str(e))

        elif p == '/api/chat':
            # Main chat endpoint
            message = data.get('message', '').strip()
            model = data.get('model', SELECTED_MODEL)
            include_files = data.get('include_files', [])
            project_id = data.get('project_id', CURRENT_PROJECT_ID)

            if not message:
                self.send_error(400, 'Missing message parameter')
                return

            try:
                # Build context from codebase
                context = build_codebase_context(message, project_id, include_files)

                # Call DeepSeek API
                response = call_deepseek(message, context, model, project_id)

                self._json({
                    'response': response,
                    'model': model,
                    'context_size': len(context)
                })
            except ValueError as e:
                self.send_error(400, str(e))
            except Exception as e:
                self.send_error(500, str(e))

        elif p == '/api/chat/clear':
            # Clear chat history
            project_id = data.get('project_id', CURRENT_PROJECT_ID)
            if project_id in PROJECTS:
                PROJECTS[project_id]['chat_history'] = []
            self._json({'success': True})

        elif p == '/api/chat/config':
            # Configure API key and model
            api_key = data.get('api_key', '').strip()
            model = data.get('model', '')

            if not api_key:
                self.send_error(400, 'API key cannot be empty')
                return

            DEEPSEEK_API_KEY = api_key

            if model:
                SELECTED_MODEL = model

            # Save to config file for persistence
            saved = save_config()

            self._json({
                'success': True,
                'model': SELECTED_MODEL,
                'api_key_set': True,
                'saved_to_file': saved
            })

        else:
            self.send_error(404)
    def _json(self, d):
        b = json.dumps(d).encode(); self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',len(b)); self.send_header('Access-Control-Allow-Origin','*'); self.end_headers(); self.wfile.write(b)
    def _text(self, t):
        b = t.encode(); self.send_response(200); self.send_header('Content-Type','text/plain'); self.send_header('Content-Length',len(b)); self.end_headers(); self.wfile.write(b)
    def _html(self):
        b = DASHBOARD_PATH.read_bytes(); self.send_response(200); self.send_header('Content-Type','text/html'); self.send_header('Content-Length',len(b)); self.end_headers(); self.wfile.write(b)
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}", flush=True)

def main():
    global CURRENT_PROJECT_ID, PROJECTS

    # Help flag
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
  ◆ CODEBASE CARTOGRAPHER - Usage

  Start with clean picker (no history):
    python3 cartographer.py --clean

  Start with recent projects:
    python3 cartographer.py

  Auto-load a project:
    python3 cartographer.py /path/to/project

  Options:
    --port <number>    Server port (default: 3000)
    --clean, --fresh   Clear recent projects history
    --help, -h         Show this help
        """)
        sys.exit(0)

    port = 3000
    if '--port' in sys.argv:
        idx = sys.argv.index('--port')
        if idx+1 < len(sys.argv): port = int(sys.argv[idx+1])

    # Clean flag: Clear recent projects history
    if '--clean' in sys.argv or '--fresh' in sys.argv:
        if RECENT_PROJECTS_FILE.exists():
            RECENT_PROJECTS_FILE.unlink()
            print(f"\n  🧹 Cleared recent projects history")

    if not DASHBOARD_PATH.exists():
        print(f"❌ dashboard.html not found at {DASHBOARD_PATH}"); sys.exit(1)

    print(f"\n  ◆ CODEBASE CARTOGRAPHER")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Load saved configuration (API key, model preferences)
    config_loaded = load_config()
    if config_loaded and DEEPSEEK_API_KEY:
        print(f"  🔑 API key loaded from config file")
    elif os.environ.get('DEEPSEEK_API_KEY'):
        print(f"  🔑 API key loaded from environment variable")

    # Load project if provided via command line (but skip if it's the Cartographer directory itself)
    if len(sys.argv) >= 2 and not sys.argv[1].startswith('--'):
        project_path = sys.argv[1]
        if not os.path.isdir(project_path):
            print(f"❌ Not a directory: {project_path}"); sys.exit(1)

        # Don't auto-load if scanning Cartographer's own directory
        project_path_resolved = str(Path(project_path).resolve())
        script_dir_resolved = str(SCRIPT_DIR)
        if project_path_resolved == script_dir_resolved:
            print(f"  📂 Cartographer directory detected - starting with project picker")
            print(f"  💡 Tip: Use a different project path to auto-load")
        else:
            print(f"  Scanning: {project_path}")
            result = load_project(project_path)
            m = result['scan_data']['metadata']
            print(f"  Files:    {m['total_files']}")
            print(f"  Edges:    {m['total_edges']}")
            print(f"  Bindings: {m['total_binding_points']}")
            print(f"  Health:   {m['health_score']}/100")
            print(f"  Languages:{', '.join(m['languages'])}")

            # Also save agent context
            ctx_path = Path(project_path) / 'CODEBASE_AGENT_CONTEXT.md'
            try:
                ctx_path.write_text(result['scan_data']['agent_context'])
                print(f"  📋 Agent context saved to: {ctx_path}")
            except: pass
    else:
        print(f"  No project loaded - select one from the dashboard")

    print(f"\n  🌐 Dashboard: http://localhost:{port}")
    print(f"  Press Ctrl+C to stop\n")

    server = HTTPServer(('', port), Handler)
    # Browser opening handled by launcher script - removed to prevent duplicate tabs
    # threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}')).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print("\n  Stopped."); server.server_close()

if __name__ == '__main__': main()
