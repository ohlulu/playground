#!make
.DEFAULT_GOAL 	:= push

.PHONY: push
push:
	@git add .
	@git commit -m "Syncup"
	@git push
	@printf "${GREEN}🚀 Pushed${NC}\n\n"


### ----------------------- Helper ----------------------- ###

NC    	= \033[0m
GREEN 	= \033[0;32m
BLUE 	= \033[0;34m
RED 	= \033[0;31m
YELLOW	= \033[1;33m