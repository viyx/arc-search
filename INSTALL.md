# Installation Guide

Follow these steps to set up and run the project:

## Step 1: Install SWI-Prolog

1. Download and install `swipl` from the [official SWI-Prolog website](https://www.swi-prolog.org/Download.html).
2. Install `aleph` package in terminal:
   ```bash
   swipl -g 'pack_install(aleph)'
   ```
3. Check installation (command should quit without errors):
    ```bash
    swipl -g 'use_module(library(aleph))',halt
    ```
This project has been tested with `SWI-Prolog version 9.2.8`, but other versions should work fine too

## Step 2: Install Python Dependencies
1. Install the required Python packages using `pip`:
    ```bash
    pip install -r requirements.txt
    ```
This project has been tested with `python 3.10`