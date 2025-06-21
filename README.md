# PakAgent

Modular pakdiff workflow system with LLM integration.

## Overview

PakAgent implements a producer-consumer pattern for automated code changes:
- **LLM Loop (Producer)**: Generates pakdiff files using AI
- **Local Loop (Consumer)**: Reviews and applies changes to codebase

## Usage

1. Set your API key in `.env`
2. Run: `poetry run python main_launcher.py`

## Features

- Pakdiff v4.3.0 format support
- Interactive change review
- Robust error handling
- Multi-language support