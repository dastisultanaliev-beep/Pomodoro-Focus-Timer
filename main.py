            text_color=COLORS["text"]
        )
        self.mode_label.pack(pady=(5, 15))

        self.progress_widget = CircularProgress(self, size=300)
        self.progress_widget.pack(pady=10)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        self.start_btn = ctk.CTkButton(
            button_frame,
            text="▶ Start",
            command=self.toggle_timer,
            width=160,
            height=48,
            corner_radius=24,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["work"],
            hover_color=COLORS["work_dark"]
        )
        self.start_btn.grid(row=0, column=0, padx=8)

        self.reset_btn = ctk.CTkButton(
            button_frame,
            text="⟲ Reset",
            command=self.reset_timer,
            width=120,
            height=48,
            corner_radius=24,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["bg_card"],
            hover_color="#2a2a3e",
            text_color=COLORS["text"]
        )
        self.reset_btn.grid(row=0, column=1, padx=8)

        self.skip_btn = ctk.CTkButton(
            button_frame,
            text="⏭ Skip",
            command=self.skip_phase,
            width=120,
            height=48,
            corner_radius=24,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["bg_card"],
            hover_color="#2a2a3e",
            text_color=COLORS["text"]
        )
        self.skip_btn.grid(row=0, column=2, padx=8)

        mode_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        mode_frame.pack(pady=10, padx=30, fill="x")

        modes = [
            ("🍅 Work", "work"),
            ("☕ Break", "short"),
            ("🌴 Long Break", "long")
        ]
        self.mode_buttons = {}

        for i, (button_text, mode) in enumerate(modes):
            button = ctk.CTkButton(
                mode_frame,
                text=button_text,
                command=lambda m=mode: self.set_mode(m),
                width=140,
                height=40,
                corner_radius=10,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color="#2a2a3e",
                text_color=COLORS["text"]
            )
            button.grid(
                row=0,
                column=i,
                padx=10,
                pady=10,
                sticky="ew"
            )
            mode_frame.grid_columnconfigure(i, weight=1)
            self.mode_buttons[mode] = button

        stats_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        stats_frame.pack(pady=10, padx=30, fill="x")

        ctk.CTkLabel(
            stats_frame,
            text="📊 Weekly Statistics",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text"]
        ).pack(pady=(12, 5))

        self.chart = tk.Canvas(
            stats_frame,
            width=620,
            height=130,
            bg=COLORS["bg_card"],
            highlightthickness=0
        )
        self.chart.pack(padx=15, pady=(0, 12))

        self._draw_week_chart()

    def _update_display(self):
        minutes, seconds = divmod(self.remaining, 60)
        time_string = f"{minutes:02d}:{seconds:02d}"

        total = self._get_total_for_mode()
        progress = self.remaining / total if total else 0

        label, color_key = MODE_LABELS[self.mode]
        color = COLORS[color_key]

        if self.running:
            subtitle = "FOCUS TIME..." if self.mode == "work" else "TAKE A BREAK..."
        else:
            subtitle = "PAUSED" if self.remaining != total else "READY?"

        self.progress_widget.set_state(
            progress,
            color,
            time_string,
            subtitle
        )
        self.mode_label.configure(text=label, text_color=color)

        self.start_btn.configure(
            text="⏸ Pause" if self.running else "▶ Start",
            fg_color=color,
            hover_color=COLORS[color_key + "_dark"]
        )

        for mode, button in self.mode_buttons.items():
            if mode == self.mode:
                button.configure(
                    fg_color=COLORS[mode],
                    text_color="white"
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=COLORS["text"]
                )

    def _get_total_for_mode(self):
        return {
            "work": WORK_TIME,
            "short": SHORT_BREAK,
            "long": LONG_BREAK
        }[self.mode]

    def toggle_timer(self):
        if self.running:
            self._pause()
        else:
            self._start()

    def _start(self):
        self.running = True
        self._update_display()
        self._tick()

    def _pause(self):
        self.running = False

        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        self._update_display()

    def _tick(self):
        if not self.running:
            return

        if self.remaining > 0:
            self.remaining -= 1
            self._update_display()
            self.after_id = self.after(1000, self._tick)
        else:
            self._finish_phase()
