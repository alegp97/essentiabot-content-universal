"""Explicit per-process Instagram configuration; no file discovery."""
import os

def refresh():
    global INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '')
    INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '')

refresh()
