# AI-Based Student Academic Advisor System

## Overview

This project is a **Rule-Based Expert System** designed to simulate how an academic advisor evaluates student performance.

The system analyzes key academic indicators such as GPA, attendance, study habits, and assignment completion to generate:

- Academic status
- Risk level
- Personalized advice
- Human-readable explanations

---

## Objectives

- Model expert-level academic decision-making
- Provide explainable and transparent recommendations
- Demonstrate core Artificial Intelligence concepts without using machine learning

---

## Why This is AI

Unlike traditional software that follows fixed instructions, this system:

- Uses a **knowledge base of rules**
- Applies a **forward-chaining inference engine**
- Simulates **human reasoning and decision-making**
- Produces **Explainable AI (XAI)** outputs

---

## Features

- Rule-Based Expert System
- Forward-Chaining Inference Engine
- Explainable AI (XAI)
- Risk Assessment System
- Hierarchical Decision Logic
- Clean CLI Interface
- Optional GUI (Tkinter-based)

---

## System Architecture

### 1. Knowledge Base (`knowledge_base.py`)

- Stores all expert rules
- Defines conditions and outcomes

### 2. Inference Engine (`inference_engine.py`)

- Evaluates rules against input data
- Triggers all applicable rules
- Resolves conflicts using priority

### 3. Reasoning Layer

- Aggregates results
- Generates explanations
- Produces structured output

### 4. Interface Layer

- CLI interface (`main.py`)
- GUI interface (`gui.py`)

---

## Inputs

- GPA (0.0 – 4.0)
- Attendance (%) (0 – 100)
- Study Hours (per day)
- Assignment Completion (Yes/No)

---

## Outputs

- Final Academic Status
- Risk Level (Low / Moderate / High)
- Severity Context (alerts)
- Advice (actionable recommendations)
- Explanation (human-readable reasoning)

---

## ▶️ How to Run

### CLI Version:

```bash
python main.py
```

### GUI Version:

```bash
python gui.py
```
