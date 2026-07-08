import asyncio
import os
import time
import winsound
from pathlib import Path
from threading import Thread

import flet as ft

from atri_indextts.service import TTSService
from atri_indextts.config import load_env


_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class TtsApp:
    def __init__(self, page: ft.Page):
        self.page = page

        load_env(str(_ENV_PATH))

        self.service = TTSService()
        self._current_audio: str | None = None
        self._is_playing = False

        self._build_ui()
        self._load_data()

    def _safe_page_update(self):
        async def _update():
            self.page.update()
        asyncio.run_coroutine_threadsafe(_update(), self.page.loop)

    def _run_on_ui_thread(self, fn):
        async def _wrapper():
            fn()
        asyncio.run_coroutine_threadsafe(_wrapper(), self.page.loop)

    # ── UI ────────────────────────────────────────────────────

    def _build_ui(self):
        p = self.page
        p.title = "ATRI-IndexTTS 语音合成"
        p.padding = 0
        p.spacing = 0
        p.window_width = 800
        p.window_min_width = 370

        p.theme = ft.Theme(
            color_scheme=ft.ColorScheme(primary=ft.Colors.INDIGO),
            use_material3=True,
        )
        p.dark_theme = ft.Theme(
            color_scheme=ft.ColorScheme(primary=ft.Colors.INDIGO_200, outline=ft.Colors.GREY_400),
            use_material3=True,
        )
        p.theme_mode = ft.ThemeMode.LIGHT

        # ---- .env warning ----
        self._txt_env_warn = ft.Text("", color=ft.Colors.ORANGE_600, size=13, visible=False)

        # ---- Required: 合成文本 ----
        self._txt_text = ft.TextField(
            label="合成文本", hint_text="请输入要合成语音的文本…",
            multiline=True, min_lines=3, max_lines=8,
            border=ft.InputBorder.OUTLINE, expand=True,
        )

        # ---- Required: 服务商 / 音色 / 参考声纹 ----
        self._dd_provider = ft.Dropdown(
            label="服务商", border=ft.InputBorder.OUTLINE, expand=True,
            on_select=self._on_provider_change,
        )
        self._dd_voice = ft.Dropdown(
            label="音色", border=ft.InputBorder.OUTLINE, expand=True,
            on_select=self._on_voice_change,
        )
        self._dd_prompt = ft.Dropdown(
            label="参考声纹", border=ft.InputBorder.OUTLINE, expand=True,
        )

        # ---- Emotion ----
        self._ck_emo = ft.Checkbox(
            label="启用情感控制", value=False, on_change=self._on_emo_toggle,
        )
        self._rg_emo = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="text", label="文本控制"),
                ft.Radio(value="audio", label="音频控制"),
            ]),
            value="text", on_change=self._on_emo_mode_change, visible=False,
        )
        self._txt_emo_text = ft.TextField(
            label="情感文本",
            border=ft.InputBorder.OUTLINE, expand=True, visible=False,
        )
        self._txt_emo_audio = ft.TextField(
            label="情感音频 URL", hint_text="https://…",
            border=ft.InputBorder.OUTLINE, expand=True, visible=False,
        )
        self._txt_alpha_val = ft.Text("0.50", size=14, width=44, text_align=ft.TextAlign.END)
        self._sl_emo_alpha = ft.Slider(
            min=0, max=1, value=0.5, width=200, on_change=self._on_alpha_change,
        )
        self._row_emo_intensity = ft.Row(
            [ft.Text("情感强度", size=14), self._sl_emo_alpha, self._txt_alpha_val],
            spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER, visible=False,
        )

        # ---- Output ----
        self._txt_output = ft.TextField(
            label="输出目录", value="temp/output",
            border=ft.InputBorder.OUTLINE, expand=True,
        )
        self._btn_open_output = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN, tooltip="打开输出目录",
            on_click=self._on_open_output,
        )

        # ---- Synthesize ----
        self._synth_status = ft.Text("", size=13, color=ft.Colors.GREY_600)
        self._btn_synth = ft.FilledButton(
            content="合成", icon=ft.Icons.VOICE_CHAT, on_click=self._on_synthesize,
        )

        # ---- Status ----
        self._txt_status = ft.Text("", selectable=True, size=13)

        # ---- Playback ----
        self._txt_file_info = ft.Text("", size=12, color=ft.Colors.GREY_600)
        self._btn_play = ft.FilledTonalButton(
            content="播放", icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_play, visible=False,
        )

        # ---- File list ----
        self._file_list_container = ft.Container(
            content=ft.Column([ft.Text("（暂无文件）", size=13, color=ft.Colors.GREY_500)], spacing=4),
            padding=ft.Padding(left=0, top=4, right=0, bottom=4),
        )

        # ── Assemble ──────────────────────────────────────────
        p.add(
            ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("ATRI-IndexTTS", size=22, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DARK_MODE, tooltip="切换深色模式",
                                on_click=self._toggle_theme,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.SETTINGS, tooltip="编辑配置",
                                on_click=self._open_config_dialog,
                            ),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        self._txt_env_warn,
                        ft.Divider(),
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("必填参数", size=15, weight=ft.FontWeight.W_600),
                                    self._txt_text,
                                    ft.ResponsiveRow([
                                        ft.Column([self._dd_provider], col={"sm": 12, "md": 4}),
                                        ft.Column([self._dd_voice], col={"sm": 12, "md": 4}),
                                        ft.Column([self._dd_prompt], col={"sm": 12, "md": 4}),
                                    ], spacing=12),
                                ], spacing=12),
                                padding=16,
                            ),
                        ),
                        ft.Divider(height=8),
                        ft.Text("情感控制", size=15, weight=ft.FontWeight.W_600),
                        self._ck_emo,
                        self._rg_emo,
                        self._txt_emo_text,
                        self._txt_emo_audio,
                        self._row_emo_intensity,
                        ft.Divider(height=8),
                        ft.ResponsiveRow([
                            ft.Column([ft.Row([self._txt_output, self._btn_open_output], spacing=4)], col={"sm": 12, "md": 8}),
                            ft.Column(
                                [ft.Row([self._btn_synth, self._synth_status], spacing=8)],
                                col={"sm": 12, "md": 4},
                            ),
                        ], spacing=12),
                        self._txt_status,
                        ft.Divider(height=8),
                        ft.Row(
                            [self._btn_play, self._txt_file_info],
                            spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Divider(height=8),
                        ft.Row([
                            ft.Text("已生成文件", size=15, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True),
                            ft.TextButton(
                                content="刷新", icon=ft.Icons.REFRESH,
                                on_click=lambda _: (self._refresh_files(), self.page.update()),
                            ),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        self._file_list_container,
                        ft.Divider(),
                    ], spacing=12),
                    padding=24,
                ),
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        )

    # ── Theme toggle ──────────────────────────────────────────

    def _toggle_theme(self, e):
        self.page.theme_mode = (
            ft.ThemeMode.DARK if self.page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        self.page.update()

    # ── Data loading ──────────────────────────────────────────

    def _load_data(self):
        if not _ENV_PATH.exists():
            self._txt_env_warn.value = (
                "⚠ 未找到 .env 文件，API 密钥未配置。请复制 gui/.env.example 为 .env 并填入密钥。"
            )
            self._txt_env_warn.visible = True
        try:
            data = self.service.list_providers()
            self._dd_provider.options = [ft.dropdown.Option(n) for n in data["providers"]]

            voices = self.service.list_voices()
            self._dd_voice.options = [ft.dropdown.Option(v.name) for v in voices]
            if voices:
                self._dd_voice.value = voices[0].name
                self._update_prompt(voices[0])

        except Exception as ex:
            self._txt_status.value = f"加载失败: {ex}"
        self._refresh_files()
        self.page.update()

    def _refresh_files(self):
        out_dir = Path(self._txt_output.value.strip() or "temp/output")
        rows = []
        if out_dir.exists():
            files = sorted(out_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
            for f in files:
                if f.suffix.lower() not in (".wav", ".mp3", ".flac", ".ogg"):
                    continue
                size_kb = f.stat().st_size / 1024
                rows.append(
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW, tooltip="播放", icon_size=18,
                            on_click=lambda _, path=str(f): self._play_file(path),
                        ),
                        ft.Text(f.name, size=13, expand=True),
                        ft.Text(f"{size_kb:.1f} KB", size=12, color=ft.Colors.GREY_600, width=70, text_align=ft.TextAlign.END),
                    ], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                )
        if not rows:
            rows.append(ft.Text("（暂无文件）", size=13, color=ft.Colors.GREY_500))
        self._file_list_container.content = ft.Column(rows, spacing=4)

    def _play_file(self, path: str):
        self._current_audio = path
        self._on_play(None)

    def _on_voice_change(self, e):
        name = self._dd_voice.value
        if not name:
            return
        for v in self.service.list_voices():
            if v.name == name:
                self._update_prompt(v)
                break

    def _on_provider_change(self, e):
        pass

    def _update_prompt(self, voice):
        self._dd_prompt.options = [
            ft.dropdown.Option(str(i), p.label or f"声纹 {i}")
            for i, p in enumerate(voice.prompts)
        ]
        self._dd_prompt.value = "0" if voice.prompts else None
        self.page.update()

    # ── Emotion toggle ────────────────────────────────────────

    def _on_emo_toggle(self, e):
        enabled = self._ck_emo.value
        self._rg_emo.visible = enabled
        self._apply_emo_visibility(enabled, self._rg_emo.value)
        self.page.update()

    def _on_emo_mode_change(self, e):
        self._apply_emo_visibility(self._ck_emo.value, e.control.value)
        self.page.update()

    def _on_alpha_change(self, e):
        self._txt_alpha_val.value = f"{e.control.value:.2f}"
        self.page.update()

    def _apply_emo_visibility(self, enabled: bool, mode: str):
        is_text = mode == "text"
        self._txt_emo_text.visible = enabled and is_text
        self._txt_emo_audio.visible = enabled and not is_text
        self._row_emo_intensity.visible = enabled and not is_text

    # ── Synthesis ─────────────────────────────────────────────

    def _on_synthesize(self, e):
        text = self._txt_text.value
        if not text or not text.strip():
            self._snack("请输入合成文本")
            return
        if not self._dd_provider.value:
            self._snack("请选择服务商")
            return
        if not self._dd_voice.value:
            self._snack("请选择音色")
            return

        self._btn_synth.disabled = True
        self._btn_synth.content = "合成中…"
        self._txt_status.value = "正在合成…"
        self._btn_play.visible = False
        self._txt_file_info.value = ""
        if self._is_playing:
            winsound.PlaySound(None, winsound.SND_PURGE)
            self._is_playing = False
        self.page.update()

        if self._ck_emo.value:
            if self._rg_emo.value == "text":
                emo_text = self._txt_emo_text.value.strip() or None
                emo_audio = None
                emo_alpha = None
            else:
                emo_text = None
                emo_audio = self._txt_emo_audio.value.strip() or None
                emo_alpha = self._sl_emo_alpha.value if emo_audio else None
        else:
            emo_text = emo_audio = emo_alpha = None

        def _run():
            # 2-second cooldown, then re-enable button
            time.sleep(2)
            self._btn_synth.disabled = False
            self._btn_synth.content = "合成"
            self._safe_page_update()

            try:
                out_dir = self._txt_output.value.strip() or "temp/output"
                out = str(Path(out_dir) / "indextts.wav")

                result = self.service.synthesize(
                    text=text.strip(),
                    provider=self._dd_provider.value,
                    voice=self._dd_voice.value,
                    output=out,
                    prompt_index=int(self._dd_prompt.value or "0"),
                    emo_text=emo_text,
                    emo_audio=emo_audio,
                    emo_alpha=emo_alpha,
                )
                self._current_audio = str(result)
                size_kb = result.stat().st_size / 1024
                self._snack(f"合成成功: {result.name}")
                self._txt_status.value = f"✓ 已生成: {result.name}"
                self._txt_file_info.value = f"{size_kb:.1f} KB"
                self._btn_play.visible = True
            except Exception as ex:
                self._snack(f"合成失败: {ex}")
                self._txt_status.value = f"✗ {ex}"
            finally:
                self._btn_play.content = "播放"
                self._btn_play.icon = ft.Icons.PLAY_ARROW
                self._run_on_ui_thread(self._refresh_files)
                self._safe_page_update()

        Thread(target=_run, daemon=True).start()

    # ── Playback (winsound) ───────────────────────────────────

    def _on_play(self, e):
        if self._is_playing:
            # Stop
            winsound.PlaySound(None, winsound.SND_PURGE)
            self._is_playing = False
            self._btn_play.content = "播放"
            self._btn_play.icon = ft.Icons.PLAY_ARROW
            self.page.update()
            return
        # Play
        if not self._current_audio or not Path(self._current_audio).exists():
            self._snack("没有可播放的音频文件")
            return
        winsound.PlaySound(None, winsound.SND_PURGE)
        try:
            winsound.PlaySound(
                self._current_audio,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )
            self._is_playing = True
            self._btn_play.content = "停止"
            self._btn_play.icon = ft.Icons.STOP
            self._btn_play.visible = True
            self.page.update()
        except Exception as ex:
            self._snack(f"播放失败: {ex}")

    def _on_open_output(self, e):
        out_dir = Path(self._txt_output.value.strip() or "temp/output")
        if not out_dir.exists():
            out_dir.mkdir(parents=True, exist_ok=True)
        os.startfile(str(out_dir))

    # ── Config dialog ─────────────────────────────────────────

    _ENV_KEY_MAP = {"gitee": "GITEE_AI_API_KEY", "astraflow": "MODELVERSE_API_KEY"}

    def _open_config_dialog(self, e):
        cfg = self.service.get_config()
        providers_dict = cfg.get("providers", {})
        provider_names = list(providers_dict.keys()) if isinstance(providers_dict, dict) else []
        current = cfg.get("default_provider")

        blank_option = ft.dropdown.Option("", "无")
        provider_options = [blank_option] + [ft.dropdown.Option(n) for n in provider_names]
        dd = ft.Dropdown(
            label="服务商",
            options=provider_options,
            value=current if current in provider_names else "",
            expand=True,
        )

        txt_api_key = ft.TextField(
            label="API Key",
            password=True,
            hint_text="",
            border=ft.InputBorder.OUTLINE,
            expand=True,
        )

        def _refresh_key_hint(provider: str | None):
            txt_api_key.value = ""
            if not provider:
                txt_api_key.hint_text = ""
                return
            has_key = bool(cfg.get("api_keys", {}).get(provider))
            if has_key:
                txt_api_key.value = "••••••••"
                txt_api_key.hint_text = "修改请重新输入"
            else:
                txt_api_key.hint_text = "输入 API Key"

        _refresh_key_hint(current)
        prev_provider = [current]  # mutable container for closure

        def _on_provider_switch(ev):
            new_provider = ev.control.value
            if new_provider == prev_provider[0]:
                return
            # Auto-save API key for previous provider
            if prev_provider[0]:
                if txt_api_key.value and txt_api_key.value != "••••••••":
                    self._save_api_key(prev_provider[0], txt_api_key.value)
            # Auto-save default_provider (always, even when coming from None)
            self.service.set_config("default_provider", new_provider)
            # Switch context
            _refresh_key_hint(new_provider)
            prev_provider[0] = new_provider
            self.page.update()

        dd.on_change = _on_provider_switch

        def _on_confirm(_ev):
            self.service.set_config("default_provider", dd.value)
            if prev_provider[0] and txt_api_key.value and txt_api_key.value != "••••••••":
                self._save_api_key(prev_provider[0], txt_api_key.value)
            dlg.open = False
            self._load_data()
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("编辑配置"),
            content=ft.Container(
                content=ft.Column([dd, txt_api_key], tight=True, spacing=12),
                padding=ft.Padding(left=0, top=4, right=0, bottom=4),
            ),
            actions=[ft.FilledButton(content="确定", on_click=_on_confirm)],
        )
        self.page.show_dialog(dlg)

    def _save_api_key(self, provider: str, key_value: str):
        env_var = self._ENV_KEY_MAP.get(provider)
        if not env_var or not key_value:
            return
        lines = []
        found = False
        if _ENV_PATH.exists():
            lines = _ENV_PATH.read_text(encoding="utf-8").splitlines()
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(f"{env_var}="):
                new_lines.append(f"{env_var}={key_value}")
                found = True
            else:
                new_lines.append(line)
        if not found:
            if new_lines and new_lines[-1] != "":
                new_lines.append("")
            new_lines.append(f"{env_var}={key_value}")
        _ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        os.environ[env_var] = key_value

    # ── Helpers ──────────────────────────────────────────────

    def _snack(self, msg: str):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(msg), open=True)
        self._safe_page_update()
