import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import csv
import math
import os
from pathlib import Path
from uuid import uuid4

# Instale com: python -m pip install customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PromixorPrototype(ctk.CTk):
    """Protótipo visual do Promixor para demonstrar wireframe, navegação e layout.

    Observação: este arquivo representa a interface em CustomTkinter. Ele não implementa
    a engine elétrica, a simulação 3D real nem a execução de código Arduino.
    """

    def __init__(self):
        super().__init__()
        self.title("Promixor - CustomTkinter — Protótipo de Interface")
        self.geometry("1360x800")
        self.minsize(1200, 700)
        self.configure(fg_color="#101722")
        self._configure_tables()

        self.project_name = tk.StringVar(value="Projeto sem título")
        self.status_text = tk.StringVar(value="Pronto")

        self.data_path = Path.home() / "Promixor" / "componentes.txt"
        self.catalog_writable = True
        self.components = self.load_components()
        self.placed_parts = []
        self.selected_part = None
        self.wires = []
        self.wire_start = None
        self.selected_wire = None
        self.dragging_part = False
        self.drag_offset = (0, 0)
        self.code_text = ""
        self._build_shell()
        self.show_screen("inicio")

    def _build_shell(self):
        # PACK: blocos grandes da aplicação: cabeçalho, corpo e rodapé.
        header = ctk.CTkFrame(self)
        header.pack(side="top", fill="x")

        ctk.CTkLabel(header, text="PROMIXOR", font=("Segoe UI", 18, "bold")).pack(side="left")
        ctk.CTkLabel(header, textvariable=self.project_name, font=("Segoe UI", 11)).pack(side="left", padx=18)
        ctk.CTkButton(header, text="Salvar", command=self.fake_save).pack(side="right")
        ctk.CTkButton(header, text="Novo", command=self.fake_new).pack(side="right", padx=(0, 8))

        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True)

        # PACK: sidebar é um grande bloco vertical; conteúdo ocupa o restante.
        sidebar = ctk.CTkFrame(body, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="NAVEGAÇÃO", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 8))
        buttons = [
            ("Início / Projetos", "inicio"),
            ("Editor de Circuito 2D", "circuito"),
            ("Simulação 3D", "simulacao"),
            ("Código + Serial", "codigo"),
            ("Diagnóstico", "diagnostico"),
            ("Componentes", "componentes"),
        ]
        self.nav_buttons = {}
        for label, key in buttons:
            button = ctk.CTkButton(sidebar, text=label, height=42, anchor="w", command=lambda k=key: self.show_screen(k))
            button.pack(fill="x", pady=4)
            self.nav_buttons[key] = button

        self.content = ctk.CTkFrame(body)
        self.content.pack(side="left", fill="both", expand=True)

        footer = ctk.CTkFrame(self)
        footer.pack(side="bottom", fill="x")
        ctk.CTkLabel(footer, textvariable=self.status_text).pack(side="left")
        ctk.CTkLabel(footer, text="Protótipo CustomTkinter - layout com pack() + grid()").pack(side="right")

    def clear_content(self):
        if hasattr(self, "editor") and self.editor.winfo_exists():
            self.code_text = self.editor.get("1.0", "end-1c")
        for child in self.content.winfo_children():
            child.destroy()

    def show_screen(self, name):
        self.clear_content()
        for key, button in self.nav_buttons.items():
            button.configure(fg_color="#2563eb" if key == name else "#243247")
        self.status_text.set(f"Tela ativa: {name}")
        screens = {
            "inicio": self.screen_inicio,
            "circuito": self.screen_circuito,
            "simulacao": self.screen_simulacao,
            "codigo": self.screen_codigo,
            "diagnostico": self.screen_diagnostico,
            "componentes": self.screen_componentes,
        }
        screens[name]()

    def title_block(self, title, subtitle):
        # PACK: título e subtítulo funcionam como um bloco superior da tela.
        box = ctk.CTkFrame(self.content)
        box.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(box, text=title, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ctk.CTkLabel(box, text=subtitle).pack(anchor="w", pady=(3, 0))

    def screen_inicio(self):
        self.title_block("Início / Projetos", "Criar, abrir e organizar protótipos do Promixor.")

        actions = ctk.CTkFrame(self.content)
        actions.pack(fill="x", pady=(0, 12))
        ctk.CTkButton(actions, text="+ Novo projeto", command=self.fake_new).pack(side="left")
        ctk.CTkButton(actions, text="Abrir projeto", command=self.demo_action).pack(side="left", padx=8)
        ctk.CTkButton(actions, text="Importar", command=self.demo_action).pack(side="left")

        # GRID: cartões/projetos em linhas e colunas regulares.
        projects = ttk.LabelFrame(self.content, text="Projetos recentes")
        projects.pack(fill="both", expand=True)
        for col in range(3):
            projects.columnconfigure(col, weight=1)

        data = [
            ("Robô seguidor de linha", "Arduino Uno + sensores"),
            ("Alarme de distância", "HC-SR04 + buzzer"),
            ("Controle de servo", "Servo + potenciômetro"),
        ]
        for i, (name, desc) in enumerate(data):
            card = ttk.LabelFrame(projects, text=name)
            card.grid(row=0, column=i, sticky="nsew", padx=6, pady=6)
            ctk.CTkLabel(card, text=desc, wraplength=220).pack(anchor="w")
            ctk.CTkButton(card, text="Abrir", command=lambda n=name: self.open_project(n)).pack(anchor="e", pady=(16, 0))

    def screen_circuito(self):
        self.title_block("Editor de Circuito 2D", "Conecte clicando em dois terminais. Arraste o corpo da peça para mover.")
        toolbar = ctk.CTkFrame(self.content)
        toolbar.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(toolbar, text="+ Cadastrar peça", command=lambda: self.show_screen("componentes")).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="Excluir seleção", command=self.delete_part).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="Cancelar fio", width=110, command=self.cancel_wire).pack(side="left", padx=5)
        ctk.CTkLabel(toolbar, text="Montagem visual • sem simulação elétrica").pack(side="left", padx=10)
        work = ctk.CTkFrame(self.content)
        work.pack(fill="both", expand=True)
        library = ctk.CTkScrollableFrame(work, label_text="Biblioteca", width=185)
        library.pack(side="left", fill="y")
        for part in self.components:
            ctk.CTkButton(library, text=part["name"], anchor="w",
                          command=lambda item=part: self.add_part(item)).pack(fill="x", pady=4)
        props = ctk.CTkFrame(work, width=220)
        props.pack(side="right", fill="y", padx=(8, 0))
        props.pack_propagate(False)
        ctk.CTkLabel(props, text="Peça selecionada", font=("Segoe UI", 16, "bold")).pack(pady=12)
        self.part_details = ctk.CTkLabel(props, text="Selecione uma peça.", wraplength=195, justify="left")
        self.part_details.pack(fill="x", padx=12)
        self.delete_piece_button = ctk.CTkButton(props, text="Excluir esta peça", fg_color="#b91c1c", hover_color="#991b1b", command=self.delete_selected_piece)
        self.delete_piece_button.pack(fill="x", padx=12, pady=18)
        self.circuit_canvas = tk.Canvas(work, background="#101722", highlightthickness=0)
        self.circuit_canvas.pack(side="left", fill="both", expand=True, padx=(8, 0))
        self.circuit_canvas.bind("<Configure>", lambda event: self.draw_circuit(self.circuit_canvas))
        self.circuit_canvas.bind("<Button-1>", self.select_part)
        self.circuit_canvas.bind("<B1-Motion>", self.move_part)
        self.circuit_canvas.bind("<ButtonRelease-1>", lambda event: setattr(self, "dragging_part", False))
        self.circuit_canvas.bind("<Escape>", lambda event: self.cancel_wire())
        self.circuit_canvas.bind("<Delete>", lambda event: self.delete_part())
        self.circuit_canvas.bind("<Motion>", self.preview_wire)
        self.refresh_part_details()

    def add_part(self, component):
        if not hasattr(self, "circuit_canvas") or not self.circuit_canvas.winfo_exists():
            self.show_screen("circuito")
        index = len(self.placed_parts)
        part = {"id": uuid4().hex, "component": dict(component), "x": 30 + (index % 3)*35, "y": 60 + (index % 5)*35}
        self.placed_parts.append(part)
        self.selected_part = part["id"]
        self.selected_wire = None
        self.draw_circuit(self.circuit_canvas)
        self.refresh_part_details()
        self.status_text.set(f"{component['name']} inserido. Arraste para posicionar.")

    def current_part(self):
        return next((p for p in self.placed_parts if p["id"] == self.selected_part), None)

    @staticmethod
    def part_height(part):
        return max(110, ((len(part["component"]["pins"])+1)//2)*26+22)

    @staticmethod
    def pin_position(part, index):
        count = len(part["component"]["pins"])
        left_count = (count+1)//2
        right = index >= left_count
        row = index-left_count if right else index
        return part["x"]+(180 if right else 0), part["y"]+24+row*26

    def endpoint_position(self, endpoint):
        part = next(p for p in self.placed_parts if p["id"] == endpoint[0])
        return self.pin_position(part, endpoint[1])

    def connect_terminals(self, start, end):
        for endpoint in (start, end):
            part = next((p for p in self.placed_parts if p["id"] == endpoint[0]), None)
            if part is None or not 0 <= endpoint[1] < len(part["component"]["pins"]):
                raise ValueError("Terminal inexistente.")
        if start == end:
            raise ValueError("Escolha outro terminal para concluir o fio.")
        if any({tuple(w["start"]), tuple(w["end"])} == {tuple(start), tuple(end)} for w in self.wires):
            raise ValueError("Esses terminais já estão conectados.")
        wire = dict(id=uuid4().hex, start=start, end=end)
        self.wires.append(wire)
        return wire

    def cancel_wire(self):
        self.wire_start = None
        self.dragging_part = False
        self.draw_circuit(self.circuit_canvas)
        self.status_text.set("Conexão cancelada. Clique em um terminal para começar.")

    def preview_wire(self, event):
        self.circuit_canvas.delete("preview")
        if self.wire_start:
            x, y = self.endpoint_position(self.wire_start)
            self.circuit_canvas.create_line(x, y, event.x, event.y, fill="#fbbf24", dash=(5, 4), width=2, tags=("preview",))

    def select_part(self, event):
        canvas = self.circuit_canvas
        canvas.focus_set()
        self.dragging_part = False
        hits = list(reversed(canvas.find_overlapping(event.x-3, event.y-3, event.x+3, event.y+3)))
        tags = [tag for item in hits for tag in canvas.gettags(item)]
        pin = next((t for t in tags if t.startswith("pin:")), None)
        if pin:
            _, part_id, index = pin.split(":")
            endpoint = (part_id, int(index))
            self.selected_part, self.selected_wire = part_id, None
            if self.wire_start is None:
                self.wire_start = endpoint
                self.status_text.set("Agora clique no terminal de destino. Esc cancela.")
            else:
                try:
                    wire = self.connect_terminals(self.wire_start, endpoint)
                except ValueError as error:
                    self.status_text.set(str(error))
                else:
                    self.wire_start = None
                    self.selected_wire = wire["id"]
                    self.selected_part = None
                    self.status_text.set("Fio conectado. Clique no fio para selecionar e excluir.")
        else:
            part_tag = next((t for t in tags if t.startswith("part:")), None)
            wire_tag = next((t for t in tags if t.startswith("wire:")), None)
            self.selected_part = part_tag[5:] if part_tag else None
            self.selected_wire = wire_tag[5:] if wire_tag and not part_tag else None
            part = self.current_part()
            if part:
                self.dragging_part = True
                self.drag_offset = (event.x-part["x"], event.y-part["y"])
        self.draw_circuit(canvas)
        self.refresh_part_details()

    def move_part(self, event):
        part = self.current_part()
        if part and self.dragging_part:
            part["x"] = max(12, min(event.x-self.drag_offset[0], self.circuit_canvas.winfo_width()-192))
            part["y"] = max(40, min(event.y-self.drag_offset[1], self.circuit_canvas.winfo_height()-self.part_height(part)-12))
            self.draw_circuit(self.circuit_canvas)

    def delete_part(self):
        if self.selected_wire:
            self.wires = [w for w in self.wires if w["id"] != self.selected_wire]
            self.selected_wire = None
            self.status_text.set("Fio removido.")
        elif self.current_part():
            removed = self.selected_part
            self.placed_parts = [p for p in self.placed_parts if p["id"] != removed]
            self.wires = [w for w in self.wires if removed not in (w["start"][0], w["end"][0])]
            if self.wire_start and self.wire_start[0] == removed:
                self.wire_start = None
            self.selected_part = None
            self.status_text.set("Peça e seus fios removidos da montagem.")
        self.draw_circuit(self.circuit_canvas)
        self.refresh_part_details()

    def refresh_part_details(self):
        part = self.current_part()
        if part:
            c = part["component"]
            text = f"{c['name']}\n\nCategoria: {c['category']}\nTensão: {c['voltage'] or '—'} V\nQuantidade cadastrada: {c['quantity']}\n\n{c['description']}"
        else:
            text = "Selecione uma peça.\n\nAs posições ficam nesta sessão. As peças cadastradas são salvas automaticamente."
        if self.selected_wire:
            text = "Fio selecionado.\n\nClique em Excluir seleção para removê-lo.\n\nConexões são visuais; não calculam tensão ou corrente."
        self.part_details.configure(text=text)
        self.delete_piece_button.configure(state="normal" if part else "disabled")

    def screen_simulacao(self):
        self.title_block("Simulação 3D", "Pré-visualização espacial do protótipo e dos componentes.")

        controls = ctk.CTkFrame(self.content)
        controls.pack(fill="x", pady=(0, 8))
        for text in ["Iniciar", "Pausar", "Resetar", "Girar câmera", "Centralizar"]:
            ctk.CTkButton(controls, text=text, width=110, command=self.demo_action).pack(side="left", padx=(0, 5))

        area = ctk.CTkFrame(self.content)
        area.pack(fill="both", expand=True)

        viewport = ttk.LabelFrame(area, text="Viewport 3D")
        viewport.pack(side="left", fill="both", expand=True)
        canvas = tk.Canvas(viewport, background="#101722", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.bind("<Configure>", lambda event: self.draw_viewport(canvas))

        side = ttk.LabelFrame(area, text="Simulação", width=250)
        side.pack(side="right", fill="y", padx=(8, 0))
        side.pack_propagate(False)

        # GRID: parâmetros de simulação organizados em formulário.
        for r, (lab, val) in enumerate([("Tempo", "0 ms"), ("Gravidade", "Ativa"), ("Escala", "1:1"), ("Unidade", "mm")]):
            ctk.CTkLabel(side, text=lab + ":").grid(row=r, column=0, sticky="w", pady=5)
            ctk.CTkLabel(side, text=val).grid(row=r, column=1, sticky="e", pady=5, padx=(10, 0))
        side.columnconfigure(1, weight=1)

    def screen_codigo(self):
        self.title_block("Código + Monitor Serial", "Escrever lógica do microcontrolador e acompanhar a saída de execução.")

        actions = ctk.CTkFrame(self.content)
        actions.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(actions, text="Executar", command=self.demo_action).pack(side="left")
        ctk.CTkButton(actions, text="Parar", command=self.demo_action).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Limpar serial", command=self.clear_serial).pack(side="left")

        # PACK: editor e monitor serial dividem verticalmente a tela.
        editor_box = ttk.LabelFrame(self.content, text="Editor de código")
        editor_box.pack(fill="both", expand=True)
        editor = ctk.CTkTextbox(editor_box, font=("Consolas", 14), undo=True, fg_color="#101722")
        editor.pack(fill="both", expand=True)
        self.editor = editor
        editor.insert("1.0", self.code_text or "void setup() {\n  pinMode(13, OUTPUT);\n}\n\nvoid loop() {\n  digitalWrite(13, HIGH);\n  delay(1000);\n  digitalWrite(13, LOW);\n  delay(1000);\n}\n")

        serial_box = ttk.LabelFrame(self.content, text="Monitor Serial")
        serial_box.pack(fill="x", pady=(8, 0))
        self.serial = serial = ctk.CTkTextbox(serial_box, height=130, font=("Consolas", 10))
        serial.pack(fill="x")
        serial.insert("1.0", "[PROMIXOR] Protótipo visual. Execução Arduino indisponível.\n")
        serial.configure(state="disabled")

    def screen_diagnostico(self):
        self.title_block("Diagnóstico do Protótipo", "Alertas de exemplo — não são calculados a partir do circuito.")

        filters = ctk.CTkFrame(self.content)
        filters.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(filters, text="Filtro:").pack(side="left")
        ctk.CTkComboBox(filters, values=["Todos", "Erro", "Aviso", "Informação"], state="readonly", width=160).pack(side="left", padx=6)
        ctk.CTkButton(filters, text="Atualizar").pack(side="left")

        # PACK: tabela é o principal bloco de conteúdo.
        table_frame = ctk.CTkFrame(self.content)
        table_frame.pack(fill="both", expand=True)
        columns = ("nivel", "componente", "mensagem", "acao")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, text, width in [
            ("nivel", "Nível", 90),
            ("componente", "Componente", 160),
            ("mensagem", "Mensagem", 420),
            ("acao", "Ação sugerida", 240),
        ]:
            tree.heading(col, text=text)
            tree.column(col, width=width, anchor="w")
        tree.pack(fill="both", expand=True, side="left")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        rows = [
            ("Aviso", "LED vermelho", "LED sem resistor limitador.", "Adicionar 220-330 ohms"),
            ("Erro", "Fio #12", "Possível conflito entre alimentação e GND.", "Revisar conexão"),
            ("Informação", "Servo #1", "Sinal configurado no pino D9.", "Nenhuma"),
        ]
        for row in rows:
            tree.insert("", "end", values=row)

    def screen_componentes(self):
        self.title_block("Biblioteca de Componentes", "Cadastre uma peça e use-a no circuito. A biblioteca é salva automaticamente.")

        outer = ctk.CTkFrame(self.content)
        outer.pack(fill="both", expand=True)

        form = ttk.LabelFrame(outer, text="Cadastro de componente", width=360)
        form.pack(side="left", fill="y")
        form.pack_propagate(False)

        # GRID: formulário estruturado em linhas e colunas.
        labels = ["Nome", "Categoria", "Tensão (V)", "Quantidade", "Descrição", "Terminais"]
        widgets = []
        for r, label in enumerate(labels):
            ctk.CTkLabel(form, text=label + ":").grid(row=r, column=0, sticky="w", pady=6)
            if label == "Categoria":
                widget = ctk.CTkComboBox(form, values=["Placa", "Sensor", "Atuador", "Passivo", "Conector"], state="readonly", width=170)
            else:
                widget = ctk.CTkEntry(form, width=170)
            widget.grid(row=r, column=1, sticky="ew", padx=(8, 0), pady=6)
            widgets.append(widget)
        form.columnconfigure(1, weight=1)
        ctk.CTkButton(form, text="Cadastrar", command=lambda: self.register_component(widgets, tree)).grid(row=len(labels), column=0, columnspan=2, sticky="ew", pady=(14, 4))
        ctk.CTkButton(form, text="Limpar", command=lambda: self.clear_form(widgets)).grid(row=len(labels)+1, column=0, columnspan=2, sticky="ew")

        list_box = ttk.LabelFrame(outer, text="Componentes cadastrados")
        list_box.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tree = ttk.Treeview(list_box, columns=("nome", "categoria", "tensao", "qtd"), show="headings")
        for c, title, width in [("nome", "Nome", 180), ("categoria", "Categoria", 130), ("tensao", "Tensão", 90), ("qtd", "Qtd.", 70)]:
            tree.heading(c, text=title)
            tree.column(c, width=width, anchor="w")
        tree.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_box, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        for item in self.components:
            tree.insert("", "end", iid=item["id"], values=self.component_row(item))
        ctk.CTkButton(form, text="Inserir selecionada no 2D", command=lambda: self.insert_registered(tree)).grid(row=8, column=0, columnspan=2, sticky="ew", pady=12)
        ctk.CTkLabel(form, text="Selecione uma peça na tabela para inseri-la.\nTerminais: nomes separados por vírgula.\nExemplo: VCC, GND, SINAL (máximo 16).", wraplength=320).grid(row=9, column=0, columnspan=2, padx=8)
        ctk.CTkButton(form, text="Excluir peça cadastrada", fg_color="#b91c1c", hover_color="#991b1b", command=lambda: self.delete_registered(tree)).grid(row=10, column=0, columnspan=2, sticky="ew", pady=12)
        ctk.CTkLabel(form, text="Excluir do cadastro remove da biblioteca.\nAs peças já inseridas no circuito permanecem.", wraplength=320).grid(row=11, column=0, columnspan=2, padx=8)
        tree.bind("<Double-1>", lambda event: self.insert_registered(tree))

    def clear_form(self, widgets):
        for widget in widgets:
            if isinstance(widget, ctk.CTkComboBox):
                widget.set("Placa")
            else:
                widget.delete(0, "end")

    @staticmethod
    def component_row(item):
        return (item["name"], item["category"], (item["voltage"] + " V") if item["voltage"] else "—", item["quantity"])

    @staticmethod
    def validate_component(name, category, voltage, quantity, description, pins=""):
        name, category, voltage, description = (v.strip() for v in (name, category, voltage, description))
        if not name or len(name) > 60:
            raise ValueError("Informe um nome com 1 a 60 caracteres.")
        if category not in ["Placa", "Sensor", "Atuador", "Passivo", "Conector"]:
            raise ValueError("Escolha uma categoria da lista.")
        try:
            amount = int(str(quantity))
            if amount <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("A quantidade deve ser um número inteiro maior que zero.") from None
        voltage = voltage.replace(",", ".")
        if voltage:
            try:
                value = float(voltage)
                if not math.isfinite(value) or value < 0:
                    raise ValueError
            except ValueError:
                raise ValueError("Informe uma tensão numérica não negativa ou deixe vazia.") from None
        if isinstance(pins, str):
            pins = [pin.strip() for pin in pins.split(",")] if pins.strip() else []
        if not pins:
            pins = {"Arduino Uno": ["5V", "GND", "D2", "D3", "D9", "D13", "A0", "A1"],
                    "ESP32": ["3V3", "GND", "GPIO2", "GPIO4"],
                    "Breadboard": ["+", "-", "A1", "B1"], "LED": ["A", "K"],
                    "Botão": ["1", "2"], "HC-SR04": ["VCC", "TRIG", "ECHO", "GND"],
                    "Servo SG90": ["VCC", "GND", "SINAL"]}.get(name, ["P1", "P2"])
        if not isinstance(pins, list) or not 2 <= len(pins) <= 16 or any(not isinstance(pin, str) or not pin.strip() or len(pin) > 12 for pin in pins):
            raise ValueError("Informe de 2 a 16 terminais, com nomes de até 12 caracteres.")
        pins = [pin.strip() for pin in pins]
        if len({pin.casefold() for pin in pins}) != len(pins):
            raise ValueError("Os nomes dos terminais não podem se repetir.")
        return dict(name=name, category=category, voltage=voltage, quantity=amount, description=description, pins=pins)

    def load_components(self):
        defaults = [("Arduino Uno", "Placa", "5", 2), ("ESP32", "Placa", "3.3", 1),
                    ("Breadboard", "Conector", "", 1), ("LED", "Passivo", "2", 5),
                    ("Botão", "Passivo", "", 2), ("HC-SR04", "Sensor", "5", 4),
                    ("Servo SG90", "Atuador", "5", 3), ("Resistor 220 ohms", "Passivo", "", 25)]
        if not self.data_path.exists():
            return [dict(id=uuid4().hex, **self.validate_component(*row, "")) for row in defaults]
        try:
            # Texto com campos separados por tabulação. Cada terminal ocupa um campo.
            with self.data_path.open("r", encoding="utf-8", newline="") as file:
                rows = list(csv.reader(file, delimiter="\t", strict=True))
            checked, ids, names = [], set(), set()
            for row in rows:
                if len(row) < 8 or not row[0].strip():
                    raise ValueError("Linha de cadastro inválida: faltam dados ou terminais.")
                item_id, name, category, voltage, quantity, description, *pins = row
                clean = self.validate_component(name, category, voltage, quantity, description, pins)
                if item_id in ids or clean["name"].casefold() in names:
                    raise ValueError("Peças duplicadas na biblioteca.")
                ids.add(item_id)
                names.add(clean["name"].casefold())
                checked.append(dict(id=item_id, **clean))
            return checked
        except (OSError, ValueError, csv.Error, KeyError, TypeError, AttributeError) as error:
            self.catalog_writable = False
            messagebox.showerror("Biblioteca não carregada", f"Não foi possível ler {self.data_path}:\n{error}\n\nO arquivo foi preservado. Corrija-o e reabra o programa para cadastrar peças.", parent=self)
            return []

    def save_components(self, items):
        if not self.catalog_writable:
            raise OSError("Cadastro bloqueado: o arquivo da biblioteca precisa ser corrigido.")
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.data_path.with_suffix(".tmp")
        try:
            with temporary.open("w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file, delimiter="\t")
                for item in items:
                    writer.writerow([item["id"], item["name"], item["category"], item["voltage"], item["quantity"], item["description"], *item["pins"]])
            os.replace(temporary, self.data_path)
        finally:
            if temporary.exists():
                temporary.unlink()

    def register_component(self, widgets, tree):
        try:
            item = self.validate_component(*(widget.get() for widget in widgets))
            if any(c["name"].casefold() == item["name"].casefold() for c in self.components):
                raise ValueError("Já existe uma peça com esse nome. Use outro nome para a nova peça.")
            item["id"] = uuid4().hex
            updated = self.components + [item]
            self.save_components(updated)
        except (ValueError, OSError) as error:
            messagebox.showwarning("Não foi possível cadastrar", str(error), parent=self)
            return
        self.components = updated
        tree.insert("", "end", iid=item["id"], values=self.component_row(item))
        tree.selection_set(item["id"])
        tree.see(item["id"])
        self.clear_form(widgets)
        self.status_text.set("Peça cadastrada e salva. Já disponível na biblioteca do circuito 2D.")

    def delete_selected_piece(self):
        if self.current_part() is None:
            self.status_text.set("Clique no corpo da peça que deseja excluir.")
            return
        self.selected_wire = None
        self.delete_part()

    def delete_registered(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Promixor", "Selecione a peça que deseja excluir na tabela.", parent=self)
            return
        removed = set(selection)
        updated = [c for c in self.components if c["id"] not in removed]
        try:
            self.save_components(updated)
        except OSError as error:
            messagebox.showwarning("Não foi possível excluir", str(error), parent=self)
            return
        self.components = updated
        for item_id in selection:
            tree.delete(item_id)
        self.status_text.set("Cadastro excluído e biblioteca atualizada. Peças já montadas foram preservadas.")

    def insert_registered(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showinfo("Promixor", "Selecione uma peça na tabela.", parent=self)
            return
        component = next(c for c in self.components if c["id"] == selection[0])
        self.show_screen("circuito")
        self.add_part(component)

    def _configure_tables(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabelframe", background="#182231", bordercolor="#334155", relief="solid")
        style.configure("TLabelframe.Label", background="#182231", foreground="#dbeafe", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", background="#182231", fieldbackground="#182231", foreground="#e7eef8", rowheight=36, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#243247", foreground="#e7eef8", font=("Segoe UI", 10, "bold"), padding=8)
        style.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "white")])

    def demo_action(self):
        self.status_text.set("Ação demonstrativa — protótipo de interface.")
        messagebox.showinfo("Promixor", "Este controle demonstra o layout. Este recurso ainda não está implementado. O cadastro e o posicionamento de peças no 2D estão disponíveis.")

    def clear_serial(self):
        self.serial.configure(state="normal")
        self.serial.delete("1.0", "end")
        self.serial.configure(state="disabled")

    def draw_circuit(self, canvas):
        canvas.delete("all")
        w, h = canvas.winfo_width(), canvas.winfo_height()
        for x in range(0, w, 24):
            for y in range(0, h, 24):
                canvas.create_oval(x, y, x+2, y+2, fill="#263449", outline="")
        canvas.create_text(w/2, 20, text="Clique em dois terminais para conectar • Esc cancela", fill="#94a3b8")
        for wire in self.wires:
            x1, y1 = self.endpoint_position(wire["start"])
            x2, y2 = self.endpoint_position(wire["end"])
            mid = (x1+x2)/2
            canvas.create_line(x1, y1, mid, y1, mid, y2, x2, y2,
                               fill="#fbbf24" if wire["id"] == self.selected_wire else "#4ade80",
                               width=4, tags=("wire:"+wire["id"],))
        if not self.placed_parts:
            canvas.create_text(w/2, h/2, text="Insira uma peça pela biblioteca à esquerda.", fill="#94a3b8", width=max(100, w-30))
        colors = {"Placa": "#2563eb", "Sensor": "#0891b2", "Atuador": "#9333ea", "Passivo": "#b45309", "Conector": "#475569"}
        for part in self.placed_parts:
            x, y, component = part["x"], part["y"], part["component"]
            height = self.part_height(part)
            tags = ("part:" + part["id"],)
            canvas.create_rectangle(x, y, x+180, y+height, fill=colors[component["category"]], outline="#f8fafc" if part["id"] == self.selected_part else "#64748b", width=3, tags=tags)
            canvas.create_text(x+90, y-12, text=component["name"], width=180, fill="white", font=("Segoe UI", 10, "bold"), tags=tags)
            for index, label in enumerate(component["pins"]):
                px, py = self.pin_position(part, index)
                pin_tags = (f"pin:{part['id']}:{index}",)
                right = px > x
                canvas.create_text(px-12 if right else px+12, py, text=label, anchor="e" if right else "w", fill="white", tags=pin_tags)
                canvas.create_oval(px-7, py-7, px+7, py+7, fill="#fbbf24" if self.wire_start == (part["id"], index) else "#e2e8f0", outline="#0f172a", width=2, tags=pin_tags)

    def draw_viewport(self, canvas):
        canvas.delete("all")
        w, h = canvas.winfo_width(), canvas.winfo_height()
        cx, cy = w/2, h*.6
        canvas.create_text(cx, h*.23, text="VIEWPORT 3D\nPrévia ilustrativa", fill="#dbeafe", font=("Segoe UI", 20, "bold"), justify="center")
        canvas.create_polygon(cx-135, cy, cx+100, cy, cx+140, cy-55, cx-95, cy-55, fill="#172e4a", outline="#60a5fa", width=2)
        canvas.create_rectangle(cx-135, cy, cx+100, cy+35, fill="#243247", outline="#60a5fa", width=2)
        for x in [cx-90, cx+55]:
            canvas.create_oval(x-25, cy+15, x+25, cy+65, fill="#101722", outline="#94a3b8", width=3)

    def fake_save(self):
        self.status_text.set("Projeto salvo (simulação de interface).")
        messagebox.showinfo("Promixor", "Demonstração do botão Salvar. Este protótipo não grava projetos em arquivo.")

    def fake_new(self):
        self.project_name.set("Novo projeto")
        self.status_text.set("Novo projeto criado.")

    def open_project(self, name):
        self.project_name.set(name)
        self.show_screen("circuito")


if __name__ == "__main__":
    app = PromixorPrototype()
    app.mainloop()
