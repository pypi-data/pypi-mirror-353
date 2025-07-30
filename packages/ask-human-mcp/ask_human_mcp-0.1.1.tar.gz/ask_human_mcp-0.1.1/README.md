# ask-human mcp 🧑‍💻🤝🤖

[![PyPI version](https://img.shields.io/pypi/v/ask-human-mcp?style=flat-square)](https://badge.fury.io/py/ask-human-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue?style=flat-square)](https://www.python.org/downloads/)
[!["Buy Me A Coffee"](https://img.shields.io/badge/buy_me_a_coffee-donate-orange?style=flat-square)](https://www.coff.ee/masonyarbrough)

stop your ai from hallucinating. gives it an escape route when confused instead of false confidence.

## the pain
ai blurts out an endpoint that never existed

the agent makes assumptions that are simply not true and has false confidence  

repeat x100 errors and your day is spent debugging false confidence and issues when you could simply ask a question

## the fix
an mcp server that lets the agent raise its hand instead of hallucinating. feels like mentoring a sharp intern who actually asks before guessing.

agent → ask_human()  
⬇  
question lands in ask_human.md  
⬇  
you swap "PENDING" for the answer  
⬇  
agent keeps coding  

### sample file:
```markdown
### Q8c4f1e2a
ts: 2025-01-15 14:30  
q: which auth endpoint do we use?  
ctx: building login form in auth.js  
answer: PENDING
```

you drop:
```markdown
answer: POST /api/v2/auth/login
```

boom. flow continues and hopefully the issues are solved.

## why it's good
- pip install ask-human-mcp → done
- zero config, cross-platform  
- watches the file, instant feedback
- multiple agents, no sweat
- locks + limits so nothing catches fire
- full q&a history in markdown (nice paper-trail for debugging)

## 30-sec setup

```bash
pip install ask-human-mcp
ask-human-mcp
```

`.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "ask-human": { "command": "ask-human-mcp" }
  }
}
```

restart cursor and vibe.

## how it works

1. ai gets stuck → calls `ask_human(question, context)`
2. question logged → appears in `ask_human.md` with unique ID  
3. human answers → replace "PENDING" with your response
4. ai continues → uses your answer to proceed

the ai receives your answer and keeps coding!

## config options (if you want them)

### command line
```bash
ask-human-mcp --help
ask-human-mcp --port 3000 --host 0.0.0.0  # http mode
ask-human-mcp --timeout 1800               # 30min timeout  
ask-human-mcp --file custom_qa.md          # custom q&a file
ask-human-mcp --max-pending 50             # max concurrent questions
ask-human-mcp --max-question-length 5000   # max question size
ask-human-mcp --rotation-size 10485760     # rotate file at 10mb
```

### different clients

cursor (local):
```json
{
  "mcpServers": {
    "ask-human": {
      "command": "ask-human-mcp",
      "args": ["--timeout", "900"]
    }
  }
}
```

cursor (http):
```json
{
  "mcpServers": {
    "ask-human": {
      "url": "http://localhost:3000/sse"
    }
  }
}
```

claude desktop:
```json
{
  "mcpServers": {
    "ask-human": {
      "command": "ask-human-mcp"
    }
  }
}
```

## what's in the box
- zero configuration → works out of the box
- file watching → instant response when you save answers  
- timeout handling → questions don't hang forever
- concurrent questions → handle multiple ai agents
- persistent logging → full q&a history in markdown
- cross-platform → windows, macos, linux
- mcp standard → works with any mcp client
- input validation → size limits and sanitization
- file rotation → automatic archiving of large files
- resource limits → prevent dos and memory leaks
- robust parsing → handles malformed markdown gracefully

## security stuff
- input sanitization → removes control characters and validates sizes
- file locking → prevents corruption from concurrent access  
- secure permissions → files created with restricted access
- resource limits → prevents memory exhaustion and dos attacks
- path validation → ensures files are written to safe locations

## limits (so nothing breaks)

| thing | default | what it does |
|-------|---------|--------------|
| question length | 10kb | max characters per question |
| context length | 50kb | max characters per context |
| pending questions | 100 | max concurrent questions |
| file size | 100mb | max ask file size |
| rotation size | 50mb | size at which files are archived |

## platform support
- windows → full support with native file locking
- macos → full support with fsevents file watching  
- linux → full support with inotify file watching

## api stuff

### ask_human(question, context="")
ask the human a question and wait for response.

```python
answer = await ask_human(
    "what database should i use for this project?",
    "building a chat app with 1000+ concurrent users"
)
```

### other tools
- `list_pending_questions()` → get questions waiting for answers
- `get_qa_stats()` → get stats about the q&a session

## development

### from source
```bash
git clone https://github.com/masonyarbrough/ask-human-mcp.git
cd ask-human-mcp
pip install -e ".[dev]"
ask-human-mcp
```

### tests
```bash
pytest tests/ -v
```

### code quality
```bash
black ask_human_mcp tests
ruff check ask_human_mcp tests  
mypy ask_human_mcp
```

## contributing

would love any contributors

### issues
use the github issue tracker to report bugs or request features.  
you can also just email me: mason@kallro.com 

include:
- python version
- operating system  
- mcp client (cursor, claude desktop, etc.)
- error messages or logs
- steps to reproduce

## changelog
see [CHANGELOG.md](CHANGELOG.md) for version history.

## license
mit license - see [LICENSE](LICENSE) file for details.

## thanks
- [model context protocol](https://github.com/modelcontextprotocol) for the excellent standard
- [anthropic](https://anthropic.com) for claude and mcp support  
- [cursor](https://cursor.sh) for mcp integration
- all contributors and users providing feedback
