warning: in the working copy of 'README.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'pyproject.toml', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/comit/cli.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/comit/config.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'src/comit/ui.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tests/test_ai.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tests/test_cli.py', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'tests/test_config.py', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/README.md b/README.md[m
[1mindex c745bd9..d075c55 100644[m
[1m--- a/README.md[m
[1m+++ b/README.md[m
[36m@@ -2,38 +2,26 @@[m
 [m
 > AI-powered Git commit messages that understand your project's commit style.[m
 [m
[31m-Comit is a lightweight developer CLI for Git. It analyzes your staged changes and recent commit history, learns your repository's commit conventions, and uses fast LLM inference through Groq to generate concise, accurate commit messages.[m
[32m+[m[32mComit is a lightweight developer CLI for Git. It analyzes your staged changes and recent commit history, learns your repository's commit conventions, and generates concise, accurate commit messages using your choice of AI provider.[m
 [m
 ## Features[m
 [m
[32m+[m[32m- **Multi-Provider Support** — Use Groq, Google Gemini, OpenAI, or local models with Ollama.[m
 - **Context-aware** — Analyzes your staged diff and recent commit history to match your repository's style.[m
 - **Developer in control** — Review, edit, regenerate, or cancel a suggested commit message before committing.[m
[32m+[m[32m- **Push Integration** — Optional safe remote pushing after creating a commit.[m
 - **Fast-track mode** — Use `-y` to automatically commit the generated message without confirmation.[m
[31m-- **Settings management** — Configure your API key and model interactively or via CLI commands without editing files.[m
[32m+[m[32m- **Settings management** — Configure your provider, model, API keys, and endpoints interactively or via CLI commands.[m
 - **Safe and non-destructive** — Only analyzes staged changes with `git diff --cached`. Comit never stages files or modifies unstaged changes.[m
[31m-- **Lightweight** — Built with Python, Typer, Rich, and the Groq SDK.[m
 [m
[31m-## How It Works[m
[32m+[m[32m## Supported Providers[m
 [m
[31m-```text[m
[31m-Staged Git Diff[m
[31m-      |[m
[31m-      v[m
[31m-Recent Commit History[m
[31m-      |[m
[31m-      v[m
[31m-   Groq LLM[m
[31m-      |[m
[31m-      v[m
[31m-Suggested Commit[m
[31m-      |[m
[31m-      v[m
[31m-User Review[m
[31m-[a] Accept  [e] Edit  [r] Regenerate  [c] Cancel[m
[31m-      |[m
[31m-      v[m
[31m-   Git Commit[m
[31m-```[m
[32m+[m[32m| Provider | Default Model | Authentication | Setup / Env Variable |[m
[32m+[m[32m| :--- | :--- | :--- | :--- |[m
[32m+[m[32m| **Groq** *(Default)* | `qwen/qwen3.8-27b` | API Key | `GROQ_API_KEY` |[m
[32m+[m[32m| **Google Gemini** | `gemini-2.5-flash` | API Key | `GEMINI_API_KEY` |[m
[32m+[m[32m| **OpenAI** | `gpt-4o-mini` | API Key | `OPENAI_API_KEY` |[m
[32m+[m[32m| **Ollama** | `llama3.2` | None (Local) | `OLLAMA_HOST` (default: `http://localhost:11434`) |[m
 [m
 ## Installation[m
 [m
[36m@@ -41,7 +29,6 @@[m [mUser Review[m
 [m
 - Python 3.11+[m
 - Git[m
[31m-- A Groq API key[m
 [m
 ### Install Comit[m
 [m
[36m@@ -57,10 +44,20 @@[m [mFor editable local development:[m
 pip install -e .[m
 ```[m
 [m
[31m-To install development and testing dependencies:[m
[32m+[m[32mTo install with additional provider SDKs:[m
 [m
 ```bash[m
[31m-pip install -e ".[test]"[m
[32m+[m[32m# Google Gemini SDK[m
[32m+[m[32mpip install -e ".[gemini]"[m
[32m+[m
[32m+[m[32m# OpenAI SDK[m
[32m+[m[32mpip install -e ".[openai]"[m
[32m+[m
[32m+[m[32m# Ollama SDK[m
[32m+[m[32mpip install -e ".[ollama]"[m
[32m+[m
[32m+[m[32m# All providers and testing tools[m
[32m+[m[32mpip install -e ".[all,test]"[m
 ```[m
 [m
 ### Windows PATH Note[m
[36m@@ -81,23 +78,25 @@[m [mCommon Python Scripts locations on Windows:[m
 git ai --version[m
 ```[m
 [m
[31m-Output:[m
[31m-```text[m
[31m-Comit version 0.1.0[m
[31m-```[m
[31m-[m
[31m-### 2. Configure Your API Key[m
[32m+[m[32m### 2. Configure Your Provider & API Key[m
 [m
[31m-Run the interactive settings manager:[m
[32m+[m[32mOpen the interactive settings menu:[m
 [m
 ```powershell[m
 git ai settings[m
 ```[m
 [m
[31m-Or set the key directly from the command line:[m
[32m+[m[32mOr configure via CLI:[m
 [m
 ```powershell[m
[32m+[m[32m# Select provider (groq, gemini, openai, ollama)[m
[32m+[m[32mgit ai settings set-provider groq[m
[32m+[m
[32m+[m[32m# Set API key for the active provider[m
 git ai settings set-key[m
[32m+[m
[32m+[m[32m# Or specify the provider directly[m
[32m+[m[32mgit ai settings set-key --provider gemini[m
 ```[m
 [m
 ### 3. Generate Commit Messages[m
[36m@@ -126,12 +125,13 @@[m [mComit provides an interactive configuration interface as well as non-interactive[m
 git ai settings[m
 ```[m
 [m
[31m-Menu options:[m
[32m+[m[32mOptions:[m
 1. View configuration[m
[31m-2. Configure Groq API key[m
[31m-3. Configure model[m
[31m-4. Reset configuration[m
[31m-5. Exit[m
[32m+[m[32m2. Select AI provider[m
[32m+[m[32m3. Configure API key / host[m
[32m+[m[32m4. Configure model[m
[32m+[m[32m5. Reset configuration[m
[32m+[m[32m6. Exit[m
 [m
 ### Settings Commands[m
 [m
[36m@@ -140,14 +140,26 @@[m [mMenu options:[m
   git ai settings show[m
   ```[m
 [m
[31m-- **Set Groq API key (hidden prompt):**[m
[32m+[m[32m- **Set AI provider:**[m
[32m+[m[32m  ```powershell[m
[32m+[m[32m  git ai settings set-provider gemini[m
[32m+[m[32m  ```[m
[32m+[m
[32m+[m[32m- **Set API key (masked prompt):**[m
   ```powershell[m
   git ai settings set-key[m
[32m+[m[32m  git ai settings set-key --provider openai[m
   ```[m
 [m
[31m-- **Set Groq model:**[m
[32m+[m[32m- **Set model:**[m
   ```powershell[m
   git ai settings set-model qwen/qwen3.8-27b[m
[32m+[m[32m  git ai settings set-model gpt-4o --provider openai[m
[32m+[m[32m  ```[m
[32m+[m
[32m+[m[32m- **Set Ollama host URL:**[m
[32m+[m[32m  ```powershell[m
[32m+[m[32m  git ai settings set-host http://localhost:11434[m
   ```[m
 [m
 - **Reset user configuration:**[m
[36m@@ -159,9 +171,12 @@[m [mMenu options:[m
 [m
 Comit resolves settings in the following order:[m
 [m
[31m-1. **Environment variables** (e.g. `GROQ_API_KEY`, `GROQ_MODEL`, or `.env` files in your workspace)[m
[31m-2. **User configuration** (`config.json` stored in your OS user directory: `%APPDATA%\comit` on Windows or `~/.config/comit` on Linux/macOS)[m
[31m-3. **Application defaults** (Model: `qwen/qwen3.8-27b`, Provider: `groq`)[m
[32m+[m[32m1. **Environment variables**:[m
[32m+[m[32m   - Provider: `COMIT_PROVIDER`[m
[32m+[m[32m   - Model: `COMIT_MODEL`, `GROQ_MODEL`, `GEMINI_MODEL`, `OPENAI_MODEL`, `OLLAMA_MODEL`[m
[32m+[m[32m   - API Keys / Endpoints: `GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `OLLAMA_HOST`[m
[32m+[m[32m2. **User configuration** (`config.json` stored in `%APPDATA%\comit` on Windows or `~/.config/comit` on Linux/macOS)[m
[32m+[m[32m3. **Application defaults** (Provider: `groq`, Model: `qwen/qwen3.8-27b`)[m
 [m
 ---[m
 [m
[36m@@ -205,7 +220,7 @@[m [mNavigate with **Up/Down arrow keys** or **k/j**, and press **Enter** to select.[m
 [m
 - **Accept (`a` or `1`)** — Creates the commit using the generated message. After the local commit succeeds, you are asked whether to push to the remote (`[y/N]`, default No).[m
 - **Edit (`e` or `2`)** — Opens an interactive inline editor with the generated message pre-populated for modification.[m
[31m-- **Regenerate (`r` or `3`)** — Requests an alternative commit message from Groq while avoiding previous attempts.[m
[32m+[m[32m- **Regenerate (`r` or `3`)** — Requests an alternative commit message from the AI provider while avoiding previous attempts.[m
 - **Cancel (`c`, `q`, or `4`)** — Exits cleanly without creating a commit or modifying staged changes.[m
 [m
 ---[m
[1mdiff --git a/pyproject.toml b/pyproject.toml[m
[1mindex 52d6786..90258b1 100644[m
[1m--- a/pyproject.toml[m
[1m+++ b/pyproject.toml[m
[36m@@ -41,6 +41,21 @@[m [mtest = [[m
 tests = [[m
     "pytest>=7.0.0",[m
 ][m
[32m+[m[32mgemini = [[m
[32m+[m[32m    "google-genai>=0.1.0",[m
[32m+[m[32m][m
[32m+[m[32mopenai = [[m
[32m+[m[32m    "openai>=1.0.0",[m
[32m+[m[32m][m
[32m+[m[32mollama = [[m
[32m+[m[32m    "ollama>=0.3.0",[m
[32m+[m[32m][m
[32m+[m[32mall = [[m
[32m+[m[32m    "groq>=0.9.0",[m
[32m+[m[32m    "google-genai>=0.1.0",[m
[32m+[m[32m    "openai>=1.0.0",[m
[32m+[m[32m    "ollama>=0.3.0",[m
[32m+[m[32m][m
 [m
 [project.scripts][m
 comit = "comit.cli:app"[m
[1mdiff --git a/src/comit/ai.py b/src/comit/ai.py[m
[1mdeleted file mode 100644[m
[1mindex 023579f..0000000[m
[1m--- a/src/comit/ai.py[m
[1m+++ /dev/null[m
[36m@@ -1,155 +0,0 @@[m
[31m-from __future__ import annotations[m
[31m-[m
[31m-from abc import ABC, abstractmethod[m
[31m-from typing import List, Optional[m
[31m-[m
[31m-from comit.config import get_api_key, get_model[m
[31m-from comit.prompts import SYSTEM_PROMPT, build_commit_prompt, sanitize_commit_message[m
[31m-[m
[31m-[m
[31m-class ComitAIError(Exception):[m
[31m-    pass[m
[31m-[m
[31m-[m
[31m-class APIKeyMissingError(ComitAIError):[m
[31m-    pass[m
[31m-[m
[31m-[m
[31m-class AIAuthenticationError(ComitAIError):[m
[31m-    pass[m
[31m-[m
[31m-[m
[31m-class AIServiceError(ComitAIError):[m
[31m-    pass[m
[31m-[m
[31m-[m
[31m-class AIResponseError(ComitAIError):[m
[31m-    pass[m
[31m-[m
[31m-[m
[31m-class AIProvider(ABC):[m
[31m-    @abstractmethod[m
[31m-    def generate_commit_message([m
[31m-        self,[m
[31m-        diff: str,[m
[31m-        recent_commits: Optional[List[str]] = None,[m
[31m-        avoid_messages: Optional[List[str]] = None,[m
[31m-    ) -> str:[m
[31m-        pass[m
[31m-[m
[31m-[m
[31m-class GroqProvider(AIProvider):[m
[31m-    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):[m
[31m-        self.api_key = get_api_key(api_key)[m
[31m-        if not self.api_key:[m
[31m-            raise APIKeyMissingError([m
[31m-                "GROQ_API_KEY is not configured.\n"[m
[31m-                "Run 'git ai settings' to set your API key or export GROQ_API_KEY in your shell."[m
[31m-            )[m
[31m-[m
[31m-        self.model = get_model(model)[m
[31m-        self._client = None[m
[31m-[m
[31m-    def _get_client(self):[m
[31m-        if self._client is None:[m
[31m-            try:[m
[31m-                from groq import Groq[m
[31m-                self._client = Groq(api_key=self.api_key)[m
[31m-            except ImportError as exc:[m
[31m-                raise AIServiceError([m
[31m-                    "The 'groq' package is not installed. Please run: pip install groq"[m
[31m-                ) from exc[m
[31m-            except Exception as exc:[m
[31m-                raise AIServiceError(f"Failed to initialize Groq client: {exc}") from exc[m
[31m-        return self._client[m
[31m-[m
[31m-    def generate_commit_message([m
[31m-        self,[m
[31m-        diff: str,[m
[31m-        recent_commits: Optional[List[str]] = None,[m
[31m-        avoid_messages: Optional[List[str]] = None,[m
[31m-    ) -> str:[m
[31m-        import groq[m
[31m-[m
[31m-        client = self._get_client()[m
[31m-        user_prompt = build_commit_prompt(diff, recent_commits, avoid_messages=avoid_messages)[m
[31m-        temperature = 0.7 if avoid_messages else 0.2[m
[31m-[m
[31m-        try:[m
[31m-            response = client.chat.completions.create([m
[31m-                model=self.model,[m
[31m-                messages=[[m
[31m-                    {"role": "system", "content": SYSTEM_PROMPT},[m
[31m-                    {"role": "user", "content": user_prompt},[m
[31m-                ],[m
[31m-                temperature=temperature,[m
[31m-                max_tokens=250,[m
[31m-            )[m
[31m-        except groq.AuthenticationError as exc:[m
[31m-            raise AIAuthenticationError([m
[31m-                "Groq authentication failed. Please verify that your GROQ_API_KEY is valid."[m
[31m-            ) from exc[m
[31m-        except groq.RateLimitError as exc:[m
[31m-            raise AIServiceError([m
[31m-                "Groq rate limit reached. Please wait a moment and try again."[m
[31m-            ) from exc[m
[31m-        except groq.APIConnectionError as exc:[m
[31m-            raise AIServiceError([m
[31m-                "Could not connect to the Groq API. Please check your internet connection."[m
[31m-            ) from exc[m
[31m-        except groq.APIStatusError as exc:[m
[31m-            raise AIServiceError([m
[31m-                f"Groq API returned an error (status {exc.status_code}): {exc.message}"[m
[31m-            ) from exc[m
[31m-        except Exception as exc:[m
[31m-            raise AIServiceError(f"Unexpected error while calling Groq API: {exc}") from exc[m
[31m-[m
[31m-        if not response.choices or not response.choices[0].message.content:[m
[31m-            raise AIResponseError("Groq API returned an empty response. Please try again.")[m
[31m-[m
[31m-        raw_message = response.choices[0].message.content[m
[31m-        cleaned = sanitize_commit_message(raw_message)[m
[31m-[m
[31m-        if avoid_messages and cleaned in avoid_messages:[m
[31m-            try:[m
[31m-                stronger_prompt = ([m
[31m-                    f"{user_prompt}\n\n"[m
[31m-                    "CRITICAL: The previous message was already generated. You MUST produce a distinct alternative phrasing."[m
[31m-                )[m
[31m-                retry_response = client.chat.completions.create([m
[31m-                    model=self.model,[m
[31m-                    messages=[[m
[31m-                        {"role": "system", "content": SYSTEM_PROMPT},[m
[31m-                        {"role": "user", "content": stronger_prompt},[m
[31m-                    ],[m
[31m-                    temperature=0.9,[m
[31m-                    max_tokens=250,[m
[31m-                )[m
[31m-                if retry_response.choices and retry_response.choices[0].message.content:[m
[31m-                    retry_cleaned = sanitize_commit_message(retry_response.choices[0].message.content)[m
[31m-                    if retry_cleaned:[m
[31m-                        return retry_cleaned[m
[31m-            except Exception:[m
[31m-                pass[m
[31m-[m
[31m-        if not cleaned:[m
[31m-            raise AIResponseError("Failed to extract a valid commit message from the AI response.")[m
[31m-[m
[31m-        return cleaned[m
[31m-[m
[31m-[m
[31m-def get_default_provider() -> AIProvider:[m
[31m-    return GroqProvider()[m
[31m-[m
[31m-[m
[31m-def generate_commit_message([m
[31m-    diff: str,[m
[31m-    recent_commits: Optional[List[str]] = None,[m
[31m-    avoid_messages: Optional[List[str]] = None,[m
[31m-    provider: Optional[AIProvider] = None,[m
[31m-) -> str:[m
[31m-    if provider is None:[m
[31m-        provider = get_default_provider()[m
[31m-    return provider.generate_commit_message([m
[31m-        diff=diff, recent_commits=recent_commits, avoid_messages=avoid_messages[m
[31m-    )[m
[1mdiff --git a/src/comit/cli.py b/src/comit/cli.py[m
[1mindex e9ec3af..5ae4dc7 100644[m
[1m--- a/src/comit/cli.py[m
[1m+++ b/src/comit/cli.py[m
[36m@@ -12,10 +12,13 @@[m [mfrom comit.ai import ([m
 )[m
 from comit.config import ([m
     get_config_summary,[m
[32m+[m[32m    get_provider,[m
     get_model,[m
[32m+[m[32m    get_ollama_host,[m
     set_user_config_value,[m
     reset_user_config,[m
     normalize_api_key,[m
[32m+[m[32m    SUPPORTED_PROVIDERS,[m
 )[m
 from comit.git import ([m
     GitError,[m
[36m@@ -42,8 +45,10 @@[m [mfrom comit.ui import ([m
     show_error,[m
     show_settings_summary,[m
     prompt_settings_menu,[m
[32m+[m[32m    prompt_provider_selection,[m
     prompt_api_key,[m
     prompt_model,[m
[32m+[m[32m    prompt_ollama_host,[m
     prompt_confirm_reset,[m
     prompt_confirm_push,[m
     show_push_success,[m
[36m@@ -116,7 +121,11 @@[m [mdef _perform_push(explicit_push: bool) -> None:[m
         return[m
 [m
     if not explicit_push:[m
[31m-        if not prompt_confirm_push():[m
[32m+[m[32m        try:[m
[32m+[m[32m            should_push = prompt_confirm_push()[m
[32m+[m[32m        except Exception:[m
[32m+[m[32m            should_push = False[m
[32m+[m[32m        if not should_push:[m
             show_push_skipped()[m
             return[m
 [m
[36m@@ -247,23 +256,40 @@[m [mdef commit_command([m
 [m
 def _run_interactive_settings() -> None:[m
     while True:[m
[31m-        choice = prompt_settings_menu()[m
[32m+[m[32m        current_p = get_provider()[m
[32m+[m[32m        choice = prompt_settings_menu(provider=current_p)[m
         if choice == "view":[m
             show_settings_summary(get_config_summary())[m
[32m+[m[32m        elif choice == "set_provider":[m
[32m+[m[32m            new_provider = prompt_provider_selection(current_provider=current_p)[m
[32m+[m[32m            if new_provider in SUPPORTED_PROVIDERS:[m
[32m+[m[32m                set_user_config_value("provider", new_provider)[m
[32m+[m[32m                show_step_success(f"AI provider set to {new_provider}.")[m
         elif choice == "set_key":[m
[31m-            key = prompt_api_key()[m
[31m-            norm_key = normalize_api_key(key)[m
[31m-            if norm_key:[m
[31m-                set_user_config_value("groq_api_key", norm_key)[m
[31m-                show_step_success("Groq API key saved.")[m
[32m+[m[32m            if current_p == "ollama":[m
[32m+[m[32m                current_host = get_ollama_host()[m
[32m+[m[32m                new_host = prompt_ollama_host(current_host)[m
[32m+[m[32m                if new_host:[m
[32m+[m[32m                    set_user_config_value("ollama_host", new_host)[m
[32m+[m[32m                    show_step_success(f"Ollama host set to {new_host}.")[m
             else:[m
[31m-                show_error("API key cannot be empty.")[m
[32m+[m[32m                key = prompt_api_key(provider=current_p)[m
[32m+[m[32m                norm_key = normalize_api_key(key)[m
[32m+[m[32m                if norm_key:[m
[32m+[m[32m                    set_user_config_value(f"{current_p}_api_key", norm_key)[m
[32m+[m[32m                    if current_p == "groq":[m
[32m+[m[32m                        set_user_config_value("groq_api_key", norm_key)[m
[32m+[m[32m                    show_step_success(f"{current_p.capitalize()} API key saved.")[m
[32m+[m[32m                else:[m
[32m+[m[32m                    show_error("API key cannot be empty.")[m
         elif choice == "set_model":[m
[31m-            current_model = get_model()[m
[31m-            new_model = prompt_model(current_model)[m
[32m+[m[32m            current_model = get_model(provider=current_p)[m
[32m+[m[32m            new_model = prompt_model(current_model, provider=current_p)[m
             if new_model:[m
[31m-                set_user_config_value("groq_model", new_model)[m
[31m-                show_step_success(f"Model set to {new_model}.")[m
[32m+[m[32m                set_user_config_value(f"{current_p}_model", new_model)[m
[32m+[m[32m                if current_p == "groq":[m
[32m+[m[32m                    set_user_config_value("groq_model", new_model)[m
[32m+[m[32m                show_step_success(f"{current_p.capitalize()} model set to {new_model}.")[m
         elif choice == "reset":[m
             if prompt_confirm_reset():[m
                 reset_user_config()[m
[36m@@ -283,29 +309,69 @@[m [mdef settings_show():[m
     show_settings_summary(get_config_summary())[m
 [m
 [m
[31m-@settings_app.command(name="set-model", help="Configure default model.")[m
[32m+[m[32m@settings_app.command(name="set-provider", help="Configure default AI provider.")[m
[32m+[m[32mdef settings_set_provider([m
[32m+[m[32m    provider: str = typer.Argument(..., help="Provider name (groq, gemini, openai, ollama)"),[m
[32m+[m[32m):[m
[32m+[m[32m    p = provider.strip().lower()[m
[32m+[m[32m    if p not in SUPPORTED_PROVIDERS:[m
[32m+[m[32m        show_error(f"Unsupported provider '{p}'. Supported providers: {', '.join(SUPPORTED_PROVIDERS)}")[m
[32m+[m[32m        raise typer.Exit(code=1)[m
[32m+[m[32m    set_user_config_value("provider", p)[m
[32m+[m[32m    show_step_success(f"AI provider set to {p}.")[m
[32m+[m
[32m+[m
[32m+[m[32m@settings_app.command(name="set-model", help="Configure default model for a provider.")[m
 def settings_set_model([m
[31m-    model: str = typer.Argument(..., help="Model name, e.g. qwen/qwen3.8-27b"),[m
[32m+[m[32m    model: str = typer.Argument(..., help="Model name"),[m
[32m+[m[32m    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Target provider (defaults to active provider)"),[m
 ):[m
     if not model.strip():[m
         show_error("Model name cannot be empty.")[m
         raise typer.Exit(code=1)[m
[31m-    set_user_config_value("groq_model", model.strip())[m
[31m-    show_step_success(f"Model set to {model.strip()}.")[m
[32m+[m[32m    p = (provider or get_provider()).strip().lower()[m
[32m+[m[32m    if p not in SUPPORTED_PROVIDERS:[m
[32m+[m[32m        show_error(f"Unsupported provider '{p}'. Supported providers: {', '.join(SUPPORTED_PROVIDERS)}")[m
[32m+[m[32m        raise typer.Exit(code=1)[m
[32m+[m[32m    set_user_config_value(f"{p}_model", model.strip())[m
[32m+[m[32m    if p == "groq":[m
[32m+[m[32m        set_user_config_value("groq_model", model.strip())[m
[32m+[m[32m    show_step_success(f"{p.capitalize()} model set to {model.strip()}.")[m
 [m
 [m
[31m-@settings_app.command(name="set-key", help="Configure Groq API key.")[m
[32m+[m[32m@settings_app.command(name="set-key", help="Configure API key for a provider.")[m
 def settings_set_key([m
[31m-    key: Optional[str] = typer.Option(None, "--key", "-k", help="Groq API key"),[m
[32m+[m[32m    key: Optional[str] = typer.Option(None, "--key", "-k", help="API key"),[m
[32m+[m[32m    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Target provider (defaults to active provider)"),[m
 ):[m
[32m+[m[32m    p = (provider or get_provider()).strip().lower()[m
[32m+[m[32m    if p == "ollama":[m
[32m+[m[32m        show_error("Ollama runs locally and does not use an API key. Use 'set-host' to configure the host.")[m
[32m+[m[32m        raise typer.Exit(code=1)[m
[32m+[m[32m    if p not in SUPPORTED_PROVIDERS:[m
[32m+[m[32m        show_error(f"Unsupported provider '{p}'. Supported providers: {', '.join(SUPPORTED_PROVIDERS)}")[m
[32m+[m[32m        raise typer.Exit(code=1)[m
     if not key:[m
[31m-        key = prompt_api_key()[m
[32m+[m[32m        key = prompt_api_key(provider=p)[m
     norm_key = normalize_api_key(key)[m
     if not norm_key:[m
         show_error("API key cannot be empty.")[m
         raise typer.Exit(code=1)[m
[31m-    set_user_config_value("groq_api_key", norm_key)[m
[31m-    show_step_success("Groq API key saved.")[m
[32m+[m[32m    set_user_config_value(f"{p}_api_key", norm_key)[m
[32m+[m[32m    if p == "groq":[m
[32m+[m[32m        set_user_config_value("groq_api_key", norm_key)[m
[32m+[m[32m    show_step_success(f"{p.capitalize()} API key saved.")[m
[32m+[m
[32m+[m
[32m+[m[32m@settings_app.command(name="set-host", help="Configure host URL for Ollama.")[m
[32m+[m[32mdef settings_set_host([m
[32m+[m[32m    host: str = typer.Argument(..., help="Ollama host URL, e.g. http://localhost:11434"),[m
[32m+[m[32m):[m
[32m+[m[32m    if not host.strip():[m
[32m+[m[32m        show_error("Host cannot be empty.")[m
[32m+[m[32m        raise typer.Exit(code=1)[m
[32m+[m[32m    set_user_config_value("ollama_host", host.strip())[m
[32m+[m[32m    show_step_success(f"Ollama host set to {host.strip()}.")[m
 [m
 [m
 @settings_app.command(name="reset", help="Reset user configuration.")[m
[1mdiff --git a/src/comit/config.py b/src/comit/config.py[m
[1mindex 7df3599..6f915a3 100644[m
[1m--- a/src/comit/config.py[m
[1m+++ b/src/comit/config.py[m
[36m@@ -11,6 +11,19 @@[m [mload_dotenv(find_dotenv(usecwd=True))[m
 [m
 DEFAULT_PROVIDER = "groq"[m
 DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"[m
[32m+[m[32mDEFAULT_GEMINI_MODEL = "gemini-2.5-flash"[m
[32m+[m[32mDEFAULT_OPENAI_MODEL = "gpt-4o-mini"[m
[32m+[m[32mDEFAULT_OLLAMA_MODEL = "llama3.2"[m
[32m+[m[32mDEFAULT_OLLAMA_HOST = "http://localhost:11434"[m
[32m+[m
[32m+[m[32mDEFAULT_MODELS = {[m
[32m+[m[32m    "groq": DEFAULT_GROQ_MODEL,[m
[32m+[m[32m    "gemini": DEFAULT_GEMINI_MODEL,[m
[32m+[m[32m    "openai": DEFAULT_OPENAI_MODEL,[m
[32m+[m[32m    "ollama": DEFAULT_OLLAMA_MODEL,[m
[32m+[m[32m}[m
[32m+[m
[32m+[m[32mSUPPORTED_PROVIDERS = ("groq", "gemini", "openai", "ollama")[m
 [m
 [m
 def get_config_dir() -> Path:[m
[36m@@ -73,13 +86,45 @@[m [mdef normalize_api_key(key: Optional[str]) -> Optional[str]:[m
     return val if val else None[m
 [m
 [m
[31m-def get_api_key(override_key: Optional[str] = None) -> Optional[str]:[m
[32m+[m[32mdef get_provider(override_provider: Optional[str] = None) -> str:[m
[32m+[m[32m    if override_provider and override_provider.strip():[m
[32m+[m[32m        return override_provider.strip().lower()[m
[32m+[m
[32m+[m[32m    for var in ("COMIT_PROVIDER", "comit_provider"):[m
[32m+[m[32m        val = os.getenv(var)[m
[32m+[m[32m        if val and val.strip():[m
[32m+[m[32m            return val.strip().lower()[m
[32m+[m
[32m+[m[32m    user_cfg = load_user_config()[m
[32m+[m[32m    cfg_val = user_cfg.get("provider")[m
[32m+[m[32m    if cfg_val and str(cfg_val).strip():[m
[32m+[m[32m        return str(cfg_val).strip().lower()[m
[32m+[m
[32m+[m[32m    return DEFAULT_PROVIDER[m
[32m+[m
[32m+[m
[32m+[m[32mdef get_api_key([m
[32m+[m[32m    override_key: Optional[str] = None,[m
[32m+[m[32m    provider: Optional[str] = None,[m
[32m+[m[32m) -> Optional[str]:[m
[32m+[m[32m    p = (provider or get_provider()).strip().lower()[m
[32m+[m
     if override_key:[m
         normalized = normalize_api_key(override_key)[m
         if normalized:[m
             return normalized[m
 [m
[31m-    for var in ("GROQ_API_KEY", "groq_api_key", "Groq_Api_Key", "GROQ_KEY"):[m
[32m+[m[32m    if p == "ollama":[m
[32m+[m[32m        return None[m
[32m+[m
[32m+[m[32m    env_vars_map = {[m
[32m+[m[32m        "groq": ("GROQ_API_KEY", "groq_api_key", "Groq_Api_Key", "GROQ_KEY"),[m
[32m+[m[32m        "gemini": ("GEMINI_API_KEY", "gemini_api_key", "Gemini_Api_Key"),[m
[32m+[m[32m        "openai": ("OPENAI_API_KEY", "openai_api_key", "Openai_Api_Key"),[m
[32m+[m[32m    }[m
[32m+[m[32m    vars_to_check = env_vars_map.get(p, (f"{p.upper()}_API_KEY",))[m
[32m+[m
[32m+[m[32m    for var in vars_to_check:[m
         val = os.getenv(var)[m
         if val:[m
             normalized = normalize_api_key(val)[m
[36m@@ -87,53 +132,79 @@[m [mdef get_api_key(override_key: Optional[str] = None) -> Optional[str]:[m
                 return normalized[m
 [m
     for k, v in os.environ.items():[m
[31m-        if k.strip().lower() in ("groq_api_key", "groq_key") and v:[m
[32m+[m[32m        if k.strip().lower() in [var.lower() for var in vars_to_check] and v:[m
             normalized = normalize_api_key(v)[m
             if normalized:[m
                 return normalized[m
 [m
     user_cfg = load_user_config()[m
[31m-    cfg_val = user_cfg.get("groq_api_key")[m
[31m-    if cfg_val:[m
[31m-        normalized = normalize_api_key(cfg_val)[m
[31m-        if normalized:[m
[31m-            return normalized[m
[32m+[m[32m    cfg_keys = [f"{p}_api_key", f"{p}_key"][m
[32m+[m[32m    if p == "groq":[m
[32m+[m[32m        cfg_keys.extend(["groq_api_key", "api_key"])[m
[32m+[m[32m    for key in cfg_keys:[m
[32m+[m[32m        cfg_val = user_cfg.get(key)[m
[32m+[m[32m        if cfg_val:[m
[32m+[m[32m            normalized = normalize_api_key(cfg_val)[m
[32m+[m[32m            if normalized:[m
[32m+[m[32m                return normalized[m
 [m
     return None[m
 [m
 [m
[31m-def get_model(override_model: Optional[str] = None) -> str:[m
[32m+[m[32mdef get_model([m
[32m+[m[32m    override_model: Optional[str] = None,[m
[32m+[m[32m    provider: Optional[str] = None,[m
[32m+[m[32m) -> str:[m
[32m+[m[32m    p = (provider or get_provider()).strip().lower()[m
[32m+[m
     if override_model and override_model.strip():[m
         return override_model.strip()[m
 [m
[31m-    for var in ("GROQ_MODEL", "groq_model", "Groq_Model"):[m
[32m+[m[32m    for var in ("COMIT_MODEL", "comit_model"):[m
[32m+[m[32m        val = os.getenv(var)[m
[32m+[m[32m        if val and val.strip():[m
[32m+[m[32m            return val.strip()[m
[32m+[m
[32m+[m[32m    env_vars_map = {[m
[32m+[m[32m        "groq": ("GROQ_MODEL", "groq_model", "Groq_Model"),[m
[32m+[m[32m        "gemini": ("GEMINI_MODEL", "gemini_model", "Gemini_Model"),[m
[32m+[m[32m        "openai": ("OPENAI_MODEL", "openai_model", "Openai_Model"),[m
[32m+[m[32m        "ollama": ("OLLAMA_MODEL", "ollama_model", "Ollama_Model"),[m
[32m+[m[32m    }[m
[32m+[m[32m    vars_to_check = env_vars_map.get(p, (f"{p.upper()}_MODEL",))[m
[32m+[m
[32m+[m[32m    for var in vars_to_check:[m
         val = os.getenv(var)[m
         if val and val.strip():[m
             return val.strip()[m
 [m
     user_cfg = load_user_config()[m
[31m-    cfg_val = user_cfg.get("groq_model") or user_cfg.get("model")[m
[32m+[m[32m    cfg_val = ([m
[32m+[m[32m        user_cfg.get(f"{p}_model")[m
[32m+[m[32m        or (user_cfg.get("model") if user_cfg.get("provider") == p or not user_cfg.get("provider") else None)[m
[32m+[m[32m        or (user_cfg.get("groq_model") if p == "groq" else None)[m
[32m+[m[32m    )[m
     if cfg_val and str(cfg_val).strip():[m
         return str(cfg_val).strip()[m
 [m
[31m-    return DEFAULT_GROQ_MODEL[m
[32m+[m[32m    return DEFAULT_MODELS.get(p, DEFAULT_GROQ_MODEL)[m
 [m
 [m
[31m-def get_provider(override_provider: Optional[str] = None) -> str:[m
[31m-    if override_provider and override_provider.strip():[m
[31m-        return override_provider.strip()[m
[32m+[m[32mdef get_ollama_host(override_host: Optional[str] = None) -> str:[m
[32m+[m[32m    if override_host and override_host.strip():[m
[32m+[m[32m        return override_host.strip()[m
 [m
[31m-    for var in ("COMIT_PROVIDER", "comit_provider"):[m
[32m+[m[32m    for var in ("OLLAMA_HOST", "ollama_host"):[m
         val = os.getenv(var)[m
         if val and val.strip():[m
             return val.strip()[m
 [m
     user_cfg = load_user_config()[m
[31m-    cfg_val = user_cfg.get("provider")[m
[32m+[m[32m    cfg_val = user_cfg.get("ollama_host")[m
     if cfg_val and str(cfg_val).strip():[m
         return str(cfg_val).strip()[m
 [m
[31m-    return DEFAULT_PROVIDER[m
[32m+[m[32m    return DEFAULT_OLLAMA_HOST[m
 [m
 [m
 def mask_api_key(key: Optional[str]) -> str:[m
[36m@@ -145,35 +216,64 @@[m [mdef mask_api_key(key: Optional[str]) -> str:[m
     return f"{clean[:4]}{'*' * 12}{clean[-4:]}"[m
 [m
 [m
[31m-def get_config_summary() -> Dict[str, Any]:[m
[31m-    api_key = get_api_key()[m
[31m-    model = get_model()[m
[31m-    provider = get_provider()[m
[32m+[m[32mdef get_config_summary(provider: Optional[str] = None) -> Dict[str, Any]:[m
[32m+[m[32m    p = get_provider(provider)[m
[32m+[m[32m    model = get_model(provider=p)[m
[32m+[m[32m    api_key = get_api_key(provider=p)[m
[32m+[m[32m    ollama_host = get_ollama_host()[m
     config_path = str(get_config_path())[m
[31m-    [m
[32m+[m[32m    user_cfg = load_user_config()[m
[32m+[m
     key_source = "not set"[m
[31m-    for var in ("GROQ_API_KEY", "groq_api_key", "Groq_Api_Key", "GROQ_KEY"):[m
[31m-        if os.getenv(var):[m
[31m-            key_source = f"environment ({var})"[m
[31m-            break[m
[31m-    if key_source == "not set" and load_user_config().get("groq_api_key"):[m
[31m-        key_source = "user configuration"[m
[32m+[m[32m    if p != "ollama":[m
[32m+[m[32m        env_vars = {[m
[32m+[m[32m            "groq": ("GROQ_API_KEY", "groq_api_key", "Groq_Api_Key", "GROQ_KEY"),[m
[32m+[m[32m            "gemini": ("GEMINI_API_KEY", "gemini_api_key", "Gemini_Api_Key"),[m
[32m+[m[32m            "openai": ("OPENAI_API_KEY", "openai_api_key", "Openai_Api_Key"),[m
[32m+[m[32m        }.get(p, (f"{p.upper()}_API_KEY",))[m
[32m+[m[32m        for var in env_vars:[m
[32m+[m[32m            if os.getenv(var):[m
[32m+[m[32m                key_source = f"environment ({var})"[m
[32m+[m[32m                break[m
[32m+[m[32m        if key_source == "not set" and (user_cfg.get(f"{p}_api_key") or (p == "groq" and user_cfg.get("groq_api_key"))):[m
[32m+[m[32m            key_source = "user configuration"[m
 [m
     model_source = "default"[m
[31m-    for var in ("GROQ_MODEL", "groq_model", "Groq_Model"):[m
[32m+[m[32m    for var in ("COMIT_MODEL", "comit_model"):[m
         if os.getenv(var):[m
             model_source = f"environment ({var})"[m
             break[m
[31m-    if model_source == "default" and (load_user_config().get("groq_model") or load_user_config().get("model")):[m
[32m+[m[32m    if model_source == "default":[m
[32m+[m[32m        provider_model_vars = {[m
[32m+[m[32m            "groq": ("GROQ_MODEL", "groq_model"),[m
[32m+[m[32m            "gemini": ("GEMINI_MODEL", "gemini_model"),[m
[32m+[m[32m            "openai": ("OPENAI_MODEL", "openai_model"),[m
[32m+[m[32m            "ollama": ("OLLAMA_MODEL", "ollama_model"),[m
[32m+[m[32m        }.get(p, ())[m
[32m+[m[32m        for var in provider_model_vars:[m
[32m+[m[32m            if os.getenv(var):[m
[32m+[m[32m                model_source = f"environment ({var})"[m
[32m+[m[32m                break[m
[32m+[m[32m    if model_source == "default" and (user_cfg.get(f"{p}_model") or user_cfg.get("model") or (p == "groq" and user_cfg.get("groq_model"))):[m
         model_source = "user configuration"[m
 [m
[32m+[m[32m    provider_source = "default"[m
[32m+[m[32m    for var in ("COMIT_PROVIDER", "comit_provider"):[m
[32m+[m[32m        if os.getenv(var):[m
[32m+[m[32m            provider_source = f"environment ({var})"[m
[32m+[m[32m            break[m
[32m+[m[32m    if provider_source == "default" and user_cfg.get("provider"):[m
[32m+[m[32m        provider_source = "user configuration"[m
[32m+[m
     return {[m
[31m-        "provider": provider,[m
[32m+[m[32m        "provider": p,[m
[32m+[m[32m        "provider_source": provider_source,[m
         "model": model,[m
         "model_source": model_source,[m
[31m-        "api_key_masked": mask_api_key(api_key),[m
[31m-        "api_key_source": key_source,[m
[31m-        "api_key_set": bool(api_key),[m
[32m+[m[32m        "api_key_masked": mask_api_key(api_key) if p != "ollama" else "N/A (local)",[m
[32m+[m[32m        "api_key_source": key_source if p != "ollama" else "N/A",[m
[32m+[m[32m        "api_key_set": bool(api_key) if p != "ollama" else True,[m
[32m+[m[32m        "ollama_host": ollama_host,[m
         "config_file": config_path,[m
         "config_exists": get_config_path().is_file(),[m
     }[m
[1mdiff --git a/src/comit/ui.py b/src/comit/ui.py[m
[1mindex b6019ec..880a47b 100644[m
[1m--- a/src/comit/ui.py[m
[1m+++ b/src/comit/ui.py[m
[36m@@ -224,17 +224,22 @@[m [mdef show_error(message: str) -> None:[m
 [m
 def show_settings_summary(summary: Dict[str, Any]) -> None:[m
     console.print("\n[bold cyan]Comit Configuration[/bold cyan]\n")[m
[31m-    console.print(f"  [bold]AI Provider:[/bold]        {summary['provider']}")[m
[31m-    console.print(f"  [bold]Groq Model:[/bold]         {summary['model']} [dim]({summary['model_source']})[/dim]")[m
[31m-    console.print(f"  [bold]Groq API Key:[/bold]       {summary['api_key_masked']} [dim]({summary['api_key_source']})[/dim]")[m
[32m+[m[32m    console.print(f"  [bold]AI Provider:[/bold]        {summary['provider']} [dim]({summary.get('provider_source', 'default')})[/dim]")[m
[32m+[m[32m    console.print(f"  [bold]Model:[/bold]              {summary['model']} [dim]({summary['model_source']})[/dim]")[m
[32m+[m[32m    if summary['provider'] == "ollama":[m
[32m+[m[32m        console.print(f"  [bold]Ollama Host:[/bold]        {summary['ollama_host']}")[m
[32m+[m[32m    else:[m
[32m+[m[32m        provider_title = summary['provider'].capitalize()[m
[32m+[m[32m        console.print(f"  [bold]{provider_title} API Key:[/bold]    {summary['api_key_masked']} [dim]({summary['api_key_source']})[/dim]")[m
     console.print(f"  [bold]Config File:[/bold]        {summary['config_file']}")[m
     console.print(f"  [bold]Config File Status:[/bold] {'Present' if summary['config_exists'] else 'Not created (using defaults)'}\n")[m
 [m
 [m
[31m-def prompt_settings_menu() -> str:[m
[32m+[m[32mdef prompt_settings_menu(provider: str = "groq") -> str:[m
     options = [[m
         ("view", "View configuration"),[m
[31m-        ("set_key", "Configure Groq API key"),[m
[32m+[m[32m        ("set_provider", "Select AI provider"),[m
[32m+[m[32m        ("set_key", f"Configure {provider.capitalize()} API key" if provider != "ollama" else "Configure Ollama host"),[m
         ("set_model", "Configure model"),[m
         ("reset", "Reset configuration"),[m
         ("exit", "Exit"),[m
[36m@@ -242,31 +247,64 @@[m [mdef prompt_settings_menu() -> str:[m
     return select_arrow_menu(options, prompt_text="Settings Menu", default_index=0, allow_quit_key=True)[m
 [m
 [m
[31m-def prompt_api_key() -> str:[m
[32m+[m[32mdef prompt_provider_selection(current_provider: str = "groq") -> str:[m
[32m+[m[32m    options = [[m
[32m+[m[32m        ("groq", "Groq (Fast inference, default)"),[m
[32m+[m[32m        ("gemini", "Google Gemini"),[m
[32m+[m[32m        ("openai", "OpenAI"),[m
[32m+[m[32m        ("ollama", "Ollama (Local models)"),[m
[32m+[m[32m    ][m
[32m+[m[32m    idx = 0[m
[32m+[m[32m    for i, (p_id, _) in enumerate(options):[m
[32m+[m[32m        if p_id == current_provider:[m
[32m+[m[32m            idx = i[m
[32m+[m[32m            break[m
[32m+[m[32m    return select_arrow_menu(options, prompt_text="Select AI Provider", default_index=idx, allow_quit_key=True)[m
[32m+[m
[32m+[m
[32m+[m[32mdef prompt_api_key(provider: str = "groq") -> str:[m
[32m+[m[32m    provider_title = provider.capitalize()[m
     key = Prompt.ask([m
[31m-        "[bold]Enter Groq API Key[/bold]",[m
[32m+[m[32m        f"[bold]Enter {provider_title} API Key[/bold]",[m
         password=True,[m
         console=console,[m
     ).strip()[m
     return key[m
 [m
 [m
[31m-def prompt_model(current_model: str) -> str:[m
[32m+[m[32mdef prompt_model(current_model: str, provider: str = "groq") -> str:[m
[32m+[m[32m    provider_title = provider.capitalize()[m
     if sys.stdin.isatty() and sys.stdout.isatty():[m
         try:[m
             from prompt_toolkit import prompt as pt_prompt[m
[31m-            model = pt_prompt("Enter Groq Model: ", default=current_model).strip()[m
[32m+[m[32m            model = pt_prompt(f"Enter {provider_title} Model: ", default=current_model).strip()[m
             return model if model else current_model[m
         except Exception:[m
             pass[m
     model = Prompt.ask([m
[31m-        "[bold]Enter Groq Model[/bold]",[m
[32m+[m[32m        f"[bold]Enter {provider_title} Model[/bold]",[m
         default=current_model,[m
         console=console,[m
     ).strip()[m
     return model if model else current_model[m
 [m
 [m
[32m+[m[32mdef prompt_ollama_host(current_host: str = "http://localhost:11434") -> str:[m
[32m+[m[32m    if sys.stdin.isatty() and sys.stdout.isatty():[m
[32m+[m[32m        try:[m
[32m+[m[32m            from prompt_toolkit import prompt as pt_prompt[m
[32m+[m[32m            host = pt_prompt("Enter Ollama Host: ", default=current_host).strip()[m
[32m+[m[32m            return host if host else current_host[m
[32m+[m[32m        except Exception:[m
[32m+[m[32m            pass[m
[32m+[m[32m    host = Prompt.ask([m
[32m+[m[32m        "[bold]Enter Ollama Host[/bold]",[m
[32m+[m[32m        default=current_host,[m
[32m+[m[32m        console=console,[m
[32m+[m[32m    ).strip()[m
[32m+[m[32m    return host if host else current_host[m
[32m+[m
[32m+[m
 def prompt_confirm_reset() -> bool:[m
     return Confirm.ask([m
         "[bold yellow]Are you sure you want to reset all user configuration?[/bold yellow]",[m
[1mdiff --git a/tests/test_ai.py b/tests/test_ai.py[m
[1mindex b754f6d..6358b58 100644[m
[1m--- a/tests/test_ai.py[m
[1m+++ b/tests/test_ai.py[m
[36m@@ -2,21 +2,49 @@[m [mfrom unittest.mock import MagicMock, patch[m
 import pytest[m
 [m
 from comit.ai import ([m
[32m+[m[32m    AIProvider,[m
     GroqProvider,[m
[32m+[m[32m    GeminiProvider,[m
[32m+[m[32m    OpenAIProvider,[m
[32m+[m[32m    OllamaProvider,[m
[32m+[m[32m    get_provider,[m
[32m+[m[32m    get_default_provider,[m
     APIKeyMissingError,[m
     AIAuthenticationError,[m
     AIServiceError,[m
     AIResponseError,[m
[32m+[m[32m    UnsupportedProviderError,[m
     generate_commit_message,[m
 )[m
 [m
 [m
[32m+[m[32mdef test_factory_get_provider():[m
[32m+[m[32m    groq_p = get_provider("groq", api_key="mock_key")[m
[32m+[m[32m    assert isinstance(groq_p, GroqProvider)[m
[32m+[m
[32m+[m[32m    gemini_p = get_provider("gemini", api_key="mock_key")[m
[32m+[m[32m    assert isinstance(gemini_p, GeminiProvider)[m
[32m+[m
[32m+[m[32m    openai_p = get_provider("openai", api_key="mock_key")[m
[32m+[m[32m    assert isinstance(openai_p, OpenAIProvider)[m
[32m+[m
[32m+[m[32m    ollama_p = get_provider("ollama")[m
[32m+[m[32m    assert isinstance(ollama_p, OllamaProvider)[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_factory_unsupported_provider():[m
[32m+[m[32m    with pytest.raises(UnsupportedProviderError) as exc_info:[m
[32m+[m[32m        get_provider("unsupported_ai")[m
[32m+[m[32m    assert "Unsupported AI provider" in str(exc_info.value)[m
[32m+[m[32m    assert "groq" in str(exc_info.value)[m
[32m+[m
[32m+[m
 def test_groq_provider_missing_key(monkeypatch):[m
     monkeypatch.delenv("GROQ_API_KEY", raising=False)[m
     monkeypatch.delenv("groq_api_key", raising=False)[m
     monkeypatch.delenv("Groq_Api_Key", raising=False)[m
     monkeypatch.delenv("GROQ_KEY", raising=False)[m
[31m-    with patch("comit.ai.get_api_key", return_value=None):[m
[32m+[m[32m    with patch("comit.config.get_api_key", return_value=None):[m
         with pytest.raises(APIKeyMissingError) as exc_info:[m
             GroqProvider(api_key="")[m
         assert "GROQ_API_KEY" in str(exc_info.value)[m
[36m@@ -62,7 +90,6 @@[m [mdef test_groq_provider_regeneration_with_avoid():[m
     assert result == "feat: add theme customizer"[m
     call_args = mock_client.chat.completions.create.call_args[1][m
     assert call_args["temperature"] == 0.7[m
[31m-    # Check avoid messages included in prompt[m
     user_msg = [m["content"] for m in call_args["messages"] if m["role"] == "user"][0][m
     assert "feat: support custom themes" in user_msg[m
 [m
[36m@@ -104,8 +131,115 @@[m [mdef test_groq_provider_empty_response():[m
         provider.generate_commit_message(diff="diff...", recent_commits=[])[m
 [m
 [m
[32m+[m[32mdef test_gemini_provider_missing_key(monkeypatch):[m
[32m+[m[32m    monkeypatch.delenv("GEMINI_API_KEY", raising=False)[m
[32m+[m[32m    monkeypatch.delenv("gemini_api_key", raising=False)[m
[32m+[m[32m    with patch("comit.config.get_api_key", return_value=None):[m
[32m+[m[32m        with pytest.raises(APIKeyMissingError) as exc_info:[m
[32m+[m[32m            GeminiProvider(api_key="")[m
[32m+[m[32m        assert "GEMINI_API_KEY" in str(exc_info.value)[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_gemini_provider_success():[m
[32m+[m[32m    mock_response = MagicMock()[m
[32m+[m[32m    mock_response.text = "feat: add gemini provider"[m
[32m+[m
[32m+[m[32m    mock_client = MagicMock()[m
[32m+[m[32m    mock_client.models.generate_content.return_value = mock_response[m
[32m+[m
[32m+[m[32m    provider = GeminiProvider(api_key="mock_gemini_key")[m
[32m+[m[32m    provider._client = mock_client[m
[32m+[m
[32m+[m[32m    result = provider.generate_commit_message([m
[32m+[m[32m        diff="diff --git a/app.py...",[m
[32m+[m[32m        recent_commits=["feat: init"],[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    assert result == "feat: add gemini provider"[m
[32m+[m[32m    mock_client.models.generate_content.assert_called_once()[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_gemini_provider_empty_response():[m
[32m+[m[32m    mock_response = MagicMock()[m
[32m+[m[32m    mock_response.text = ""[m
[32m+[m
[32m+[m[32m    mock_client = MagicMock()[m
[32m+[m[32m    mock_client.models.generate_content.return_value = mock_response[m
[32m+[m
[32m+[m[32m    provider = GeminiProvider(api_key="mock_gemini_key")[m
[32m+[m[32m    provider._client = mock_client[m
[32m+[m
[32m+[m[32m    with pytest.raises(AIResponseError):[m
[32m+[m[32m        provider.generate_commit_message(diff="diff...", recent_commits=[])[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_openai_provider_missing_key(monkeypatch):[m
[32m+[m[32m    monkeypatch.delenv("OPENAI_API_KEY", raising=False)[m
[32m+[m[32m    monkeypatch.delenv("openai_api_key", raising=False)[m
[32m+[m[32m    with patch("comit.config.get_api_key", return_value=None):[m
[32m+[m[32m        with pytest.raises(APIKeyMissingError) as exc_info:[m
[32m+[m[32m            OpenAIProvider(api_key="")[m
[32m+[m[32m        assert "OPENAI_API_KEY" in str(exc_info.value)[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_openai_provider_success():[m
[32m+[m[32m    mock_choice = MagicMock()[m
[32m+[m[32m    mock_choice.message.content = "feat: add openai provider"[m
[32m+[m[32m    mock_response = MagicMock(choices=[mock_choice])[m
[32m+[m
[32m+[m[32m    mock_client = MagicMock()[m
[32m+[m[32m    mock_client.chat.completions.create.return_value = mock_response[m
[32m+[m
[32m+[m[32m    provider = OpenAIProvider(api_key="mock_openai_key")[m
[32m+[m[32m    provider._client = mock_client[m
[32m+[m
[32m+[m[32m    result = provider.generate_commit_message([m
[32m+[m[32m        diff="diff --git a/app.py...",[m
[32m+[m[32m        recent_commits=["feat: init"],[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    assert result == "feat: add openai provider"[m
[32m+[m[32m    mock_client.chat.completions.create.assert_called_once()[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_ollama_provider_no_api_key_required():[m
[32m+[m[32m    provider = OllamaProvider(model="llama3.2")[m
[32m+[m[32m    assert provider.model == "llama3.2"[m
[32m+[m[32m    assert "localhost" in provider.host or "127.0.0.1" in provider.host[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_ollama_provider_success():[m
[32m+[m[32m    mock_client = MagicMock()[m
[32m+[m[32m    mock_client.chat.return_value = {[m
[32m+[m[32m        "message": {"content": "feat: add ollama local inference"}[m
[32m+[m[32m    }[m
[32m+[m
[32m+[m[32m    provider = OllamaProvider(model="llama3.2")[m
[32m+[m[32m    provider._client = mock_client[m
[32m+[m
[32m+[m[32m    result = provider.generate_commit_message([m
[32m+[m[32m        diff="diff --git a/app.py...",[m
[32m+[m[32m        recent_commits=["feat: init"],[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    assert result == "feat: add ollama local inference"[m
[32m+[m[32m    mock_client.chat.assert_called_once()[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_ollama_provider_connection_error():[m
[32m+[m[32m    mock_client = MagicMock()[m
[32m+[m[32m    mock_client.chat.side_effect = Exception("Failed to connect to host: ConnectionRefusedError")[m
[32m+[m
[32m+[m[32m    provider = OllamaProvider(model="llama3.2")[m
[32m+[m[32m    provider._client = mock_client[m
[32m+[m
[32m+[m[32m    with pytest.raises(AIServiceError) as exc_info:[m
[32m+[m[32m        provider.generate_commit_message(diff="diff...", recent_commits=[])[m
[32m+[m[32m    assert "Could not connect to Ollama server" in str(exc_info.value)[m
[32m+[m
[32m+[m
 def test_generate_commit_message_with_custom_provider():[m
[31m-    class DummyProvider:[m
[32m+[m[32m    class DummyProvider(AIProvider):[m
         def generate_commit_message(self, diff, recent_commits=None, avoid_messages=None):[m
             return "refactor: simplify test setup"[m
 [m
[1mdiff --git a/tests/test_cli.py b/tests/test_cli.py[m
[1mindex 785b405..785df89 100644[m
[1m--- a/tests/test_cli.py[m
[1m+++ b/tests/test_cli.py[m
[36m@@ -101,7 +101,7 @@[m [mdef test_cli_settings_set_model(tmp_path, monkeypatch):[m
     monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)[m
     result = runner.invoke(app, ["settings", "set-model", "test-llama-model"])[m
     assert result.exit_code == 0[m
[31m-    assert "Model set to test-llama-model" in result.stdout[m
[32m+[m[32m    assert "model set to test-llama-model" in result.stdout.lower()[m
 [m
     from comit.config import get_model[m
     monkeypatch.delenv("GROQ_MODEL", raising=False)[m
[36m@@ -136,7 +136,7 @@[m [mdef test_cli_settings_reset(tmp_path, monkeypatch):[m
 [m
 def test_cli_settings_interactive_exit(tmp_path, monkeypatch):[m
     monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)[m
[31m-    result = runner.invoke(app, ["settings"], input="5\n")[m
[32m+[m[32m    result = runner.invoke(app, ["settings"], input="6\n")[m
     assert result.exit_code == 0[m
     assert "Settings Menu" in result.stdout[m
 [m
[36m@@ -148,6 +148,35 @@[m [mdef test_cli_settings_interactive_q_exit(tmp_path, monkeypatch):[m
     assert "Settings Menu" in result.stdout[m
 [m
 [m
[32m+[m[32mdef test_cli_settings_set_provider(tmp_path, monkeypatch):[m
[32m+[m[32m    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)[m
[32m+[m[32m    result = runner.invoke(app, ["settings", "set-provider", "gemini"])[m
[32m+[m[32m    assert result.exit_code == 0[m
[32m+[m[32m    assert "AI provider set to gemini" in result.stdout[m
[32m+[m
[32m+[m[32m    from comit.config import get_provider[m
[32m+[m[32m    monkeypatch.delenv("COMIT_PROVIDER", raising=False)[m
[32m+[m[32m    assert get_provider() == "gemini"[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_cli_settings_set_provider_unsupported(tmp_path, monkeypatch):[m
[32m+[m[32m    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)[m
[32m+[m[32m    result = runner.invoke(app, ["settings", "set-provider", "unknown_provider"])[m
[32m+[m[32m    assert result.exit_code == 1[m
[32m+[m[32m    assert "Unsupported provider" in result.stderr or "Unsupported provider" in result.stdout[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_cli_settings_set_host(tmp_path, monkeypatch):[m
[32m+[m[32m    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)[m
[32m+[m[32m    result = runner.invoke(app, ["settings", "set-host", "http://127.0.0.1:11434"])[m
[32m+[m[32m    assert result.exit_code == 0[m
[32m+[m[32m    assert "Ollama host set to http://127.0.0.1:11434" in result.stdout[m
[32m+[m
[32m+[m[32m    from comit.config import get_ollama_host[m
[32m+[m[32m    monkeypatch.delenv("OLLAMA_HOST", raising=False)[m
[32m+[m[32m    assert get_ollama_host() == "http://127.0.0.1:11434"[m
[32m+[m
[32m+[m
 def test_cli_settings_set_key_double_quoted(tmp_path, monkeypatch):[m
     monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)[m
     result = runner.invoke(app, ["settings", "set-key", "--key", '"gsk_quoted_1234567890"'])[m
[36m@@ -160,7 +189,7 @@[m [mdef test_cli_settings_set_key_double_quoted(tmp_path, monkeypatch):[m
     monkeypatch.delenv("Groq_Api_Key", raising=False)[m
     monkeypatch.delenv("GROQ_KEY", raising=False)[m
     assert load_user_config()["groq_api_key"] == "gsk_quoted_1234567890"[m
[31m-    assert get_api_key() == "gsk_quoted_1234567890"[m
[32m+[m[32m    assert get_api_key(provider="groq") == "gsk_quoted_1234567890"[m
 [m
 [m
 def test_cli_settings_set_key_single_quoted(tmp_path, monkeypatch):[m
[36m@@ -175,7 +204,26 @@[m [mdef test_cli_settings_set_key_single_quoted(tmp_path, monkeypatch):[m
     monkeypatch.delenv("Groq_Api_Key", raising=False)[m
     monkeypatch.delenv("GROQ_KEY", raising=False)[m
     assert load_user_config()["groq_api_key"] == "gsk_single_1234567890"[m
[31m-    assert get_api_key() == "gsk_single_1234567890"[m
[32m+[m[32m    assert get_api_key(provider="groq") == "gsk_single_1234567890"[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_cli_settings_set_key_gemini(tmp_path, monkeypatch):[m
[32m+[m[32m    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)[m
[32m+[m[32m    result = runner.invoke(app, ["settings", "set-key", "--provider", "gemini", "--key", "AIzaSy_custom_key"])[m
[32m+[m[32m    assert result.exit_code == 0[m
[32m+[m[32m    assert "Gemini API key saved" in result.stdout[m
[32m+[m
[32m+[m[32m    from comit.config import get_api_key, load_user_config[m
[32m+[m[32m    monkeypatch.delenv("GEMINI_API_KEY", raising=False)[m
[32m+[m[32m    assert load_user_config()["gemini_api_key"] == "AIzaSy_custom_key"[m
[32m+[m[32m    assert get_api_key(provider="gemini") == "AIzaSy_custom_key"[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_cli_settings_set_key_ollama_rejected(tmp_path, monkeypatch):[m
[32m+[m[32m    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)[m
[32m+[m[32m    result = runner.invoke(app, ["settings", "set-key", "--provider", "ollama", "--key", "any_key"])[m
[32m+[m[32m    assert result.exit_code == 1[m
[32m+[m[32m    assert "Ollama runs locally" in result.stderr or "Ollama runs locally" in result.stdout[m
 [m
 [m
 @patch("comit.cli.prompt_settings_menu", side_effect=["set_key", "exit"])[m
[36m@@ -192,7 +240,21 @@[m [mdef test_cli_settings_interactive_set_key_normalization(mock_prompt_key, mock_pr[m
     monkeypatch.delenv("Groq_Api_Key", raising=False)[m
     monkeypatch.delenv("GROQ_KEY", raising=False)[m
     assert load_user_config()["groq_api_key"] == "gsk_interactive_1234567890"[m
[31m-    assert get_api_key() == "gsk_interactive_1234567890"[m
[32m+[m[32m    assert get_api_key(provider="groq") == "gsk_interactive_1234567890"[m
[32m+[m
[32m+[m
[32m+[m[32m@patch("comit.cli.prompt_settings_menu", side_effect=["set_provider", "exit"])[m
[32m+[m[32m@patch("comit.cli.prompt_provider_selection", return_value="openai")[m
[32m+[m[32mdef test_cli_settings_interactive_set_provider(mock_select_p, mock_menu, tmp_path, monkeypatch):[m
[32m+[m[32m    monkeypatch.setattr("comit.config.get_config_dir", lambda: tmp_path)[m
[32m+[m[32m    result = runner.invoke(app, ["settings"])[m
[32m+[m[32m    assert result.exit_code == 0[m
[32m+[m[32m    assert "AI provider set to openai" in result.stdout[m
[32m+[m
[32m+[m[32m    from comit.config import get_provider[m
[32m+[m[32m    monkeypatch.delenv("COMIT_PROVIDER", raising=False)[m
[32m+[m[32m    assert get_provider() == "openai"[m
[32m+[m
 [m
 [m
 @patch("comit.cli.is_git_repository", return_value=True)[m
[1mdiff --git a/tests/test_config.py b/tests/test_config.py[m
[1mindex fc92c33..ec1eb9f 100644[m
[1m--- a/tests/test_config.py[m
[1m+++ b/tests/test_config.py[m
[36m@@ -14,10 +14,15 @@[m [mfrom comit.config import ([m
     get_api_key,[m
     get_model,[m
     get_provider,[m
[32m+[m[32m    get_ollama_host,[m
     mask_api_key,[m
     normalize_api_key,[m
     get_config_summary,[m
     DEFAULT_GROQ_MODEL,[m
[32m+[m[32m    DEFAULT_GEMINI_MODEL,[m
[32m+[m[32m    DEFAULT_OPENAI_MODEL,[m
[32m+[m[32m    DEFAULT_OLLAMA_MODEL,[m
[32m+[m[32m    DEFAULT_OLLAMA_HOST,[m
     DEFAULT_PROVIDER,[m
 )[m
 [m
[36m@@ -63,37 +68,70 @@[m [mdef test_config_precedence_api_key(temp_config_dir: Path, monkeypatch):[m
     monkeypatch.delenv("Groq_Api_Key", raising=False)[m
     monkeypatch.delenv("GROQ_KEY", raising=False)[m
 [m
[31m-    # 1. No env and no config[m
[31m-    assert get_api_key() is None[m
[32m+[m[32m    assert get_api_key(provider="groq") is None[m
 [m
[31m-    # 2. User config set[m
     set_user_config_value("groq_api_key", "gsk_user_config_key")[m
[31m-    assert get_api_key() == "gsk_user_config_key"[m
[32m+[m[32m    assert get_api_key(provider="groq") == "gsk_user_config_key"[m
 [m
[31m-    # 3. Environment variable overrides user config[m
     monkeypatch.setenv("GROQ_API_KEY", "gsk_env_key")[m
[31m-    assert get_api_key() == "gsk_env_key"[m
[32m+[m[32m    assert get_api_key(provider="groq") == "gsk_env_key"[m
 [m
[31m-    # 4. Explicit override takes absolute precedence[m
[31m-    assert get_api_key("gsk_override_key") == "gsk_override_key"[m
[32m+[m[32m    assert get_api_key("gsk_override_key", provider="groq") == "gsk_override_key"[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_config_precedence_gemini_key(temp_config_dir: Path, monkeypatch):[m
[32m+[m[32m    monkeypatch.delenv("GEMINI_API_KEY", raising=False)[m
[32m+[m[32m    assert get_api_key(provider="gemini") is None[m
[32m+[m
[32m+[m[32m    set_user_config_value("gemini_api_key", "AIzaSy_user_key")[m
[32m+[m[32m    assert get_api_key(provider="gemini") == "AIzaSy_user_key"[m
[32m+[m
[32m+[m[32m    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSy_env_key")[m
[32m+[m[32m    assert get_api_key(provider="gemini") == "AIzaSy_env_key"[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_config_precedence_openai_key(temp_config_dir: Path, monkeypatch):[m
[32m+[m[32m    monkeypatch.delenv("OPENAI_API_KEY", raising=False)[m
[32m+[m[32m    assert get_api_key(provider="openai") is None[m
[32m+[m
[32m+[m[32m    set_user_config_value("openai_api_key", "sk-proj-user-key")[m
[32m+[m[32m    assert get_api_key(provider="openai") == "sk-proj-user-key"[m
[32m+[m
[32m+[m[32m    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-env-key")[m
[32m+[m[32m    assert get_api_key(provider="openai") == "sk-proj-env-key"[m
[32m+[m
[32m+[m
[32m+[m[32mdef test_ollama_host_and_key(temp_config_dir: Path, monkeypatch):[m
[32m+[m[32m    monkeypatch.delenv("OLLAMA_HOST", raising=False)[m
[32m+[m[32m    assert get_api_key(provider="ollama") is None[m
[32m+[m[32m    assert get_ollama_host() == DEFAULT_OLLAMA_HOST[m
[32m+[m
[32m+[m[32m    set_user_config_value("ollama_host", "http://192.168.1.50:11434")[m
[32m+[m[32m    assert get_ollama_host() == "http://192.168.1.50:11434"[m
[32m+[m
[32m+[m[32m    monkeypatch.setenv("OLLAMA_HOST", "http://remote-gpu:11434")[m
[32m+[m[32m    assert get_ollama_host() == "http://remote-gpu:11434"[m
 [m
 [m
 def test_config_precedence_model(temp_config_dir: Path, monkeypatch):[m
     monkeypatch.delenv("GROQ_MODEL", raising=False)[m
     monkeypatch.delenv("groq_model", raising=False)[m
[32m+[m[32m    monkeypatch.delenv("COMIT_MODEL", raising=False)[m
 [m
[31m-    # 1. Default model[m
[31m-    assert get_model() == DEFAULT_GROQ_MODEL[m
[32m+[m[32m    assert get_model(provider="groq") == DEFAULT_GROQ_MODEL[m
[32m+[m[32m    assert get_model(provider="gemini") == DEFAULT_GEMINI_MODEL[m
[32m+[m[32m    assert get_model(provider="openai") == DEFAULT_OPENAI_MODEL[m
[32m+[m[32m    assert get_model(provider="ollama") == DEFAULT_OLLAMA_MODEL[m
 [m
[31m-    # 2. User config model[m
     set_user_config_value("groq_model", "model-from-user-config")[m
[31m-    assert get_model() == "model-from-user-config"[m
[32m+[m[32m    assert get_model(provider="groq") == "model-from-user-config"[m
 [m
[31m-    # 3. Environment variable overrides user config[m
     monkeypatch.setenv("GROQ_MODEL", "model-from-env")[m
[31m-    assert get_model() == "model-from-env"[m
[32m+[m[32m    assert get_model(provider="groq") == "model-from-env"[m
[32m+[m
[32m+[m[32m    monkeypatch.setenv("COMIT_MODEL", "universal-model-override")[m
[32m+[m[32m    assert get_model(provider="groq") == "universal-model-override"[m
 [m
[31m-    # 4. Explicit override takes absolute precedence[m
     assert get_model("model-override") == "model-override"[m
 [m
 [m
[36m@@ -101,11 +139,11 @@[m [mdef test_get_provider_default(temp_config_dir: Path, monkeypatch):[m
     monkeypatch.delenv("COMIT_PROVIDER", raising=False)[m
     assert get_provider() == DEFAULT_PROVIDER[m
 [m
[31m-    set_user_config_value("provider", "custom_provider")[m
[31m-    assert get_provider() == "custom_provider"[m
[32m+[m[32m    set_user_config_value("provider", "gemini")[m
[32m+[m[32m    assert get_provider() == "gemini"[m
 [m
[31m-    monkeypatch.setenv("COMIT_PROVIDER", "env_provider")[m
[31m-    assert get_provider() == "env_provider"[m
[32m+[m[32m    monkeypatch.setenv("COMIT_PROVIDER", "openai")[m
[32m+[m[32m    assert get_provider() == "openai"[m
 [m
 [m
 def test_normalize_api_key():[m
[36m@@ -119,6 +157,8 @@[m [mdef test_normalize_api_key():[m
     assert normalize_api_key("  'gsk_abc123'  ") == "gsk_abc123"[m
     assert normalize_api_key('  "  gsk_abc123  "  ') == "gsk_abc123"[m
     assert normalize_api_key('gsk_"inner"_123') == 'gsk_"inner"_123'[m
[32m+[m[32m    assert normalize_api_key('  "AIzaSy_12345"  ') == "AIzaSy_12345"[m
[32m+[m[32m    assert normalize_api_key("  'sk-proj-12345'  ") == "sk-proj-12345"[m
 [m
 [m
 def test_mask_api_key_with_quotes():[m
[36m@@ -134,17 +174,19 @@[m [mdef test_get_api_key_with_existing_incorrectly_quoted_config(temp_config_dir: Pa[m
     monkeypatch.delenv("GROQ_KEY", raising=False)[m
 [m
     save_user_config({"groq_api_key": '"gsk_already_quoted_1234567890"'})[m
[31m-    assert get_api_key() == "gsk_already_quoted_1234567890"[m
[32m+[m[32m    assert get_api_key(provider="groq") == "gsk_already_quoted_1234567890"[m
[32m+[m
 [m
 def test_get_config_summary(temp_config_dir: Path, monkeypatch):[m
     monkeypatch.delenv("GROQ_API_KEY", raising=False)[m
     monkeypatch.delenv("groq_api_key", raising=False)[m
[32m+[m[32m    monkeypatch.delenv("COMIT_PROVIDER", raising=False)[m
[32m+[m[32m    set_user_config_value("provider", "groq")[m
     set_user_config_value("groq_api_key", "gsk_1234567890abcdef")[m
     set_user_config_value("groq_model", "test-model")[m
 [m
     summary = get_config_summary()[m
[32m+[m[32m    assert summary["provider"] == "groq"[m
     assert summary["model"] == "test-model"[m
     assert summary["api_key_masked"] == "gsk_************cdef"[m
     assert summary["config_exists"] is True[m
[31m-[m
[31m-[m
