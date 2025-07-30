# 😎 smugify

> Because why should you try harder?

**smugify** is a one-import wonder that replaces dozens of lines of Python boilerplate with a single, elegant command. Logging, alerts, formatting, HTTP calls, and CLI generation—all in one smug little package.

It’s not just a utility library. It’s a lifestyle.

---

## ✨ Features

- **`log()`** – Colorful, emoji-fueled terminal logs with timestamps.
- **`notify()`** – Cross-platform alerts (macOS, Linux, Windows, even console fallback).
- **`get()` / `post()`** – Lazy wrappers around HTTP requests (because you’re lazy).
- **`cli()`** – Turn any function into a CLI tool *automagically*.

---

## 🧪 Example

```python
from smugify import *

def main(name: str = "friend", times: int = 1):
    for _ in range(times):
        log(f"Hello, {name}!", "info")
    notify(f"Greeted {name} {times} times.")
    cat_fact = get("https://catfact.ninja/fact")
    log(f"Fun cat fact: {cat_fact['fact']}", "debug")

cli()
```

Run it like this:
```
$ python greet.py --name You --times 3
```
And bask in the glow of your own productivity.

🤔 Why?

“I replaced 2000 lines of enterprise glue code with smugify. Then I got promoted.”
– Definitely Real Engineer

Let’s face it: your code is fine. But it could be smugger.

📦 Installation
```
pip install smugify
```
Or just clone this repo like a rebel:
```
git clone https://github.com/Vu2n/smugify
cd smugify
```

📚 Docs

There are no docs. That’s how confident we are.

Just type from smugify import * and trust the vibes.

---

🐍 Requirements

Python 3.7+

requests

win10toast (for Windows notifications)

---

💡 Contributing

Want to make smugify even worse? Open a PR.

Want to ask a question? Open an issue.

Want to complain? Talk to your therapist.

---

⭐ Star Policy
If this repo made you feel something—anything—go ahead and smash that ⭐.

It’s the only currency we accept.

---

🧠 Fun Fact
If you stare at smugify long enough, it starts auto-formatting your life decisions.