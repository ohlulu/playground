#!make
.DEFAULT_GOAL := run

# ====== 基礎設定 ====== #
PYTHON = python3
SRC_DIR = src

# Colors for pretty output
NC    	= \033[0m
GREEN 	= \033[0;32m
BLUE 	= \033[0;34m
RED 	= \033[0;31m
YELLOW	= \033[1;33m

# ====== 預設目標 ====== #
.PHONY: run
run:
	@echo "$(BLUE)開始執行主程式...$(NC)"
	NO_JSON=1 $(PYTHON) -m $(SRC_DIR).main

# ====== 安裝依賴 ====== #
.PHONY: install
install:
	@echo "$(BLUE)開始安裝依賴套件...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)依賴套件安裝完成！$(NC)"

# ====== 清理任務 ====== #

# 清理暫存檔案
.PHONY: clean
clean:
	@echo "$(YELLOW)清理暫存檔案中...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".DS_Store" -delete
	@find . -type d -name "*.egg-info" -exec rm -r {} +
	@find . -type f -name "*.egg" -delete
	@echo "$(GREEN)✓ 暫存檔案清理完成！$(NC)"

# 清理分析報告
.PHONY: clean-reports
clean-reports:
	@echo "$(YELLOW)清理分析報告中...$(NC)"
	@rm -rf reports/*
	@rm -rf plots/*
	@echo "$(GREEN)✓ 分析報告清理完成！$(NC)"

# ====== 幫助信息 ====== #
.PHONY: help
help:
	@echo "$(BLUE)=============================="
	@echo "     可用的 make 指令列表"
	@echo "==============================$(NC)"
	@echo "$(GREEN)基本操作:$(NC)"
	@echo "  $(YELLOW)make run$(NC)           - 執行主程式"
	@echo "  $(YELLOW)make install$(NC)       - 安裝依賴套件"
	@echo ""
	@echo "$(GREEN)清理任務:$(NC)"
	@echo "  $(YELLOW)make clean$(NC)         - 清理暫存檔案"
	@echo "  $(YELLOW)make clean-reports$(NC)  - 清理分析報告"
	@echo ""
	@echo "$(GREEN)其他:$(NC)"
	@echo "  $(YELLOW)make help$(NC)          - 顯示此幫助信息"
	@echo "$(BLUE)==============================$(NC)"