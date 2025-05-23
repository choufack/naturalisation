import json
import Flask
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from moteur.moteur_eligibilite import MoteurEligibilite, Profil  # Import du moteur d'éligibilité
from experta import Fact

app = Flask(__name__)
class ResidencePermitApp:
    def __init__(self, root, questions_file):
        self.root = root
        self.root.title("Simulateur de Titre de Séjour")
        self.questions_file = questions_file
        self.questions = self.load_questions()
        self.responses = {}
        self.current_question_index = 0

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Question label
        self.question_label = ttk.Label(self.main_frame, text="", wraplength=400, anchor="center")
        self.question_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Dynamic widget for answers
        self.answer_widget = None

        # Navigation buttons
        self.prev_button = ttk.Button(self.main_frame, text="Précédent", command=self.prev_question)
        self.prev_button.grid(row=2, column=0, pady=10, sticky=tk.W)

        self.next_button = ttk.Button(self.main_frame, text="Suivant", command=self.next_question)
        self.next_button.grid(row=2, column=1, pady=10, sticky=tk.E)

        # Start with the first question
        self.show_question()

    def load_questions(self):
        """Charger les questions depuis le fichier JSON."""
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Erreur", "Impossible de charger le fichier des questions.")
            return []

    def show_question(self):
        """Afficher la question actuelle."""
        if not self.questions:
            return

        question = self.questions[self.current_question_index]
        self.question_label.config(text=question["label"])

        # Clear previous widget
        if self.answer_widget:
            self.answer_widget.destroy()

        # Create widget based on question type
        if question["type"] == "checkbox":
            self.answer_widget = ttk.Frame(self.main_frame)
            self.answer_widget.grid(row=1, column=0, columnspan=2)
            self.responses[question["question_id"]] = []
            for option in question["options"]:
                var = tk.BooleanVar()
                checkbox = ttk.Checkbutton(
                    self.answer_widget,
                    text=option["label"],
                    variable=var,
                    command=lambda opt=option, var=var: self.update_checkbox_response(question["question_id"], opt, var)
                )
                checkbox.pack(anchor="w")
        elif question["type"] == "select":
            self.answer_widget = ttk.Combobox(self.main_frame, state="readonly")
            self.answer_widget.grid(row=1, column=0, columnspan=2)
            self.answer_widget["values"] = [option["label"] for option in question["options"]]
            self.answer_widget.bind("<<ComboboxSelected>>", lambda e: self.update_select_response(question["question_id"]))
        elif question["type"] == "number":
            self.answer_widget = ttk.Entry(self.main_frame)
            self.answer_widget.grid(row=1, column=0, columnspan=2)
            self.answer_widget.bind("<FocusOut>", lambda e: self.update_number_response(question["question_id"]))

    def update_checkbox_response(self, question_id, option, var):
        """Mettre à jour les réponses pour les questions à choix multiples."""
        if var.get():
            self.responses[question_id].append(option["value"])
        else:
            self.responses[question_id].remove(option["value"])

    def update_select_response(self, question_id):
        """Mettre à jour les réponses pour les questions à choix unique."""
        selected_label = self.answer_widget.get()
        for option in self.questions[self.current_question_index]["options"]:
            if option["label"] == selected_label:
                self.responses[question_id] = option["value"]
                break

    def update_number_response(self, question_id):
        """Mettre à jour les réponses pour les questions numériques."""
        try:
            self.responses[question_id] = int(self.answer_widget.get())
        except ValueError:
            self.responses[question_id] = None

    def next_question(self):
        """Passer à la question suivante."""
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.show_question()
        else:
            self.show_results()

    def prev_question(self):
        """Revenir à la question précédente."""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.show_question()

    def show_results(self):
        """Envoyer les réponses à l'API Flask et afficher les résultats."""
        try:
            # URL de l'API Flask
            api_url = "http://127.0.0.1:5000/eligibilite"

            # Envoyer les réponses sous forme de JSON
            response = requests.post(api_url, json=self.responses)

            # Vérifier la réponse de l'API
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    result_text = "Résultats basés sur vos réponses :\n" + "\n".join(f"- {result}" for result in results)
                else:
                    result_text = "Aucune éligibilité détectée."
            else:
                result_text = f"Erreur de l'API : {response.json().get('error', 'Erreur inconnue')}"

        except Exception as e:
            result_text = f"Erreur lors de la communication avec l'API : {str(e)}"

        # Afficher les résultats dans une boîte de dialogue
        messagebox.showinfo("Résultats", result_text)
        self.root.quit()

    def convert_responses_to_facts(self):
        """Convert user responses to Experta facts."""
        facts = []
        for question_id, response in self.responses.items():
            if isinstance(response, list):
                for value in response:
                    facts.append(Profil(**{question_id: value}))
            else:
                facts.append(Profil(**{question_id: response}))
        return facts

if __name__ == "__main__":
    app.run(debug=True)
    app = ResidencePermitApp(root, "schemas/questions.json")

