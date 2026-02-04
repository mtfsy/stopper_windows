# Variables
NAME = "MyStopper"
SCRIPT = "stopper.py"

# Default task: Build the EXE
build:
	pyinstaller --noconsole --onefile --name $(NAME) $(SCRIPT)

# Clean up PyInstaller's mess (folders and spec file)
clean:
	@if exist build rmdir /s /q build
	@if exist dist rmdir /s /q dist
	@if exist $(NAME).spec del /q $(NAME).spec

# Rebuild from scratch
rebuild: clean build